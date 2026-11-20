# Định nghĩa phép đo — nguồn sự thật chung của nhóm

**Nhóm 01 · HR-04 · 15DHTH07 · HK1 2026–2027**
Người chốt: Duy (Planner) · Ngày chốt: **2026-11-20** · Phiên bản: **1.2** (RV-17 + đồng bộ CLI `measure_runtime.py`)
Ai cũng đọc. **Không ai sửa** (muốn đổi phải qua Duy, ghi phiên bản mới).

Mục đích: để 4 người đo ra số ghép được với nhau. Mọi file CSV trong `results/` phải theo đúng file này. Tuyên bố đang kiểm chứng: `docs/v1_tuyen_bo.md` (C5).

---

## 1. Đo cái gì

### 1.1 Chỉ tiêu chính — HAI đại lượng, tên gọi khác nhau

Tuyên bố nói về **vòng lặp retargeting**, nhưng phần mềm chạy **cả tiến trình** (nạp dữ liệu + khởi tạo + render + ghi pkl). Vì vậy phải định nghĩa **cả hai**:

- **`ms_per_frame`** (không hậu tố) = **vòng lặp retarget** — đại lượng chính thức để kết luận tuyên bố C5.
- **Mọi đại lượng đo cả tiến trình đều có hậu tố `_process`.**

**Nhóm A — đo vòng lặp retarget (đại lượng của tuyên bố):**

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `t_i` | thời gian xử lý frame thứ *i* | ms | `(perf_counter() sau retarget) − (perf_counter() trước retarget)`, **chỉ** bọc lời gọi `retargeter.retarget(frame)` — không render, không ghi file |
| `ms_per_frame` | trung vị `t_i` của **một lần chạy** | ms/frame | `median(t_i)` trên các frame được tính (xem §3) |
| `ms_per_frame_mean` | trung bình cộng `t_i` | ms/frame | `mean(t_i)` |
| `ms_per_frame_p95` | phân vị 95 | ms/frame | `percentile(t_i, 95)` — bắt đuôi chậm |
| `fps_out` | thông lượng retarget | frame/s | `1000 / ms_per_frame` |
| `realtime_factor` | hệ số thời gian thực của retarget | lần | `fps_out / fps_src` |

**Nhóm B — đo cả tiến trình (cận trên chẩn đoán):**

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `T_process` | wall-clock toàn tiến trình | s | từ dòng đầu tiên của `__main__` đến khi tiến trình thoát; **gồm** nạp BVH, `GMR(...)`, khởi tạo viewer, vòng lặp retarget + render, ghi pkl |
| `ms_per_frame_process` | thời gian trung bình mỗi frame của cả tiến trình | ms/frame | `T_process × 1000 / n_frames_total` |
| `fps_out_process` | thông lượng đầu-cuối | frame/s | `1000 / ms_per_frame_process` |
| `realtime_factor_process` | hệ số thời gian thực đầu-cuối | lần | `fps_out_process / fps_src` |

Quan hệ: `ms_per_frame_process` **luôn ≥** `ms_per_frame` (chứa thêm mọi overhead). Vì vậy Nhóm B là **cận trên bảo thủ** của Nhóm A, **không** dùng thay Nhóm A để kết luận.

**Giai đoạn 1 (V3) đo đại lượng nào:** đo **cả hai trong cùng một lần chạy** bằng `scripts/measure_runtime.py` — script tự bật **2 process**:

1. **process entry script** (`bvh_to_robot.py` / `smplx_to_robot.py` chạy nguyên bản, có viewer) → cho `ms_per_frame_process`;
2. **process probe** (chạy lại chính script với `--retarget-only`, **không** dựng viewer, không render) → cho `ms_per_frame`; `t_init` lấy từ probe.

Cả hai process đều chạy với `CUDA_VISIBLE_DEVICES=""` do script đặt.

**Ngưỡng 33,3 ms áp cho đại lượng nào:** áp cho **`ms_per_frame`** (đại lượng của tuyên bố). Bảng bắc cầu khi chỉ có số `_process`: xem §6.1.

**Ghi chú overhead:** Review đo trên V3 thấy phần tiến trình nhiều hơn phần retarget khoảng **8 %** (khởi tạo + render + ghi pkl). Con số 8 % là **quan sát một lần trên một máy**, **không phải hằng số** — **cấm** quy đổi `ms_per_frame = 0,92 × ms_per_frame_process`.

