"""Test cho scripts/measure_runtime.py.

Chỉ dùng thư viện chuẩn + pytest, KHÔNG cần conda env gmr, KHÔNG cần mạng.
Test gọi CLI qua subprocess đúng như lệnh Review/Run sẽ chạy.

Hợp đồng được khoá ở đây:
- cột tổng hợp = docs/dinh_nghia_phep_do.md §5.1 + 4 cột bắt buộc của V1 §3.3;
- file raw = §5.2;
- `ms_per_frame*` chỉ đo `retarget()`, `ms_per_frame_process` đo cả tiến trình;
- giao thức 1..N warm-up + M lần đo chạy bằng một lệnh.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_runtime.py"

# Nguyên văn header §5.1 (không đổi thứ tự, không đổi tên).
CONTRACT_5_1 = [
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
]

EXTRA_COLUMNS_V1 = [
    "n_frames_total",
    "ms_per_frame_process",
    "fps_out_process",
    "realtime_factor_process",
    "process_cmd",
]

COLUMNS = CONTRACT_5_1 + EXTRA_COLUMNS_V1
RAW_COLUMNS = ["run", "motion", "robot", "frame", "included", "ms"]


def run_cli(*args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_summary_has_contract_columns_and_full_protocol(tmp_path):
    out = tmp_path / "v3_runtime.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--robot",
        "unitree_g1",
        "--runs",
        "4",
        "--warmup-runs",
        "1",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    header, rows = read_csv(out)
    assert header == COLUMNS
    assert header[: len(CONTRACT_5_1)] == CONTRACT_5_1
    assert [int(row["run"]) for row in rows] == [1, 2, 3, 4]


def test_raw_file_marks_warmup_run_and_warmup_frames(tmp_path):
    out = tmp_path / "summary.csv"
    raw = tmp_path / "raw.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--raw-out",
        str(raw),
        "--runs",
        "4",
        "--warmup-runs",
        "1",
        "--frames",
        "100",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    header, rows = read_csv(raw)
    assert header == RAW_COLUMNS
    assert len(rows) == 4 * 100

    run1 = [row for row in rows if row["run"] == "1"]
    assert {row["included"] for row in run1} == {"0"}  # cả lần warm-up bị loại
    run2 = [row for row in rows if row["run"] == "2"]
    assert [row["included"] for row in run2[:30]] == ["0"] * 30
    assert set(row["included"] for row in run2[30:]) == {"1"}
    assert sum(int(row["included"]) for row in rows) == 3 * 70


def test_retarget_metrics_follow_definition(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--runs",
        "2",
        "--warmup-runs",
        "1",
        "--frames",
        "300",
        "--warmup-frames",
        "30",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    row = rows[0]
    # Dry-run: 30 frame đầu 40 ms (bị loại), 270 frame còn lại đúng 22,0 ms.
    assert int(row["n_frames_total"]) == 300
    assert int(row["n_frames"]) == 270
    assert int(row["n_warmup_frames"]) == 30
    assert row["ms_per_frame"] == "22.0"
    assert row["ms_per_frame_mean"] == "22.0"
    assert row["ms_per_frame_p95"] == "22.0"
    assert row["fps_out"] == "45.5"  # 1000 / 22,0
    assert row["realtime_factor"] == "1.52"  # 45,5 / 30
    assert row["fps_src"] == "30"
    assert row["t_init_s"] == "0.500"
    # Process là đại lượng khác: 300 frame x 22 ms + 0,5 s overhead.
    assert float(row["ms_per_frame_process"]) > float(row["ms_per_frame"])
    assert float(row["realtime_factor_process"]) < float(row["realtime_factor"])


def test_machine_columns_are_filled(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli("--dry-run", "--out", str(out), "--runs", "2", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    row = rows[0]
    for column in ["cpu", "ram_gb", "os", "python", "git_head", "timestamp", "cmd"]:
        assert row[column], column
    for column in ["numpy", "mujoco", "mink", "torch"]:
        assert row[column] == "dry-run", column


def test_v1_style_flags_and_aliases(tmp_path):
    out = tmp_path / "summary.csv"
    raw = tmp_path / "raw.csv"

    result = run_cli(
        "--dry-run",
        "--csv",
        str(out),
        "--raw_out",
        str(raw),
        "--bvh_file",
        "walk1_subject1.bvh",
        "--warmup_runs",
        "1",
        "--warmup_frames",
        "10",
        "--runs",
        "2",
        "--frames",
        "120",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    row = rows[0]
    assert row["bvh_file"] == "walk1_subject1.bvh"  # suy ra --script bvh
    assert "--script bvh" in row["cmd"]
    assert "bvh_to_robot.py" in row["process_cmd"]
    assert int(row["n_warmup_frames"]) == 10
    assert int(row["n_frames"]) == 110
    assert raw.exists()


def test_smplx_has_empty_bvh_file_and_quoted_cmd(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--motion",
        "my motion.npz",
        "--runs",
        "2",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    row = rows[0]
    assert row["bvh_file"] == ""
    assert "measure_runtime.py" in row["cmd"]
    assert "--retarget-only" in row["cmd"]
    assert '"my motion.npz"' in row["cmd"]


def test_mixed_motion_types_use_their_own_entry_script(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--motion",
        "walk.bvh",
        "run.npz",
        "--runs",
        "2",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    bvh_rows = [row for row in rows if row["motion"] == "walk.bvh"]
    npz_rows = [row for row in rows if row["motion"] == "run.npz"]
    assert bvh_rows and npz_rows
    assert bvh_rows[0]["bvh_file"] == "walk.bvh"
    assert npz_rows[0]["bvh_file"] == ""
    assert "bvh_to_robot.py" in bvh_rows[0]["process_cmd"]
    assert "smplx_to_robot.py" in npz_rows[0]["process_cmd"]
    assert "--script bvh" in bvh_rows[0]["cmd"]
    assert "--script smplx" in npz_rows[0]["cmd"]


def test_dry_run_needs_no_gmr_checkout(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli(
        "--dry-run",
        "--out",
        str(out),
        "--gmr-dir",
        str(tmp_path / "khong_ton_tai"),
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert out.exists()


def test_real_run_requires_motion(tmp_path):
    out = tmp_path / "summary.csv"

    result = run_cli("--out", str(out), cwd=tmp_path)

    assert result.returncode != 0
    assert not out.exists()


def test_help_works_on_windows_console(tmp_path):
    result = run_cli("--help", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "--warmup-runs" in result.stdout


STUB_ENTRY = """
import argparse, os, time

