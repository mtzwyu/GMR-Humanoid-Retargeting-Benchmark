# V6 — chay 1 dieu kien nhieu (N1..N4) hoac ban sach, khong mo viewer.
# Khong sua scripts/ cua repo: script nay lap lai dung vong retarget cua bvh_to_robot.py
# (cung GeneralMotionRetargeting, cung loader lafan1) nhung bo phan visualize.
#
# Dung:
#   python v6_run.py --mode clean            --out results/pkl/v6_clean.pkl
#   python v6_run.py --mode n1 --level 2     --seed 0 --out results/pkl/v6_n1_2deg.pkl
#   python v6_run.py --mode n2 --level 3     --out results/pkl/v6_n2_k3.pkl
#   python v6_run.py --mode n3 --level 5     --seed 0 --out results/pkl/v6_n3_5pct.pkl
#   python v6_run.py --mode n4 --level -0.2  --out results/pkl/v6_n4_m20.pkl
import argparse
import pickle
import time

import numpy as np
from scipy.spatial.transform import Rotation as R

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan_vendor.extract import read_bvh
import general_motion_retargeting.utils.lafan_vendor.utils as utils

ROT_MAT = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
ROT_QUAT = R.from_matrix(ROT_MAT).as_quat(scalar_first=True)


def load_anim(bvh_file):
    data = read_bvh(bvh_file)
    return data


def frames_from_anim(anim, quats=None, pos=None):
    """Sao lai dung cach load_bvh_file (lafan1.py) dung: global FK -> dict moi frame."""
    quats = anim.quats if quats is None else quats
    pos = anim.pos if pos is None else pos
    grot, gpos = utils.quat_fk(quats, pos, anim.parents)
    n = pos.shape[0]
    frames = []
    for f in range(n):
        res = {}
        for i, bone in enumerate(anim.bones):
            orientation = utils.quat_mul(ROT_QUAT, grot[f, i])
            position = gpos[f, i] @ ROT_MAT.T / 100.0   # cm -> m
            res[bone] = [position, orientation]
        res["LeftFootMod"] = [res["LeftFoot"][0], res["LeftToe"][1]]
        res["RightFootMod"] = [res["RightFoot"][0], res["RightToe"][1]]
        frames.append(res)
    return frames


def perturb_joints(quats, sigma_deg, rng):
    """N1: cong Gaussian(sigma) vao moi kenh rotation (3 truc) cua tung joint, tung frame."""
    n, j, _ = quats.shape
    delta = rng.normal(0.0, np.deg2rad(sigma_deg), size=(n, j, 3))
    out = np.empty_like(quats)
    for f in range(n):
        for i in range(j):
            dq = R.from_rotvec(delta[f, i]).as_quat(scalar_first=True)
            out[f, i] = utils.quat_mul(quats[f, i], dq)
    return out


def shift_frames(frames, k):
    """N2: dich chuoi frame di k (frame t nhan du lieu cua t-k; k frame dau giu frame 0)."""
    out = []
    for t in range(len(frames)):
        src = max(0, t - k)
        out.append(frames[src])
    return out


def drop_and_interpolate(frames, pct, rng):
    """N3: bo ngau nhien pct% frame roi noi suy tuyen tinh (pos) / nlerp (quat) de lap lai."""
    n = len(frames)
    k = int(round(n * pct / 100.0))
    if k <= 0:
        return frames
    drop = np.sort(rng.choice(np.arange(1, n - 1), size=k, replace=False))
    keep = np.setdiff1d(np.arange(n), drop)
    bones = list(frames[0].keys())
    out = []
    for t in range(n):
        if t in keep:
            out.append(frames[t])
            continue
        lo = keep[keep < t].max()
        hi = keep[keep > t].min()
        w = (t - lo) / (hi - lo)
        fr = {}
        for b in bones:
            p0, q0 = frames[lo][b]
            p1, q1 = frames[hi][b]
            p = (1 - w) * np.asarray(p0) + w * np.asarray(p1)
            q = (1 - w) * np.asarray(q0) + w * np.asarray(q1)
            q = q / np.linalg.norm(q)
            fr[b] = [p, q]
        out.append(fr)
    return out


def scale_human(frames, scale):
    """N4: scale vi tri moi khop quanh goc toa do (nguoi cao/thap hon)."""
    out = []
    for fr in frames:
        out.append({b: [np.asarray(p) * scale, q] for b, (p, q) in fr.items()})
    return out


p = argparse.ArgumentParser()
p.add_argument("--mode", required=True, choices=["clean", "n1", "n2", "n3", "n4"])
p.add_argument("--level", type=float, default=0.0)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--bvh", default="../data/lafan1/walk1_subject1.bvh")
p.add_argument("--robot", default="unitree_g1")
p.add_argument("--out", required=True)
a = p.parse_args()

rng = np.random.default_rng(a.seed)
anim = load_anim(a.bvh)
quats, pos = anim.quats.copy(), anim.pos.copy()

t0 = time.time()
if a.mode == "n1":
    quats = perturb_joints(quats, a.level, rng)
frames = frames_from_anim(anim, quats, pos)
human_height = 1.75   # giong lafan1.py

if a.mode == "n2":
    frames = shift_frames(frames, int(a.level))
elif a.mode == "n3":
    frames = drop_and_interpolate(frames, a.level, rng)
elif a.mode == "n4":
    frames = scale_human(frames, 1.0 + a.level / 100.0)

retargeter = GMR(src_human="bvh_lafan1", tgt_robot=a.robot, actual_human_height=human_height, verbose=False)

qpos_list = []
for fr in frames:
    qpos_list.append(np.asarray(retargeter.retarget(fr)))
qpos = np.array(qpos_list)

ok = bool(np.isfinite(qpos).all())
with open(a.out, "wb") as f:
    pickle.dump({"mode": a.mode, "level": a.level, "seed": a.seed, "fps": 30,
                 "qpos": qpos, "frames": len(frames), "finite": ok,
                 "wall_s": round(time.time() - t0, 3)}, f)
print(f"{a.mode} level={a.level} frames={len(frames)} qpos={qpos.shape} finite={ok} wall={time.time()-t0:.1f}s -> {a.out}")
