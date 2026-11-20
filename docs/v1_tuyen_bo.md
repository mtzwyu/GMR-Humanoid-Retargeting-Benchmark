# V1 — Tuyên bố cần kiểm chứng

**Nhóm 01 · HR-04 · Lớp 15DHTH07 · HK1 2026–2027 · ĐH Công Thương TP.HCM**
Người chốt: Trần Nguyễn Khánh Duy (NT) · Ngày chốt: 2026-11-20
Nguồn gốc: arXiv:2510.02252**v1** (9 trang) · repo https://github.com/YanjieZe/GMR, nhánh `master`, HEAD `25f56db7` (2026-10-23 giờ VN), giấy phép MIT.
Ghi chú đọc bài: `docs/paper_notes.md` · Định nghĩa phép đo: `docs/dinh_nghia_phep_do.md`

---

## 0. Câu chốt (dùng nguyên văn trong báo cáo)

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm kiểm chứng bằng cách đo thời gian xử lý mỗi frame khi retarget chuyển động LAFAN1 (30 fps) sang **Unitree G1** trên CPU, **không** bật `--rate_limit`; **sau 1 lần warm-up bị loại, chạy 5 lần**; tiêu chí: **giá trị cuối của `ms_per_frame`** theo quy tắc §4 (**mean khi CV ≤ 5 %, median khi CV > 5 %**) **≤ 33,33 ms** thì tuyên bố **tái lập được**. Kết quả giai đoạn 1 có số ở mức **cả tiến trình**: **CV = 2,13 %** → **mean = 17,349 ms/frame** (`fps_out_process` = **57,6**, `realtime_factor_process` = **1,92**) ≤ 33,33 ms → **tái lập được** (áp bảng bắc cầu §6.1). Số `ms_per_frame` (chỉ vòng lặp retarget) **không đo được** trong giai đoạn 1.**

Bốn điều bắt buộc phải ghi kèm câu trên — thiếu một điều là sai:

1. **Nguồn của tuyên bố là repo, không phải bài báo.** Câu "real-time" lấy từ `README` (mục *Key features*, dòng 1) và mô tả repo GitHub (*"in real time on CPU"*).
2. **Paper không công bố số, nhưng repo thì CÓ.** arXiv:2510.02252 (9 trang) **không** có con số `ms/frame` hay FPS nào (đã kiểm tra toàn văn — `docs/paper_notes.md` §12). **Nhưng README repo có mục "Speed Benchmark"** với số định lượng: **35~45 FPS** trên 13th Gen Intel Core i9-13900K 24-Cores và **60~70 FPS** trên AMD Ryzen Threadripper 7960X 24-Cores (bản `25f56db7`). Đây là **mốc đối chiếu duy nhất** của chính repo — phải nêu, không được nói "repo không có số".
3. **Ngưỡng 33,33 ms là ngưỡng của nhóm**, không phải ngưỡng của paper: `1000/30`, suy ra từ tốc độ phát của chính dữ liệu nguồn LAFAN1 (README Ubisoft: *"496,672 motion frames at 30fps"*). Nhóm đặt trước, không đổi sau khi thấy số.
4. **Giai đoạn 1 đo đại lượng nào — chỉ `ms_per_frame_process`.** Bản đo V3 đã dùng là **bản đo cũ**: `results/v3_runtime.csv` có **13 cột** và **chỉ có `ms_per_frame_process`**, không có cột `ms_per_frame`. Script `scripts/measure_runtime.py` (@`5f9cdd5`) **có khả năng** đo cả hai (2 process) nhưng **chưa được dùng cho số liệu giai đoạn 1**, và Planner đã chốt **không chạy lại** V3/V5 bằng script mới. Vì vậy: (a) trong báo cáo phải gọi file đó là **"bản đo cũ"**, **không** trình bày như file đúng hợp đồng §5.1; (b) kết luận phải áp **bảng bắc cầu §6.1** của `docs/dinh_nghia_phep_do.md`, **không** suy ra `ms_per_frame`, **không** nhân hệ số 0,92.

---

## 1. Vì sao tuyên bố này, không phải tuyên bố khác

Đề tài HR-04 yêu cầu đúng hai việc (PDF hướng dẫn, trang 2): *"Đo tốc độ xử lý thật và chất lượng ánh xạ, đối chiếu với bài báo"*. Trong 5 tuyên bố ứng viên dưới đây, **chỉ C5 đo được trong giai đoạn 1** vì nó không cần GPU, không cần IsaacSim, không cần train RL và không cần SMPL-X (có bản quyền).

Bốn tuyên bố còn lại đều là **kết quả của policy đã train** — muốn đo lại phải dựng IsaacSim + BeyondMimic + train 21 policy × 4 phương pháp. Ngoài khả năng của nhóm (CPU, 10 ngày, không GPU). Đây là kết luận quan trọng, không phải lý do để bỏ qua: nó được ghi thành mục "phạm vi kiểm chứng" trong báo cáo.

