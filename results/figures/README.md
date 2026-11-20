# Ảnh bằng chứng — Nhóm 01 · HR-04 · worktree `gmr-run`

Quy ước: PNG, mỗi ảnh ≤ 1 MB, tên `<nhiệm vụ>_<nội dung>_<yyyy-mm-dd>.png`.
**Toàn bộ ảnh do máy của nhóm chạy ra** (chụp màn hình cửa sổ qua `orca computer`, render offscreen bằng chính mô hình MuJoCo của repo, hoặc trích từ clip do repo ghi) — không dùng ảnh minh hoạ lấy từ repo gốc.
Người chụp/thực hiện: **Đặng Duy Mạnh (Run)**.

## 1. Ảnh terminal — lệnh đo và thời gian

| Ảnh | Nội dung | Lệnh / công cụ sinh ra | Ngày |
|---|---|---|---|
| `v3_terminal_start_g1_2026-11-20.png` | Cửa sổ Windows PowerShell 5.1 hiện lệnh đo đang chạy: máy, thời điểm 22:03:51, env `gmr`, input `lafan1/walk1_subject1.bvh` (7840 frame, 30 fps, 261,3 s), đúng dòng lệnh `python scripts/bvh_to_robot.py ...` — **chèn cho slide "phương pháp đo"** | `Start-Process powershell -ArgumentList '-NoExit','-File', 'tools/v3_evidence_run.ps1'` rồi `orca computer get-app-state --app WindowsTerminal` | 2026-11-20 |
| `v3_terminal_result_g1_2026-11-20.png` | ⚠️ **KHÔNG dùng cho báo cáo.** Ảnh của lần chạy minh hoạ 22:03 (`13,117 ms/frame`, rtf 2,541) — lần chạy đơn, không thuộc lô 5 lần đo. Giữ lại chỉ để minh hoạ quy trình | như trên, chụp lại sau khi tiến trình kết thúc | 2026-11-20 |
| `v3_terminal_run6_2026-11-21.png` | Cửa sổ in lại bằng chứng **lần chạy run6**: lệnh đầy đủ, dòng `END wall_s=135.413 ms_per_frame=17.272 rtf=1.93 frames=7840 exit=0 at=2026-11-20 22:59:59` lấy từ chính `results/logs/v3_walk1_subject1_run6.log`, dòng tương ứng trong `results/v3_runtime.csv` (`phase=measure_5`). Ảnh **chứng minh một lần chạy thật**; dòng cuối trên màn hình ghi rõ: **số chốt của báo cáo là mean `17,349` ms/frame (n = 5, CV 2,13 %)**, 33,333/17,349 = **1,92×**; dòng `END` là của **một** lần chạy | `Start-Process powershell -ArgumentList '-NoExit','-File','tools\show_run6_evidence.ps1'` rồi `orca computer get-app-state --app WindowsTerminal` | 2026-11-21 |

## 2. Ảnh render robot trong MuJoCo

| Ảnh | Nội dung | Lệnh / công cụ sinh ra | Ngày |
|---|---|---|---|
| `v3_render_mujoco_g1_2026-11-20.png` | Cửa sổ MuJoCo `MuJoCo : g1_mocap` đang phát Unitree G1 trong lúc chạy V3 (chụp màn hình cửa sổ thật) — **slide "demo chạy được"** | `python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk4_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ...` + `orca computer get-app-state --app python` | 2026-11-20 |
| `fix_walk4_frame2000_g1_2026-11-20.png` | KI-01: G1 tại frame 2000 của `walk4_subject1` — gập người về trước (waist 29,5°) — **slide "known issue"** | `python tools/analyze_pose.py results/pkl/g1_walk4_no_rate_limit_1.pkl third_party/GMR/assets/unitree_g1/g1_mocap_29dof.xml <ảnh> 2000` | 2026-11-20 |
| `fix_walk4_frame0_g1_2026-11-20.png` | KI-01: G1 tại frame 0 của cùng pkl (tư thế đầu clip) | như trên, frame 0 | 2026-11-20 |
| `fix_walk3_frame2000_g1_2026-11-20.png` | Đối chứng: G1 tại frame 2000 của `walk3_subject1` (waist 25,2°) | `python tools/analyze_pose.py results/pkl/fix_walk3_subject1_unitree_g1.pkl ... 2000` | 2026-11-20 |
| `fix_dance1_frame2000_g1_2026-11-20.png` | Đối chứng: G1 tại frame 2000 của `dance1_subject2` (clip repo đánh dấu `[x]`) | `python tools/analyze_pose.py results/pkl/fix_dance1_g1.pkl ... 2000` | 2026-11-20 |
| `v5_sim2sim_g1_frame2000_2026-11-20.png` | V5: Unitree G1, frame 2000 của `walk1_subject1` — **slide "sim2sim"**. Sinh từ pkl **bản đầu** `results/pkl/v5_unitree_g1_walk1_subject1.pkl` (ảnh tạo 23:03, trước khi đo lại RV-15 lúc 23:18); pkl này có SHA256 **trùng** với `…_run1.pkl` nên nội dung ảnh y hệt | `python tools/analyze_pose.py results/pkl/v5_unitree_g1_walk1_subject1.pkl <xml G1> <ảnh> 2000` | 2026-11-20 |
| `v5_sim2sim_t1_frame2000_2026-11-20.png` | V5: Booster T1 29dof, cùng frame 2000. Sinh từ pkl **bản đầu** `v5_booster_t1_29dof_walk1_subject1.pkl`, SHA256 trùng `…_run1.pkl` (`4E7161873D508ABE…`) | `... v5_booster_t1_29dof_walk1_subject1.pkl <xml T1> ...` | 2026-11-20 |
| `v5_sim2sim_pm01_frame2000_2026-11-20.png` | V5: ENGINEAI PM01, cùng frame 2000. Sinh từ pkl **bản đầu** `v5_engineai_pm01_walk1_subject1.pkl`, SHA256 trùng `…_run1.pkl` (`57B693A8AAC72FE8…`) | `... v5_engineai_pm01_walk1_subject1.pkl <xml PM01> ...` | 2026-11-20 |

