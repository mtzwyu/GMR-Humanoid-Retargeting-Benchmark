# Định nghĩa phép đo — nguồn sự thật chung của nhóm

**Nhóm 01 · HR-04 · 15DHTH07 · HK1 2026–2027**
Người chốt: Duy (Planner) · Ngày chốt: **2026-11-20** · Phiên bản: **1.4** (đồng bộ `tools/quality_metrics.py` + DEC-03 + chuẩn làm tròn)
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

**Giai đoạn 1 (V3) đo đại lượng nào:** **chỉ `ms_per_frame_process`**, bằng **bản đo cũ** (đo thẳng `bvh_to_robot.py`, không qua script mới). Bản đo cũ là `results/v3_runtime.csv`: **13 cột**, **6 dòng** (1 warm-up + 5 lần đo), **không có cột `ms_per_frame`**; cột `realtime_factor` trong file đó thực chất là **`realtime_factor_process`**.

`scripts/measure_runtime.py` (@`5f9cdd5`) **có khả năng** đo cả hai trong một lần chạy — 2 process: (1) entry script (`bvh_to_robot.py`, có viewer) → `ms_per_frame_process`; (2) probe (`--retarget-only`, không viewer) → `ms_per_frame` + `t_init`; cả hai chạy với `CUDA_VISIBLE_DEVICES=""` do script đặt. **Nhưng script này chưa được dùng cho số liệu giai đoạn 1**, và Planner đã chốt **không chạy lại** V3/V5. Vì vậy mọi kết luận giai đoạn 1 phải đi qua bảng bắc cầu §6.1.

**Ngưỡng 33,33 ms áp cho đại lượng nào:** áp cho **`ms_per_frame`** (đại lượng của tuyên bố). Bảng bắc cầu khi chỉ có số `_process`: xem §6.1.

**Ghi chú overhead:** Review đo trên V3 thấy phần tiến trình nhiều hơn phần retarget khoảng **8 %** (khởi tạo + render + ghi pkl). Con số 8 % là **quan sát một lần trên một máy**, **không phải hằng số** — **cấm** quy đổi `ms_per_frame = 0,92 × ms_per_frame_process`.

Các trường chung:

| Ký hiệu | Đại lượng | Đơn vị | Định nghĩa |
|---|---|---|---|
| `fps_src` | tốc độ phát của dữ liệu nguồn | frame/s | **30** với LAFAN1 (README Ubisoft: *"496,672 motion frames at 30fps"*); truyền vào script bằng `--fps-src` (mặc định 30) và đối chiếu header `Frame Time` của file BVH |
| `t_init` | thời gian khởi tạo retargeter | s | thời gian `GMR(...)` (load MJCF + config), đo từ **probe**; **không** cộng vào đại lượng nào ở trên, báo cáo riêng |
| `n_frames` | số frame **được tính** vào Nhóm A | frame | tổng frame − 30 (xem §3) |
| `n_frames_total` | tổng số frame của clip | frame | dùng cho Nhóm B, **không** trừ warm-up |

Cách ghi: xem **§1.3 Chuẩn làm tròn** (một chuẩn duy nhất cho cả tài liệu).

Quy tắc đặt tên (giữ nguyên): số nào đo **cả tiến trình** thì **bắt buộc** có hậu tố `_process`; chỉ Nhóm A mới được dùng tên trần `ms_per_frame` / `fps_out` / `realtime_factor`.

### 1.2 Chỉ tiêu phụ về chất lượng ánh xạ

Dùng để mô tả "ánh xạ có bị hỏng không" khi chạy sim2sim, **không** dùng để kết luận tuyên bố chính.

**Nguồn chuẩn:** `tools/quality_metrics.py` (nhánh `main`, commit `f00421e`). Định nghĩa dưới đây chép **theo code**, không theo trực giác. Mọi chỉ số tính trên `qpos` của file `.pkl`; FK bằng MuJoCo (`mj_forward`), bỏ body world (id 0).