---

## 2. Năm tuyên bố định lượng ứng viên

### C1 — Success rate của policy tracking

| Trường | Nội dung |
|---|---|
| Đại lượng | success rate = số rollout chạm cuối clip / tổng rollout (**%**) |
| Số hiệu | **Bảng I, trang 6** |
| Giá trị gốc | GMR: 100 % trên "Dance 1" và "Dance 2" (sim), trong khi PHC = **0 %** ở cả sim / sim-dr / sim2sim. Ngược lại GMR chỉ đạt **51 %** trên "Dance 5" ở sim2sim. PHC "Run (stop & go)" sim = 17 %; ProtoMotions cùng motion sim = 20 % |
| Điều kiện đo | robot **Unitree G1**; 21 chuỗi LAFAN1 (5,5 s – 130,5 s); policy **BeyondMimic**, 1 policy/clip; IsaacSim cho sim & sim-dr, MuJoCo/ROS cho sim2sim; **100** trial (sim), **4096** (sim-dr), **100** (sim2sim); sim tắt domain randomization; rollout bắt đầu từ default pose; episode dừng khi ngã hoặc lệch anchor quá ngưỡng |
| Đo lại được? | **Không.** Cần GPU + IsaacSim + train 84 policy (21 clip × 4 phương pháp). Paper không nêu cấu hình phần cứng nên không thể tái lập môi trường |

### C2 — Sai số tracking của policy

| Trường | Nội dung |
|---|---|
| Đại lượng | `E_g-mpbpe` (**mm**), `E_mpbpe` (**mm**), `E_mpjpe` (**10⁻³ rad**) — trung bình trên body, tính trên các frame policy còn sống |
| Số hiệu | **Bảng II, trang 6**; định nghĩa metric ở mục III-D, trang 4 |
| Giá trị gốc (mean) | GMR: **104,1 mm / 28,1 mm / 561,7 ×10⁻³ rad**. PHC: 247,8 / 40,2 / 778,5. ProtoMotions: 139,7 / 33,2 / 641,8. Unitree: 77,2 / 23,2 / 483,0 |
| Điều kiện đo | như C1, chế độ **sim**, **100** rollout/policy, 21 motion, Unitree G1, BeyondMimic |
| Đo lại được? | **Không** — cùng lý do C1; thêm nữa sai số này đo trên **quỹ đạo policy**, không phải trên file retarget |

### C3 — Độ nhạy theo frame bắt đầu của reference

| Trường | Nội dung |
|---|---|
| Đại lượng | success rate sim2sim (**%**) theo `start frame` |
| Số hiệu | **Bảng III, trang 7** |
| Giá trị gốc | "Walk 2", GMR: **64 %** (start frame 0) → **100 %** (start frame 7). "Turn 1", PHC: 14 % (frame 0) → 100 % (frame 49) |
| Điều kiện đo | sim2sim MuJoCo, 100 rollout, **cùng một policy** chỉ đổi frame bắt đầu; Unitree G1 |
| Đo lại được? | **Không** — cần policy đã train; đây là hiện tượng của policy, không phải của retargeter |

### C4 — Artifact hình học của file retarget

| Trường | Nội dung |
|---|---|
| Đại lượng | độ xuyên sàn / độ bay (**cm**), số điểm self-intersection, số sudden jump của joint (**lần**, **giây**) |
| Số hiệu | mục **V-B, trang 6** (và mục III-B, trang 4) |
| Giá trị gốc | PHC xuyên sàn **60 cm** ("Dance 1"/"Dance 2"). Hậu xử lý PHC gây bay **≥ 30 cm**. GMR "Dance 5" có sudden jump waist roll trên đoạn **10 giây**, **< 2 %** toàn dataset |
| Điều kiện đo | Unitree G1, LAFAN1, quan sát trực tiếp file retarget (không cần policy) |
| Đo lại được? | **Một phần** — không cần train, nhưng (a) phải dựng lại **PHC** (cần SMPL-X có bản quyền + chuyển BVH→SMPL-X), (b) paper **không định nghĩa** "sudden jump" bằng ngưỡng số, nên mọi ngưỡng sẽ do nhóm tự đặt → không so sánh được với con số 2 % của paper |

### C5 — Tốc độ retarget "theo thời gian thực trên CPU" ⭐ **TUYÊN BỐ CHÍNH**

