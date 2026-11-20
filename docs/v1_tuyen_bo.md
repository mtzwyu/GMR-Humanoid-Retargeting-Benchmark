# V1 — Tuyên bố cần kiểm chứng

**Nhóm 01 · HR-04 · Lớp 15DHTH07 · HK1 2026–2027 · ĐH Công Thương TP.HCM**
Người chốt: Trần Nguyễn Khánh Duy (NT) · Ngày chốt: 2026-11-20
Nguồn gốc: arXiv:2510.02252**v1** (9 trang) · repo https://github.com/YanjieZe/GMR, nhánh `master`, HEAD `25f56db7` (2026-10-22), giấy phép MIT.
Ghi chú đọc bài: `docs/paper_notes.md` · Định nghĩa phép đo: `docs/dinh_nghia_phep_do.md`

---

## 0. Câu chốt (dùng nguyên văn trong báo cáo)

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm kiểm chứng bằng cách đo thời gian xử lý mỗi frame (`ms_per_frame`) khi retarget chuyển động LAFAN1 (30 fps) sang **Unitree G1** trên CPU, **không** bật `--rate_limit`; tuyên bố được coi là **tái lập được** nếu trung bình 3 lần chạy (sau 1 lần warm-up bị loại) có `ms_per_frame` trung vị ≤ **33,3 ms**, tức `fps_out` ≥ **30** và `realtime_factor` ≥ **1,00**.**

Bốn điều bắt buộc phải ghi kèm câu trên — thiếu một điều là sai:

1. **Nguồn của tuyên bố là repo, không phải bài báo.** Câu "real-time" lấy từ `README` (mục *Key features*, dòng 1) và mô tả repo GitHub (*"in real time on CPU"*).
2. **Paper không công bố số.** arXiv:2510.02252 (9 trang) **không** có bất kỳ con số `ms/frame` hay FPS nào, cũng không nêu cấu hình CPU/GPU (đã kiểm tra toàn văn — `docs/paper_notes.md` §12). Vì vậy "giá trị gốc" của tuyên bố này là **định tính**.
3. **Ngưỡng 33,3 ms là ngưỡng của nhóm**, không phải ngưỡng của paper: `1000/30`, suy ra từ tốc độ phát của chính dữ liệu nguồn LAFAN1 (README Ubisoft: *"496,672 motion frames at 30fps"*). Nhóm đặt trước, không đổi sau khi thấy số.
4. **Giai đoạn 1 đo đại lượng nào:** V3 đo **cả hai** trong một lần chạy bằng `scripts/measure_runtime.py` — `ms_per_frame` (probe không viewer) và `ms_per_frame_process` (entry script). Ngưỡng 33,3 ms áp cho `ms_per_frame`; quy tắc bắc cầu khi thiếu số Nhóm A ở `docs/dinh_nghia_phep_do.md` §6.1 — **không** được quy đổi bằng hệ số 0,92.

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
| Số hiệu | **README repo, mục "Key features", dòng 1**: *"Real-time high-quality retargeting"*; **mô tả repo GitHub**: *"Retarget human motions into diverse humanoid robots **in real time on CPU**"*. **Bài báo: không có bảng/hình nào về tốc độ** (xem `paper_notes.md` §12) |
| Giá trị gốc | **Không có số.** Paper không nêu ms/frame, không nêu FPS, không nêu cấu hình CPU. Repo cũng không nêu số. Giá trị gốc chỉ là **định tính: "real time"** |
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

**Giai đoạn 1 (V3) đo cả hai trong một lần chạy** bằng `scripts/measure_runtime.py` (Code đã chốt @ `5f9cdd5`). Ngưỡng 33,3 ms áp cho **`ms_per_frame`**; `_process` chỉ là cận trên chẩn đoán. Bảng bắc cầu khi thiếu số Nhóm A: `docs/dinh_nghia_phep_do.md` §6.1 (**không** nhân hệ số 0,92).

Script tự chạy 2 process con:

1. **entry script** — `bvh_to_robot.py` chạy nguyên bản, có viewer → `ms_per_frame_process`;
2. **probe** — chạy lại chính script với `--retarget-only`, **không** dựng `RobotMotionViewer` → `ms_per_frame`, và `t_init`.