parser = argparse.ArgumentParser()
parser.add_argument("--smplx_file")
parser.add_argument("--bvh_file")
parser.add_argument("--robot")
parser.add_argument("--save_path")
args = parser.parse_args()

time.sleep(float(os.environ.get("STUB_S", "0.5")))
"""

FAKE_PKG_INIT = """
import os, time

class GeneralMotionRetargeting:
    _calls = 0

    def __init__(self, src_human, tgt_robot, actual_human_height=None, **kwargs):
        time.sleep(float(os.environ.get("FAKE_INIT_S", "0.30")))

    def retarget(self, human_data):
        idx = type(self)._calls
        type(self)._calls = idx + 1
        slow = idx < int(os.environ.get("FAKE_SLOW_CALLS", "0"))
        key = "FAKE_SLOW_S" if slow else "FAKE_FAST_S"
        time.sleep(float(os.environ.get(key, "0.004")))
        return []
"""

FAKE_SMPL = """
import os, time

def load_smplx_file(path, folder):
    time.sleep(float(os.environ.get("FAKE_LOAD_S", "0.10")))
    return {}, None, None, 1.70

def get_smplx_data_offline_fast(data, body_model, output, tgt_fps=30):
    return [{}] * int(os.environ.get("FAKE_FRAMES", "40")), 30.0
