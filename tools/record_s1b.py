# S1 — ghi 10 s dau vao CHUYEN DONG NGUOI, co ve diem khop nguoi (human_point_scale = 0.1).
#
# Vi sao khong dung thang RobotMotionViewer.record_video: trong robot_motion_viewer.py,
# diem khop nguoi duoc ve vao `self.viewer.user_scn` (scene cua cua so), con video lai render
# bang mot `mj.Renderer` rieng -> diem nguoi KHONG vao file mp4. Script nay tu dung scene cua
# renderer, ve marker nguoi vao do, roi moi render. Khong sua scripts/ hay thu vien cua repo.
#
# Dung: python record_s1b.py --start 300 --frames 300 --out results/media/s1_human_input.mp4
import argparse

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
from scipy.spatial.transform import Rotation as R

from general_motion_retargeting import ROBOT_BASE_DICT, ROBOT_XML_DICT, VIEWER_CAM_DISTANCE_DICT
from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan1 import load_bvh_file

RGBA = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]


def add_frame(scene, pos, mat, size):
    """Ve 3 truc (X do, Y xanh la, Z xanh duong) tai mot khop nguoi, giong draw_frame cua repo."""
    for i in range(3):
        if scene.ngeom >= scene.maxgeom:
            return
        geom = scene.geoms[scene.ngeom]
        mj.mjv_initGeom(geom, type=mj.mjtGeom.mjGEOM_ARROW, size=[0.01, 0.01, 0.01],
                        pos=pos, mat=mat.flatten(), rgba=RGBA[i])
        mj.mjv_connector(geom, type=mj.mjtGeom.mjGEOM_ARROW, width=0.005,
                         from_=pos, to=pos + size * mat[:, i])
        scene.ngeom += 1


p = argparse.ArgumentParser()
p.add_argument("--bvh", default="../data/lafan1/walk1_subject1.bvh")
p.add_argument("--robot", default="unitree_g1")
p.add_argument("--start", type=int, default=300)
p.add_argument("--frames", type=int, default=300)      # 300 frame @30 fps = 10,00 s
p.add_argument("--out", required=True)
a = p.parse_args()

frames, height = load_bvh_file(a.bvh, format="lafan1")
retargeter = GMR(src_human="bvh_lafan1", tgt_robot=a.robot, actual_human_height=height, verbose=False)

model = mj.MjModel.from_xml_path(str(ROBOT_XML_DICT[a.robot]))
data = mj.MjData(model)
base_body = model.body(ROBOT_BASE_DICT[a.robot]).id

renderer = mj.Renderer(model, height=720, width=1280)
cam = mj.MjvCamera()
cam.type = mj.mjtCamera.mjCAMERA_FREE
cam.elevation = -10
cam.distance = VIEWER_CAM_DISTANCE_DICT[a.robot]

writer = imageio.get_writer(a.out, fps=30)
start = min(a.start, len(frames) - a.frames)
for i in range(start, start + a.frames):
    qpos = retargeter.retarget(frames[i])
    data.qpos[:3] = qpos[:3]
    data.qpos[3:7] = qpos[3:7]
    data.qpos[7:] = qpos[7:]
    mj.mj_forward(model, data)

    cam.lookat[:] = data.xpos[base_body]
    renderer.update_scene(data, camera=cam)
    # ve diem khop nguoi (scaled_human_data) vao chinh scene cua renderer
    for _, (pos, rot) in retargeter.scaled_human_data.items():
        mat = R.from_quat(rot, scalar_first=True).as_matrix()
        add_frame(renderer.scene, np.asarray(pos, dtype=float), mat, 0.1)
    writer.append_data(renderer.render())

writer.close()
print(f"wrote {a.out}: frames {start}..{start + a.frames - 1} ({a.frames / 30:.2f}s), human points = {len(retargeter.scaled_human_data)}")