| Ký hiệu | Định nghĩa **theo code** | Đơn vị |
|---|---|---|
| `foot_slide` (L, R, mean) | Với **từng bàn chân riêng biệt** (trái, phải), dùng vị trí **tâm thân bàn chân** `data.xpos[foot_body]` (**không** phải mesh, **không** phải CoM). Gọi `z` = cao độ tâm thân bàn chân theo từng frame. Frame **tiếp đất** := `z − min(z của chính bàn chân đó trong cả clip) ≤ 30 mm` (`CONTACT_TOL_MM = 30`). Với mọi **cặp frame liên tiếp** mà **cả hai** frame đều tiếp đất, cộng `‖Δxy‖` (mm). Chỉ số = `Σ‖Δxy‖ ÷ (n_pairs / fps)` → **mm/s**. `foot_slide_mean = nanmean([L, R])` (trung bình cộng **hai chân**, không phải trung vị theo frame) | mm/s |
| `min_body_height` | `min` trên **mọi frame × mọi body** của cao độ **gốc body** (`xpos[1:,2]`) — tức "độ cao gốc của body thấp nhất", **không** phải tâm thân của một bàn chân cụ thể. Code báo **mm** (`×1000`) | m (báo cáo **mm**) |
| `rest_offset` | cao độ gốc body thấp nhất khi robot ở **tư thế nghỉ** `qpos0` (mm). Dùng để quy đổi `Δ = min_body_height − rest_offset` | mm |
| `pct_frames_penetration` | `100 × #{frame có ít nhất 1 body với z×1000 < −1 mm} ÷ n_frames` (`PENETRATION_MM = −1`) | % |
| `joint_limit_saturation_pct` | `100 × #{frame có ít nhất 1 khớp limited với \|q − q_lo\| ≤ 0,5° **hoặc** \|q − q_hi\| ≤ 0,5°} ÷ n_frames` (`LIMIT_TOL_DEG = 0,5`). Đây là **bão hoà** (tiến sát giới hạn), **không phải** vượt giới hạn | % |

Ghi chú kỹ thuật (bắt buộc khi cài lại hoặc kiểm chéo):

- `q_lo, q_hi` lấy từ `model.jnt_range`; **bỏ** khớp free và khớp không `limited`.
- `foot_slide`: nếu `n_pairs = 0` → `NaN` (code trả `nan`; `nanmean` bỏ qua).
- `foot_slide` và `min_body_height` **không** đo cùng một thứ: cái đầu đo trượt ngang của **tâm thân bàn chân** khi tiếp đất; cái sau đo cao độ **gốc body** thấp nhất trong toàn clip.

> Bốn chỉ số này **không** phải số của paper. Paper chỉ nêu artifact ở dạng định tính + vài ca cụ thể (60 cm xuyên sàn của PHC, < 2 % sudden jump của GMR "Dance 5"), không định nghĩa foot slide hay penetration.

**Ngưỡng chất lượng: xem §6.4** (một ngưỡng giữ, một ngưỡng rút theo DEC-03).

### 1.3 Chuẩn làm tròn (áp cho **mọi** số trong tài liệu và trong báo cáo)

| Quy tắc | Nội dung |
|---|---|
| Số chữ số thập phân | **3** — cho mọi đại lượng đo (`ms_per_frame`, `fps_out`, `realtime_factor`, `foot_slide`, `min_body_height`, `pct_frames_penetration`, `joint_limit_saturation_pct`, `rest_offset`, CV, …) |
| Dấu thập phân | **dấu phẩy** (chuẩn Việt Nam): `17,349` · `57,640` · `1,921` · `2,129` |
| Ngoại lệ | số **đếm** (frame, lần chạy) là số nguyên; **ngưỡng** và **số trích từ `docs/quyet_dinh.md` (DEC-03)** ghi đúng như văn bản quyết định (`33,33 ms`, `50 mm/s`, `30 mm`, `−1 mm`, `0,5°`, `49,0`, `83,1`, `2,13 %`) |
| Cấm | ghi "khoảng", "gần", "~"; trộn dấu chấm thập phân với dấu phẩy trong cùng một tài liệu; tự thêm/bớt chữ số giữa các bảng |
| CSV | CSV là định dạng **máy đọc** nên vẫn dùng **dấu chấm** (code xuất `round(..., 3)`); chuẩn dấu phẩy chỉ áp cho **tài liệu và báo cáo** |

Ví dụ chuẩn: `ms_per_frame_process = 17,349 ms` · `fps_out_process = 57,640` · `realtime_factor_process = 1,921` · `CV = 2,13 %`.

---

## 2. Đo trên cấu hình nào

Ghi **đủ** các trường sau vào mọi CSV (cùng dòng với số đo):

```
cpu, ram_gb, os, python, numpy, mujoco, mink, torch, git_head, cuda_visible
```

Quy tắc cứng:

