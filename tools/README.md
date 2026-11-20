# tools/ — mã của nhóm (Run) cho GMR

Toàn bộ script dùng để **đo, kiểm chứng và dựng bằng chứng** cho báo cáo. Trước đây chúng nằm trong
`third_party/_run/` (bị `.gitignore` chặn nên không vào repo); nay chuyển ra `tools/` để nộp như
"mã của nhóm".

> **Đường dẫn máy:** các script có biến `$root` / `ROOT` trỏ tới
> `C:\Users\xpaga\orca\workspaces\GMR-Humanoid-Retargeting-Benchmark\gmr-run`.
> Chạy trên máy khác thì sửa đúng một dòng đó (và đường dẫn `python` của env `gmr`).
> Repo GMR gốc vẫn nằm ở `third_party/GMR` (không commit), dữ liệu LAFAN1 ở `third_party/data/lafan1`.

## A. Đo thời gian chạy (V3, V5)

| Script | Việc | Cách chạy |
|---|---|---|
| `measure_v3.ps1` | 1 warm-up + N lần đo retarget G1 trên `walk1_subject1.bvh` (**không** `--rate_limit`), mỗi lần ghi dòng `END wall_s=… ms_per_frame_process=… rtf=…` vào **chính file log** của lần đó, xuất `results/v3_raw.csv` | `powershell -File tools\measure_v3.ps1 -Warmup 1 -Measured 5 -StartIndex 1` |
| `build_csv.ps1` | Gộp `results/v3_raw.csv` → `results/v3_runtime.csv`, in mean/median/sd/CV | `powershell -File tools\build_csv.ps1` |
| `measure_v5.ps1` | V5 sim2sim: mỗi robot 1 warm-up + N lần đo (mặc định PM01 → T1 29dof → G1 để loại trừ thermal), ghi nhiệt độ GPU + dòng `END`, xuất `results/v5_raw.csv` | `powershell -File tools\measure_v5.ps1 -RobotList "engineai_pm01,booster_t1_29dof,unitree_g1" -Measured 3` |
| `build_v5.ps1` | Gộp `results/v5_raw.csv` → `results/v5_sim2sim.csv` (thêm dòng H1 `blocked`), in mean/median/CV từng robot | `powershell -File tools\build_v5.ps1` |

Chạy bổ sung cho một robot có CV > 5 %: `-Warmup 0 -Measured 2 -StartIndex 5 -Append`.

## B. Đo độ bền theo nhiễu (V6)

| Script | Việc | Cách chạy |
|---|---|---|
| `v6_run.py` | Chạy **một** điều kiện nhiễu hoặc bản sạch; lặp lại đúng vòng retarget của `bvh_to_robot.py` nhưng không mở viewer. `--mode clean|n1|n2|n3|n4` (N1 cộng Gaussian vào kênh rotation; N2 dịch frame; N3 bỏ frame + nội suy; N4 scale vị trí khớp) | `python tools\v6_run.py --mode n1 --level 2 --seed 0 --out results\pkl\v6_n1_2deg.pkl` |
| `v6_all.ps1` | Chạy lần lượt 15 mức của 4 phép thử | `powershell -File tools\v6_all.ps1` |
| `v6_metrics.py` | Tính `dq_mean`, `dq_max`, `dr_rmse_mm`, `pct_frames_gt5deg`, `still_converges`, cộng `n_saturated_frames`, `n_frames_hit_limit_max`, `max_dev_frame_index` so với baseline; N2 so **đúng cặp frame** (dịch kết quả đi k frame) | `python tools\v6_metrics.py --baseline <pkl> --cond "n1|2|results/pkl/v6_n1_2deg.pkl|0" ... --csv results\v6_noise_sweep.csv` |
| `v6_plot.py` | Đồ thị 3 panel ngang (bản dùng cho báo cáo in): `dq_mean`, `pct>5°`, `n_saturated_frames` | `python tools\v6_plot.py` |
| `v6_plot_slide.py` | Bản **2000×1125 (16:9), 3 panel xếp dọc, chữ ≥ 18 pt** cho slide/video | `python tools\v6_plot_slide.py` |

> **Phải chạy `v6_run.py` từ `third_party/GMR`** (tham số `--bvh` mặc định là `../data/lafan1/...`):
> `cd third_party\GMR` rồi `python ..\..\tools\v6_run.py --mode n1 --level 2 --seed 0 --out ..\..\results\pkl\v6_n1_2deg.pkl`.
> `v6_all.ps1` đã trỏ đúng `tools\v6_run.py` và tự `Set-Location` vào `third_party\GMR`.

## C. Phân tích tư thế & đồ thị thời gian

| Script | Việc | Cách chạy |
|---|---|---|
| `analyze_pose.py` | Đọc pkl, in mean/std của waist/hip/knee/ankle, root_z, kiểm tra quaternion, đồng thời render **một frame chỉ định** ra PNG | `python tools\analyze_pose.py <pkl> <xml> <out.png> 2000` |
| `plot_v3.py` | Vẽ đồ thị V3 (5 lần đo) và V5 (trung vị + min–max) từ CSV | `python tools\plot_v3.py` |
| `v3_evidence_run.ps1` | Chạy **một** lần đo trong cửa sổ console hiển thị để chụp ảnh bằng chứng (in lệnh, thời điểm, kết quả) | `Start-Process powershell -ArgumentList '-NoExit','-File','tools\v3_evidence_run.ps1'` |
| `show_run6_evidence.ps1` | In lại lệnh + dòng `END` + dòng CSV của **lần chạy run6** để chụp ảnh đối chiếu số báo cáo | `Start-Process powershell -ArgumentList '-NoExit','-File','tools\show_run6_evidence.ps1'` |

