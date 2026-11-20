# Chat luong anh xa (ve thu 2 cua HR-04): 4 chi so tren pkl da co, KHONG chay lai retarget.
#
# Dinh nghia (ghi trong logs/nhat_ky_cai_dat.md + tools/README.md):
#   foot_slide_mm_per_s  : voi moi ban chan, frame tiep dat = chieu cao than ban chan trong 30 mm
#                          so voi chinh muc thap nhat cua no trong clip; tong dich ngang (xy)
#                          giua cac cap frame lien tiep cung tiep dat / tong thoi gian tiep dat.
#                          Tinh rieng trai/phai roi lay trung binh.
#   min_body_height_mm   : do cao thap nhat cua BAT KY than nao so voi mat dat z=0 trong ca clip.
#                          Am = xuyen san.
#   pct_frames_penetration: % frame co it nhat 1 than duoi mat dat (z < -1 mm).
#   joint_limit_violation_pct: % frame co it nhat 1 khop cach qpos_lo/qpos_hi duoi 0,5 do.
#
# Dung: python tools\quality_metrics.py --out results\v6_quality.csv
import argparse
import csv
import os
import pickle

import mujoco as mj
import numpy as np

from general_motion_retargeting.params import ROBOT_XML_DICT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# than ban chan dung de do foot slide (theo tung model)
FOOT_BODIES = {
    "unitree_g1": ("left_ankle_roll_link", "right_ankle_roll_link"),
    "unitree_g1_with_hands": ("left_ankle_roll_link", "right_ankle_roll_link"),
    "unitree_h1_2": ("left_ankle_roll_link", "right_ankle_roll_link"),
    "booster_t1_29dof": ("left_foot_link", "right_foot_link"),
    "engineai_pm01": ("LINK_FOOT_L", "LINK_FOOT_R"),
}
CONTACT_TOL_MM = 30.0
PENETRATION_MM = -1.0
LIMIT_TOL_DEG = 0.5


def load_pkl(path):
    d = pickle.load(open(path, "rb"))
    fps = float(d.get("fps", 30.0))
    if "qpos" in d:
        return np.asarray(d["qpos"], dtype=float), fps
    return np.concatenate([d["root_pos"], d["root_rot"][:, [3, 0, 1, 2]], d["dof_pos"]], axis=1), fps


def foot_slide_mm_per_s(xyz, fps):
    """xyz: (N,3) vi tri than ban chan (m). Tra ve mm/s."""
    z = xyz[:, 2]
    contact = (z - z.min()) <= CONTACT_TOL_MM / 1000.0
    step = np.linalg.norm(np.diff(xyz[:, :2], axis=0), axis=1) * 1000.0     # mm
    pair = contact[1:] & contact[:-1]
    n_pairs = int(pair.sum())
    if n_pairs == 0:
        return float("nan")
    duration = n_pairs / fps
    return float(step[pair].sum() / duration)


def joint_limit_pct(qpos, model):
    idx, lo, hi = [], [], []
    for j in range(model.njnt):
        if model.jnt_type[j] == mj.mjtJoint.mjJNT_FREE or not model.jnt_limited[j]:
            continue
        idx.append(model.jnt_qposadr[j])
        lo.append(model.jnt_range[j, 0])
        hi.append(model.jnt_range[j, 1])
    q = qpos[:, np.array(idx)]
    sat = (np.abs(q - np.array(lo)) <= np.deg2rad(LIMIT_TOL_DEG)) | \
          (np.abs(q - np.array(hi)) <= np.deg2rad(LIMIT_TOL_DEG))
    return float(100.0 * sat.any(axis=1).mean())


p = argparse.ArgumentParser()
p.add_argument("--robots", default="unitree_g1,booster_t1_29dof,engineai_pm01")
p.add_argument("--pkl-pattern", default="results/pkl/v5_{robot}_walk1_subject1_run1.pkl")
p.add_argument("--out", default="results/v6_quality.csv")
a = p.parse_args()

rows = []
for robot in [r.strip() for r in a.robots.split(",") if r.strip()]:
    pkl_rel = a.pkl_pattern.format(robot=robot)
    pkl = os.path.join(ROOT, pkl_rel)
    qpos, fps = load_pkl(pkl)

    model = mj.MjModel.from_xml_path(str(ROBOT_XML_DICT[robot]))
    data = mj.MjData(model)

    lname, rname = FOOT_BODIES[robot]
    lid, rid = model.body(lname).id, model.body(rname).id
    lpos, rpos, min_h, pen = [], [], [], 0
    for i in range(len(qpos)):
        data.qpos[:] = qpos[i]
        mj.mj_forward(model, data)
        lpos.append(data.xpos[lid].copy())
        rpos.append(data.xpos[rid].copy())
        z = data.xpos[1:, 2]                      # bo world (id 0)
        min_h.append(float(z.min()))
        if (z * 1000.0 < PENETRATION_MM).any():
            pen += 1

    slide_l = foot_slide_mm_per_s(np.array(lpos), fps)
    slide_r = foot_slide_mm_per_s(np.array(rpos), fps)
    rows.append({
        "robot": robot,
        "n_frames": len(qpos),
        "foot_slide_L": round(slide_l, 3),
        "foot_slide_R": round(slide_r, 3),
        "foot_slide_mean": round(float(np.nanmean([slide_l, slide_r])), 3),
        "min_body_height_mm": round(min(min_h) * 1000.0, 3),
        "pct_frames_penetration": round(100.0 * pen / len(qpos), 3),
        "joint_limit_violation_pct": round(joint_limit_pct(qpos, model), 3),
        "pkl": pkl_rel.replace(os.sep, "/"),
        "cmd": f"python tools/quality_metrics.py --robots {robot} --out {a.out}",
    })
    print(f"{robot:18s} slide L={slide_l:8.2f} R={slide_r:8.2f} mean={np.nanmean([slide_l, slide_r]):8.2f} mm/s | "
          f"min_z={min(min_h)*1000:8.2f} mm | pen={100.0*pen/len(qpos):6.2f}% | "
          f"limit={rows[-1]['joint_limit_violation_pct']:6.2f}%")

out = os.path.join(ROOT, a.out)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("wrote", out)