Các trường chung:

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `fps_src` | tốc độ phát của dữ liệu nguồn | frame/s | **30** với LAFAN1 (README Ubisoft: *"496,672 motion frames at 30fps"*); truyền vào script bằng `--fps-src` (mặc định 30) và đối chiếu header `Frame Time` của file BVH |
| `t_init` | thời gian khởi tạo retargeter | s | thời gian `GMR(...)` (load MJCF + config), đo từ **probe**; **không** cộng vào đại lượng nào ở trên, báo cáo riêng |
| `n_frames` | số frame **được tính** vào Nhóm A | frame | tổng frame − 30 (xem §3) |
| `n_frames_total` | tổng số frame của clip | frame | dùng cho Nhóm B, **không** trừ warm-up |

Cách ghi (bắt buộc):

- `ms_per_frame`, `ms_per_frame_process`: **1 chữ số thập phân**, đơn vị ms. Ví dụ `18.4`.
- `fps_out`, `fps_out_process`: **1 chữ số thập phân**, đơn vị frame/s. Ví dụ `54.3`.
- `realtime_factor`, `realtime_factor_process`: **2 chữ số thập phân**. Ví dụ `1.81`.
- Không bao giờ ghi "khoảng", "gần", "~" trong CSV. Chỉ số.
- Số nào đo **cả tiến trình** thì **bắt buộc** có hậu tố `_process`. Chỉ Nhóm A mới được dùng tên trần `ms_per_frame` / `fps_out` / `realtime_factor`.

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
2. `CUDA_VISIBLE_DEVICES=""` — `scripts/measure_runtime.py` tự đặt cho cả 2 process con; nếu đo tay thì phải tự đặt. Ghi `cuda_visible` vào CSV (script ghi sẵn).
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
- `n_frames` trong CSV = số frame **thực sự được tính** vào Nhóm A (tổng frame − 30). `n_frames_total` = tổng frame của clip, **không** trừ.
- Frame bị bỏ **không** được tính vào `ms_per_frame`, nhưng file raw vẫn ghi lại (cột `included = 0/1`) để người Review kiểm tra.
- `ms_per_frame_process` **không** trừ 30 frame: `T_process` phủ toàn bộ clip, chia cho `n_frames_total`. Như vậy 30 frame warm-up vẫn nằm trong tử số → đại lượng **bảo thủ** (hơi cao), đúng ý đồ của một cận trên.
- Thời gian chạy mỗi lần ≥ 200 frame. Clip chính: **`walk1_subject1.bvh` — 7840 frame, 261,3 s @ 30 fps**. **Không** được gọi clip này là "Walk 1" của Bảng I paper: "Walk 1" trong Bảng I chỉ dài **33 s** (mục V-D và Bảng I, trang 6). Hai thứ khác nhau, không được gộp.

**Cấm:**

- Bật `--rate_limit` (giới hạn nhịp theo chuyển động người → kết quả luôn ≈ 30 fps, tự ứng nghiệm).
- Dùng con số `Actual rendering FPS` do `scripts/bvh_to_robot.py` in ra (đó là FPS của vòng lặp **có render**, không phải retargeting).
- Dùng `scripts/bvh_to_robot_dataset.py` làm phép đo chính (hardcode `device = "cuda:0"`).
- Dựng `RobotMotionViewer` **khi đo `ms_per_frame`** (cần display, làm nhiễu số). Ngược lại, khi đo `ms_per_frame_process` thì **phải giữ nguyên** viewer như lúc V3 chạy thật — bỏ viewer đi sẽ làm đại lượng "cả tiến trình" không còn là cận trên đúng nghĩa.
- Dùng `time.time()` — bắt buộc `time.perf_counter()`.

---

## 4. Tính số cuối cùng

Với mỗi cấu hình (robot × clip × máy), tính **riêng cho từng đại lượng**:

```
# Nhóm A — vòng lặp retarget
ms_per_frame_final = mean( ms_per_frame của run 2, 3, 4 )
sd_A     = độ lệch chuẩn mẫu (ddof = 1) của 3 giá trị trên
CV_A     = sd_A / ms_per_frame_final × 100 %
fps_out  = 1000 / ms_per_frame_final
realtime_factor = fps_out / fps_src

# Nhóm B — cả tiến trình
ms_per_frame_process_final = mean( ms_per_frame_process của run 2, 3, 4 )
sd_B     = độ lệch chuẩn mẫu (ddof = 1) của 3 giá trị trên
CV_B     = sd_B / ms_per_frame_process_final × 100 %
fps_out_process = 1000 / ms_per_frame_process_final
realtime_factor_process = fps_out_process / fps_src
```