## 3. Đồ thị

| Ảnh | Nội dung | Lệnh / công cụ sinh ra | Ngày |
|---|---|---|---|
| `v3_ms_per_frame_g1_2026-11-20.png` | ms/frame theo từng lần đo (5 lần, **không** `--rate_limit`), đường ngưỡng 33,33 ms — **slide "kết quả V3"** | `python tools/plot_v3.py` (đọc `results/v3_runtime.csv`) | 2026-11-20 |
| `v5_ms_per_frame_robots_2026-11-20.png` | ms/frame theo robot cho V5 sim2sim, áp quy tắc §4: **mean** nếu CV ≤ 5 % (PM01 **34,97**, G1 **16,76**), **median** nếu CV > 5 % (T1 29dof **13,03**); thanh sai số = min–max — **slide "sim2sim"** | `python tools/plot_v3.py` (đọc `results/v5_sim2sim.csv`) | 2026-11-21 |
| `v6_noise_vs_deviation.png` | V6: 3 panel — `dq_mean`, `pct_frames_gt5deg`, `n_saturated_frames` (số frame có ≥1 khớp chạm giới hạn ±0,5°, có đường baseline 1865 frame) theo 15 mức nhiễu của 4 phép thử N1–N4 — **slide "độ bền theo nhiễu"** | `python tools/v6_plot.py` (đọc `results/v6_noise_sweep.csv`) | 2026-11-21 |
| `v6_noise_slide.png` | **Bản 16:9 riêng cho slide/video** (2000×1125): 3 panel **xếp dọc**, chữ ≥ 18 pt, nhóm N1–N4 ghi phía trên panel 1, legend 1 hàng ở đáy, có đường baseline 1865 frame — cùng số liệu với hình trên, chỉ vẽ lại cho dễ đọc trên video | `python tools/v6_plot_slide.py` (đọc `results/v6_noise_sweep.csv`) | 2026-11-21 |

## 4. Ảnh mở file CSV kết quả

| Ảnh | Nội dung | Lệnh / công cụ sinh ra | Ngày |
|---|---|---|---|
| `v3_csv_open_notepad_2026-11-20.png` | Notepad đang mở `results/v3_runtime.csv`: thấy header `mode, phase, robot, input, frames, motion_duration_s, wall_clock_s, ms_per_frame_process, realtime_factor, exit_code, cmd, log, note` và các dòng số — **slide "dữ liệu thô"**. *Lưu ý: ảnh chụp từ phiên bản CSV trước RV-13/RV-17 (còn cột `ms_per_frame`), số liệu đã thay đổi sau đó — ảnh chỉ minh hoạ định dạng tệp.* | `Start-Process notepad results\v3_runtime.csv` rồi `orca computer get-app-state --app notepad` | 2026-11-20 |

## 5. Khung ảnh trích từ video demo (25 / 50 / 75 %)

Nguồn: 3 clip trong `results/media/` (60,00 s = 1800 frame, 1280×720). Trích bằng
`python tools/extract_frames.py <mp4> <tiền_tố> 1800`.

| Ảnh | Clip | Frame | Chèn cho slide |
|---|---|---|---|
| `slide_v3_walk1_g1_f450.png` | `v3_walk1_g1.mp4` | 450 (25 %) | V3 — motion chính thức `walk1_subject1`, tư thế đi bộ |
| `slide_v3_walk1_g1_f900.png` | `v3_walk1_g1.mp4` | 900 (50 %) | V3 — motion chính thức, giữa clip |
| `slide_v3_walk1_g1_f1350.png` | `v3_walk1_g1.mp4` | 1350 (75 %) | V3 — motion chính thức, cuối clip |
| `slide_v3_walk4_g1_f450.png` | `v3_walk4_g1.mp4` | 450 (25 %) | KI-01 — minh hoạ clip khom lưng |
| `slide_v3_walk4_g1_f900.png` | `v3_walk4_g1.mp4` | 900 (50 %) | KI-01 — thấy rõ robot gập người |
| `slide_v3_walk4_g1_f1350.png` | `v3_walk4_g1.mp4` | 1350 (75 %) | KI-01 — cuối clip |
| `slide_v5_sim2sim_f450.png` | `v5_sim2sim_g1_t1_pm01.mp4` | 450 (25 %) | Sim2sim — đoạn 1: Unitree G1 |
| `slide_v5_sim2sim_f900.png` | `v5_sim2sim_g1_t1_pm01.mp4` | 900 (50 %) | Sim2sim — đoạn 2: Booster T1 29dof |
| `slide_v5_sim2sim_f1350.png` | `v5_sim2sim_g1_t1_pm01.mp4` | 1350 (75 %) | Sim2sim — đoạn 3: ENGINEAI PM01 |
