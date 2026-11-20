# Định nghĩa phép đo — nguồn sự thật chung của nhóm

**Nhóm 01 · HR-04 · 15DHTH07 · HK1 2026–2027**
Người chốt: Duy (Planner) · Ngày chốt: **2026-11-20** · Phiên bản: **1.0**
Ai cũng đọc. **Không ai sửa** (muốn đổi phải qua Duy, ghi phiên bản mới).

Mục đích: để 4 người đo ra số ghép được với nhau. Mọi file CSV trong `results/` phải theo đúng file này. Tuyên bố đang kiểm chứng: `docs/v1_tuyen_bo.md` (C5).

---

## 1. Đo cái gì

### 1.1 Chỉ tiêu chính (dùng để kết luận tuyên bố)

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `t_i` | thời gian xử lý frame thứ *i* | ms | `(perf_counter() sau retarget) − (perf_counter() trước retarget)`, **chỉ** bọc lời gọi `retargeter.retarget(frame)` |
| `ms_per_frame` | thời gian xử lý trung vị mỗi frame của **một lần chạy** | ms/frame | `median(t_i)` trên các frame được tính (xem §3) |
| `ms_per_frame_mean` | trung bình cộng mỗi frame của một lần chạy | ms/frame | `mean(t_i)` |
| `ms_per_frame_p95` | phân vị 95 | ms/frame | `percentile(t_i, 95)` — bắt đuôi chậm |
| `fps_out` | thông lượng | frame/s | `1000 / ms_per_frame` (dùng **cùng** một `ms_per_frame`, không tính lại từ mean) |
| `fps_src` | tốc độ phát của dữ liệu nguồn | frame/s | **30** với LAFAN1 (README Ubisoft: *"496,672 motion frames at 30fps"*); phải đối chiếu header `Frame Time` của file BVH và ghi lại giá trị header |
| `realtime_factor` | hệ số thời gian thực | lần (không đơn vị) | `fps_out / fps_src` |
| `t_init` | thời gian khởi tạo retargeter | s | thời gian `GMR(...)` (load MJCF + config), **không** cộng vào `ms_per_frame` |
| `n_frames` | số frame của clip | frame | đếm từ danh sách frame nạp vào |

Cách ghi (bắt buộc):

- `ms_per_frame`: **1 chữ số thập phân**, đơn vị ms. Ví dụ `18.4`.
- `fps_out`: **1 chữ số thập phân**, đơn vị frame/s. Ví dụ `54.3`.
- `realtime_factor`: **2 chữ số thập phân**. Ví dụ `1.81`.
- Không bao giờ ghi "khoảng", "gần", "~" trong CSV. Chỉ số.

### 1.2 Chỉ tiêu phụ về chất lượng ánh xạ (nhóm tự định nghĩa — **không** phải số của paper)

Dùng để chứng minh "ánh xạ không bị hỏng" khi chạy sim2sim, **không** dùng để kết luận tuyên bố chính.

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `min_body_height` | chiều cao thấp nhất của mọi body trong toàn clip | m | FK trên `qpos` đã lưu; lấy min theo mọi frame × mọi body. Paper (trang 5) trừ chiều cao nhỏ nhất nên giá trị kỳ vọng ≈ 0 |
| `foot_slide` | tốc độ trượt chân khi chân đang tiếp đất | mm/s | với mỗi frame mà body bàn chân có `z < 0.01 m`, lấy |Δxy| giữa 2 frame liên tiếp × `fps_src` × 1000; lấy trung vị trên toàn clip |

Ngưỡng chấp nhận (nhóm đặt, ghi rõ là do nhóm đặt):

- `min_body_height` ∈ **[−0.005, +0.005] m** → coi là "không xuyên sàn, không bay".
- `foot_slide` ≤ **50 mm/s** → coi là "không trượt chân đáng kể".

> Đây là ngưỡng của **nhóm**, không phải của paper. Paper chỉ nêu artifact ở dạng định tính + vài ca cụ thể (60 cm xuyên sàn của PHC, < 2 % sudden jump của GMR "Dance 5"), không định nghĩa ngưỡng foot slide.

---

## 2. Đo trên cấu hình nào

Ghi **đủ** các trường sau vào mọi CSV (cùng dòng với số đo):

```
cpu, ram_gb, os, python, numpy, mujoco, mink, torch, git_head, cuda_visible
```

Quy tắc cứng:

