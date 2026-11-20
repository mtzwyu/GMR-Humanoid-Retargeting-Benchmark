"""Đo thời gian retargeting GMR theo docs/dinh_nghia_phep_do.md và V1 §3.

Một lệnh chạy trọn giao thức (1..N warm-up + M lần đo), xuất 2 file:

  <out>.csv     1 dòng / lần chạy  (hợp đồng §5.1 + cột bắt buộc của V1 §3.3)
  <raw>.csv     1 dòng / frame    (hợp đồng §5.2)

Hai đại lượng tách bạch, không suy ra nhau:

- `ms_per_frame*` (median / mean / p95): chỉ bọc `retargeter.retarget(frame)`.
  Đây là số dùng để kết luận tuyên bố C5.
- `ms_per_frame_process`: wall-clock của cả tiến trình entry script GMR
  (`bvh_to_robot.py` / `smplx_to_robot.py`, gồm khởi tạo, viewer, render, ghi pkl),
  chia cho số frame của clip. Chỉ là cận trên chẩn đoán, không dùng thay `_retarget`.

Chạy thật (tab Run, env gmr):

    conda run -n gmr python scripts/measure_runtime.py \
        --motion <walk1_subject1.bvh> --robot unitree_g1 \
        --runs 4 --warmup-runs 1 --warmup-frames 30 \
        --out results/v3_runtime.csv --raw-out results/v3_runtime_raw.csv

Chạy khô, không cần env gmr (dữ liệu giả):

    python scripts/measure_runtime.py --dry-run --runs 4 --warmup-runs 1

Mỗi dòng của file tổng hợp ứng với một process đo; mỗi lần đo là một process mới.
"""

import argparse
import csv
import ctypes
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from platform import machine, processor, python_version, release, system

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_GMR_DIR = REPO_ROOT / "third_party" / "GMR"

# Hợp đồng docs/dinh_nghia_phep_do.md §5.1, sau đó là các cột V1 §3.3 bắt buộc.
SUMMARY_COLUMNS = [
    "run",
    "robot",
    "motion",
    "bvh_file",
    "n_frames",
    "n_warmup_frames",
    "fps_src",
    "ms_per_frame",
    "ms_per_frame_mean",
    "ms_per_frame_p95",
    "fps_out",
    "realtime_factor",
    "t_init_s",
    "cpu",
    "ram_gb",
    "os",
    "python",
    "numpy",
    "mujoco",
    "mink",
    "torch",
    "git_head",
    "cuda_visible",
    "cmd",
    "timestamp",
    "n_frames_total",
    "ms_per_frame_process",
    "fps_out_process",
    "realtime_factor_process",
    "process_cmd",
]

# Hợp đồng §5.2.
RAW_COLUMNS = ["run", "motion", "robot", "frame", "included", "ms"]

# (tên entry script trong repo GMR, cờ truyền file motion)
ENTRY_SCRIPTS = {
    "smplx": ("smplx_to_robot.py", "--smplx_file"),
    "bvh": ("bvh_to_robot.py", "--bvh_file"),
}

# Chỉ dùng cho --dry-run: warm-up frame giả chậm 40 ms, frame tính toán 22 ms,
# mỗi lần chạy cộng 0,5 s overhead khởi tạo + render + ghi pkl.
DRY_RUN_WARMUP_MS = 40.0
DRY_RUN_RETARGET_MS = 22.0
DRY_RUN_OVERHEAD_S = 0.5
DRY_RUN_T_INIT_S = 0.5
DRY_RUN_VERSIONS = {"numpy": "dry-run", "mujoco": "dry-run", "mink": "dry-run", "torch": "dry-run"}


def build_command(python_exe, gmr_dir, script, robot, motion, save_path):
    """Lệnh chạy entry script gốc; dùng cho ms_per_frame_process."""
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
    """Lệnh đo riêng retarget(); giá trị cột `cmd` và cách tái lập số `_retarget`."""
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


def percentile_95(values):
    """Phân vị 95 kiểu nội suy tuyến tính (giống numpy.percentile mặc định)."""
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * 0.95
    low = int(pos)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def summarize_retarget(samples, warmup_frames):
    """median/mean/p95 của t_i sau khi bỏ warm-up frame (docs §1.1, §3)."""
    counted = samples[warmup_frames:]
    if not counted:
        raise SystemExit(
            f"Khong du frame: {len(samples)} mau, bo {warmup_frames} warm-up. "
            "Tang do dai clip hoac giam --warmup-frames."
        )
    return {
        "median": statistics.median(counted),
        "mean": statistics.fmean(counted),
        "p95": percentile_95(counted),
    }


def package_versions():
    """Phiên bản package trong env đang chạy (probe chạy trong env gmr)."""
    found = {}
    for name in ("numpy", "mujoco", "mink", "torch"):
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            found[name] = "not-installed"
    return found