1. **Cùng một máy** cho cả 3 lần đo của một cấu hình. Đổi máy → đổi `machine_id`, không trộn.
2. `CUDA_VISIBLE_DEVICES=""` — `scripts/measure_runtime.py` tự đặt cho cả 2 process con. **Bản đo cũ không có cột `cuda_visible`**, nên khi trích số giai đoạn 1 phải ghi rõ "không xác minh được biến này".
3. Tắt ứng dụng nặng, cắm sạc, không chạy song song việc khác trong lúc đo.
4. **Ghim commit** repo GMR: hiện tại `25f56db7` (2026-10-23 giờ VN). Mọi CSV ghi `git_head`.
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
- Nếu đo bằng `bvh_to_robot.py` trực tiếp (không qua script) — **đúng trường hợp bản đo giai đoạn 1**: chỉ có `_process`; các cột Nhóm A **để trống**, **không** suy ra từ `_process`.

**Bản đo cũ `results/v3_runtime.csv` (số liệu giai đoạn 1)** — 13 cột, 6 dòng, **không** theo §5.1:

`mode, phase, robot, input, frames, motion_duration_s, wall_clock_s, ms_per_frame_process, realtime_factor, exit_code, cmd, log, note`

| Cột trong file cũ | Đọc là | Ghi chú |
|---|---|---|
| `ms_per_frame_process` | `ms_per_frame_process` | đúng tên, đơn vị ms |
| `realtime_factor` | **`realtime_factor_process`** | được tính từ `ms_per_frame_process`, **không phải** của vòng lặp retarget |
| `phase = warmup` | — | bị loại, không tính |
| `phase = measure_1..5` | 5 lần đo | tính CV trên **cả 5** |
| (không có) | `ms_per_frame`, `fps_out`, `realtime_factor` | **không đo được** — bắt buộc áp §6.1 |

Khi viết báo cáo: gọi file này là **"bản đo cũ"**, không gọi là "file đúng hợp đồng §5.1".

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

### 6.1 Ngưỡng 33,33 ms áp cho đại lượng nào

**Ngưỡng 33,33 ms (= 1000/30) áp cho `ms_per_frame`** — đại lượng của tuyên bố ("retarget theo thời gian thực").

Giai đoạn 1 **chỉ có** `ms_per_frame_process` (bản đo cũ), **không có** `ms_per_frame` → **bắt buộc** dùng bảng bắc cầu dưới đây, không được suy ra số Nhóm A:

| Tình huống | Được kết luận |
|---|---|
| `ms_per_frame_process` ≤ 33,33 ms | **Tái lập được** — điều kiện **đủ**: `retarget ≤ process ≤ 33,33 ms` |
| `ms_per_frame_process` > 33,33 ms **và** `ms_per_frame` ≤ 33,33 ms | **Tái lập một phần** — vòng lặp retarget đạt real-time, nhưng đầu-cuối (init + render + ghi pkl) thì không (chỉ xảy ra nếu sau này có probe) |
| `ms_per_frame_process` > 33,33 ms **và** `ms_per_frame` > 33,33 ms | **Không tái lập được** (theo mức < 0,80 thì phải thử máy thứ hai) |
| `ms_per_frame_process` > 33,33 ms, **không có** `ms_per_frame` | **Chưa kết luận được** — không được suy ra; muốn kết luận phải chạy probe (`scripts/measure_runtime.py`) |

**Cấm** quy đổi `ms_per_frame = 0,92 × ms_per_frame_process`. Tỉ lệ overhead 8 % là quan sát một lần của Review trên một máy, không phải hằng số; dùng nó để "sửa" số là bịa số.

### 6.2 Bảng sai số

| Chỉ tiêu | Sai số chấp nhận | Nếu vượt |
|---|---|---|
| `ms_per_frame` và `ms_per_frame_process` giữa các lần chạy | **CV ≤ 5 %** (tính riêng cho mỗi đại lượng) | chạy thêm 2 lần, báo trung vị (§4) |
| Cùng đại lượng, chạy lại trên máy khác | **≤ 25 %** | ghi thành 2 dòng riêng, **không** trộn vào một con số |
| `min_body_height` | **không còn ngưỡng** (xem §6.4, DEC-03); chỉ kiểm độ tái lập giữa các lần FK | kiểm tra lại FK / đơn vị |
| `foot_slide` | ± 10 % (độ tái lập của phép đo, **khác** ngưỡng chất lượng 50 mm/s) | kiểm tra lại công thức tiếp đất (§1.2) |
| Làm tròn khi báo cáo | **3 chữ số thập phân, dấu phẩy** (§1.3) | — |