| Trường | Nội dung |
|---|---|
| Đại lượng | `ms_per_frame` (**ms/frame**), `fps_out` (**frame/s**), `realtime_factor` = `fps_out` / `fps_src` (**lần**). Phụ: `ms_per_frame_process` (cả tiến trình) |
| Số hiệu | **README repo, mục "Key features", dòng 1**: *"Real-time high-quality retargeting"*; **mô tả repo GitHub**: *"Retarget human motions into diverse humanoid robots **in real time on CPU**"*; **README, mục "Speed Benchmark"**: bảng 2 CPU (xem "Giá trị gốc"). **Bài báo: không có bảng/hình nào về tốc độ** (xem `paper_notes.md` §12) |
| Giá trị gốc | **Có số, nhưng của repo — paper không có.** README *Speed Benchmark* (bản `25f56db7`): **35~45 FPS** (13th Gen Intel Core i9-13900K 24-Cores), **60~70 FPS** (AMD Ryzen Threadripper 7960X 24-Cores). **README không nêu điều kiện đo** (motion nào, robot nào, có `--rate_limit` không, có tính render không) → không tái lập chính xác được |
| Điều kiện đo | CPU (không GPU cho đường đo); robot **Unitree G1** (robot duy nhất paper dùng, trang 3); dữ liệu **LAFAN1 BVH 30 fps**; retarget tuần tự từng frame, frame trước làm initial guess (đúng như mục IV, trang 5); solver dừng ở 0,001 hoặc 10 vòng lặp; **không** bật `--rate_limit` |
| Đo lại được? | **Có.** Chỉ cần: repo + LAFAN1 BVH + Python 3.10 + MuJoCo CPU. Không cần GPU, không cần SMPL-X, không cần train |

**Vì sao C5 là lựa chọn đúng (ma trận khả thi):**

| | C1 | C2 | C3 | C4 | **C5** |
|---|---|---|---|---|---|
| Cần GPU / IsaacSim | ✔ | ✔ | ✔ | ✘ | **✘** |
| Cần train RL (84 policy) | ✔ | ✔ | ✔ | ✘ | **✘** |
| Cần giấy phép SMPL-X | ✘ | ✘ | ✘ | ✔ | **✘** |
| Cần dataset LAFAN1 | ✔ | ✔ | ✔ | ✔ | **✔** (miễn phí) |
| Đo được trên CPU trong 10 ngày | ✘ | ✘ | ✘ | ~ | **✔** |
| Là trọng tâm PDF hướng dẫn (trang 2) | ✘ | ~ | ✘ | ✘ | **✔** |

→ Danh sách đầy đủ **3 bảng số của paper**, giá trị gốc, và điều kiện tái lập từng bảng: **§8**. Kết luận dự kiến (tái lập một phần): **§9**.

---

## 3. Cách đo lại tuyên bố chính (C5)

### 3.1 Nguyên tắc: hai đại lượng, tên phải đúng

`scripts/bvh_to_robot.py` chạy **retarget và render trong cùng một vòng lặp**; dòng `print(f"Actual rendering FPS: …")` trong script là FPS **có render**, không phải throughput retargeting. Dùng số đó là **đo sai đối tượng** → loại.

Vì vậy phải tách **hai** đại lượng (định nghĩa đầy đủ: `docs/dinh_nghia_phep_do.md` §1.1):

| Đại lượng | Lấy từ | Gồm những gì |
|---|---|---|
| `ms_per_frame` | process **probe** (`--retarget-only`, không viewer) | **chỉ** lời gọi `retarget()` từng frame |
| `ms_per_frame_process` | process **entry script** (`bvh_to_robot.py`) | nạp BVH + `GMR(...)` + viewer + retarget + render + ghi pkl |

**Giai đoạn 1 (V3) đo đại lượng nào — thực tế chỉ có `ms_per_frame_process`.** Số liệu đã thu dùng **bản đo cũ** (đo thẳng `bvh_to_robot.py`, không qua script mới), nên **không** có `ms_per_frame` (chỉ vòng lặp retarget). Script `scripts/measure_runtime.py` (@`5f9cdd5`) đã có khả năng đo cả hai, nhưng **chưa dùng** cho số giai đoạn 1 và Planner chốt **không chạy lại** V3/V5. Ngưỡng 33,33 ms vẫn áp cho `ms_per_frame`, nên khi viết báo cáo **bắt buộc** đi qua bảng bắc cầu `docs/dinh_nghia_phep_do.md` §6.1; **không** nhân hệ số 0,92.

Nếu dùng `scripts/measure_runtime.py` (chưa dùng cho giai đoạn 1) thì nó tự chạy 2 process con:

1. **entry script** — `bvh_to_robot.py` chạy nguyên bản, có viewer → `ms_per_frame_process`;
2. **probe** — chạy lại chính script với `--retarget-only`, **không** dựng `RobotMotionViewer` → `ms_per_frame`, và `t_init`.

Cả hai process đều được script đặt `CUDA_VISIBLE_DEVICES=""`.

- Đo bằng `time.perf_counter()` (đồng hồ đơn điệu, độ phân giải cao). **Không** dùng `time.time()` như script gốc.
- Ghi riêng `t_init` = thời gian khởi tạo `GMR(...)` (load MJCF + config), **không** cộng vào `ms_per_frame`.

