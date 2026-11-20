"""Test cho scripts/measure_runtime.py.

Chỉ dùng thư viện chuẩn + pytest, KHÔNG import general_motion_retargeting,
KHÔNG cần conda env gmr. Mọi test chạy script qua subprocess đúng như
lệnh mà Review sẽ tái lập.
"""

import csv
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
]


def run_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
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


def test_cmd_column_is_reproducible(tmp_path):
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


STUB_SCRIPT = """
import argparse, pickle, time

parser = argparse.ArgumentParser()
parser.add_argument("--smplx_file")
parser.add_argument("--robot")
parser.add_argument("--save_path")
args = parser.parse_args()

time.sleep(0.05)
data = {"fps": 30, "root_pos": None, "root_rot": None,
        "dof_pos": [[0.0] * 29] * 7, "local_body_pos": None,
        "link_body_list": None}
with open(args.save_path, "wb") as f:
    pickle.dump(data, f)
"""


def test_real_mode_times_entry_script(tmp_path):
    gmr = tmp_path / "gmr"
    (gmr / "scripts").mkdir(parents=True)
    (gmr / "scripts" / "smplx_to_robot.py").write_text(STUB_SCRIPT, encoding="utf-8")
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
    assert int(row["frames"]) == 7
    assert float(row["wall_s"]) >= 0.05
    assert float(row["fps"]) > 0