Mọi ngưỡng trong bảng trên là **do nhóm đặt trước**; bài báo không nêu ngưỡng sai số nào. Chỉ các con số artifact cụ thể (60 cm xuyên sàn của PHC, < 2 % sudden jump của GMR) là số của paper và **không** dùng làm ngưỡng ở đây.

**Không có sai số "so với paper"** cho tuyên bố C5, vì bài báo không nêu bất kỳ con số thời gian nào (đã kiểm tra toàn văn 9 trang — `docs/paper_notes.md` §12). Mọi câu so sánh với paper về tốc độ là **bịa**. Ngưỡng duy nhất được dùng là `realtime_factor ≥ 1,00`, tức "nhanh ít nhất bằng tốc độ phát của chính dữ liệu nguồn".

### 6.3 Ba mức kết luận (chốt trước, **không đổi sau khi thấy số**)

Áp cho `realtime_factor` (tức `ms_per_frame`). Khi thiếu số Nhóm A thì áp theo bảng §6.1.

| `realtime_factor` | Kết luận |
|---|---|
| ≥ 1,00 | tái lập được |
| 0,80 – 0,99 | tái lập một phần |
| < 0,80 | không tái lập được (phải thử máy thứ hai trước khi kết luận) |

### 6.4 Ngưỡng chất lượng: giữ một, rút một — theo **DEC-03**

Quyết định gốc: `docs/quyet_dinh.md` **DEC-03** (ngày 2026-11-21, commit `f00421e`). Không được xoá dấu vết ngưỡng cũ.

| Chỉ số | Ngưỡng | Trạng thái |
|---|---|---|
| `foot_slide` | **≤ 50 mm/s** | **GIỮ và ÁP** — đo cùng đại lượng với code (§1.2), phân biệt rõ 3 robot |
| `min_body_height` | **± 5 mm** | **RÚT** — ngưỡng cũ đã đặt ngày **2026-11-20**, rút ngày **2026-11-21**; lý do: đại lượng này đo **gốc body thấp nhất**, mà mỗi model có độ cao gốc ở tư thế nghỉ khác nhau (**G1 +16,1 mm · T1 +36,7 mm · PM01 +45,0 mm**), nên ngưỡng ±5 mm đo "model nghỉ cao bao nhiêu" chứ không đo "có xuyên sàn hay không" |

**Thay thế `min_body_height ± 5 mm` bằng hai đại lượng hậu kiểm** (báo cáo số, **không** gắn nhãn đạt/không đạt):

1. `Δ so với vị trí nghỉ` = `min_body_height − rest_offset` (mm)
2. `pct_frames_penetration` (%) — % frame có ít nhất 1 body dưới −1 mm

Câu bắt buộc trong báo cáo:

> *"Một ngưỡng đã đăng ký được áp dụng (`foot_slide ≤ 50 mm/s`); một ngưỡng bị rút sau khi đo với lý do kỹ thuật, và phần thay thế là hậu kiểm."*

**Kết quả khi áp ngưỡng (số của nhóm, từ DEC-03):**

| Chỉ số | Ngưỡng | G1 | T1-29dof | PM01 |
|---|---|---|---|---|
| `foot_slide` (mm/s) | ≤ 50 | **49,0 ✅** (sát ngưỡng) | 83,1 ❌ | 118,4 ❌ |
| `min_body_height` (mm) — *ngưỡng đã rút* | — | +9,9 | −7,6 | +43,8 |
| `Δ` so với nghỉ (mm) | hậu kiểm | −6,25 | −44,29 | −1,10 |
| `pct_frames_penetration` (%) | hậu kiểm | 0 | 2,13 | 0 |

Hệ quả cho kết luận: vẫn **"tái lập một phần"**, nhưng lý do phải viết là **chỉ 1/3 robot đạt `foot_slide`**, và T1 xuyên sàn ở **2,13 %** frame — **không** được viết "vì nhóm không đặt ngưỡng".

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

Với mỗi robot: chạy đúng §3 (1 warm-up + 3 lần), cùng một file BVH, ghi `results/v5_sim2sim.csv`, kèm **toàn bộ bộ chỉ số chất lượng §1.2** (`foot_slide` L/R/mean, `min_body_height`, `rest_offset`, `pct_frames_penetration`, `joint_limit_saturation_pct`).

