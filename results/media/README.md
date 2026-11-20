# Video demo — Nhóm 01 · HR-04 (local, KHÔNG commit)

Quy ước: H.264, **1280×720 (16:9)**, 30 fps, mỗi clip **60,00 s** (1.800 frame).
File `.mp4` nằm trong thư mục này nhưng **đã bị `.gitignore` chặn** (`*.mp4`) — chỉ giữ trên máy, không đẩy lên repo.

Đường dẫn tuyệt đối trên máy nhóm:
`C:\Users\xpaga\orca\workspaces\GMR-Humanoid-Retargeting-Benchmark\gmr-run\results\media\`

| Tệp | pkl nguồn | Lệnh sinh | Thời lượng | Frame đã trích (25 / 50 / 75 %) |
|---|---|---|---|---|
| `v3_walk1_g1.mp4` | `results/pkl/g1_walk1_subject1_no_rate_limit_1.pkl` (G1, walk1_subject1) | `python third_party/_run/record_clip.py --robot unitree_g1 --robot_motion_path <pkl> --video_path results/media/v3_walk1_g1.mp4 --frames 1800 --start 0` | 60,00 s · 1800 frame | 450 / 900 / 1350 |
| `v3_walk4_g1.mp4` | `results/pkl/g1_walk4_no_rate_limit_1.pkl` (G1, walk4_subject1 — clip khom lưng, KI-01) | `python third_party/_run/record_clip.py --robot unitree_g1 --robot_motion_path <pkl> --video_path results/media/v3_walk4_g1.mp4 --frames 1800 --start 0` | 60,00 s · 1800 frame | 450 / 900 / 1350 |
| `v5_sim2sim_g1_t1_pm01.mp4` | 3 pkl `results/pkl/v5_{unitree_g1,booster_t1_29dof,engineai_pm01}_walk1_subject1.pkl` | ghi 3 đoạn 600 frame (`--start 300`) rồi `ffmpeg -f concat -c copy` | 60,00 s · 1800 frame (3 × 20 s) | 450 (G1) / 900 (T1) / 1350 (PM01) |

**Vì sao dùng `third_party/_run/record_clip.py` thay vì chạy trực tiếp `scripts/vis_robot_motion.py`:**
`scripts/vis_robot_motion.py` chạy `while True` và reset `frame_idx` về 0 khi hết motion, nên **không bao giờ gọi `env.close()`** → writer MP4 không được đóng, file hỏng; ngoài ra script không có tham số `video_width/video_height` (mặc định 640×480, không phải 16:9) và không giới hạn số frame.
Wrapper chỉ gọi đúng lớp `RobotMotionViewer` của repo, không sửa dòng nào trong `scripts/`.

**Kiểm tra bằng ffmpeg (số đo thật):**

```
v3_walk1_g1.mp4              Duration: 00:01:00.00 | 1280x720, 30 fps, h264
v3_walk4_g1.mp4              Duration: 00:01:00.00 | 1280x720, 30 fps, h264
v5_sim2sim_g1_t1_pm01.mp4    Duration: 00:01:00.00 | 1280x720, 30 fps, h264
```

Ảnh trích từ video nằm ở `results/figures/slide_*.png` (có commit), caption trong `results/figures/README.md`.