def total_ram_gb():
    if sys.platform == "win32":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        return status.ullTotalPhys / 1024**3

    pages = os.sysconf("SC_PHYS_PAGES")
    page_size = os.sysconf("SC_PAGE_SIZE")
    return pages * page_size / 1024**3


def machine_info():
    try:
        ram_gb = f"{total_ram_gb():.1f}"
    except (AttributeError, OSError, ValueError):
        ram_gb = "unknown"
    return {
        "cpu": processor() or machine(),
        "ram_gb": ram_gb,
        "os": f"{system()} {release()}",
        "python": python_version(),
        "cuda_visible": "",
    }


def git_head(gmr_dir):
    try:
        result = subprocess.run(
            ["git", "-C", str(gmr_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unknown"
    return result.stdout.strip() or "unknown"


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_retarget_probe(args):
    """Chế độ --retarget-only: chạy bên trong env gmr, chỉ bấm giờ retarget()."""
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
        json.dumps(
            {
                "t_init_s": t_init,
                "ms": samples,
                "n_frames_total": len(frames),
                "versions": package_versions(),
            }
        ),
        encoding="utf-8",
    )
    return 0


def script_for(args, motion):
    """Entry script cho từng motion: ưu tiên --script, ngược lại theo đuôi file."""
    if args.script is not None:
        return args.script
    return "bvh" if str(motion).lower().endswith(".bvh") else "smplx"


def measure_run(run, robot, motion, args, info):
    """Đo 1 lần chạy: process thật + probe retarget; trả (summary_row, raw_rows)."""
    script = script_for(args, motion)
    bvh_file = str(motion) if script == "bvh" else ""
    save_path = Path(args.work_dir) / f"run{run}_{robot}_{Path(motion).stem}.pkl"
    probe_json = Path(args.work_dir) / f"run{run}_{robot}_{Path(motion).stem}.json"
    process_cmd = build_command(
        args.python, args.gmr_dir, script, robot, motion, save_path
    )
    probe_cmd = build_probe_command(
        args.python, script, robot, motion, args.gmr_dir, probe_json
    )

    if args.dry_run:
        n_total = args.frames
        samples = [
            DRY_RUN_WARMUP_MS if i < args.warmup_frames else DRY_RUN_RETARGET_MS
            for i in range(n_total)
        ]
        t_init = DRY_RUN_T_INIT_S
        versions = DRY_RUN_VERSIONS
        wall_s = n_total * DRY_RUN_RETARGET_MS / 1000.0 + DRY_RUN_OVERHEAD_S
        cmd = probe_cmd
    else:
        env = subprocess_env(args)
        start = time.perf_counter()
        subprocess.run(process_cmd, check=True, env=env)
        wall_s = time.perf_counter() - start

        subprocess.run(probe_cmd, check=True, env=env)
        payload = json.loads(probe_json.read_text(encoding="utf-8"))
        samples = payload["ms"]
        n_total = payload["n_frames_total"]
        t_init = payload["t_init_s"]
        versions = payload.get("versions", {})
        cmd = probe_cmd

    stats = summarize_retarget(samples, args.warmup_frames)
    fps_out = 1000.0 / stats["median"]
    ms_process = wall_s * 1000.0 / n_total
    fps_process = n_total / wall_s

    summary = {
        "run": run,
        "robot": robot,
        "motion": str(motion),
        "bvh_file": bvh_file,
        "n_frames": len(samples) - args.warmup_frames,
        "n_warmup_frames": args.warmup_frames,
        "fps_src": f"{args.fps_src:g}",
        "ms_per_frame": f"{stats['median']:.1f}",
        "ms_per_frame_mean": f"{stats['mean']:.1f}",
        "ms_per_frame_p95": f"{stats['p95']:.1f}",
        "fps_out": f"{fps_out:.1f}",
        "realtime_factor": f"{fps_out / args.fps_src:.2f}",
        "t_init_s": f"{t_init:.3f}",
        "cpu": info["cpu"],
        "ram_gb": info["ram_gb"],
        "os": info["os"],
        "python": info["python"],
        "numpy": versions.get("numpy", "unknown"),
        "mujoco": versions.get("mujoco", "unknown"),
        "mink": versions.get("mink", "unknown"),
        "torch": versions.get("torch", "unknown"),
        "git_head": info["git_head"],
        "cuda_visible": info["cuda_visible"],
        "cmd": format_command(cmd),
        "timestamp": timestamp(),
        "n_frames_total": n_total,
        "ms_per_frame_process": f"{ms_process:.1f}",
        "fps_out_process": f"{fps_process:.1f}",
        "realtime_factor_process": f"{fps_process / args.fps_src:.2f}",
        "process_cmd": format_command(process_cmd),
    }

    is_warmup_run = run <= args.warmup_runs
    raw = [
        {
            "run": run,
            "motion": str(motion),
            "robot": robot,
            "frame": index,
            "included": 0
            if is_warmup_run or index < args.warmup_frames
            else 1,
            "ms": f"{value:.3f}",
        }
        for index, value in enumerate(samples)
    ]
    return summary, raw


def write_csv(path, columns, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Do thoi gian retargeting GMR: retarget() va ca tien trinh."
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
        "--out",
        "--csv",
        dest="out",
        default=None,
        help="File CSV tong hop (1 dong / lan chay). Alias cu: --csv.",
    )
    parser.add_argument(
        "--raw-out",
        "--raw_out",
        dest="raw_out",
        default=None,
        help="File CSV raw (1 dong / frame). Mac dinh: <out>_raw.csv.",
    )
    parser.add_argument(
        "--motion",
        "--bvh-file",
        "--bvh_file",
        dest="motion",
        nargs="+",
        default=None,
        help="File motion dau vao (.bvh hoac .npz). Alias: --bvh-file.",
    )
    parser.add_argument(
        "--robot",
        nargs="+",
        default=["unitree_g1"],
        help="Ten robot GMR (vd unitree_g1).",
    )
    parser.add_argument(
        "--script",
        choices=sorted(ENTRY_SCRIPTS),
        default=None,
        help="Entry script GMR; mac dinh suy ra tu duoi file motion.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=4,
        help="Tong so lan chay, gom ca warm-up (V1: 4 = 1 warm-up + 3 do).",
    )
    parser.add_argument(
        "--warmup-runs",
        "--warmup_runs",
        dest="warmup_runs",
        type=int,
        default=1,
        help="So lan chay dau bi loai khoi moi phep tinh (mac dinh 1).",
    )
    parser.add_argument(
        "--warmup-frames",
        "--warmup_frames",
        dest="warmup_frames",
        type=int,
        default=30,
        help="So frame dau moi lan chay bi loai khoi thong ke (mac dinh 30).",
    )
    parser.add_argument(
        "--fps-src",
        "--fps_src",
        dest="fps_src",
        type=float,
        default=30.0,
        help="fps phat cua du lieu nguon (LAFAN1 = 30).",
    )
    parser.add_argument(
        "--gmr-dir",
        default=str(DEFAULT_GMR_DIR),
        help="Thu muc clone repo GMR.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python cua env gmr dung de chay entry script va probe.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=300,
        help="So frame cua clip gia (chi --dry-run).",
    )
    parser.add_argument(
        "--work-dir",
        default=None,
        help="Noi ghi file .pkl/.json tam. Mac dinh: thu muc tam.",
    )
    args = parser.parse_args(argv)

    if args.dry_run and args.retarget_only:
        parser.error("--retarget-only khong dung voi --dry-run")
    if args.warmup_frames < 0:
        parser.error("--warmup-frames phai >= 0")
    if args.warmup_runs < 0:
        parser.error("--warmup-runs phai >= 0")
    if args.runs <= args.warmup_runs:
        parser.error("--runs phai lon hon --warmup-runs (can it nhat 1 lan do)")
    if args.fps_src <= 0:
        parser.error("--fps-src phai > 0")

    if args.retarget_only:
        if args.motion is None or args.out_json is None:
            parser.error("--retarget-only can --motion va --out-json")
        if len(args.motion) != 1 or len(args.robot) != 1:
            parser.error("--retarget-only nhan dung 1 --motion va 1 --robot")
        if args.script is None:
            args.script = "bvh" if args.motion[0].lower().endswith(".bvh") else "smplx"
        return args

    if args.motion is None:
        if args.dry_run:
            args.motion = ["fake_motion.bvh"]
        else:
            parser.error("can --motion khi chay that (khong co --dry-run)")

    if args.work_dir is None:
        args.work_dir = tempfile.mkdtemp(prefix="gmr_measure_")
    if args.out is None:
        args.out = (
            str(Path(args.work_dir) / "dry_run.csv")
            if args.dry_run
            else "v3_runtime.csv"
        )
    if args.raw_out is None:
        out_path = Path(args.out)
        args.raw_out = str(out_path.with_name(out_path.stem + "_raw.csv"))

    return args


def main(argv=None):
    args = parse_args(argv)
    if args.retarget_only:
        return run_retarget_probe(args)

    info = machine_info()
    info["git_head"] = git_head(args.gmr_dir)

    summaries, raws = [], []
    for motion in args.motion:
        for robot in args.robot:
            for run in range(1, args.runs + 1):
                summary, raw = measure_run(run, robot, motion, args, info)
                summaries.append(summary)
                raws.extend(raw)

    write_csv(args.out, SUMMARY_COLUMNS, summaries)
    write_csv(args.raw_out, RAW_COLUMNS, raws)
    print(f"Wrote {len(summaries)} runs to {args.out}")
    print(f"Wrote {len(raws)} frame rows to {args.raw_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
