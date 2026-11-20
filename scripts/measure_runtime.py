"""Đo thời gian chạy retargeting của GMR (repo YanjieZe/GMR).

Chạy thật cần conda env gmr + quyền mở cửa sổ MuJoCo; chỉ tab Run thực hiện:

    python scripts/measure_runtime.py --motion <file.npz> --robot unitree_g1 booster_t1 \
        --csv results/v3_runtime.csv

Kiểm tra đường ống mà không cần env (dữ liệu giả, không gọi GMR):

    python scripts/measure_runtime.py --dry-run --csv runtime_dryrun.csv

Một dòng CSV = một lần chạy một robot với một motion. Cột `cmd` là lệnh đầy đủ
đã chạy để Review tái lập.
"""

import argparse
import csv
import pickle
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
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
]

# (tên script trong repo GMR, cờ truyền file motion)
ENTRY_SCRIPTS = {
    "smplx": ("smplx_to_robot.py", "--smplx_file"),
    "bvh": ("bvh_to_robot.py", "--bvh_file"),
}

# Chỉ dùng cho --dry-run: coi như đo được 40 fps để số liệu giả ổn định.
DRY_RUN_FPS = 40.0


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


def format_command(cmd):
    """Nối lệnh thành một chuỗi copy-paste được trên Windows và POSIX."""
    return " ".join(f'"{part}"' if " " in part else part for part in cmd)


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


def measure(run_id, robot, motion, args):
    pkl_path = (
        Path(args.work_dir) / f"run{run_id}_{robot}_{Path(motion).stem}.pkl"
    )
    cmd = build_command(
        args.python, args.gmr_dir, args.script, robot, motion, pkl_path
    )

    if args.dry_run:
        write_fake_motion(pkl_path, args.frames)
        wall_s = args.frames / DRY_RUN_FPS
    else:
        start = time.perf_counter()
        subprocess.run(cmd, check=True)
        wall_s = time.perf_counter() - start

    frames = count_frames(pkl_path)
    return {
        "run_id": run_id,
        "robot": robot,
        "motion": str(motion),
        "wall_s": f"{wall_s:.3f}",
        "frames": frames,
        "ms_per_frame": f"{wall_s * 1000.0 / frames:.2f}",
        "fps": f"{frames / wall_s:.2f}",
        "cmd": format_command(cmd),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Do thoi gian chay retargeting GMR va xuat CSV."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dung du lieu gia, khong goi GMR (khong can env gmr).",
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