"""

FAKE_LAFAN1 = """
import os

def load_bvh_file(path, format="lafan1"):
    return [{}] * int(os.environ.get("FAKE_FRAMES", "40")), 1.70
"""


def make_fake_gmr(tmp_path):
    gmr = tmp_path / "gmr"
    pkg = gmr / "general_motion_retargeting"
    (pkg / "utils").mkdir(parents=True)
    (pkg / "__init__.py").write_text(FAKE_PKG_INIT, encoding="utf-8")
    (pkg / "utils" / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "utils" / "smpl.py").write_text(FAKE_SMPL, encoding="utf-8")
    (pkg / "utils" / "lafan1.py").write_text(FAKE_LAFAN1, encoding="utf-8")
    (gmr / "scripts").mkdir()
    (gmr / "scripts" / "bvh_to_robot.py").write_text(STUB_ENTRY, encoding="utf-8")
    (gmr / "assets").mkdir()
    return gmr


def test_real_mode_separates_retarget_from_init_and_process(tmp_path):
    gmr = make_fake_gmr(tmp_path)
    out = tmp_path / "summary.csv"
    raw = tmp_path / "raw.csv"
    env = {
        **os.environ,
        "FAKE_INIT_S": "0.3",
        "FAKE_LOAD_S": "0.1",
        "FAKE_FRAMES": "40",
        "FAKE_FAST_S": "0.004",
        "STUB_S": "0.5",
    }

    result = run_cli(
        "--out",
        str(out),
        "--raw-out",
        str(raw),
        "--gmr-dir",
        str(gmr),
        "--motion",
        "walk.bvh",
        "--runs",
        "2",
        "--warmup-runs",
        "0",
        "--warmup-frames",
        "10",
        "--fps-src",
        "60",
        "--python",
        sys.executable,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    assert len(rows) == 2
    row = rows[0]
    retarget_ms = float(row["ms_per_frame"])
    # init 0,3 s + load 0,1 s không được lọt vào t_retarget (nếu lọt: > 100 ms).
    assert 1.0 < retarget_ms < 15.0
    assert float(row["t_init_s"]) > 0.2
    # Cả tiến trình 0,5 s / 40 frame = 12,5 ms/frame > 2 lần retarget.
    assert float(row["ms_per_frame_process"]) > 2 * retarget_ms
    assert int(row["n_frames_total"]) == 40
    assert int(row["n_frames"]) == 30
    assert row["fps_src"] == "60"
    assert abs(
        float(row["realtime_factor"]) - float(row["fps_out"]) / 60.0
    ) < 0.01
    assert row["numpy"]  # phiên bản thật từ env đang chạy (hoặc not-installed)
    _, raw_rows = read_csv(raw)
    assert len(raw_rows) == 2 * 40
    assert sum(int(r["included"]) for r in raw_rows) == 2 * 30


def test_median_drops_warmup_frames_of_each_run(tmp_path):
    gmr = make_fake_gmr(tmp_path)
    out = tmp_path / "summary.csv"
    env = {
        **os.environ,
        "FAKE_INIT_S": "0.01",
        "FAKE_LOAD_S": "0.01",
        "FAKE_FRAMES": "60",
        "FAKE_SLOW_CALLS": "30",
        "FAKE_SLOW_S": "0.05",
        "FAKE_FAST_S": "0.002",
        "STUB_S": "0.01",
    }

    result = run_cli(
        "--out",
        str(out),
        "--gmr-dir",
        str(gmr),
        "--motion",
        "walk.bvh",
        "--runs",
        "1",
        "--warmup-runs",
        "0",
        "--python",
        sys.executable,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    # 30 frame đầu cố tình 50 ms; bỏ đi thì trung vị phải < 20 ms.
    # Nếu quên bỏ, trung vị của 60 mẫu sẽ ~26 ms.
    assert float(rows[0]["ms_per_frame"]) < 20.0
