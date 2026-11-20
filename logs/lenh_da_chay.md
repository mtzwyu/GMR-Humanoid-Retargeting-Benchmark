# Lệnh đã chạy — GMR (Nhóm 01, HR-04) · worktree `gmr-run`

Mọi lệnh dưới đây chép nguyên văn để tái lập. Shell: **Windows PowerShell 5.1 trên Windows 11**.
Env conda `gmr` tại `C:\Users\xpaga\miniconda3\envs\gmr`; python dùng trực tiếp
`C:\Users\xpaga\miniconda3\envs\gmr\python.exe` (Windows không cần `conda activate`).

## 0. Thông tin môi trường (đo trên máy)

```powershell
conda --version                # conda 26.7.1
python --version               # Python 3.12.10 (base, KHÔNG dùng cho dự án)
git --version                  # git version 2.51.1.windows.1
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
# NVIDIA GeForce RTX 4050 Laptop GPU, 621.14, 6141 MiB  (dự án chạy CPU, GPU không dùng)
```

## 1. Clone repo gốc (không commit — `third_party/` đã nằm trong `.gitignore`)

```powershell
git clone https://github.com/YanjieZe/GMR third_party/GMR
cd third_party/GMR
git rev-parse --short HEAD      # 25f56db
git rev-parse HEAD              # 25f56db79ac411258b377b6d4ccba0c8ff3372ac
Get-Content LICENSE             # MIT, "Copyright 2025 YanjieZe"
```

## 2. Cài đặt (đúng thứ tự README, có 1 bước ghim phiên bản)

```powershell
conda create -n gmr python=3.10 -y
conda activate gmr                               # hoặc gọi thẳng python của env
pip install "proxsuite==0.7.2.post1"             # BẮT BUỘC: proxsuite 0.8.x không có wheel win-64
pip install -e .                                 # trong third_party/GMR
conda install -n gmr -c conda-forge libstdcxx-ng -y   # THẤT BẠI trên win-64 (gói chỉ có cho linux) — xem nhật ký mục 7
```

Chốt môi trường:

```powershell
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" -m pip freeze | Set-Content requirements.txt -Encoding utf8
```

Cổng G1:

```powershell
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" scripts/smplx_to_robot.py --help      # exit 0
```

## 3. Dữ liệu chuyển động

SMPL-X (AMASS/OMOMO) cần license đăng ký tại smpl-x.is.tue.mpg.de → **không dùng được** (nhật ký mục 9).
Đường thay thế: BVH LAFAN1 (Ubisoft La Forge, CC BY-NC-ND 4.0, tải công khai).

```powershell
curl.exe -L -o third_party\data\lafan1.zip https://media.githubusercontent.com/media/ubisoft/ubisoft-laforge-animation-dataset/master/lafan1/lafan1.zip
Expand-Archive -Path third_party\data\lafan1.zip -DestinationPath third_party\data\lafan1 -Force
# 144.051.503 byte zip → 77 file .bvh, 30 fps (Frame Time: 0.033333)
```

## 4. Lệnh retarget dùng chung

```powershell
cd third_party\GMR
# không rate limit
python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/out.pkl
# có rate limit
python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/out.pkl --rate_limit
```

## 5. Đo V3 (1 warm-up + 3 lần đo, KHÔNG dùng `--rate_limit`)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File third_party\_run\measure_v3.ps1   # sinh results\_v3_tmp.csv
powershell -NoProfile -ExecutionPolicy Bypass -File third_party\_run\build_csv.ps1    # gộp thành results\v3_runtime.csv
```

Kiểm tra bản chất cờ `--rate_limit` (không dùng cờ này để đo throughput):

```powershell
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" -c "import time; from loop_rate_limiters import RateLimiter; rl=RateLimiter(frequency=30, warn=False); n=300; t0=time.perf_counter(); [rl.sleep() for _ in range(n)]; dt=time.perf_counter()-t0; print(f'{n/dt:.2f} Hz, {dt/n*1000:.2f} ms/lan')"
# do duoc: 21.42 Hz, 46.68 ms/lan tren Windows
```

Một lần đo lẻ (ví dụ lần đo hiển thị trong ảnh bằng chứng):

```powershell
Measure-Command { python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/g1_walk1_subject1_evidence.pkl }
```

## 6. Đo V5 sim2sim (mỗi robot 1 warm-up + 3 lần đo, PM01 chạy đầu tiên)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File third_party\_run\measure_v5.ps1 -RobotList "engineai_pm01,booster_t1_29dof,unitree_g1" -Measured 3   # sinh results\v5_raw.csv
powershell -NoProfile -ExecutionPolicy Bypass -File third_party\_run\build_v5.ps1    # gộp thành results\v5_sim2sim.csv
```

