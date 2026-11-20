# GMR — Ánh xạ chuyển động người sang robot hình người

Kiểm chứng tuyên bố "retarget thời gian thực trên CPU" của GMR bằng số đo của nhóm, trên mô phỏng MuJoCo, không cần robot thật.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![MuJoCo](https://img.shields.io/badge/MuJoCo-3.17-1f6feb)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Giai%20%C4%91o%E1%BA%A1n%201%20%C2%B7%20Ho%C3%A0n%20th%C3%A0nh-brightgreen)

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Kết quả chính](#kết-quả-chính)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Yêu cầu và cài đặt](#yêu-cầu-và-cài-đặt)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Tái lập](#tái-lập)
- [Mã của nhóm](#mã-của-nhóm)
- [Kết quả trong `results/`](#kết-quả-trong-results)
- [Hạn chế và ghi chú trung thực](#hạn-chế-và-ghi-chú-trung-thực)
- [Tài liệu](#tài-liệu)
- [Nhóm thực hiện](#nhóm-thực-hiện)
- [Giấy phép và ghi công](#giấy-phép-và-ghi-công)

## Giới thiệu

Đồ án lấy repo mã nguồn mở **GMR** (General Motion Retargeting), chạy lại pipeline trên máy CPU, rồi kiểm chứng lại một tuyên bố định lượng của chính repo. Nhóm đo thời gian retarget chuyển động LAFAN1 sang humanoid, đo chất lượng ánh xạ trên 3 robot, và ghi lại cả những chỗ không tái lập được. Bài báo gốc là arXiv:2510.02252; mọi số trong repo này do nhóm tự đo, không chép từ paper.

## Kết quả chính

| Hạng mục | Kết quả đo của nhóm | Nguồn / cách đọc |
|---|---|---|
| **V3 — tốc độ 1 robot** (Unitree G1, `walk1_subject1.bvh` 7.840 frame, CPU, không `--rate_limit`) | `ms_per_frame_process` = **17,349 ms** (mean, n = 5; median 17,272; CV 2,13 %) → **57,6 FPS** quy đổi, `realtime_factor` ≈ **1,92** | `results/v3_runtime.csv`; 1 warm-up bị loại, 5 lần đo |
| **V5 — sim2sim 3 robot** (cùng một motion) | G1 **16,758 ms** (mean, n = 3) · Booster T1 29dof **13,034 ms** (median, n = 5) · ENGINEAI PM01 **34,975 ms** (mean, n = 3) | `results/v5_sim2sim.csv`; H1 ghi `blocked`, xem `results/v5_h1_note.md` |
| **Chất lượng ánh xạ** (pkl V5, 7.839 frame) | `foot_slide_mean` 49,0 / 83,1 / 118,4 mm/s (ngưỡng nhóm ≤ 50 mm/s: **chỉ G1 đạt**); `pct_frames_penetration` — frame có **gốc body** dưới −1 mm: 0 / 2,13 / 0 %; `min_body_height` +9,9 / −7,6 / +43,8 mm; bão hòa khớp 23,8 / 43,3 / 24,1 % | `results/v6_quality.csv` (G1 / T1 / PM01), ngưỡng theo `docs/quyet_dinh.md` DEC-03 |

**Phép thử nhiễu (V6):** N1 σ = 0,5° → 0,51 % frame lệch > 5°; σ = 2° → **87,74 %**; trễ 1–5 frame và mất 1–10 % frame gần như không đổi (`dq_mean` 0,001°); scale vị trí ±20 % → 90,4–98,0 % frame lệch > 5° (`results/v6_noise_sweep.csv`).

> Cột `ms_per_frame_process` là **wall-clock của cả tiến trình** `bvh_to_robot.py` (nạp BVH, khởi tạo, render, ghi pkl) chia cho số frame — cận trên của thời gian retarget thuần. Ngưỡng 33,33 ms là ngưỡng **nhóm tự đặt** theo nguồn 30 fps, không phải ngưỡng của paper.
>
> `pct_frames_penetration` đo tại **gốc body** (body origin), không đo bề mặt/mesh: 0 % chỉ nghĩa là không có gốc body nào dưới −1 mm, **không** chứng minh bàn chân/geom không xuyên sàn.

## Cấu trúc repo

```text
.
├─ docs/                    tuyên bố V1, định nghĩa phép đo, quyết định, known issues
│  ├─ v1_tuyen_bo.md        câu chốt + 3 bảng paper và lý do không tái lập
│  ├─ dinh_nghia_phep_do.md nguồn sự thật về đại lượng, đơn vị, quy trình đo
│  ├─ known_issues.md       lỗi đang mở, kèm bằng chứng
│  ├─ quyet_dinh.md         DEC-01 (chọn tuyên bố), DEC-02 (sim2sim + nhiễu)
│  └─ ke_hoach/             kế hoạch 4 vai, video demo
├─ logs/                    nhật ký cài đặt, lệnh đã chạy
├─ results/                 CSV/JSON/hash/ảnh bằng chứng (số liệu chính thức)
├─ scripts/                 script của nhóm (đo runtime, dựng video demo)
├─ tools/                   script đo/kiểm chứng/dựng bằng chứng (PowerShell + Python)
├─ report/                  báo cáo giai đoạn 1
├─ .agents/skills/          skill riêng của project cho agent
├─ LICENSE                  MIT License của mã nhóm
├─ requirements.txt         môi trường đường BVH LAFAN1 (đường chính)
├─ requirements-xsens.txt   phụ kiện cho đường Xsens
└─ third_party/             clone GMR + dữ liệu LAFAN1 (KHÔNG commit)
```

## Yêu cầu và cài đặt

- Windows 10/11 hoặc Linux, CPU (không cần GPU), Python **3.10**.
- Repo GMR gốc được ghim ở `25f56db` và cài trực tiếp qua `requirements.txt`.
- Asset robot (MJCF) nằm trong repo GMR; dữ liệu LAFAN1 và `results/pkl/` **không commit** (xem `.gitignore`).

**Đường chính — BVH LAFAN1** (đã chốt, dùng cho mọi số trong README):

```bash
conda create -n gmr python=3.10 -y
conda activate gmr
pip install -r requirements.txt
```

**Đường Xsens** (tuỳ chọn, chỉ khi chạy `xsens_bvh_to_robot.py`): cài **sau** đường chính, vì cần PyQt6 và biến môi trường UTF-8 cho console Windows.

```bash
pip install -r requirements.txt
pip install -r requirements-xsens.txt
# PowerShell: $env:PYTHONIOENCODING = 'utf-8'
```

SMPL-X không nằm trong hai đường trên: body model phải tải riêng và bị chặn bởi license, nên nhóm chỉ dùng đầu vào BVH.

## Bắt đầu nhanh

```powershell
# 1) Repo + môi trường + GMR gốc ghim đúng commit
git clone https://github.com/mtzwyu/GMR-Humanoid-Retargeting-Benchmark.git
cd GMR-Humanoid-Retargeting-Benchmark
git clone https://github.com/YanjieZe/GMR.git third_party/GMR
git -C third_party/GMR checkout 25f56db
conda create -n gmr python=3.10 -y
conda activate gmr
pip install -r requirements.txt

# 2) Chạy GMR gốc: BVH LAFAN1 -> Unitree G1 (cần walk1_subject1.bvh trong third_party/data/lafan1)
New-Item -ItemType Directory -Force -Path results/pkl | Out-Null
python third_party/GMR/scripts/bvh_to_robot.py `
  --bvh_file third_party/data/lafan1/walk1_subject1.bvh `
  --format lafan1 --robot unitree_g1 --save_path results/pkl/g1_walk1.pkl

# 3) Đo runtime: 1 warm-up + 5 lần đo, rồi gộp CSV
powershell -File tools/measure_v3.ps1 -Warmup 1 -Measured 5 -StartIndex 1
powershell -File tools/build_csv.ps1

# 4) Xem kết quả
powershell -Command "Import-Csv results/v3_runtime.csv | Select-Object phase,ms_per_frame_process,realtime_factor | Format-Table"
```

Kiểm tra nhanh `scripts/measure_runtime.py` mà không cần env `gmr`: `python scripts/measure_runtime.py --dry-run`.
Các script trong `tools/` có biến `$root` / `ROOT` trỏ đường dẫn máy nhóm — chạy trên máy khác thì sửa đúng dòng đó.

## Tái lập

| Bằng chứng | Nội dung |
|---|---|
| `results/media/demo_manifest.md` | Timecode 7 shot của video demo (S1–S4c) + khối CSV cho máy đọc; tổng thời lượng thực tế **67 s**, không phải 90 s |
| `results/pkl_sha256.txt` | SHA256 + size + robot/motion/run của **56 pkl**; 40 file nhóm `determinism(RV-23)` chứng minh cùng đầu vào cho cùng kết quả |
| `results/v6_provenance.json` | Git HEAD của GMR (`25f56db`), phiên bản numpy/mujoco/mink/torch, 15 điều kiện V6 kèm lệnh và kết quả |
| `results/logs/*.log` | **20 log** có dòng cuối `END wall_s=… ms_per_frame=… rtf=… frames=… exit=…` để đối chiếu từng dòng CSV (42 log tổng) |

Video demo (mp4) và pkl không commit; chỉ commit manifest, hash, provenance và log. Bản phát hành 720p/540p (67 s): [v1.0-demo](https://github.com/mtzwyu/GMR-Humanoid-Retargeting-Benchmark/releases/tag/v1.0-demo).

## Mã của nhóm

### `tools/` — đo, kiểm chứng, dựng bằng chứng

| Nhóm | Script | Việc |
|---|---|---|
| **A. Đo V3/V5** | `measure_v3.ps1`, `build_csv.ps1` | 1 warm-up + N lần đo G1 trên `walk1_subject1.bvh`, ghi `END` vào log, xuất/gộp `v3_runtime.csv` |
| | `measure_v5.ps1`, `build_v5.ps1` | Sim2sim 3 robot, nhiệt độ GPU, dòng H1 `blocked`, gộp `v5_sim2sim.csv` |
| **B. Nhiễu V6** | `v6_run.py`, `v6_all.ps1` | Chạy 15 điều kiện N1–N4, không mở viewer |
| | `v6_metrics.py`, `v6_plot.py`, `v6_plot_slide.py` | Chỉ số so baseline + đồ thị báo cáo/slide |
| **C. Phân tích** | `analyze_pose.py`, `plot_v3.py` | Đọc pkl, thống kê tư thế, render frame chỉ định; vẽ đồ thị V3/V5 |
| | `v3_evidence_run.ps1`, `show_run6_evidence.ps1` | Chạy/in lại lệnh + số để chụp ảnh bằng chứng |
| **D. Video** | `record_clip.py`, `record_s1c.py` | Ghi clip robot từ pkl; vẽ bộ xương người từ `scaled_human_data` cho cảnh S1 |
| | `record_s1.py`, `record_s1b.py`, `extract_frames.py` | Hai bản thử không dùng; trích khung 25/50/75 % |
| **E. Chất lượng** | `quality_metrics.py`, `quality_plot.py` | 4 chỉ số trên pkl có sẵn (không chạy lại retarget) + đồ thị |
| **F. Tiện ích** | `make_pkl_sha256.py`, `make_v6_provenance.py`, `resolve_conflicts.py` | Sinh hash pkl, provenance V6, gỡ conflict markdown |

### `scripts/` — script của nhóm

| Script | Việc |
|---|---|
| `measure_runtime.py` | Đo **riêng** `retarget()` (median/mean/p95) và **cả tiến trình**, xuất đúng hợp đồng `results/v3_runtime.csv` §5.1 + raw từng frame; có `--dry-run` không cần env |
| `build_demo.py` | Dựng video demo 6 cảnh bằng ffmpeg + PIL theo manifest, xuất 720p/540p + thumbnail, kiểm tra duration/size/audio |

Kèm `scripts/NOTES.md` (cấu trúc `.pkl`, cách gọi script) và `scripts/test_measure_runtime.py` (test không cần env `gmr`).

## Kết quả trong `results/`

| File | Ý nghĩa |
|---|---|
| `v3_runtime.csv` | 1 warm-up + 5 lần đo V3: `ms_per_frame_process`, `realtime_factor`, `cmd`, `log` |
| `v3_raw.csv` | Bản ghi thô từng lần chạy trước khi gộp |
| `v5_sim2sim.csv` | 3 robot × (warm-up + đo) + dòng `unitree_h1` trạng thái `blocked` |
| `v5_raw.csv` | Bản ghi thô V5 (kèm nhiệt độ GPU) |
| `v6_quality.csv` | `foot_slide`, `min_body_height` + `rest_offset`, % xuyên sàn, % bão hòa khớp |
| `v6_noise_sweep.csv` | 15 điều kiện nhiễu N1–N4 với `dq`/`dr` và cờ hội tụ |
| `v6_provenance.json` | Môi trường + lệnh + kết quả từng điều kiện V6 |
| `pkl_sha256.txt` | Hash 56 pkl (kiểm chứng tất định không cần file nặng) |
| `v5_h1_quality.csv`, `v5_h1_note.md` | Chất lượng H1_2 qua Xsens và lý do H1 bị chặn |
| `figures/` | Ảnh bằng chứng: terminal, render MuJoCo, đồ thị, khung video |
| `media/` | Clip demo (local, không commit), `README.md`, `demo_manifest.md` |
| `logs/` | Log từng lần chạy, có dòng `END` để đối chiếu CSV |

## Hạn chế và ghi chú trung thực

1. **Paper không công bố FPS.** Ba bảng của paper đều đo policy đã train, không đo retargeter; con số tốc độ duy nhất là bảng *Speed Benchmark* trong README repo (35–45 FPS trên i9-13900K). Vì vậy báo cáo không được so tốc độ "với paper".
2. **`ms_per_frame_process` là cận trên**, gồm khởi tạo, render và ghi pkl; thời gian retarget thuần chỉ có khi dùng `scripts/measure_runtime.py`. Ngưỡng 33,33 ms do nhóm đặt, không phải của paper.
3. **`foot_slide` là chỉ số proxy.** Định nghĩa "tiếp đất" theo mức thấp nhất của chính bàn chân và đo tại tâm thân bàn chân, nên chỉ dùng **so sánh tương đối** giữa 3 robot, không phải số tuyệt đối.
4. **`min_body_height` phụ thuộc offset nghỉ của model** (G1 +16,1 mm, T1 +36,6 mm, PM01 +45,0 mm). Ngưỡng ±5 mm đặt trước khi đo đã **bị rút** (DEC-03) vì nó đo độ cao gốc body, không đo xuyên sàn; phần thay thế (`pct_frames_penetration`, `min_body_height − rest_offset`) là **hậu kiểm**.
5. **Ngưỡng chất lượng:** một ngưỡng đăng ký trước được **giữ và áp dụng** — `foot_slide ≤ 50 mm/s`, chỉ G1 đạt; một ngưỡng (`min_body_height ±5 mm`) bị rút sau khi đo vì lý do kỹ thuật. Vì vậy kết luận chất lượng chỉ mang tính tương đối, và `pct_frames_penetration` đo tại **gốc body** (không phải bề mặt/mesh): 0 % chỉ là "không có gốc body dưới −1 mm".
6. **V4 — không huấn luyện.** GMR là retargeting dựa trên tối ưu (mink + MuJoCo), không phải RL, không có checkpoint để train; V4 được thay bằng chạy lại pipeline với 3 cấu hình.
7. **H1 bị chặn trên đường LAFAN1** (không có `bvh_lafan1_to_h1.json`, `--robot unitree_h1` không hợp lệ); **H1_2 chạy được qua Xsens 120 Hz**, nhưng không dùng để so tốc độ vì script Xsens bật rate-limit mặc định.
8. **KI-02:** bốn dòng `rate_limit` từng có `cmd` ghi cờ chưa từng chạy; đã xoá khỏi CSV và ghi lại trong `docs/known_issues.md`.

## Tài liệu

- [`docs/v1_tuyen_bo.md`](docs/v1_tuyen_bo.md) — tuyên bố cần kiểm chứng + 3 bảng paper.
- [`docs/dinh_nghia_phep_do.md`](docs/dinh_nghia_phep_do.md) — định nghĩa đại lượng, đơn vị, quy trình 1 warm-up + 3 lần.
- [`docs/known_issues.md`](docs/known_issues.md) — lỗi đang mở kèm bằng chứng.
- [`docs/quyet_dinh.md`](docs/quyet_dinh.md) — DEC-01, DEC-02.
- [`docs/ke_hoach/`](docs/ke_hoach/) — kế hoạch 4 vai, video demo, tự thuật.
- [`tools/README.md`](tools/README.md) — chi tiết từng script đo và định nghĩa chỉ số.
- [`scripts/NOTES.md`](scripts/NOTES.md) — cấu trúc `.pkl` và cách gọi script GMR.

## Nhóm thực hiện

| Thành viên | Vai trò |
|---|---|
| Trần Nguyễn Khánh Duy | Planner · Research (V1) · Writing mục 1, 2, 7 |
| Đặng Duy Mạnh | Run (env, đo V3/V5/V6, bằng chứng) · Writing mục 3 |
| Trương Thái Vỹ | Code (script đo, video demo) · Writing mục 5 |
| Hà Mạnh Trường | Review độc lập · Writing mục 6 |

Lớp 15DHTH07 · HK1 2026–2027 · ĐH Công Thương TP.HCM · Nhóm 01 · đề tài HR-04.

## Giấy phép và ghi công

Mã của nhóm phát hành theo **MIT** (xem [`LICENSE`](LICENSE)); repo gốc YanjieZe/GMR cũng dùng MIT (xem `third_party/GMR/LICENSE` sau khi clone — [bản trên GitHub](https://github.com/YanjieZe/GMR/blob/25f56db/LICENSE)).

Dựa trên [YanjieZe/GMR](https://github.com/YanjieZe/GMR) @ `25f56db` (MIT, Copyright 2025 Yanjieze) và bài báo *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking* (arXiv:2510.02252). Mọi số đo trong `results/` do nhóm thực hiện trên máy của nhóm.