### 3.2 Lệnh chạy

> ⚠ **Số liệu giai đoạn 1 KHÔNG dùng lệnh dưới đây.** Bản đo cũ đã chốt, Planner không cho chạy lại V3/V5. Lệnh dưới chỉ là **quy trình chuẩn** nếu sau này đo lại (hoặc cho V5), và để Run biết CLI đã chốt.

CLI chính thức của `scripts/measure_runtime.py`:
`--motion` (alias `--bvh-file`), `--robot`, `--runs N` (**tổng** số lần chạy; mặc định của script là `4` = 1 warm-up + 3 đo — **bản chính thức dùng `6`**), `--warmup-runs`, `--warmup-frames`, `--out` (alias `--csv`), `--raw-out`, `--fps-src`, `--script`, `--gmr-dir`, `--python`, `--dry-run`, `--frames`, `--work-dir`.

```bash
# (0) chạy khô, không cần env gmr (dữ liệu giả) — kiểm hợp đồng CSV
python scripts/measure_runtime.py --dry-run --runs 4 --warmup-runs 1

# (1) BẢN NHANH: 1 warm-up + 3 lần đo — CHỈ để kiểm tra chạy được, KHÔNG dùng cho số trong báo cáo
conda run -n gmr python scripts/measure_runtime.py \
  --motion <LAFAN1>/walk1_subject1.bvh \
  --robot unitree_g1 \
  --runs 4 --warmup-runs 1 --warmup-frames 30 \
  --fps-src 30 \
  --out results/v3_runtime_check.csv \
  --raw-out results/v3_runtime_check_raw.csv

# (2) BẢN TÁI LẬP SỐ CHÍNH THỨC V3: 1 warm-up + 5 lần đo — DÙNG CHO SỐ TRONG BÁO CÁO
conda run -n gmr python scripts/measure_runtime.py \
  --motion <LAFAN1>/walk1_subject1.bvh \
  --robot unitree_g1 \
  --runs 6 --warmup-runs 1 --warmup-frames 30 \
  --fps-src 30 \
  --out results/v3_runtime.csv \
  --raw-out results/v3_runtime_raw.csv
```

> ⚠ **Phân biệt hai bản.** Bản đo chính thức V3 là **1 warm-up + 5 lần đo** (`--runs 6`). Lệnh `--runs 4` chỉ tạo ra 3 lần đo → **không tái lập được** bộ số trong báo cáo. Bản nhanh ghi ra file `_check.csv` riêng để không ghi đè số chính thức.

- `--gmr-dir` mặc định `third_party/GMR`; nếu clone chỗ khác thì truyền vào.
- `--python` mặc định là python đang chạy script — trong `conda run -n gmr` thì đúng env `gmr`.
- `--raw-out` mặc định là `<out>_raw.csv` nếu bỏ trống.

Lệnh tham chiếu để lấy file `.pkl` (chạy được, nhưng **không dùng để đo** vì có render):

```bash
conda run -n gmr python scripts/bvh_to_robot.py \
  --bvh_file <LAFAN1>/walk1_subject1.bvh --robot unitree_g1 \
  --save_path results/v3/walk1_g1.pkl
```

> ⚠ **Cảnh báo tên clip (bắt buộc đọc).** `walk1_subject1.bvh` dài **7840 frame = 261,3 giây** ở 30 fps. **Không được gọi nó là "Walk 1" của Bảng I paper** — "Walk 1" trong Bảng I chỉ dài **33 s** (trang 6). Đây là hai clip khác nhau; gộp lại là sai số liệu. Tên file LAFAN1 theo quy ước `[theme][take]_[subject].bvh` của Ubisoft — Run ghi lại **tên file thực tế + số frame** vào CSV.

### 3.3 Đầu ra — phân biệt "bản đo cũ" và hợp đồng mới

**Số liệu giai đoạn 1 là bản đo cũ**, không phải định dạng §5.1. Ghi rõ trong báo cáo:

`results/v3_runtime.csv` (bản đo cũ) — **13 cột**, **6 dòng** (1 warm-up + 5 lần đo):

`mode, phase, robot, input, frames, motion_duration_s, wall_clock_s, ms_per_frame_process, realtime_factor, exit_code, cmd, log, note`

Ba điều bắt buộc khi trích số từ file này:

1. **Không có cột `ms_per_frame`** → kết luận phải đi qua bảng bắc cầu `docs/dinh_nghia_phep_do.md` §6.1, và nêu rõ số Nhóm A **không đo được** trong giai đoạn 1.
2. Cột `realtime_factor` **trong file cũ là của cả tiến trình** (nó được tính từ `ms_per_frame_process`), nên khi viết báo cáo phải gọi đúng là **`realtime_factor_process`** — không được trình bày như `realtime_factor` của vòng lặp retarget.
3. Dòng `phase = warmup` bị loại; chỉ dùng `measure_*`. Không cộng tất cả 6 dòng.