Ba robot chạy được trên đường BVH: `unitree_g1`, `booster_t1_29dof`, `engineai_pm01`.
`unitree_h1` bị argparse từ chối (exit 2) — lệnh và log:

```powershell
python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_h1 --save_path x.pkl
# error: argument --robot: invalid choice: 'unitree_h1' -> results/logs/v5_h1_blocked.log
```

## 7. Phân tích tư thế + render 1 frame

```powershell
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" third_party\_run\analyze_pose.py <pkl> <xml> <out.png> <frame_index>
# ví dụ
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" third_party\_run\analyze_pose.py results\pkl\g1_walk4_no_rate_limit_1.pkl third_party\GMR\assets\unitree_g1\g1_mocap_29dof.xml results\figures\fix_walk4_frame2000_g1_2026-11-20.png 2000
```

## 8. Đồ thị

```powershell
python third_party\_run\plot_v3.py       # dùng python BASE 3.12 (có matplotlib) — env gmr không cài matplotlib
```

## 9. Video demo + trích khung

```powershell
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" third_party\_run\record_clip.py --robot unitree_g1 --robot_motion_path <pkl> --video_path results\media\v3_walk1_g1.mp4 --frames 1800 --start 0
& "C:\Users\xpaga\miniconda3\envs\gmr\python.exe" third_party\_run\extract_frames.py results\media\v3_walk1_g1.mp4 results\figures\slide_v3_walk1_g1 1800
# ghép 3 đoạn V5 (mỗi đoạn 600 frame) rồi trích khung
ffmpeg -f concat -safe 0 -i results\media\_concat.txt -c copy results\media\v5_sim2sim_g1_t1_pm01.mp4
```

## 10. Ảnh bằng chứng (chụp cửa sổ thật)

```powershell
Start-Process powershell -ArgumentList '-NoExit','-File','<repo>\third_party\_run\v3_evidence_run.ps1'
orca computer get-app-state --app WindowsTerminal --window-id <id> --json     # ảnh terminal
orca computer get-app-state --app python --window-id <id> --json              # ảnh cửa sổ MuJoCo
Start-Process notepad results\v3_runtime.csv
orca computer get-app-state --app notepad --window-id <id> --json             # ảnh mở CSV
```

## 11. V6 — phép thử nhiễu (theo `docs/v6_noise_spec.md`, DEC-02)

Mỗi mức nhiễu chạy **1 lần** (đo độ lệch có hệ thống, **không** đo thời gian).

