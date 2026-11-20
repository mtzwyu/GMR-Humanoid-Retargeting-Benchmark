"""Test cho scripts/measure_runtime.py.

Chỉ dùng thư viện chuẩn + pytest, KHÔNG import general_motion_retargeting,
KHÔNG cần conda env gmr. Mọi test chạy script qua subprocess đúng như
lệnh mà Review sẽ tái lập.

Hai đại lượng được kiểm riêng:
- `ms_per_frame_retarget`: chỉ bọc `retargeter.retarget(frame)` (theo
  docs/dinh_nghia_phep_do.md §1.1), phải loại thời gian load dữ liệu và
  khởi tạo `GMR(...)`.
- `ms_per_frame_process`: toàn tiến trình GMR (khởi tạo + render + ghi pkl),
  chỉ là số chẩn đoán.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_runtime.py"

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


def test_dry_run_writes_required_columns(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--dry-run",
        "--csv",
        str(out),
        "--robot",
        "unitree_g1",
        "booster_t1",
        "--runs",
        "3",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    header, rows = read_csv(out)
    assert header == COLUMNS
    assert len(rows) == 6  # 2 robot x 3 lần chạy


def test_dry_run_metrics_are_consistent(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--dry-run",
        "--csv",
        str(out),
        "--robot",
        "unitree_g1",
        "--runs",
        "2",
        "--frames",
        "120",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    assert [row["run_id"] for row in rows] == ["1", "2"]
    for row in rows:
        wall_s = float(row["wall_s"])
        frames = int(row["frames"])
        assert frames == 120  # lấy từ file .pkl giả, không phải hằng số
        assert abs(float(row["ms_per_frame"]) - wall_s * 1000.0 / frames) < 0.01
        assert abs(float(row["fps"]) - frames / wall_s) < 0.01
        assert (
            abs(float(row["ms_per_frame_process"]) - wall_s * 1000.0 / frames)
            < 0.05
        )
        # Chỉ bọc retarget() thì luôn nhanh hơn cả tiến trình.
        assert 0 < float(row["ms_per_frame_retarget"]) < float(
            row["ms_per_frame_process"]
        )


def test_cmd_columns_are_reproducible(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--dry-run",
        "--csv",
        str(out),
        "--robot",
        "unitree_g1",
        "--runs",
        "1",
        "--motion",
        "my motion.npz",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    cmd = rows[0]["cmd"]
    assert "smplx_to_robot.py" in cmd
    assert "--smplx_file" in cmd
    assert '"my motion.npz"' in cmd  # đường dẫn có dấu cách vẫn copy-paste được
    assert "--robot unitree_g1" in cmd
    assert "--save_path" in cmd

    retarget_cmd = rows[0]["retarget_cmd"]
    assert "measure_runtime.py" in retarget_cmd
    assert "--retarget-only" in retarget_cmd
    assert '"my motion.npz"' in retarget_cmd


def test_bvh_script_uses_bvh_flag(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--dry-run",
        "--script",
        "bvh",
        "--csv",
        str(out),
        "--robot",
        "unitree_g1",
        "--runs",
        "1",
        "--motion",
        "walk.bvh",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    assert "bvh_to_robot.py" in rows[0]["cmd"]
    assert "--bvh_file" in rows[0]["cmd"]
    assert "--script bvh" in rows[0]["retarget_cmd"]


def test_real_run_requires_motion(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli("--csv", str(out), cwd=tmp_path)

    assert result.returncode != 0
    assert not out.exists()


def test_dry_run_needs_no_gmr_checkout(tmp_path):
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--dry-run",
        "--csv",
        str(out),
        "--gmr-dir",
        str(tmp_path / "khong_ton_tai"),
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert out.exists()


def test_help_works_on_windows_console(tmp_path):
    result = run_cli("--help", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "--dry-run" in result.stdout


STUB_ENTRY = """
import argparse, os, pickle, time