## D. Ghi video demo

| Script | Việc | Cách chạy |
|---|---|---|
| `record_clip.py` | Ghi clip MP4 16:9 từ một pkl bằng chính `RobotMotionViewer` của repo (thêm `video_width/height`, giới hạn số frame — `scripts/vis_robot_motion.py` chạy `while True` nên không đóng được writer) | `python tools\record_clip.py --robot unitree_g1 --robot_motion_path <pkl> --video_path results\media\x.mp4 --frames 1800` |
| `record_s1.py` | **Không dùng** — ghi bằng viewer của repo; marker người nằm ở scene cửa sổ nên **không vào mp4** | — |
| `record_s1b.py` | Bản thử: robot + marker người trong cùng scene renderer (marker bị robot che) | — |
| `record_s1c.py` | **Bản dùng thật cho cảnh S1**: vẽ bộ xương người + trục khớp 0,1 m từ `retargeter.scaled_human_data` lên sàn phẳng, camera bám `Hips`, 1280×720 30 fps | `python tools\record_s1c.py --start 300 --frames 300 --out results\media\s1_human_input.mp4` |
| `extract_frames.py` | Trích 3 khung 25/50/75 % từ clip → PNG (ffmpeg 9: cần `-update 1`) | `python tools\extract_frames.py <mp4> <tiền_tố> <số_frame>` |

> **`record_s1c.py` cũng phải chạy từ `third_party/GMR`** (tham số `--bvh` mặc định `../data/lafan1/walk1_subject1.bvh`):
> `cd third_party\GMR` rồi `python ..\..\tools\record_s1c.py --start 300 --frames 300 --out ..\..\results\media\s1_human_input.mp4`.

## E. Chất lượng ánh xạ (vế thứ 2 của đề tài: "tốc độ **và chất lượng**")

| Script | Việc | Cách chạy |
|---|---|---|
| `quality_metrics.py` | Tính 4 chỉ số chất lượng trên pkl đã có (**không chạy lại retarget**) | `python tools\quality_metrics.py --out results\v6_quality.csv` |
| `quality_plot.py` | Vẽ 2 panel: `foot_slide` theo robot (cột = trung bình 2 chân, chấm = trái/phải) và `min_body_height` theo robot (có đường 0) | `python tools\quality_plot.py` |

**Định nghĩa từng chỉ số** (nguồn: đặc tả của Planner, 2026-11-21):

1. **`foot_slide_L` / `foot_slide_R` / `foot_slide_mean`** (mm/s)
   Với mỗi bàn chân: một frame là **tiếp đất** khi độ cao thân bàn chân nằm trong **30 mm** so với chính mức thấp nhất của nó trong cả clip.
   Tổng dịch ngang (mặt phẳng xy) giữa các **cặp frame liên tiếp cùng tiếp đất** chia cho tổng thời gian tiếp đất → mm/s.
   Tính riêng chân trái, chân phải; `mean` là trung bình hai chân.
2. **`min_body_height_mm`** (mm) — độ cao **thấp nhất của bất kỳ thân (body) nào** so với mặt đất `z = 0` trong toàn clip. **Âm nghĩa là xuyên sàn**.
3. **`pct_frames_penetration`** (%) — phần trăm frame có **ít nhất 1 thân** dưới mặt đất (`z < -1 mm`).
4. **`joint_limit_violation_pct`** (%) — phần trăm frame có **ít nhất 1 khớp** cách giới hạn `qpos_lo`/`qpos_hi` dưới **0,5°** (dùng lại đúng công cụ của V6).

Thân bàn chân dùng để đo: `unitree_g1` → `left_ankle_roll_link`/`right_ankle_roll_link`; `booster_t1_29dof` → `left_foot_link`/`right_foot_link`; `engineai_pm01` → `LINK_FOOT_L`/`LINK_FOOT_R`; `unitree_h1_2` → `left_ankle_roll_link`/`right_ankle_roll_link`.

`fps` được đọc từ chính pkl (không hardcode 30), nên dùng được cho cả clip Xsens 120 Hz. Đo robot/motion khác: `--robots <tên> --pkl-pattern "results/pkl/<file>.pkl" --out <csv>`.

## F. Tiện ích

| Script | Việc |
|---|---|
| `resolve_conflicts.py` | Gỡ conflict mark trong file markdown khi merge, giữ phần HEAD: `python tools\resolve_conflicts.py <file...>` |
| `make_pkl_sha256.py` | Sinh `results/pkl_sha256.txt`: SHA256 + size + robot + motion + run cho **toàn bộ** pkl trong `results/pkl` (người chấm kiểm chứng tuyên bố tất định mà không cần file pkl nặng) |
| `make_v6_provenance.py` | Sinh `results/v6_provenance.json`: git HEAD của GMR, version numpy/mujoco/mink/torch, input, 15 điều kiện V6 kèm lệnh và kết quả |
| `show_run6_evidence.ps1` | In lại lệnh + dòng `END` + dòng CSV của **lần chạy run6** để chụp ảnh đối chiếu số báo cáo |

## Ghi chú

- `.pkl`, `.mp4` sinh ra bởi các script này **không commit** (đã nằm trong `.gitignore`).
- Số liệu chính thức nằm ở `results/*.csv`; ảnh ở `results/figures/`; lệnh đã chạy ở `logs/lenh_da_chay.md`.