```powershell
cd third_party\GMR

# baseline sạch (kiểm chứng script cho ra đúng pkl cũ: |Δq| = 0,0000°, dr_rmse = 0,000 mm)
python ..\_run\v6_run.py --mode clean --out ..\..\results\pkl\v6_clean.pkl

# N1 — nhiễu khớp: sigma 0,5 / 1 / 2 / 5 độ, seed 0
python ..\_run\v6_run.py --mode n1 --level 0.5 --seed 0 --out ..\..\results\pkl\v6_n1_0p5deg.pkl
python ..\_run\v6_run.py --mode n1 --level 1   --seed 0 --out ..\..\results\pkl\v6_n1_1deg.pkl
python ..\_run\v6_run.py --mode n1 --level 2   --seed 0 --out ..\..\results\pkl\v6_n1_2deg.pkl
python ..\_run\v6_run.py --mode n1 --level 5   --seed 0 --out ..\..\results\pkl\v6_n1_5deg.pkl

# N2 — trễ điều khiển k = 1 / 2 / 3 / 5 frame
python ..\_run\v6_run.py --mode n2 --level 1 --out ..\..\results\pkl\v6_n2_k1.pkl
python ..\_run\v6_run.py --mode n2 --level 2 --out ..\..\results\pkl\v6_n2_k2.pkl
python ..\_run\v6_run.py --mode n2 --level 3 --out ..\..\results\pkl\v6_n2_k3.pkl
python ..\_run\v6_run.py --mode n2 --level 5 --out ..\..\results\pkl\v6_n2_k5.pkl

# N3 — mất frame p = 1 / 5 / 10 %, seed 0 (bỏ ngẫu nhiên rồi nội suy tuyến tính)
python ..\_run\v6_run.py --mode n3 --level 1  --seed 0 --out ..\..\results\pkl\v6_n3_1pct.pkl
python ..\_run\v6_run.py --mode n3 --level 5  --seed 0 --out ..\..\results\pkl\v6_n3_5pct.pkl
python ..\_run\v6_run.py --mode n3 --level 10 --seed 0 --out ..\..\results\pkl\v6_n3_10pct.pkl

# N4 — lệch tỉ lệ người ±10 % / ±20 % (scale vị trí khớp)
python ..\_run\v6_run.py --mode n4 --level -20 --out ..\..\results\pkl\v6_n4_m20pct.pkl
python ..\_run\v6_run.py --mode n4 --level -10 --out ..\..\results\pkl\v6_n4_m10pct.pkl
python ..\_run\v6_run.py --mode n4 --level 10  --out ..\..\results\pkl\v6_n4_p10pct.pkl
python ..\_run\v6_run.py --mode n4 --level 20  --out ..\..\results\pkl\v6_n4_p20pct.pkl

# Tính 5 chỉ số so với baseline (N2 so ĐÚNG cặp frame: dịch kết quả đi k frame)
python ..\_run\v6_metrics.py --baseline ..\..\results\pkl\g1_walk1_subject1_run1.pkl ^
  --cond "n1|0.5|results/pkl/v6_n1_0p5deg.pkl|0" --cond "n1|1|results/pkl/v6_n1_1deg.pkl|0" ^
  --cond "n1|2|results/pkl/v6_n1_2deg.pkl|0" --cond "n1|5|results/pkl/v6_n1_5deg.pkl|0" ^
  --cond "n2|1|results/pkl/v6_n2_k1.pkl|1" --cond "n2|2|results/pkl/v6_n2_k2.pkl|2" ^
  --cond "n2|3|results/pkl/v6_n2_k3.pkl|3" --cond "n2|5|results/pkl/v6_n2_k5.pkl|5" ^
  --cond "n3|1|results/pkl/v6_n3_1pct.pkl|0" --cond "n3|5|results/pkl/v6_n3_5pct.pkl|0" ^
  --cond "n3|10|results/pkl/v6_n3_10pct.pkl|0" --cond "n4|-20|results/pkl/v6_n4_m20pct.pkl|0" ^
  --cond "n4|-10|results/pkl/v6_n4_m10pct.pkl|0" --cond "n4|10|results/pkl/v6_n4_p10pct.pkl|0" ^
  --cond "n4|20|results/pkl/v6_n4_p20pct.pkl|0" --csv ..\..\results\v6_noise_sweep.csv

# Đồ thị (python BASE 3.12 vì env gmr không cài matplotlib)
python third_party\_run\v6_plot.py
```

Driver `v6_run.py` **không sửa `scripts/`**: nó lặp lại đúng vòng retarget của `bvh_to_robot.py` (cùng `GeneralMotionRetargeting`, cùng loader `lafan1`, cùng `actual_human_height = 1,75`) nhưng bỏ phần mở viewer; baseline vẫn là pkl của lần chạy `bvh_to_robot.py` và đã được kiểm chứng trùng khớp tuyệt đối.

`v6_metrics.py` ghi thêm 2 cột bão hòa (`n_saturated_frames`, `n_frames_hit_limit_max`) + `max_dev_frame_index`, tính bằng `qpos_lo/qpos_hi` của `assets/unitree_g1/g1_mocap_29dof.xml` với dung sai 0,5°.

## Ghi chú tái lập

- `tools/*.ps1|*.py` là script phụ trợ của Run (đo, vẽ, render, ghi video). Nằm trong `third_party/` nên **không commit**; nội dung đã chép trong log này và trong `logs/nhat_ky_cai_dat.md`.
- `results/pkl/*.pkl` và `results/logs/*.log`: pkl bị `.gitignore` chặn (dung lượng), log thì commit.
