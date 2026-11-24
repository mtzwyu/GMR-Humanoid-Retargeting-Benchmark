# S1 - clip 10 s "chuyen dong NGUOI dau vao" (diem khop + xuong nguoi) cho video demo.
#
# Vi sao khong dung thang RobotMotionViewer.record_video: trong robot_motion_viewer.py cac diem
# khop nguoi duoc ve vao `self.viewer.user_scn` (scene cua CUA SO), con video ghi bang mot
# `mj.Renderer` rieng -> marker nguoi KHONG vao file mp4 (da thu: mp4 chi co robot). Script nay
# dung dung `retargeter.scaled_human_data` (diem khop nguoi sau khi scale theo chieu cao) va ve
# vao scene cua renderer, tren mot san phang toi gian. Khong sua scripts/ hay thu vien cua repo.
#
# Dung: python record_s1c.py --start 300 --frames 300 --out results/media/s1_human_input.mp4
import argparse

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
from scipy.spatial.transform import Rotation as R

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan1 import load_bvh_file

# xuong nguoi (LAFAN1): moi cap noi bang mot hinh tru
BONES = [
    ("Hips", "Spine2"), ("Spine2", "LeftArm"), ("LeftArm", "LeftForeArm"),
    ("LeftForeArm", "LeftHand"), ("Spine2", "RightArm"), ("RightArm", "RightForeArm"),
    ("RightForeArm", "RightHand"), ("Hips", "LeftUpLeg"), ("LeftUpLeg", "LeftLeg"),
    ("LeftLeg", "LeftFootMod"), ("Hips", "RightUpLeg"), ("RightUpLeg", "RightLeg"),
    ("RightLeg", "RightFootMod"),
]
JOINTS = ["Hips", "Spine2", "LeftArm", "RightArm", "LeftLeg", "RightLeg", "LeftFootMod", "RightFootMod"]

FLOOR_XML = """
<mujoco>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight ambient="0.45 0.45 0.45" diffuse="0.55 0.55 0.55" specular="0.1 0.1 0.1"/>
    <quality shadowsize="2048"/>
  </visual>
  <asset>
    <texture name="skybox" type="skybox" builtin="gradient"
             rgb1="0.35 0.52 0.72" rgb2="0.93 0.95 0.98" width="512" height="3072"/>
  </asset>
  <worldbody>
    <light pos="2 -2 4" dir="-0.4 0.4 -1" diffuse="0.5 0.5 0.5"/>
    <geom name="floor" type="plane" size="30 30 0.1" rgba="0.82 0.82 0.84 1"/>
  </worldbody>
</mujoco>
"""


def add_capsule(scene, p0, p1, width, rgba):
    if scene.ngeom >= scene.maxgeom:
        return
    geom = scene.geoms[scene.ngeom]
    mj.mjv_initGeom(geom, type=mj.mjtGeom.mjGEOM_CAPSULE, size=[width, 0, 0],
                    pos=(np.asarray(p0) + np.asarray(p1)) / 2, mat=np.eye(3).flatten(), rgba=rgba)
    mj.mjv_connector(geom, type=mj.mjtGeom.mjGEOM_CAPSULE, width=width, from_=p0, to=p1)
    scene.ngeom += 1


def add_axes(scene, pos, mat, size):
    for i, rgba in enumerate(([1, 0, 0, 1], [0, 0.8, 0, 1], [0, 0.2, 1, 1])):
        if scene.ngeom >= scene.maxgeom:
            return
        geom = scene.geoms[scene.ngeom]
        mj.mjv_initGeom(geom, type=mj.mjtGeom.mjGEOM_ARROW, size=[0.008, 0.008, 0.008],
                        pos=np.asarray(pos), mat=mat.flatten(), rgba=rgba)
        mj.mjv_connector(geom, type=mj.mjtGeom.mjGEOM_ARROW, width=0.006,
                         from_=pos, to=np.asarray(pos) + size * mat[:, i])
        scene.ngeom += 1


p = argparse.ArgumentParser()
p.add_argument("--bvh", default="../data/lafan1/walk1_subject1.bvh")
p.add_argument("--start", type=int, default=300)
p.add_argument("--frames", type=int, default=300)      # 300 frame @30 fps = 10,00 s
p.add_argument("--out", required=True)
a = p.parse_args()

frames, height = load_bvh_file(a.bvh, format="lafan1")
retargeter = GMR(src_human="bvh_lafan1", tgt_robot="unitree_g1", actual_human_height=height, verbose=False)

model = mj.MjModel.from_xml_string(FLOOR_XML)
data = mj.MjData(model)
renderer = mj.Renderer(model, height=720, width=1280)
cam = mj.MjvCamera()
cam.type = mj.mjtCamera.mjCAMERA_FREE
cam.elevation = -5
cam.distance = 3.0
cam.azimuth = 90

writer = imageio.get_writer(a.out, fps=30)
start = min(a.start, len(frames) - a.frames)
if a.frames > len(frames):
    raise SystemExit(f"--frames {a.frames} > số frame của clip ({len(frames)}) — sẽ làm start âm và cắt sai nội dung")
if start < 0:
    raise SystemExit(f"--start {a.start} vượt quá độ dài clip: chỉ còn {len(frames) - a.frames} frame khả dụng")
for i in range(start, start + a.frames):
    retargeter.retarget(frames[i])              # cap nhat scaled_human_data
    human = retargeter.scaled_human_data
    mj.mj_forward(model, data)

    hips = np.asarray(human["Hips"][0], dtype=float)
    cam.lookat[:] = [hips[0], hips[1], 0.9]
    renderer.update_scene(data, camera=cam)
    scene = renderer.scene

    for b0, b1 in BONES:
        if b0 in human and b1 in human:
            add_capsule(scene, np.asarray(human[b0][0], dtype=float),
                        np.asarray(human[b1][0], dtype=float), 0.022, [0.15, 0.45, 0.85, 1])
    # stub "dau" cho de doc dang nguoi (scaled_human_data khong co khop co/dau)
    if "Spine2" in human:
        top = np.asarray(human["Spine2"][0], dtype=float)
        add_capsule(scene, top, top + np.array([0.0, 0.0, 0.18]), 0.042, [0.15, 0.45, 0.85, 1])
    for j in JOINTS:
        if j in human:
            pos, rot = human[j]
            add_axes(scene, np.asarray(pos, dtype=float),
                     R.from_quat(rot, scalar_first=True).as_matrix(), 0.1)
    writer.append_data(renderer.render())

writer.close()
print(f"wrote {a.out}: frames {start}..{start + a.frames - 1} ({a.frames / 30:.2f}s), {len(human)} khop nguoi")