Nếu sau này có người chạy lại bằng script mới, **định dạng đích** (hợp đồng §5.1, `SUMMARY_COLUMNS` @ `5f9cdd5`) là:

`run, robot, motion, bvh_file, n_frames, n_warmup_frames, fps_src, ms_per_frame, ms_per_frame_mean, ms_per_frame_p95, fps_out, realtime_factor, t_init_s, cpu, ram_gb, os, python, numpy, mujoco, mink, torch, git_head, cuda_visible, cmd, timestamp, n_frames_total, ms_per_frame_process, fps_out_process, realtime_factor_process, process_cmd`

- `ms_per_frame*` / `fps_out` / `realtime_factor`: từ **probe** (`--retarget-only`, không viewer).
- `ms_per_frame_process` / `fps_out_process` / `realtime_factor_process`: từ **entry script**.
- `cmd` = lệnh probe; `process_cmd` = lệnh entry script.

`results/v3_runtime_raw.csv` (chỉ có khi chạy script mới) — 1 dòng / frame: `run, motion, robot, frame, included, ms`.

### 3.4 Sai số chấp nhận

| Mức | Ngưỡng | Cách xử lý |
|---|---|---|
| Lặp lại giữa các lần chạy | **CV ≤ 5 %**, tính **riêng** cho `ms_per_frame` và `ms_per_frame_process` | nếu > 5 %: chạy thêm 2 lần, báo **trung vị** thay vì trung bình, và ghi rõ máy không ổn định. Bản đo cũ có **5** lần đo → tính CV trên **cả 5**, không cắt còn 3 |
| Ngưỡng quyết định tuyên bố | `realtime_factor` ≥ **1,00** — áp cho **`ms_per_frame`** | giai đoạn 1 không có số này: đọc cột cũ thành `realtime_factor_process` và áp §6.1 |
| Dung sai kỹ thuật của phép đo | ± 5 % (làm tròn 0,1 ms; 0,1 fps) | — |

**Không có sai số "so với paper"** vì paper không có số. Đây là điểm yếu cố hữu của tuyên bố này và phải viết thẳng trong báo cáo.

### 3.5 Ba mức kết luận (chốt trước, không đổi sau khi thấy số)

| `realtime_factor` (mean nếu CV ≤ 5 %, median nếu CV > 5 %; n = 5) | Kết luận |
|---|---|
| ≥ 1,00 | **Tái lập được** — GMR retarget nhanh ít nhất bằng tốc độ phát của dữ liệu nguồn trên CPU |
| 0,80 – 0,99 | **Tái lập một phần** — gần real-time, phải nêu cấu hình CPU và đề xuất CPU mạnh hơn |
| < 0,80 | **Không tái lập được** — phải thử thêm máy thứ hai trước khi kết luận; nếu vẫn < 0,80 thì kết luận "không tái lập trên CPU phổ thông", kèm phân tích nút thắt (2 stage IK × 10 vòng lặp) |

Bảng trên định nghĩa cho `ms_per_frame` (số chính thức, lấy từ probe). **Giai đoạn 1 không có số này**, nên khi áp cho bản đo cũ thì: (a) đọc `realtime_factor` thành **`realtime_factor_process`**, và (b) dùng bảng bắc cầu `docs/dinh_nghia_phep_do.md` **§6.1** — `_process` ≤ 33,33 ms là **điều kiện đủ** để kết luận tái lập; nếu `_process` > 33,33 ms thì **chưa kết luận được** vì thiếu số Nhóm A (không được suy ra).

### 3.6 So với Speed Benchmark của repo — vì sao nhóm đo **nhanh hơn** i9-13900K

Đây là mốc đối chiếu **duy nhất** phía repo (bản `25f56db7`). Bảng dưới là so sánh **tham khảo**, không phải so sánh có kiểm soát:

| Nguồn | CPU | Tốc độ | Điều kiện đo |
|---|---|---|---|
| README GMR, *Speed Benchmark* | 13th Gen Intel Core i9-13900K 24-Cores | **35~45 FPS** | **README không nêu** |
| README GMR, *Speed Benchmark* | AMD Ryzen Threadripper 7960X 24-Cores | **60~70 FPS** | **README không nêu** |
| Nhóm đo (bản đo cũ V3) | 12th Gen Intel Core i5-12450HX (8 core) | **57,6 FPS** (mean 17,349 ms/frame) | `walk1_subject1.bvh` (7840 frame, 30 fps), `unitree_g1`, **không** `--rate_limit`, đo **cả tiến trình** |

Nhóm đo **cao hơn** khoảng 28–65 % so với mức của i9-13900K dù CPU yếu hơn, và **thấp hơn** mức Threadripper. Bốn lý do, theo thứ tự quan trọng:

1. **README không nêu điều kiện đo** — không biết họ đo motion nào, robot nào, clip dài bao nhiêu, có `--rate_limit` hay không, có tính khởi tạo + render hay không. Vì vậy **không tái lập chính xác được**; đây là so sánh tham khảo.
2. **Độ khó của motion** — clip càng nhiều động tác nhanh/biên độ lớn thì solver càng lâu hội tụ (2 stage × tối đa 10 vòng lặp, ngưỡng 0,001). `walk1_subject1` là **đi bộ**, nhẹ hơn nhiều so với dance/kungfu trong Bảng I.
3. **Đời CPU** — i5-12450HX (12th Gen, 8 core) vs i9-13900K (13th Gen, 24 core): xung đơn nhân khác nhau, nhưng GMR chạy tuần tự từng frame nên khoảng cách không tỉ lệ với số core.
4. **Đại lượng khác nghĩa** — số của nhóm là **cả tiến trình** (init + render + ghi pkl), tức **đã gồm overhead**; nếu lệch thì nó làm nhóm **chậm đi**. Vậy phần retarget thuần còn nhanh hơn 57,6 FPS.

**Không được kết luận** "GMR chạy nhanh hơn trên CPU yếu hơn" — điều kiện đo của README không rõ. Kết luận tuyên bố vẫn chỉ dựa trên ngưỡng 33,33 ms ở §3.5.

---

## 4. Rủi ro không tái lập

| # | Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|---|
| 1 | **Paper không nêu phần cứng**; README chỉ nêu **2 CPU** và **không nêu motion/robot/điều kiện** của Speed Benchmark | Không có mốc so sánh có kiểm soát; "real time" của họ có thể là máy/motion khác hẳn | Ghi rõ CPU/RAM/OS của nhóm; nêu cả 2 mốc README (35~45 FPS i9-13900K, 60~70 FPS 7960X) khi so sánh, không chọn 1 mốc có lợi |
| 2 | **Đo sai đối tượng** — dùng FPS render của script | Kết quả vô nghĩa, thường thấp hơn thực tế rất nhiều | Dùng `scripts/measure_runtime.py` (probe `--retarget-only`); cấm dùng `Actual rendering FPS` |
| 3 | **Bật `--rate_limit`** | Entry script bị áp nhịp theo motion fps → `ms_per_frame_process` luôn ≈ 33 ms (tự ứng nghiệm); probe không bị ảnh hưởng | `measure_runtime.py` không truyền cờ này; nếu đo tay thì không bật, và ghi vào `cmd` |
| 4 | **Đường batch cần CUDA** — `bvh_to_robot_dataset.py` hardcode `device = "cuda:0"` | Máy chỉ CPU chạy batch sẽ lỗi → tưởng "không cài được" | Dùng `scripts/measure_runtime.py`; không dùng batch cho phép đo chính |
| 5 | **Viewer cần display** | Headless/SSH làm entry script chết | Probe `--retarget-only` không dựng viewer; entry script (đo `_process`) vẫn cần display — chạy trên máy có màn hình |
| 6 | **Trôi phiên bản repo** — PDF hướng dẫn (8/2025) dùng conda + `pip install -e .`, README hiện tại dùng `uv sync`; repo từ 12 → 19 robot | Số đo khác nhau giữa các lần | **Ghim commit `25f56db7`**; ghi `git rev-parse --short HEAD` vào mọi CSV |
| 7 | **Sai `fps_src`** — GMR hardcode 30 fps, không đọc header BVH | Nếu lỡ dùng file 120 Hz (ví dụ `assets/xsens_bvh_test/…120Hz…bvh`) thì `realtime_factor` sai **4 lần** | Chỉ dùng LAFAN1 (30 fps, theo README Ubisoft); đọc header `Frame Time` để đối chiếu và ghi cả hai vào CSV |
| 8 | **OS** — README chỉ test Ubuntu 22.04/20.04; worktree này là Windows | Cài đặt có thể tắc (MuJoCo, Mink/qpsolvers) | Nếu tắc: ghi nhật ký theo AGENTS.md (tắc ở đâu, đã thử gì); dùng WSL2 và ghi rõ |
| 9 | **Python 3.10** bắt buộc theo hướng dẫn | Lệch version → API Mink khác | Dùng đúng 3.10; lưu `requirements.txt` thực tế |
| 10 | **Máy đo có GPU** | torch/MuJoCo có thể chọn backend khác → số không so được với "CPU" | Script mới tự đặt `CUDA_VISIBLE_DEVICES=""` và ghi cột `cuda_visible`; **bản đo cũ không có cột này** → phải ghi rõ "không xác minh được" |
| 11 | **Clip quá ngắn** | Ảnh hưởng warm-up lên trung bình | Dùng clip dài (`walk1_subject1.bvh`, 7840 frame / 261,3 s) và loại 30 frame đầu mỗi lần |
| 12 | **Nhầm tên clip** — `walk1_subject1.bvh` (7840 frame, 261,3 s) bị gọi là "Walk 1" của Bảng I (33 s) | Bảng so sánh ghép sai đối tượng, sai số liệu | CSV ghi `bvh_file` + `n_frames_total`; trong báo cáo luôn ghi tên file thật, không dùng nhãn "Walk 1" cho clip này |
| 13 | **Nhầm tên đại lượng** — dùng `ms_per_frame` cho số đo cả tiến trình | Kết luận áp sai ngưỡng, Review không đối chiếu được | `ms_per_frame` = **chỉ** vòng lặp retarget (Nhóm A, tên chính thức); mọi số đầu-cuối **bắt buộc** có hậu tố `_process` |
| 14 | **Trình bày bản đo cũ như file đúng hợp đồng §5.1** — file chỉ có 13 cột, không có `ms_per_frame`, cột `realtime_factor` là của `_process` | Báo cáo tuyên bố mạnh hơn thực tế đã đo | Gọi đúng "bản đo cũ"; đổi nhãn cột khi trích số; kết luận đi qua §6.1 |