Báo cáo dạng:

- **`ms_per_frame` = X ± Y ms (mean ± sd, n = 3)** + `ms_per_frame_p95` của lần chạy có trung vị gần `..._final` nhất.
- **`ms_per_frame_process` = X ± Y ms (mean ± sd, n = 3)**.

Nếu `CV > 5 %` (áp cho cả hai):

1. chạy thêm 2 lần (`run=5,6`);
2. báo **trung vị** của 5 giá trị thay cho trung bình;
3. ghi rõ trong log "máy không ổn định, CV = …%";
4. **không** được chọn tay lần chạy đẹp nhất.

---

## 5. Định dạng file CSV (hợp đồng bắt buộc)

### 5.1 `results/v3_runtime.csv` — 1 dòng / lần chạy

```
run,robot,motion,bvh_file,n_frames,n_warmup_frames,fps_src,ms_per_frame,ms_per_frame_mean,ms_per_frame_p95,fps_out,realtime_factor,t_init_s,cpu,ram_gb,os,python,numpy,mujoco,mink,torch,git_head,cuda_visible,cmd,timestamp,n_frames_total,ms_per_frame_process,fps_out_process,realtime_factor_process,process_cmd
```

Đây là **đúng thứ tự cột** mà `scripts/measure_runtime.py` xuất ra (`SUMMARY_COLUMNS`, commit `5f9cdd5`). Không đổi thứ tự, không đổi tên.

