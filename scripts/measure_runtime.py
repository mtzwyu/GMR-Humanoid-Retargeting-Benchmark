"""Đo thời gian chạy retargeting của GMR (repo YanjieZe/GMR).

Xuất **hai** đại lượng tách biệt, theo docs/dinh_nghia_phep_do.md §1.1:

- `ms_per_frame_retarget`: chỉ bọc `retargeter.retarget(frame)` — trung vị
  trên các frame được tính, bỏ `--warmup-frames` frame đầu. Đây là số dùng
  để kết luận tuyên bố tốc độ.
- `ms_per_frame_process`: cả tiến trình GMR (khởi tạo model + render MuJoCo +
  ghi pkl) chia cho số frame. Chỉ là số chẩn đoán, không dùng để kết luận.

Chạy thật cần conda env gmr + quyền mở cửa sổ MuJoCo; chỉ tab Run thực hiện:

    conda run -n gmr python scripts/measure_runtime.py --motion <file.npz> \
        --robot unitree_g1 --csv measure_runtime.csv

Kiểm tra đường ống mà không cần env (dữ liệu giả, không gọi GMR):

    python scripts/measure_runtime.py --dry-run --csv runtime_dryrun.csv

Một dòng CSV = một lần chạy một robot với một motion.
"""

import argparse
import csv
import json
import os
import pickle
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_GMR_DIR = REPO_ROOT / "third_party" / "GMR"

COLUMNS = [
    "run_id",
    "robot",
    "motion",
    "wall_s",
    "frames",
    "ms_per_frame",
    "fps",
    "cmd",
    "ms_per_frame_retarget",
    "ms_per_frame_process",
    "retarget_cmd",
]

# (tên script trong repo GMR, cờ truyền file motion)
ENTRY_SCRIPTS = {
    "smplx": ("smplx_to_robot.py", "--smplx_file"),
    "bvh": ("bvh_to_robot.py", "--bvh_file"),
}

# Chỉ dùng cho --dry-run: mỗi frame retarget giả 22 ms, cộng 0,5 s overhead
# của khởi tạo + render + ghi pkl để hai cột không bằng nhau.
DRY_RUN_RETARGET_MS = 22.0
DRY_RUN_OVERHEAD_S = 0.5


def build_command(python_exe, gmr_dir, script, robot, motion, save_path):
    """Lệnh đầy đủ để GMR chạy một motion; cũng là giá trị cột `cmd`."""
    script_name, motion_flag = ENTRY_SCRIPTS[script]
    return [
        python_exe,
        str(Path(gmr_dir) / "scripts" / script_name),
        motion_flag,
        str(motion),
        "--robot",
        robot,
        "--save_path",
        str(save_path),
    ]


def build_probe_command(python_exe, script, robot, motion, gmr_dir, out_json):
    """Lệnh đo riêng retarget(); cũng là giá trị cột `retarget_cmd`."""
    return [
        python_exe,
        str(SCRIPT_PATH),
        "--retarget-only",
        "--script",
        script,
        "--motion",
        str(motion),
        "--robot",
        robot,
        "--gmr-dir",
        str(gmr_dir),
        "--out-json",
        str(out_json),
    ]


def format_command(cmd):
    """Nối lệnh thành một chuỗi copy-paste được trên Windows và POSIX."""
    return " ".join(f'"{part}"' if " " in part else part for part in cmd)


def subprocess_env(args):
    """Ép đo trên CPU (docs §2.2) và cho phép import package từ --gmr-dir."""
    env = dict(os.environ)
    env["CUDA_VISIBLE_DEVICES"] = ""
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(args.gmr_dir) + (
        os.pathsep + pythonpath if pythonpath else ""
    )
    return env


def count_frames(pkl_path):
    """Số frame = số phần tử của dof_pos trong file .pkl GMR lưu ra."""
    with open(pkl_path, "rb") as f:
        motion_data = pickle.load(f)
    return len(motion_data["dof_pos"])


def write_fake_motion(pkl_path, frames):
    """Ghi file .pkl giả cùng cấu trúc file thật để test đường đọc frame."""
    motion_data = {
        "fps": 30,
        "root_pos": [[0.0, 0.0, 0.0]] * frames,
        "root_rot": [[0.0, 0.0, 0.0, 1.0]] * frames,
        "dof_pos": [[0.0] * 29] * frames,
        "local_body_pos": None,
        "link_body_list": None,
    }
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl_path, "wb") as f:
        pickle.dump(motion_data, f)


def summarize_retarget_ms(samples, warmup_frames):
    """Trung vị ms/frame sau khi bỏ `warmup_frames` frame đầu (docs §3)."""
    kept = samples[warmup_frames:]
    if not kept:
        raise SystemExit(
            f"Khong du frame: {len(samples)} mau, bo {warmup_frames} warm-up. "
            "Tang do dai motion hoac giam --warmup-frames."
        )
    return statistics.median(kept)