Câu hỏi V5 trả lời: **thời gian xử lý và chất lượng hình học có giữ được khi đổi embodiment không** — không phải "robot nào giỏi hơn".

---

## 8. Bảng phân công theo file này

| Vai | Việc | Không được làm |
|---|---|---|
| Code (Vỹ) | **Đã xong**: `scripts/measure_runtime.py` @ `5f9cdd5` (nhánh `task/code-scripts3`), xuất đúng §5 | không sửa ngưỡng trong file này |
| Run (Mạnh) | **Không chạy lại V3/V5** (Planner chốt); số giai đoạn 1 giữ nguyên bản đo cũ | không trộn lô mới với bản đo cũ |
| Review (Trường) | với bản đo cũ: kiểm 13 cột, **không** gọi cột `realtime_factor` là của vòng lặp retarget, loại dòng `warmup`, CV ≤ 5 % trên cả 5 lần đo | không tự đo lại rồi trộn số |
| Writing | điền bảng `bài báo | nhóm đo được` | không chép số paper sang cột nhóm |

---

## 9. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi | Người |
|---|---|---|---|
| 1.0 | 2026-11-20 | Bản đầu: chốt `ms_per_frame` / `fps_out` / `realtime_factor`, 1 warm-up + 3 lần, CV ≤ 5 %, ngưỡng 1,00; thêm V5 3 robot | Duy |
| 1.1 | 2026-11-20 | **RV-17**: tách hai đại lượng (vòng lặp retarget với hậu tố `_retarget`, và cả tiến trình với `_process`); ngưỡng 33,33 ms áp cho đại lượng retarget; thêm bảng §6.1; cấm quy đổi bằng hệ số 0,92; sửa ghi chú clip `walk1_subject1.bvh` (7840 frame, 261,3 s) ≠ "Walk 1" (33 s) của Bảng I | Duy |
| 1.2 | 2026-11-21 | **Đồng bộ với CLI cuối của Code** (`scripts/measure_runtime.py` @ `5f9cdd5`): đổi tên `ms_per_frame_retarget` → **`ms_per_frame`** và `ms_per_frame_retarget_p95` → **`ms_per_frame_p95`** (đây mới là tên chính thức); mọi số đo cả tiến trình giữ hậu tố `_process`; §5.1 chép đúng thứ tự cột của `SUMMARY_COLUMNS` (thêm `n_frames_total`, `process_cmd`); mô tả khả năng đo **2 process** của script | Duy |
| 1.3 | 2026-11-21 | **RV-29**: sửa lại cho đúng thực tế — giai đoạn 1 đo bằng **bản đo cũ**, **chỉ có `ms_per_frame_process`** (13 cột, 6 dòng = 1 warm-up + 5 lần đo), **không có** `ms_per_frame`; script `5f9cdd5` mới chỉ là **khả năng**, chưa dùng cho số giai đoạn 1 và Planner chốt không chạy lại V3/V5. §1.1, §5.1 (thêm bảng map cột cũ: `realtime_factor` → `realtime_factor_process`), §6.1 (bắt buộc dùng bảng bắc cầu), §2 (bản đo cũ không có `cuda_visible`) | Duy |
| 1.4 | 2026-11-21 | **Đồng bộ với code `tools/quality_metrics.py` @ `f00421e`** (audit công thức phát hiện lệch): §1.2 viết lại `foot_slide` (tâm thân bàn chân, `CONTACT_TOL_MM = 30`, tổng dịch ngang trên tổng thời gian tiếp đất, riêng L/R rồi **trung bình** — không phải `z < 1 cm` + trung vị như bản cũ) và `min_body_height` (min **gốc body** trên mọi body, báo mm); thêm `rest_offset`, `pct_frames_penetration` (`PENETRATION_MM = −1`), `joint_limit_saturation_pct` (`LIMIT_TOL_DEG = 0,5`, bão hoà không phải vượt). **DEC-03**: giữ `foot_slide ≤ 50 mm/s`, **rút** `min_body_height ± 5 mm` (đặt 2026-11-20, rút 2026-11-21, lý do kỹ thuật), thay bằng `Δ` so với vị trí nghỉ + `pct_frames_penetration`; thêm §6.4. Thêm **§1.3 chuẩn làm tròn** 3 chữ số thập phân, dấu phẩy | Duy |