1. **Cùng một máy** cho cả 3 lần đo của một cấu hình. Đổi máy → đổi `machine_id`, không trộn.
2. Đặt `CUDA_VISIBLE_DEVICES=""` để chắc chắn đo trên CPU (tuyên bố là "on CPU").
3. Tắt ứng dụng nặng, cắm sạc, không chạy song song việc khác trong lúc đo.
4. **Ghim commit** repo GMR: hiện tại `25f56db7` (2026-10-22). Mọi CSV ghi `git_head`.
5. `fps_src` phải khớp dữ liệu: LAFAN1 = 30. **Cấm** trộn file 120 Hz (ví dụ `assets/xsens_bvh_test/251021_04_boxing_120Hz_cm_3DsMax.bvh`) vào bảng so sánh chính.
6. Robot mặc định: **`unitree_g1`** (robot duy nhất paper dùng — trang 3). Các robot khác chỉ dùng cho V5.

---

## 3. Quy trình chạy: 1 warm-up + 3 lần đo

```
lần 1  → WARM-UP, ghi vào CSV với run=1 nhưng BỊ LOẠI khỏi mọi phép tính
lần 2  → đo, run=2
lần 3  → đo, run=3
lần 4  → đo, run=4        (có thể chạy thêm run=5,6 nếu CV > 5 %)
```

- Mỗi lần là **một process mới** (tránh cache/heap tích tụ giữa các lần).
- Trong mỗi lần đo, **bỏ 30 frame đầu** (≈ 1 s ở 30 fps) để loại chi phí khởi tạo lười (JIT/allocation lần đầu). Ghi rõ số frame bị bỏ vào `n_warmup_frames`.
- `n_frames` trong CSV = số frame **thực sự được tính** (tổng frame − 30).
- Frame bị bỏ **không** được tính vào `ms_per_frame`, nhưng file raw vẫn ghi lại (cột `included = 0/1`) để người Review kiểm tra.
- Thời gian chạy mỗi lần ≥ 200 frame. Clip khuyến nghị: "Walk 1" 33 s ≈ 990 frame.

**Cấm:**

- Bật `--rate_limit` (giới hạn nhịp theo chuyển động người → kết quả luôn ≈ 30 fps, tự ứng nghiệm).
- Dùng con số `Actual rendering FPS` do `scripts/bvh_to_robot.py` in ra (đó là FPS của vòng lặp **có render**, không phải retargeting).
- Dùng `scripts/bvh_to_robot_dataset.py` làm phép đo chính (hardcode `device = "cuda:0"`).
- Dựng `RobotMotionViewer` trong lúc đo (cần display, làm nhiễu số).
- Dùng `time.time()` — bắt buộc `time.perf_counter()`.

---

## 4. Tính số cuối cùng

Với mỗi cấu hình (robot × clip × máy):

```
ms_per_frame_final = mean( ms_per_frame của run 2, 3, 4 )
sd                 = độ lệch chuẩn mẫu (ddof = 1) của 3 giá trị trên
CV                 = sd / ms_per_frame_final × 100 %
fps_final          = 1000 / ms_per_frame_final
realtime_final     = fps_final / fps_src
```

Báo cáo dạng: **`ms_per_frame` = X ± Y ms (mean ± sd, n = 3)**, kèm `ms_per_frame_p95` của lần chạy có trung vị gần `ms_per_frame_final` nhất.

Nếu `CV > 5 %`:

1. chạy thêm 2 lần (`run=5,6`);
2. báo **trung vị** của 5 giá trị thay cho trung bình;
3. ghi rõ trong log "máy không ổn định, CV = …%";
4. **không** được chọn tay lần chạy đẹp nhất.

---

## 5. Định dạng file CSV (hợp đồng bắt buộc)

### 5.1 `results/v3_runtime.csv` — 1 dòng / lần chạy

```
run,robot,motion,bvh_file,n_frames,n_warmup_frames,fps_src,ms_per_frame,ms_per_frame_mean,ms_per_frame_p95,fps_out,realtime_factor,t_init_s,cpu,ram_gb,os,python,numpy,mujoco,mink,torch,git_head,cuda_visible,cmd,timestamp
```

- `run`: 1 = warm-up (bị loại), 2–4 = đo.
- `cmd`: **nguyên văn** lệnh đã chạy (dấu nháy được phép, dấu phẩy thì bọc trong `"`).
- `timestamp`: ISO-8601, ví dụ `2026-11-21T14:03:11+07:00`.
- `realtime_factor` được tính từ `fps_src` của **chính dòng đó**, không copy từ dòng khác.

### 5.2 `results/v3_runtime_raw.csv` — 1 dòng / frame

```
run,motion,robot,frame,included,ms
```