---

## 5. Sẽ báo cáo thế nào (tách cột, không trộn)

| Đại lượng | Bài báo | Nhóm đo được |
|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | **không đo** — bản đo cũ không có cột này |
| `ms_per_frame_process` (ms) — G1, LAFAN1 | **không nêu** (repo: xem dòng dưới) | **17,349** (mean, n = 5, CV 2,13 %) — `results/v3_runtime.csv`, bản đo cũ |
| `fps_out` (frame/s) | **không nêu** | không đo (chỉ suy ra được từ `ms_per_frame`) |
| `fps_out_process` (frame/s) | **không nêu** | **57,6** (= 1000 / 17,349) |
| `realtime_factor` (lần) | **không nêu** — chỉ có chữ "real time" | không đo; cột `realtime_factor` trong file cũ **là của `_process`** |
| `realtime_factor_process` (lần) | **không nêu** | **1,92** (cột mang tên `realtime_factor` trong file cũ) |
| FPS — README *Speed Benchmark* (bản `25f56db7`) | **không nêu** (số này của repo) | xem dòng dưới |
| FPS — nhóm đo (i5-12450HX) | README: **35~45 FPS** (i9-13900K) và **60~70 FPS** (Threadripper 7960X) | **57,6 FPS** (mean 17,349 ms, cả tiến trình) |
| Success rate "Dance 5" sim2sim (%) | 51 | không đo (ngoài phạm vi) |
| `E_g-mpbpe` mean GMR (mm) | 104,1 | không đo (ngoài phạm vi) |
| Xuyên sàn PHC "Dance 1" (cm) | 60 | không đo (ngoài phạm vi) |

Nguyên tắc: chỉ điền số **đã Review PASS**; không suy diễn, không nội suy, không chép số paper sang cột của nhóm. Số `ms_per_frame` để **trống** — giai đoạn 1 không đo được, và **không** được thay bằng số `_process`.

---

## 6. Ba điều nhóm **không** được tuyên bố

1. **Không** được nói "GMR nhanh hơn PHC/ProtoMotions" — paper không đo tốc độ, nhóm cũng không.
2. **Không** được nói "nhóm tái lập Bảng I / Bảng II" — hai bảng đó cần train RL.
3. **Không** được nói "paper tuyên bố real-time" — paper **không** nói vậy; tuyên bố real-time nằm ở **README và mô tả repo**. Câu chốt ở §0 đã ghi đúng nguồn.

---

## 7. Việc tiếp theo (bàn giao)

| Cho ai | Việc | Điều kiện xong |
|---|---|---|
| **Code (Vỹ)** | **Đã xong**: `scripts/measure_runtime.py` @ `5f9cdd5` (nhánh `task/code-scripts3`). CLI và cột CSV đã chốt — V1 chỉ đọc, không sửa script | `--dry-run` chạy được; xuất đúng 2 file CSV |
| **Run (Mạnh)** | **Không chạy lại V3/V5** bằng script mới (Planner đã chốt). Số giai đoạn 1 giữ nguyên bản đo cũ `results/v3_runtime.csv` | Không sinh thêm file runtime mới; nếu có chạy lại thì phải ghi rõ là lô khác, không trộn |
| **Review (Trường)** | Kiểm bản đo cũ: đúng file, **không** được gọi cột `realtime_factor` là của vòng lặp retarget, đủ 13 cột, dòng `warmup` bị loại, CV ≤ 5 % | PASS/FAIL theo mẫu 5 dòng |
| **Writing** | Điền §5, gọi file là **"bản đo cũ"** | Không ô nào ở cột "nhóm đo được" bị chép từ paper; `ms_per_frame` để trống |

---

## 8. Các tuyên bố định lượng trong paper và vì sao **không** tái lập được

