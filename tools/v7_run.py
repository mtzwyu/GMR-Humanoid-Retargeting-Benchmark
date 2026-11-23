# V7 — chay retarget (headless) va luu pkl DUNG dinh dang cua scripts/bvh_to_robot.py
# de so sha256 voi baseline da co. Dung: python tools\v7_run.py --out results\pkl\v7_x.pkl
import argparse, hashlib, os, pickle, time

import numpy as np

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan1 import load_bvh_file

p = argparse.ArgumentParser()
p.add_argument("--bvh", default="../data/lafan1/walk1_subject1.bvh")
p.add_argument("--robot", default="unitree_g1")
p.add_argument("--out", required=True)
a = p.parse_args()

frames, height = load_bvh_file(a.bvh, format="lafan1")
retargeter = GMR(src_human="bvh_lafan1", tgt_robot=a.robot, actual_human_height=height, verbose=False)

t0 = time.perf_counter()
qpos_list = []
for fr in frames:
    qpos_list.append(retargeter.retarget(fr))
wall = time.perf_counter() - t0

# bvh_to_robot.py khong append frame cuoi (append nam sau buoc tang i va break)
qpos = np.array(qpos_list[:-1])
motion = {
    "fps": 30,
    "root_pos": np.ascontiguousarray(qpos[:, :3]),
    "root_rot": np.ascontiguousarray(qpos[:, 3:7][:, [1, 2, 3, 0]]),   # wxyz -> xyzw
    "dof_pos": np.ascontiguousarray(qpos[:, 7:]),
    "local_body_pos": None,
    "link_body_list": None,
}
with open(a.out, "wb") as f:
    pickle.dump(motion, f)

h = hashlib.sha256(open(a.out, "rb").read()).hexdigest()
n = len(qpos)
print(f"saved {a.out} | frames={n} | wall_s={wall:.3f} | ms_per_frame_process={wall*1000/n:.3f} | sha256={h}")