parser = argparse.ArgumentParser()
parser.add_argument("--smplx_file")
parser.add_argument("--robot")
parser.add_argument("--save_path")
args = parser.parse_args()

time.sleep(0.2)
frames = int(os.environ.get("STUB_PKL_FRAMES", "5"))
data = {"fps": 30, "root_pos": None, "root_rot": None,
        "dof_pos": [[0.0] * 29] * frames, "local_body_pos": None,
        "link_body_list": None}
with open(args.save_path, "wb") as f:
    pickle.dump(data, f)
"""

# Package general_motion_retargeting giả: __init__ và load dữ liệu ngủ
# (bị loại khỏi phép đo retarget), chỉ retarget() là được bấm giờ.
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
    return [{}] * int(os.environ.get("FAKE_FRAMES", "60")), 30.0
"""

FAKE_LAFAN1 = """
import os

def load_bvh_file(path, format="lafan1"):
    return [{}] * int(os.environ.get("FAKE_FRAMES", "60")), 1.70
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
    (gmr / "scripts" / "smplx_to_robot.py").write_text(STUB_ENTRY, encoding="utf-8")
    (gmr / "assets").mkdir()
    return gmr


def test_real_mode_times_entry_script(tmp_path):
    gmr = make_fake_gmr(tmp_path)
    out = tmp_path / "runtime.csv"

    result = run_cli(
        "--csv",
        str(out),
        "--gmr-dir",
        str(gmr),
        "--motion",
        "walk.npz",
        "--robot",
        "unitree_g1",
        "--runs",
        "1",
        "--python",
        sys.executable,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    row = rows[0]
    assert int(row["frames"]) == 5
    assert float(row["wall_s"]) >= 0.2
    assert float(row["fps"]) > 0


def test_retarget_column_excludes_init_and_data_loading(tmp_path):
    gmr = make_fake_gmr(tmp_path)
    out = tmp_path / "runtime.csv"
    env = {
        **os.environ,
        "FAKE_INIT_S": "0.3",
        "FAKE_LOAD_S": "0.1",
        "FAKE_FRAMES": "40",
        "FAKE_FAST_S": "0.004",
        "FAKE_SLOW_CALLS": "0",
    }

    result = run_cli(
        "--csv",
        str(out),
        "--gmr-dir",
        str(gmr),
        "--motion",
        "walk.npz",
        "--robot",
        "unitree_g1",
        "--runs",
        "1",
        "--python",
        sys.executable,
        "--warmup-frames",
        "10",
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    retarget_ms = float(rows[0]["ms_per_frame_retarget"])
    process_ms = float(rows[0]["ms_per_frame_process"])
    # Nếu thời gian load (0,1 s) hoặc init (0,3 s) bị tính vào, con số sẽ
    # vượt xa 15 ms/frame; nếu đo cả tiến trình thì ~0,2 s/5 frame = 40 ms.
    assert 1.0 < retarget_ms < 15.0
    assert process_ms > retarget_ms


def test_retarget_median_drops_30_warmup_frames(tmp_path):
    gmr = make_fake_gmr(tmp_path)
    out = tmp_path / "runtime.csv"
    env = {
        **os.environ,
        "FAKE_INIT_S": "0.01",
        "FAKE_LOAD_S": "0.01",
        "FAKE_FRAMES": "60",
        "FAKE_SLOW_CALLS": "30",
        "FAKE_SLOW_S": "0.05",
        "FAKE_FAST_S": "0.002",
    }

    result = run_cli(
        "--csv",
        str(out),
        "--gmr-dir",
        str(gmr),
        "--motion",
        "walk.npz",
        "--robot",
        "unitree_g1",
        "--runs",
        "1",
        "--python",
        sys.executable,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    _, rows = read_csv(out)
    # 30 frame đầu cố tình chậm 50 ms; bỏ chúng đi thì trung vị phải < 20 ms.
    # Nếu quên bỏ warm-up, trung vị của 60 mẫu sẽ ≈ 26 ms.
    assert float(rows[0]["ms_per_frame_retarget"]) < 20.0