Đây là mục trả lời trực tiếp yêu cầu của đề tài ("kiểm chứng một tuyên bố định lượng trong bài báo"). Bài báo có **đúng 3 bảng số**. Cả ba đều đo **policy đã train**, không đo retargeter — nên không thể tái lập nếu không có GPU + IsaacSim.

| # | Bảng | Đại lượng (đơn vị) | Giá trị GMR | Cần gì để tái lập |
|---|---|---|---|---|
| 1 | **Bảng I**, trang 6 | success rate (%), 21 motion × 4 phương pháp × 3 chế độ | 100 % ở "Dance 1"/"Dance 2"; **51 %** ở "Dance 5" sim2sim | IsaacSim + BeyondMimic + **policy đã train** cho từng clip × từng phương pháp + 100/4096/100 rollout |
| 2 | **Bảng II**, trang 6 | tracking error: `E_g-mpbpe` (mm), `E_mpbpe` (mm), `E_mpjpe` (10⁻³ rad) | mean **`E_g-mpbpe` = 104,1 mm**; `E_mpbpe` = 28,1 mm; `E_mpjpe` = 561,7 | như trên, chế độ **sim**, 100 rollout/policy; sai số đo trên **quỹ đạo policy**, không phải file retarget |
| 3 | **Bảng III**, trang 7 | success rate sim2sim (%) theo `start frame` | "Walk 2": 64 % (frame 0) → 100 % (frame 7) | **cùng một policy đã train**, chỉ đổi frame đầu + 100 rollout MuJoCo |

**Khối lượng thật của một lần tái lập:** 21 clip × 4 phương pháp (GMR, PHC, ProtoMotions, Unitree) = **84 policy**, mỗi policy chạy 100 + 4096 + 100 rollout. Cộng thêm: dựng PHC (cần SMPL-X có bản quyền), chuyển BVH→SMPL(-X), và bộ dữ liệu Unitree **không công khai** (paper tự ghi là closed-source).

**Kết luận: ngoài phạm vi giai đoạn 1.** Nhóm **không có GPU**, không có IsaacSim, không có license SMPL-X, và thời lượng giai đoạn 1 là 10 ngày. Đây không phải "chưa làm" mà là **không thể làm** với nguồn lực hiện có — và chính paper cũng không công bố cấu hình phần cứng để tái lập (xem `paper_notes.md` §12).

Hệ quả: mọi bảng trong báo cáo phải tách hai cột. Cột "bài báo" chép đúng số + số hiệu bảng; cột "nhóm đo được" để **trống** ở các dòng Bảng I/II/III và ghi rõ "không đo — ngoài phạm vi".

---

## 9. Kết luận dự kiến của V1 (khung cho mục 7 báo cáo)

Kết luận phải viết được thành **tái lập một phần**, không phải "tái lập được" cũng không phải "không tái lập được":

> **Tái lập một phần.** Phần **thời gian thực** kiểm chứng được ở mức **cả tiến trình**: `ms_per_frame_process` = **17,349 ms** (`realtime_factor_process` = **1,92**, **5** lần đo, **CV = 2,13 %**) theo **bản đo cũ** `results/v3_runtime.csv` — tương đương **57,6 FPS** trên i5-12450HX, so với mốc README 35~45 FPS (i9-13900K) và 60~70 FPS (Threadripper 7960X); áp bảng bắc cầu §6.1 với ngưỡng 33,33 ms → **tái lập được**. Số `ms_per_frame` (chỉ vòng lặp retarget) **không đo được** trong giai đoạn 1 vì bản đo cũ không có cột đó, và script mới chưa được dùng. Phần **bảng số của paper** (Bảng I, II, III) **không tái lập được**, vì các bảng đó đo policy đã train trong IsaacSim trên GPU — nhóm không có GPU, không có IsaacSim và không thể train 84 policy trong 10 ngày; con số 104,1 mm của Bảng II được ghi ở cột "bài báo" và **không** được đối chiếu với bất kỳ số nào nhóm tự đo.

Điều kiện để câu trên đúng:

1. Chỉ điền số vào chỗ `…` khi có `results/v3_runtime.csv` (**bản đo cũ**) do Review chấm PASS.
2. Không đổi ngưỡng 33,33 ms sau khi thấy số.
3. Không dùng từ "tái lập được" cho toàn bộ bài báo — chỉ cho phần thời gian thực.
4. **Không** được viết "retarget đạt real-time" như thể đã đo riêng vòng lặp retarget. Chỉ được nói đúng mức đã đo: **cả tiến trình**. Nếu muốn nói chắc hơn thì phải chạy probe (script `5f9cdd5`) — việc này chưa được làm.
5. Nếu phần thời gian thực cũng không đạt, câu kết luận phải đổi thành "không tái lập được", **không** được giữ nguyên "một phần" cho đẹp.