Cả hai process đều được script đặt `CUDA_VISIBLE_DEVICES=""`.

- Đo bằng `time.perf_counter()` (đồng hồ đơn điệu, độ phân giải cao). **Không** dùng `time.time()` như script gốc.
- Ghi riêng `t_init` = thời gian khởi tạo `GMR(...)` (load MJCF + config), **không** cộng vào `ms_per_frame`.

### 3.2 Lệnh chạy (tab Run thực thi)

CLI chính thức của `scripts/measure_runtime.py`:
`--motion` (alias `--bvh-file`), `--robot`, `--runs N` (**tổng** số lần chạy, mặc định `4` = 1 warm-up + 3 đo), `--warmup-runs`, `--warmup-frames`, `--out` (alias `--csv`), `--raw-out`, `--fps-src`, `--script`, `--gmr-dir`, `--python`, `--dry-run`, `--frames`, `--work-dir`.

```bash
# chạy khô trước, không cần env gmr (dữ liệu giả) — kiểm hợp đồng CSV
python scripts/measure_runtime.py --dry-run --runs 4 --warmup-runs 1

# chạy thật: 1 warm-up + 3 lần đo, mỗi lần một process mới
conda run -n gmr python scripts/measure_runtime.py \
  --motion <LAFAN1>/walk1_subject1.bvh \
  --robot unitree_g1 \
  --runs 4 --warmup-runs 1 --warmup-frames 30 \
  --fps-src 30 \
  --out results/v3_runtime.csv \
  --raw-out results/v3_runtime_raw.csv
```

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

### 3.3 Đầu ra bắt buộc

Script đo **cả hai đại lượng trong một lần chạy** và tự xuất 2 file; không cần chạy tay lần thứ hai.

`results/v3_runtime.csv` — 1 dòng / lần chạy, đúng thứ tự cột của `SUMMARY_COLUMNS` (`scripts/measure_runtime.py` @ `5f9cdd5`), xem `docs/dinh_nghia_phep_do.md` §5.1. Tối thiểu phải có:

`run, motion, bvh_file, n_frames, n_frames_total, fps_src, ms_per_frame, ms_per_frame_mean, ms_per_frame_p95, fps_out, realtime_factor, t_init_s, ms_per_frame_process, fps_out_process, realtime_factor_process, cpu, os, python, git_head, cuda_visible, cmd, process_cmd, timestamp`

- `ms_per_frame*` / `fps_out` / `realtime_factor`: từ **probe** (`--retarget-only`), **không** dựng viewer.
- `ms_per_frame_process` / `fps_out_process` / `realtime_factor_process`: từ **entry script**, có viewer + render + ghi pkl.
- `cmd` = lệnh probe; `process_cmd` = lệnh entry script — hai cột này là bằng chứng tái lập, Review kiểm cả hai.
- `t_init_s`: lấy từ probe.

`results/v3_runtime_raw.csv` — 1 dòng / frame, đúng hợp đồng `RAW_COLUMNS`: `run, motion, robot, frame, included, ms`.

### 3.4 Sai số chấp nhận

| Mức | Ngưỡng | Cách xử lý |
|---|---|---|
| Lặp lại giữa 3 lần chạy | **CV ≤ 5 %**, tính **riêng** cho `ms_per_frame` và `ms_per_frame_process` | nếu > 5 %: chạy thêm 2 lần, báo **trung vị** thay vì trung bình, và ghi rõ máy không ổn định |
| Ngưỡng quyết định tuyên bố | `realtime_factor` ≥ **1,00** — áp cho **`ms_per_frame`** | xem §3.5 và `dinh_nghia_phep_do.md` §6.1 |
| Dung sai kỹ thuật của phép đo | ± 5 % (làm tròn 0,1 ms; 0,1 fps) | — |

**Không có sai số "so với paper"** vì paper không có số. Đây là điểm yếu cố hữu của tuyên bố này và phải viết thẳng trong báo cáo.

### 3.5 Ba mức kết luận (chốt trước, không đổi sau khi thấy số)

