# Tao results/v6_provenance.json â€” ghi lai moi thu can de truy vet 15 phep thu nhiem V6.
# Dung: python tools\make_v6_provenance.py
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

rows = []
csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "v6_noise_sweep.csv")
with open(csv_path, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({
            "mode": r["mode"], "level": float(r["level"]), "seed": 0,
            "cmd": (f'python tools/v6_run.py --mode {r["mode"]} --level {r["level"]} --seed 0 '
                    f'--out results/pkl/v6_{r["mode"]}_{r["level"]}.pkl'),
            "n_frames": int(r["n_frames"]),
            "result": {k: r[k] for k in ("dq_mean", "dq_max", "dr_rmse_mm",
                                         "pct_frames_gt5deg", "still_converges",
                                         "n_saturated_frames", "n_frames_hit_limit_max")},
        })

doc = {
    "experiment": "V6 â€” 4 phĂ©p thá»­ nhiá»…u (DEC-02, docs/v6_noise_spec.md)",
    "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "gmr": {"repo": "https://github.com/YanjieZe/GMR", "git_head": gmr_head(),
            "license": "MIT"},
    "input": {"bvh": "third_party/data/lafan1/walk1_subject1.bvh",
              "frames": 7840, "fps": 30, "robot": "unitree_g1",
              "baseline_pkl": "results/pkl/g1_walk1_subject1_run1.pkl (SHA256 E7E3B906â€¦)"},
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
    "driver": "tools/v6_run.py (láº·p láº¡i vĂ²ng retarget cá»§a scripts/bvh_to_robot.py, khĂ´ng má»Ÿ viewer)",
    "metrics": "tools/v6_metrics.py (so vá»›i baseline; N2 so Ä‘Ăºng cáº·p frame)",
    "conditions": rows,
    "notes": [
        "Má»—i má»©c cháº¡y 1 láº§n: phĂ©p thá»­ Ä‘o Ä‘á»™ lá»‡ch cĂ³ há»‡ thá»‘ng, khĂ´ng Ä‘o thá»i gian.",
        "pkl cá»§a tá»«ng má»©c khĂ´ng commit (gitignore); hash pkl xem results/pkl_sha256.txt.",
    ],
}

out = os.path.join(ROOT, "results", "v6_provenance.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print("wrote", out, "| conditions:", len(rows), "| gmr:", doc["gmr"]["git_head"])

