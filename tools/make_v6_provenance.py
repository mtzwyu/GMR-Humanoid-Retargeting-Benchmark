# Tao results/v6_provenance.json — ghi lai moi thu can de truy vet 15 phep thu nhiem V6.
# Dung: python tools\make_v6_provenance.py [duong_dan_csv]
import csv, json, os, platform, subprocess, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GMR = os.path.join(ROOT, "third_party", "GMR")

import numpy, mujoco, mink, torch
import general_motion_retargeting
from importlib.metadata import version as pkg_version


def ver(name, fallback="n/a"):
    try:
        return pkg_version(name)
    except Exception:                          # noqa: BLE001
        return fallback


def gmr_head():
    try:
        return subprocess.check_output(["git", "-C", GMR, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception as e:                     # noqa: BLE001
        return f"unknown ({e})"


def pkl_name(mode, level):
    """Ten file pkl that su dung trong v6_all.ps1 (de nguoi cham lam theo cmd tim dung file)."""
    lv = float(level)
    if mode == "n1":
        return f"v6_n1_{('%g' % lv).replace('.', 'p')}deg.pkl"
    if mode == "n2":
        return f"v6_n2_k{int(lv)}.pkl"
    if mode == "n3":
        return f"v6_n3_{int(lv)}pct.pkl"
    return f"v6_n4_{'m' if lv < 0 else 'p'}{int(abs(lv))}pct.pkl"


rows = []
csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "v6_noise_sweep.csv")
with open(csv_path, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        name = pkl_name(r["mode"], r["level"])
        rows.append({
            "mode": r["mode"], "level": float(r["level"]), "seed": 0,
            "cmd": (f'python tools/v6_run.py --mode {r["mode"]} --level {r["level"]} --seed 0 '
                    f'--out results/pkl/{name}'),
            "pkl_exists": os.path.exists(os.path.join(ROOT, "results", "pkl", name)),
            "n_frames": int(r["n_frames"]),
            "result": {k: r[k] for k in ("dq_mean", "dq_max", "dr_rmse_mm",
                                         "pct_frames_gt5deg", "still_converges",
                                         "n_saturated_frames", "n_frames_hit_limit_max")},
        })

doc = {
    "experiment": "V6 — 4 phép thử nhiễu (DEC-02, docs/v6_noise_spec.md)",
    "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "gmr": {"repo": "https://github.com/YanjieZe/GMR", "git_head": gmr_head(),
            "license": "MIT"},
    "input": {"bvh": "third_party/data/lafan1/walk1_subject1.bvh",
              "frames": 7840, "fps": 30, "robot": "unitree_g1",
              "baseline_pkl": "results/pkl/g1_walk1_subject1_run1.pkl (SHA256 E7E3B906…)"},
    "env": {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "mujoco": mujoco.__version__,
        "mink": ver("mink"),
        "torch": torch.__version__,
        "general_motion_retargeting": ver("general_motion_retargeting", "0.2.0"),
        "solver": "daqp", "damping": 0.5, "max_iter": 10,
    },
    "driver": "tools/v6_run.py (lặp lại vòng retarget của scripts/bvh_to_robot.py, không mở viewer)",
    "metrics": "tools/v6_metrics.py (so với baseline; N2 so đúng cặp frame)",
    "conditions": rows,
    "notes": [
        "Mỗi mức chạy 1 lần: phép thử đo độ lệch có hệ thống, không đo thời gian.",
        "pkl của từng mức không commit (gitignore); hash pkl xem results/pkl_sha256.txt.",
    ],
}

out = os.path.join(ROOT, "results", "v6_provenance.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("wrote", out, "| conditions:", len(rows), "| gmr:", doc["gmr"]["git_head"])
