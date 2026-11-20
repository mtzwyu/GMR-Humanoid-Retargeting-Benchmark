# S1 — ghi 10 s dau vao CHUYEN DONG NGUOI bang viewer cua GMR (co ve diem khop nguoi).
# Khong sua scripts/: lap lai vong retarget cua bvh_to_robot.py va truyen human_motion_data
# (retargeter.scaled_human_data) voi human_point_scale = 0.1, video 1280x720 30 fps.
#
# Dung: python record_s1.py --start 300 --frames 300 --out results/media/s1_human_input.mp4
import argparse

from general_motion_retargeting import RobotMotionViewer
from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan1 import load_bvh_file

p = argparse.ArgumentParser()
p.add_argument("--bvh", default="../data/lafan1/walk1_subject1.bvh")
p.add_argument("--robot", default="unitree_g1")
p.add_argument("--start", type=int, default=300)
p.add_argument("--frames", type=int, default=300)      # 300 frame @30fps = 10,00 s
p.add_argument("--out", required=True)
a = p.parse_args()

frames, height = load_bvh_file(a.bvh, format="lafan1")
retargeter = GMR(src_human="bvh_lafan1", tgt_robot=a.robot, actual_human_height=height, verbose=False)

viewer = RobotMotionViewer(
    robot_type=a.robot,
    motion_fps=30,
    camera_follow=True,
    record_video=True,
    video_path=a.out,
    video_width=1280,
    video_height=720,
)

start = min(a.start, len(frames) - a.frames)
for i in range(start, start + a.frames):
    qpos = retargeter.retarget(frames[i])
    viewer.step(
        root_pos=qpos[:3],
        root_rot=qpos[3:7],
        dof_pos=qpos[7:],
        human_motion_data=retargeter.scaled_human_data,
        human_point_scale=0.1,
        show_human_body_name=False,
        rate_limit=True,
        follow_camera=True,
    )
viewer.close()
print(f"wrote {a.out}: frames {start}..{start + a.frames - 1} ({(a.frames)/30:.2f}s)")
