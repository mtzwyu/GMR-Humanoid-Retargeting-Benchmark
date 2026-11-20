# V6 — tinh chi so cho tung dieu kien nhieu so voi baseline sach + phan tich bao hoa khop.
# Baseline: pkl cua lan chay sach bang scripts/bvh_to_robot.py (g1_walk1_subject1_run1.pkl).
# Dung:
#   python v6_metrics.py --baseline <pkl> --cond "mode|level|path|shift" ... --csv <out>
import argparse
import csv
import pickle

import numpy as np
import mujoco as mj

from general_motion_retargeting.params import ROBOT_XML_DICT

TOL_DEG = 0.5


def load_qpos(path):
    d = pickle.load(open(path, "rb"))
    if "qpos" in d:
        return d["qpos"], d.get("frames", len(d["qpos"])), d.get("finite", True)
    pos = d["root_pos"]
    rot_xyzw = d["root_rot"]
    quat_wxyz = rot_xyzw[:, [3, 0, 1, 2]]
    q = np.concatenate([pos, quat_wxyz, d["dof_pos"]], axis=1)
    return q, len(q), True


def quat_angle_deg(q1, q2):
    q1 = q1 / np.linalg.norm(q1, axis=1, keepdims=True)
    q2 = q2 / np.linalg.norm(q2, axis=1, keepdims=True)
    dot = np.abs(np.sum(q1 * q2, axis=1))
    return np.degrees(2 * np.arccos(np.clip(dot, -1, 1)))


def limit_arrays(xml):
    """Tra ve (qpos_index, lo, hi) cho cac khop co gioi han (bo qua free joint)."""
    m = mj.MjModel.from_xml_path(xml)
    idx, lo, hi = [], [], []
    for j in range(m.njnt):
        if m.jnt_type[j] == mj.mjtJoint.mjJNT_FREE or not m.jnt_limited[j]:
            continue
        idx.append(m.jnt_qposadr[j])
        lo.append(m.jnt_range[j, 0])
        hi.append(m.jnt_range[j, 1])
    return np.array(idx), np.array(lo), np.array(hi)


a = argparse.ArgumentParser()
a.add_argument("--baseline", required=True)
a.add_argument("--cond", action="append", default=[])
a.add_argument("--csv", required=True)
a.add_argument("--xml", default=str(ROBOT_XML_DICT["unitree_g1"]))
args = a.parse_args()

qidx, qlo, qhi = limit_arrays(args.xml)
tol = np.deg2rad(TOL_DEG)
base, nbase, _ = load_qpos(args.baseline)
rows = []
for spec in args.cond:
    mode, level, path, shift = spec.split("|")
    shift = int(shift)
    q, n, finite = load_qpos(path)
    if shift > 0:
        qq = q[shift:]
        bb = base[: len(qq)]
    else:
        m = min(len(q), len(base))
        qq = q[:m]
        bb = base[:m]
    dq = np.degrees(np.abs(qq[:, 7:] - bb[:, 7:]))
    per_frame = dq.max(axis=1)
    dr = np.linalg.norm(qq[:, :3] - bb[:, :3], axis=1) * 1000.0

    # bao hoa: khop nam trong 0,5 do so voi gioi han tren hoac duoi
    qj = qq[:, qidx]
    sat = (np.abs(qj - qlo) <= tol) | (np.abs(qj - qhi) <= tol)
    n_sat_frames = int((sat.any(axis=1)).sum())
    max_sat_joints = int(sat.sum(axis=1).max()) if len(qq) else 0
    base_sat = ((np.abs(base[:, qidx] - qlo) <= tol) | (np.abs(base[:, qidx] - qhi) <= tol))
    base_n_sat = int(base_sat.any(axis=1).sum())
    base_max_sat = int(base_sat.sum(axis=1).max()) if len(base) else 0

    rows.append(dict(mode=mode, level=level, n_frames=len(qq),
                     dq_mean=round(float(dq.mean()), 4),
                     dq_max=round(float(dq.max()), 4),
                     dr_rmse_mm=round(float(np.sqrt((dr ** 2).mean())), 4),
                     pct_frames_gt5deg=round(float(100.0 * (per_frame > 5.0).mean()), 3),
                     still_converges=1 if (finite and len(qq) > 0) else 0,
                     dq_rootrot_mean=round(float(quat_angle_deg(qq[:, 3:7], bb[:, 3:7]).mean()), 4),
                     n_saturated_frames=n_sat_frames,
                     n_frames_hit_limit_max=max_sat_joints,
                     max_dev_frame_index=int(np.argmax(per_frame)),
                     baseline_n_saturated_frames=base_n_sat,
                     baseline_n_frames_hit_limit_max=base_max_sat))
    print(f"{mode:5s} level={level:>5s} dq_mean={rows[-1]['dq_mean']:8.4f} pct>5={rows[-1]['pct_frames_gt5deg']:7.3f}% "
          f"sat_frames={n_sat_frames:5d} (baseline {base_n_sat:5d}) sat_max={max_sat_joints:2d} "
          f"maxdev_frame={rows[-1]['max_dev_frame_index']:5d}")

with open(args.csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("wrote", args.csv, "| baseline sat_frames =", base_n_sat, "sat_max =", base_max_sat)