def run_retarget_probe(args):
    """Chế độ --retarget-only: chỉ bấm giờ từng lời gọi retarget().

    Chạy bên trong env gmr nên import GMR ở đây, không import ở đầu file.
    """
    motion = args.motion[0]
    robot = args.robot[0]

    from general_motion_retargeting import GeneralMotionRetargeting as GMR

    if args.script == "smplx":
        from general_motion_retargeting.utils.smpl import (
            get_smplx_data_offline_fast,
            load_smplx_file,
        )

        smplx_data, body_model, smplx_output, human_height = load_smplx_file(
            motion, str(Path(args.gmr_dir) / "assets" / "body_models")
        )
        frames, _ = get_smplx_data_offline_fast(
            smplx_data, body_model, smplx_output, tgt_fps=30
        )
        src_human = "smplx"
    else:
        from general_motion_retargeting.utils.lafan1 import load_bvh_file

        frames, human_height = load_bvh_file(motion)
        src_human = "bvh_lafan1"

    start = time.perf_counter()
    retargeter = GMR(
        src_human=src_human,
        tgt_robot=robot,
        actual_human_height=human_height,
    )
    t_init = time.perf_counter() - start

    samples = []
    for frame in frames:
        start = time.perf_counter()
        retargeter.retarget(frame)
        samples.append((time.perf_counter() - start) * 1000.0)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"t_init_s": t_init, "ms": samples}), encoding="utf-8"
    )
    return 0


def measure(run_id, robot, motion, args):
    stem = Path(motion).stem
    pkl_path = Path(args.work_dir) / f"run{run_id}_{robot}_{stem}.pkl"
    probe_json = Path(args.work_dir) / f"run{run_id}_{robot}_{stem}_retarget.json"
    cmd = build_command(
        args.python, args.gmr_dir, args.script, robot, motion, pkl_path
    )
    probe_cmd = build_probe_command(
        args.python, args.script, robot, motion, args.gmr_dir, probe_json
    )

    if args.dry_run:
        write_fake_motion(pkl_path, args.frames)
        wall_s = args.frames * DRY_RUN_RETARGET_MS / 1000.0 + DRY_RUN_OVERHEAD_S
        retarget_samples = [DRY_RUN_RETARGET_MS] * args.frames
    else:
        env = subprocess_env(args)
        start = time.perf_counter()
        subprocess.run(cmd, check=True, env=env)
        wall_s = time.perf_counter() - start
        subprocess.run(probe_cmd, check=True, env=env)
        retarget_samples = json.loads(probe_json.read_text(encoding="utf-8"))["ms"]

    frames = count_frames(pkl_path)
    retarget_ms = summarize_retarget_ms(retarget_samples, args.warmup_frames)
    return {
        "run_id": run_id,
        "robot": robot,
        "motion": str(motion),
        "wall_s": f"{wall_s:.3f}",
        "frames": frames,
        "ms_per_frame": f"{wall_s * 1000.0 / frames:.2f}",
        "fps": f"{frames / wall_s:.2f}",
        "cmd": format_command(cmd),
        "ms_per_frame_retarget": f"{retarget_ms:.1f}",
        "ms_per_frame_process": f"{wall_s * 1000.0 / frames:.1f}",
        "retarget_cmd": format_command(probe_cmd),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Do thoi gian retargeting GMR: rieng retarget() va ca tien trinh."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dung du lieu gia, khong goi GMR (khong can env gmr).",
    )
    parser.add_argument(
        "--retarget-only",
        action="store_true",
        help="Che do noi bo: chi do retarget() va ghi JSON (chay trong env gmr).",
    )
    parser.add_argument(
        "--out-json",
        default=None,
        help="File JSON ket qua khi --retarget-only.",
    )
    parser.add_argument(
        "--csv",
        default=None,
        help="File CSV dau ra. Mac dinh: thu muc tam khi --dry-run, "
        "nguoc lai la runtime.csv.",
    )
    parser.add_argument(
        "--robot",
        nargs="+",
        default=["unitree_g1", "booster_t1"],
        help="Ten robot GMR (vd unitree_g1 booster_t1).",
    )
    parser.add_argument(
        "--motion",
        nargs="+",
        default=None,
        help="File motion dau vao (.npz cho smplx, .bvh cho bvh).",
    )
    parser.add_argument(
        "--script",
        choices=sorted(ENTRY_SCRIPTS),
        default="smplx",
        help="Entry script cua GMR se chay.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="So lan chay lap lai cho moi (robot, motion) = run_id.",
    )
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=30,
        help="So frame dau bi loai khoi ms_per_frame_retarget (docs §3).",
    )
    parser.add_argument(
        "--gmr-dir",
        default=str(DEFAULT_GMR_DIR),
        help="Thu muc clone repo GMR.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python cua env gmr dung de chay entry script.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=300,
        help="So frame cua motion gia (chi --dry-run).",
    )
    parser.add_argument(
        "--work-dir",
        default=None,
        help="Noi ghi file .pkl tam. Mac dinh: thu muc tam.",
    )
    args = parser.parse_args(argv)

    if args.dry_run and args.retarget_only:
        parser.error("--retarget-only khong dung voi --dry-run")
    if args.warmup_frames < 0:
        parser.error("--warmup-frames phai >= 0")

    if args.retarget_only:
        if args.motion is None or args.out_json is None:
            parser.error("--retarget-only can --motion va --out-json")
        if len(args.motion) != 1 or len(args.robot) != 1:
            parser.error("--retarget-only nhan dung 1 --motion va 1 --robot")
        return args

    if args.dry_run:
        if args.motion is None:
            args.motion = ["fake_motion_1.npz"]
    elif args.motion is None:
        parser.error("can --motion khi chay that (khong co --dry-run)")

    if args.work_dir is None:
        args.work_dir = tempfile.mkdtemp(prefix="gmr_measure_")
    if args.csv is None:
        if args.dry_run:
            args.csv = str(Path(args.work_dir) / "dry_run.csv")
        else:
            args.csv = "runtime.csv"

    return args


def main(argv=None):
    args = parse_args(argv)
    if args.retarget_only:
        return run_retarget_probe(args)

    rows = [
        measure(run_id, robot, motion, args)
        for motion in args.motion
        for robot in args.robot
        for run_id in range(1, args.runs + 1)
    ]

    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
