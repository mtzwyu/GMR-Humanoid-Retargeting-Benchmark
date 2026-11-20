# Demo manifest — video 90 s (V6)

Dựng theo `docs/ke_hoach/video_demo.md` (commit `05cd5da`). Run cung cấp **clip + timecode**; Code cắt/ghép bằng ffmpeg theo bảng dưới.
Mọi clip gốc: **1280×720, 30 fps, H.264, không audio**. `.mp4` **không commit** (đã gitignore) — chỉ nằm trên máy Run ở `results/media/`.

## Bảng cảnh

| Cảnh | File nguồn | start_s | duration_s | Nội dung | Ghi chú |
|---|---|---|---|---|---|
| **S1** | `results/media/s1_human_input.mp4` | 0,0 | 10,0 | **Chuyển động người đầu vào**: bộ xương người + trục khớp (đỏ/xanh lá/xanh dương), đi bộ | Clip **quay mới** bằng dữ liệu người của GMR (`scaled_human_data`, trục khớp dài 0,1 m), lấy frame 300–599 của `walk1_subject1.bvh` |
| **S2** | `results/media/v3_walk1_g1.mp4` | 18,0 | 10,0 | Retarget → Unitree G1, đi bộ nhìn thẳng, thấy rõ sải chân | **Tránh 0–3 s** (còn tư thế T-pose đầu clip) |
| **S3a** | `results/media/v3_walk4_g1.mp4` | 10,0 | 10,0 | KI-01: robot **khom lưng** (clip gốc `walk4_subject1`) | Dùng cho nửa **TRÁI** của cảnh ghép |
| **S3b** | `results/media/v3_walk1_g1.mp4` | 18,0 | 10,0 | Đối chứng: tư thế **chuẩn** (`walk1_subject1`) | Nửa **PHẢI**; cùng độ dài 10 s với S3a |
| **S4a** | `results/media/v5_sim2sim_g1_t1_pm01.mp4` | 5,0 | 10,0 | Sim2sim — **Unitree G1** | Đoạn G1 nằm trong 0–20 s của clip |
| **S4b** | `results/media/v5_sim2sim_g1_t1_pm01.mp4` | 25,0 | 10,0 | Sim2sim — **Booster T1 29dof** | Đoạn T1 nằm trong 20–40 s |
| **S4c** | `results/media/v5_sim2sim_g1_t1_pm01.mp4` | 45,0 | 10,0 | Sim2sim — **ENGINEAI PM01** | Đoạn PM01 nằm trong 40–60 s |

## Bản máy đọc (Code parse khối này)

```csv
shot,source,start_s,duration_s,content,note
S1,results/media/s1_human_input.mp4,0.0,10.0,human input skeleton,recorded from walk1_subject1 frames 300-599
S2,results/media/v3_walk1_g1.mp4,18.0,10.0,retarget to G1 walking,avoid 0-3s T-pose
S3a,results/media/v3_walk4_g1.mp4,10.0,10.0,KI-01 hunched walk,left half
S3b,results/media/v3_walk1_g1.mp4,18.0,10.0,upright reference,right half
S4a,results/media/v5_sim2sim_g1_t1_pm01.mp4,5.0,10.0,sim2sim Unitree G1,segment 0-20s
S4b,results/media/v5_sim2sim_g1_t1_pm01.mp4,25.0,10.0,sim2sim Booster T1 29dof,segment 20-40s
S4c,results/media/v5_sim2sim_g1_t1_pm01.mp4,45.0,10.0,sim2sim ENGINEAI PM01,segment 40-60s
```

## Gợi ý dựng

- Cắt chính xác frame: đặt `-ss` **sau** `-i` (hoặc `-ss` trước `-i` nếu chỉ cần nhanh, sai số < 1 frame): `ffmpeg -i <src> -ss 18 -t 10 -c:v libx264 -crf 20 -an <out>`.
- **S3** (2 cạnh nhau): scale mỗi bên `640:720`, rồi `hstack=inputs=2` → 1280×720.
- **S4** (3 robot cùng lúc, 10 s): lấy S4a/S4b/S4c, scale mỗi đoạn `426:720` (hoặc `640:360` xếp dọc/ngang tuỳ bố cục), rồi `hstack=inputs=3` → 1278×720 (pad 1 px cho chẵn). Nếu muốn tuần tự thì 30 s.
- Phụ đề: `drawtext` font `C\:/Windows/Fonts/segoeui.ttf`, `box=1:boxcolor=black@0.55`, chữ ≥ 36 px.

## Ghi chú về S1 (khác kế hoạch một chi tiết)

Kế hoạch ghi "quay bằng viewer của GMR (có vẽ điểm khớp người, `human_point_scale=0.1`)". Đã thử đúng cách đó: `RobotMotionViewer(record_video=True)` + `human_motion_data=retargeter.scaled_human_data` → **video ra chỉ có robot, không có điểm khớp người**, vì `robot_motion_viewer.py` vẽ marker vào `self.viewer.user_scn` (scene của **cửa sổ**) còn video được ghi bằng một `mj.Renderer` riêng — marker không đi vào file mp4.

Cách đã dùng: `tools/record_s1c.py` lấy **đúng** `retargeter.scaled_human_data` (dữ liệu người sau scale của GMR), vẽ bộ xương + trục khớp dài **0,1 m** vào scene của renderer, trên sàn phẳng, camera bám khớp `Hips`. Vẫn là dữ liệu người của GMR và cùng engine MuJoCo; khác duy nhất là không phải cửa sổ viewer gốc. **Không sửa `scripts/` hay thư viện repo.**

## Số liệu để đặt phụ đề

- S2: **`17,349 ms/frame`** (mean n = 5, CV 2,13 %) → nhanh hơn **1,92×** thời gian thực (33,333 / 17,349). *(1,93× là của một lần chạy riêng `measure_5` = 17,272 ms; 1,96 là của V5 G1 — không dùng cho S2.)*
- S4: T1 29dof **13,0** ms (median, CV 11,3 %) · G1 **16,8** ms (mean, CV 4,6 %) · PM01 **35,0** ms (mean, CV 3,0 %).
- S5 (nếu dùng): `results/figures/v6_noise_vs_deviation.png`.