| `realtime_factor` (trung bình 3 lần) | Kết luận |
|---|---|
| ≥ 1,00 | **Tái lập được** — GMR retarget nhanh ít nhất bằng tốc độ phát của dữ liệu nguồn trên CPU |
| 0,80 – 0,99 | **Tái lập một phần** — gần real-time, phải nêu cấu hình CPU và đề xuất CPU mạnh hơn |
| < 0,80 | **Không tái lập được** — phải thử thêm máy thứ hai trước khi kết luận; nếu vẫn < 0,80 thì kết luận "không tái lập trên CPU phổ thông", kèm phân tích nút thắt (2 stage IK × 10 vòng lặp) |

Bảng trên dành cho `ms_per_frame` (số chính thức, lấy từ probe). Chỉ khi **thiếu** số Nhóm A (probe lỗi, hoặc ai đó đo tay bằng `bvh_to_robot.py`) mới dùng bảng bắc cầu ở `docs/dinh_nghia_phep_do.md` **§6.1**: `_process` ≤ 33,3 ms là **điều kiện đủ** để kết luận tái lập; `_process` > 33,3 ms mà `ms_per_frame` ≤ 33,3 ms thì **tái lập một phần**; không có `ms_per_frame` thì **chưa kết luận được**.

---

## 4. Rủi ro không tái lập

| # | Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|---|
| 1 | **Paper không nêu phần cứng** | Không có mốc để so; "real time" của họ có thể là máy khác hẳn | Ghi rõ CPU/RAM/OS; coi ngưỡng 30 fps là ngưỡng vật lý, không phải ngưỡng của paper |
| 2 | **Đo sai đối tượng** — dùng FPS render của script | Kết quả vô nghĩa, thường thấp hơn thực tế rất nhiều | Dùng `scripts/measure_runtime.py` (probe `--retarget-only`); cấm dùng `Actual rendering FPS` |
| 3 | **Bật `--rate_limit`** | Entry script bị áp nhịp theo motion fps → `ms_per_frame_process` luôn ≈ 33 ms (tự ứng nghiệm); probe không bị ảnh hưởng | `measure_runtime.py` không truyền cờ này; nếu đo tay thì không bật, và ghi vào `cmd` |
| 4 | **Đường batch cần CUDA** — `bvh_to_robot_dataset.py` hardcode `device = "cuda:0"` | Máy chỉ CPU chạy batch sẽ lỗi → tưởng "không cài được" | Dùng `scripts/measure_runtime.py`; không dùng batch cho phép đo chính |
| 5 | **Viewer cần display** | Headless/SSH làm entry script chết | Probe `--retarget-only` không dựng viewer; entry script (đo `_process`) vẫn cần display — chạy trên máy có màn hình |
| 6 | **Trôi phiên bản repo** — PDF hướng dẫn (8/2025) dùng conda + `pip install -e .`, README hiện tại dùng `uv sync`; repo từ 12 → 19 robot | Số đo khác nhau giữa các lần | **Ghim commit `25f56db7`**; ghi `git rev-parse --short HEAD` vào mọi CSV |
| 7 | **Sai `fps_src`** — GMR hardcode 30 fps, không đọc header BVH | Nếu lỡ dùng file 120 Hz (ví dụ `assets/xsens_bvh_test/…120Hz…bvh`) thì `realtime_factor` sai **4 lần** | Chỉ dùng LAFAN1 (30 fps, theo README Ubisoft); đọc header `Frame Time` để đối chiếu và ghi cả hai vào CSV |
| 8 | **OS** — README chỉ test Ubuntu 22.04/20.04; worktree này là Windows | Cài đặt có thể tắc (MuJoCo, Mink/qpsolvers) | Nếu tắc: ghi nhật ký theo AGENTS.md (tắc ở đâu, đã thử gì); dùng WSL2 và ghi rõ |
| 9 | **Python 3.10** bắt buộc theo hướng dẫn | Lệch version → API Mink khác | Dùng đúng 3.10; lưu `requirements.txt` thực tế |
| 10 | **Máy đo có GPU** | torch/MuJoCo có thể chọn backend khác → số không so được với "CPU" | Script tự đặt `CUDA_VISIBLE_DEVICES=""` cho cả 2 process; CSV có cột `cuda_visible` để kiểm |
| 11 | **Clip quá ngắn** | Ảnh hưởng warm-up lên trung bình | Dùng clip dài (`walk1_subject1.bvh`, 7840 frame / 261,3 s) và loại 30 frame đầu mỗi lần |
| 12 | **Nhầm tên clip** — `walk1_subject1.bvh` (7840 frame, 261,3 s) bị gọi là "Walk 1" của Bảng I (33 s) | Bảng so sánh ghép sai đối tượng, sai số liệu | CSV ghi `bvh_file` + `n_frames_total`; trong báo cáo luôn ghi tên file thật, không dùng nhãn "Walk 1" cho clip này |
| 13 | **Nhầm tên đại lượng** — dùng `ms_per_frame` cho số đo cả tiến trình | Kết luận áp sai ngưỡng, Review không đối chiếu được | `ms_per_frame` = **chỉ** vòng lặp retarget (Nhóm A, tên chính thức); mọi số đầu-cuối **bắt buộc** có hậu tố `_process` |