- `ms_per_frame`, `ms_per_frame_mean`, `ms_per_frame_p95`, `fps_out`, `realtime_factor`: từ **probe** (chỉ retarget()).
- `ms_per_frame_process`, `fps_out_process`, `realtime_factor_process`: từ **entry script** (cả tiến trình).
- `process_cmd`: lệnh entry script đã chạy — dùng để tái lập cột `_process`; `cmd` là lệnh probe — dùng để tái lập cột `ms_per_frame`.
- `t_init_s`: lấy từ probe.
- Nếu ai đó đo tay bằng `bvh_to_robot.py` (không qua script): chỉ có `_process`; các cột Nhóm A **để trống**, **không** suy ra từ `_process`.

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
robot,robot_dof,motion,bvh_file,n_frames,n_frames_total,fps_src,ms_per_frame_process,ms_per_frame,fps_out_process,fps_out,realtime_factor_process,realtime_factor,min_body_height,foot_slide,git_head,cmd,timestamp
```

---

## 6. Sai số chấp nhận

### 6.1 Ngưỡng 33,3 ms áp cho đại lượng nào

**Ngưỡng 33,3 ms (= 1000/30) áp cho `ms_per_frame`** — đại lượng của tuyên bố ("retarget theo thời gian thực").

Giai đoạn 1 **có đủ cả hai** số (script đo 2 process trong một lần chạy) → kết luận thẳng theo `ms_per_frame` ở §6.3. Bảng dưới chỉ dùng cho trường hợp **thiếu** số Nhóm A (ví dụ ai đó đo tay bằng `bvh_to_robot.py`, hoặc probe lỗi):

| Tình huống | Được kết luận |
|---|---|
| `ms_per_frame_process` ≤ 33,3 ms | **Tái lập được** — điều kiện **đủ**: `retarget ≤ process ≤ 33,3 ms` |
| `ms_per_frame_process` > 33,3 ms **và** `ms_per_frame` ≤ 33,3 ms | **Tái lập một phần** — vòng lặp retarget đạt real-time, nhưng đầu-cuối (init + render + ghi pkl) thì không |
| `ms_per_frame_process` > 33,3 ms **và** `ms_per_frame` > 33,3 ms | **Không tái lập được** (theo mức < 0,80 thì phải thử máy thứ hai) |
| `ms_per_frame_process` > 33,3 ms, **không có** `ms_per_frame` | **Chưa kết luận được** — phải chạy `scripts/measure_runtime.py` (probe) trước |

**Cấm** quy đổi `ms_per_frame = 0,92 × ms_per_frame_process`. Tỉ lệ overhead 8 % là quan sát một lần của Review trên một máy, không phải hằng số; dùng nó để "sửa" số là bịa số.

### 6.2 Bảng sai số

| Chỉ tiêu | Sai số chấp nhận | Nếu vượt |
|---|---|---|
| `ms_per_frame` và `ms_per_frame_process` giữa các lần chạy | **CV ≤ 5 %** (tính riêng cho mỗi đại lượng) | chạy thêm 2 lần, báo trung vị (§4) |
| Cùng đại lượng, chạy lại trên máy khác | **≤ 25 %** | ghi thành 2 dòng riêng, **không** trộn vào một con số |
| `min_body_height` | ± 5 mm | kiểm tra lại FK / đơn vị |
| `foot_slide` | ± 10 % | kiểm tra ngưỡng tiếp đất 1 cm |
| Làm tròn khi báo cáo | ms: 0,1 · fps: 0,1 · lần: 0,01 · m: 0,001 · mm/s: 1 | — |

Mọi ngưỡng trong bảng trên là **do nhóm đặt trước**; bài báo không nêu ngưỡng sai số nào. Chỉ các con số artifact cụ thể (60 cm xuyên sàn của PHC, < 2 % sudden jump của GMR) là số của paper và **không** dùng làm ngưỡng ở đây.

**Không có sai số "so với paper"** cho tuyên bố C5, vì bài báo không nêu bất kỳ con số thời gian nào (đã kiểm tra toàn văn 9 trang — `docs/paper_notes.md` §12). Mọi câu so sánh với paper về tốc độ là **bịa**. Ngưỡng duy nhất được dùng là `realtime_factor ≥ 1,00`, tức "nhanh ít nhất bằng tốc độ phát của chính dữ liệu nguồn".

### 6.3 Ba mức kết luận (chốt trước, **không đổi sau khi thấy số**)

Áp cho `realtime_factor` (tức `ms_per_frame`). Khi thiếu số Nhóm A thì áp theo bảng §6.1.

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
| Code (Vỹ) | **Đã xong**: `scripts/measure_runtime.py` @ `5f9cdd5` (nhánh `task/code-scripts3`), xuất đúng §5 | không sửa ngưỡng trong file này |
| Run (Mạnh) | chạy §3 bằng CLI của script, sinh CSV, ghi log | không bỏ lần chạy xấu, không chọn tay |
| Review (Trường) | kiểm CSV đủ cột, **đúng tên đại lượng** (`ms_per_frame` vs `_process`), có `cmd` + `process_cmd`, `git_head`, CV ≤ 5 % | không tự đo lại rồi trộn số |
| Writing | điền bảng `bài báo | nhóm đo được` | không chép số paper sang cột nhóm |

---

## 9. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi | Người |
|---|---|---|---|
| 1.0 | 2026-11-20 | Bản đầu: chốt `ms_per_frame` / `fps_out` / `realtime_factor`, 1 warm-up + 3 lần, CV ≤ 5 %, ngưỡng 1,00; thêm V5 3 robot | Duy |
| 1.1 | 2026-11-20 | **RV-17**: tách hai đại lượng (vòng lặp retarget với hậu tố `_retarget`, và cả tiến trình với `_process`); ngưỡng 33,3 ms áp cho đại lượng retarget; thêm bảng §6.1; cấm quy đổi bằng hệ số 0,92; sửa ghi chú clip `walk1_subject1.bvh` (7840 frame, 261,3 s) ≠ "Walk 1" (33 s) của Bảng I | Duy |
| 1.2 | 2026-11-21 | **Đồng bộ với CLI cuối của Code** (`scripts/measure_runtime.py` @ `5f9cdd5`): đổi tên `ms_per_frame_retarget` → **`ms_per_frame`** và `ms_per_frame_retarget_p95` → **`ms_per_frame_p95`** (đây mới là tên chính thức); mọi số đo cả tiến trình giữ hậu tố `_process`; §5.1 chép đúng thứ tự cột của `SUMMARY_COLUMNS` (thêm `n_frames_total`, `process_cmd`); ghi rõ script đo **2 process** trong một lần chạy (entry script cho `_process`, probe `--retarget-only` cho `ms_per_frame`, `t_init` lấy từ probe); §6.1 chỉ còn là quy tắc dự phòng khi thiếu số Nhóm A | Duy |
