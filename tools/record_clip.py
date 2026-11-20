# Ghi clip MP4 từ pkl bằng chính RobotMotionViewer của repo (16:9, giới hạn số frame).
# Lý do không dùng trực tiếp scripts/vis_robot_motion.py: script đó chạy `while True` và reset
# frame_idx về 0 nên không bao giờ gọi env.close() -> writer MP4 không được đóng, file hỏng.
# Script này chỉ gọi đúng lớp RobotMotionViewer với video_width/video_height và số frame.
import argparse
import numpy as np

from general_motion_retargeting import RobotMotionViewer, load_robot_motion

p = argparse.ArgumentParser()
p.add_argument("--robot", required=True)
p.add_argument("--robot_motion_path", required=True)
p.add_argument("--video_path", required=True)
p.add_argument("--frames", type=int, default=1800)
p.add_argument("--start", type=int, default=0)
p.add_argument("--width", type=int, default=1280)
p.add_argument("--height", type=int, default=720)
a = p.parse_args()

motion_data, motion_fps, root_pos, root_rot, dof_pos, _, _ = load_robot_motion(
    a.robot_motion_path
)
n = len(root_pos)
start = min(a.start, n - 1)
end = min(start + a.frames, n)

env = RobotMotionViewer(
    robot_type=a.robot,
    motion_fps=motion_fps,
    camera_follow=False,
    record_video=True,
    video_path=a.video_path,
    video_width=a.width,
    video_height=a.height,
)
for i in range(start, end):
    env.step(root_pos[i], root_rot[i], dof_pos[i], rate_limit=True)
env.close()
print(f"wrote {a.video_path}: frames {start}..{end-1} ({end-start} frame, fps={motion_fps})")