---

## 5. Sẽ báo cáo thế nào (tách cột, không trộn)

| Đại lượng | Bài báo | Nhóm đo được |
|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | *(điền sau khi Run chạy)* |
| `ms_per_frame_process` (ms) — G1, LAFAN1 | **không nêu** | *(điền sau)* |
| `fps_out` (frame/s) | **không nêu** | *(điền sau)* |
| `realtime_factor` (lần) | **không nêu** — chỉ có chữ "real time" | *(điền sau)* |
| Success rate "Dance 5" sim2sim (%) | 51 | không đo (ngoài phạm vi) |
| `E_g-mpbpe` mean GMR (mm) | 104,1 | không đo (ngoài phạm vi) |
| Xuyên sàn PHC "Dance 1" (cm) | 60 | không đo (ngoài phạm vi) |

Nguyên tắc: ô "nhóm đo được" **để trống** cho tới khi có CSV. Không suy diễn, không nội suy, không chép số paper sang cột của nhóm.

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
| **Run (Mạnh)** | Dựng env `gmr` @ commit `25f56db7`, tải LAFAN1, chạy đúng lệnh §3.2 | `results/v3_runtime.csv` có 3 dòng `run=2,3,4`, đủ cột `ms_per_frame` và `ms_per_frame_process` |
| **Review (Trường)** | Kiểm 5 dòng: đúng file, đúng **tên đại lượng** (`ms_per_frame` vs `_process`), có `cmd` **và** `process_cmd`, `git_head`, CV ≤ 5 % | PASS/FAIL theo mẫu 5 dòng |
| **Writing** | Điền §5 | Không ô nào ở cột "nhóm đo được" bị chép từ paper |

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

> **Tái lập một phần.** Phần **thời gian thực** kiểm chứng được: GMR retarget chuyển động LAFAN1 sang Unitree G1 trên CPU với `ms_per_frame` = … ms (`realtime_factor` = …, trung bình 3 lần, CV = … %), so với ngưỡng do nhóm đặt trước 33,3 ms → kết luận tái lập / không tái lập theo bảng §3.5. Phần **bảng số của paper** (Bảng I, II, III) **không tái lập được**, vì các bảng đó đo policy đã train trong IsaacSim trên GPU — nhóm không có GPU, không có IsaacSim và không thể train 84 policy trong 10 ngày; con số 104,1 mm của Bảng II được ghi ở cột "bài báo" và **không** được đối chiếu với bất kỳ số nào nhóm tự đo.

Điều kiện để câu trên đúng:

1. Chỉ điền số vào chỗ `…` khi có `results/v3_runtime.csv` do Review chấm PASS.
2. Không đổi ngưỡng 33,3 ms sau khi thấy số.
3. Không dùng từ "tái lập được" cho toàn bộ bài báo — chỉ cho phần thời gian thực.
4. Nếu vì lý do nào đó phần thời gian thực cũng không đạt, câu kết luận phải đổi thành "không tái lập được", **không** được giữ nguyên "một phần" cho đẹp.