`included = 0` cho 30 frame warm-up và cho toàn bộ `run=1`.

### 5.3 `results/v5_sim2sim.csv` — 1 dòng / (robot × clip)

```
robot,robot_dof,motion,bvh_file,n_frames,fps_src,ms_per_frame,ms_per_frame_p95,fps_out,realtime_factor,min_body_height,foot_slide,git_head,cmd,timestamp
```

---

## 6. Sai số chấp nhận

| Chỉ tiêu | Sai số chấp nhận | Nếu vượt |
|---|---|---|
| `ms_per_frame` giữa các lần chạy | **CV ≤ 5 %** | chạy thêm 2 lần, báo trung vị (§4) |
| `ms_per_frame` so với lần chạy lại trên máy khác | **≤ 25 %** | ghi thành 2 dòng riêng, **không** trộn vào một con số |
| `min_body_height` | ± 5 mm | kiểm tra lại FK / đơn vị |
| `foot_slide` | ± 10 % | kiểm tra ngưỡng tiếp đất 1 cm |
| Làm tròn khi báo cáo | ms: 0,1 · fps: 0,1 · lần: 0,01 · m: 0,001 · mm/s: 1 | — |

Mọi ngưỡng trong bảng trên là **do nhóm đặt trước**; bài báo không nêu ngưỡng sai số nào. Chỉ các con số artifact cụ thể (60 cm xuyên sàn của PHC, < 2 % sudden jump của GMR) là số của paper và **không** dùng làm ngưỡng ở đây.

**Không có sai số "so với paper"** cho tuyên bố C5, vì bài báo không nêu bất kỳ con số thời gian nào (đã kiểm tra toàn văn 9 trang — `docs/paper_notes.md` §12). Mọi câu so sánh với paper về tốc độ là **bịa**. Ngưỡng duy nhất được dùng là `realtime_factor ≥ 1,00`, tức "nhanh ít nhất bằng tốc độ phát của chính dữ liệu nguồn".

Ba mức kết luận (chốt trước, **không đổi sau khi thấy số**):

| `realtime_factor` | Kết luận |
|---|---|
| ≥ 1,00 | tái lập được |
| 0,80 – 0,99 | tái lập một phần |
| < 0,80 | không tái lập được (phải thử máy thứ hai trước khi kết luận) |

---

## 7. V5 — sim2sim mức 3 (cùng chuyển động → ≥ 3 robot)

Giữ nguyên simulator (MuJoCo CPU), **không** huấn luyện lại gì, chỉ đổi robot:

| # | Robot | `--robot` | DoF | Ghi chú |
|---|---|---|---|---|
| 1 | Unitree G1 | `unitree_g1` | 29 | robot của paper (trang 3) |
| 2 | Booster T1 29dof | `booster_t1_29dof` | TBD trong README | có cột BVH ✅ |
| 3 | ENGINEAI PM01 | `engineai_pm01` | TBD trong README | có cột BVH ✅ |

Dự phòng (cũng có BVH ✅): `fourier_n1`, `stanford_toddy`, `unitree_h2`.
**Không dùng** `unitree_h1` / `unitree_h1_2` cho đường BVH: README đang để **TBD** ở cột BVH(LAFAN1).

Với mỗi robot: chạy đúng §3 (1 warm-up + 3 lần), cùng một file BVH, ghi `results/v5_sim2sim.csv`, kèm `min_body_height` và `foot_slide`.

Câu hỏi V5 trả lời: **thời gian xử lý và chất lượng hình học có giữ được khi đổi embodiment không** — không phải "robot nào giỏi hơn".

---

## 8. Bảng phân công theo file này

| Vai | Việc | Không được làm |
|---|---|---|
| Code (Vỹ) | `scripts/measure_retarget_runtime.py` xuất đúng §5 | không sửa ngưỡng trong file này |
| Run (Mạnh) | chạy §3, sinh CSV, ghi log | không bỏ lần chạy xấu, không chọn tay |
| Review (Trường) | kiểm CSV đủ cột, có `cmd`, `git_head`, CV ≤ 5 %, không có `--rate_limit` | không tự đo lại rồi trộn số |
| Writing | điền bảng `bài báo | nhóm đo được` | không chép số paper sang cột nhóm |

---

## 9. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi | Người |
|---|---|---|---|
| 1.0 | 2026-11-20 | Bản đầu: chốt `ms_per_frame` / `fps_out` / `realtime_factor`, 1 warm-up + 3 lần, CV ≤ 5 %, ngưỡng 1,00; thêm V5 3 robot | Duy |
