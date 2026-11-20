# V1 — Tuyên bố cần kiểm chứng

**Nhóm 01 · HR-04 · Lớp 15DHTH07 · HK1 2026–2027 · ĐH Công Thương TP.HCM**
Người chốt: Trần Nguyễn Khánh Duy (NT) · Ngày chốt: 2026-11-20
Nguồn gốc: arXiv:2510.02252**v1** (9 trang) · repo https://github.com/YanjieZe/GMR, nhánh `master`, HEAD `25f56db7` (2026-10-22), giấy phép MIT.
Ghi chú đọc bài: `docs/paper_notes.md` · Định nghĩa phép đo: `docs/dinh_nghia_phep_do.md`

---

## 0. Câu chốt (dùng nguyên văn trong báo cáo)

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm kiểm chứng bằng cách đo thời gian xử lý mỗi frame (`ms_per_frame`) khi retarget chuyển động LAFAN1 (30 fps) sang **Unitree G1** trên CPU, thời gian đo riêng phần `retarget()`, **không** bật `--rate_limit`; tuyên bố được coi là **tái lập được** nếu trung bình 3 lần chạy (sau 1 lần warm-up bị loại) có `ms_per_frame` trung vị ≤ **33,3 ms**, tức `fps_out` ≥ **30** và `realtime_factor` ≥ **1,00**.**

Lưu ý bắt buộc phải ghi kèm câu trên: **bài báo arXiv:2510.02252 không nêu bất kỳ con số thời gian nào** (xem `paper_notes.md` §12). Vì vậy "giá trị gốc" của tuyên bố này là **định tính** ("real time"), và ngưỡng 33,3 ms là **ngưỡng nhóm đặt trước** suy ra từ tốc độ phát của chính dữ liệu nguồn (LAFAN1 = 30 fps), không phải số chép từ paper.

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
| Đại lượng | `ms_per_frame` (**ms/frame**), `fps_out` (**frame/s**), `realtime_factor` = `fps_out` / `fps_src` (**lần**) |
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

---

## 3. Cách đo lại tuyên bố chính (C5)

### 3.1 Nguyên tắc: đo `retarget()`, không đo script

`scripts/bvh_to_robot.py` chạy **retarget và render trong cùng một vòng lặp**; dòng `print(f"Actual rendering FPS: …")` trong script là FPS **có render**, không phải throughput retargeting. Dùng số đó là **đo sai đối tượng** → loại.

Vì vậy phép đo hợp lệ là một wrapper do tab **Code** viết (`scripts/measure_retarget_runtime.py`, ~40 dòng), dùng đúng API mà script gốc dùng:

```
from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting.utils.lafan1 import load_bvh_file

frames, height = load_bvh_file(<bvh>, format="lafan1")
rt = GMR(src_human="bvh_lafan1", tgt_robot="unitree_g1", actual_human_height=height)
for f in frames:
    t0 = time.perf_counter()
    qpos = rt.retarget(f)
    ms = (time.perf_counter() - t0) * 1e3
```

- Đo bằng `time.perf_counter()` (đồng hồ đơn điệu, độ phân giải cao). **Không** dùng `time.time()` như script gốc.
- **Không** dựng `RobotMotionViewer` (cần display, và làm nhiễu phép đo).
- Ghi riêng `t_init` = thời gian khởi tạo `GMR(...)` (load MJCF + config), **không** cộng vào `ms_per_frame`.

### 3.2 Lệnh chạy (tab Run thực thi)

Các cờ `--runs`, `--warmup_runs`, `--warmup_frames`, `--out`, `--raw_out` là do wrapper tự định nghĩa (GMR không có sẵn); `--bvh_file` và `--robot` giữ đúng tên cờ của repo.

```bash
# 1 lần warm-up (bị loại) + 3 lần đo, mỗi lần một process mới
conda run -n gmr python scripts/measure_retarget_runtime.py \
  --bvh_file <LAFAN1>/walk1_subject1.bvh \
  --robot unitree_g1 \
  --runs 4 --warmup_runs 1 --warmup_frames 30 \
  --out results/v3_runtime.csv \
  --raw_out results/v3_runtime_raw.csv
```

Lệnh tham chiếu để lấy file `.pkl` (chạy được, nhưng **không dùng để đo** vì có render):

```bash
conda run -n gmr python scripts/bvh_to_robot.py \
  --bvh_file <LAFAN1>/walk1_subject1.bvh --robot unitree_g1 \
  --save_path results/v3/walk1_g1.pkl
```

Tên file LAFAN1 theo quy ước `[theme][take]_[subject].bvh` của Ubisoft — Run ghi lại **tên file thực tế** vào CSV, không dùng tên trong tài liệu này.

### 3.3 Đầu ra bắt buộc

`results/v3_runtime.csv` (1 dòng / lần chạy) với các cột ở `docs/dinh_nghia_phep_do.md` §5, tối thiểu:
`run, robot, motion, n_frames, fps_src, ms_per_frame, ms_per_frame_mean, ms_per_frame_p95, fps_out, realtime_factor, t_init_s, cpu, os, python, git_head, cmd`.

`results/v3_runtime_raw.csv` (1 dòng / frame): `run, frame, ms`.

### 3.4 Sai số chấp nhận

| Mức | Ngưỡng | Cách xử lý |
|---|---|---|
| Lặp lại giữa 3 lần chạy | hệ số biến thiên **CV ≤ 5 %** của `ms_per_frame` | nếu > 5 %: chạy thêm 2 lần, báo **trung vị** thay vì trung bình, và ghi rõ máy không ổn định |
| Ngưỡng quyết định tuyên bố | `realtime_factor` ≥ **1,00** | xem §3.5 |
| Dung sai kỹ thuật của phép đo | ± 5 % (làm tròn 0,1 ms; 0,1 fps) | — |

**Không có sai số "so với paper"** vì paper không có số. Đây là điểm yếu cố hữu của tuyên bố này và phải viết thẳng trong báo cáo.

### 3.5 Ba mức kết luận (chốt trước, không đổi sau khi thấy số)

| `realtime_factor` (trung bình 3 lần) | Kết luận |
|---|---|
| ≥ 1,00 | **Tái lập được** — GMR retarget nhanh ít nhất bằng tốc độ phát của dữ liệu nguồn trên CPU |
| 0,80 – 0,99 | **Tái lập một phần** — gần real-time, phải nêu cấu hình CPU và đề xuất CPU mạnh hơn |
| < 0,80 | **Không tái lập được** — phải thử thêm máy thứ hai trước khi kết luận; nếu vẫn < 0,80 thì kết luận "không tái lập trên CPU phổ thông", kèm phân tích nút thắt (2 stage IK × 10 vòng lặp) |

---

## 4. Rủi ro không tái lập

| # | Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|---|
| 1 | **Paper không nêu phần cứng** | Không có mốc để so; "real time" của họ có thể là máy khác hẳn | Ghi rõ CPU/RAM/OS; coi ngưỡng 30 fps là ngưỡng vật lý, không phải ngưỡng của paper |
| 2 | **Đo sai đối tượng** — dùng FPS render của script | Kết quả vô nghĩa, thường thấp hơn thực tế rất nhiều | Chỉ đo `retarget()`; cấm dùng `Actual rendering FPS` |
| 3 | **Bật `--rate_limit`** | Thời gian bị áp theo motion fps → luôn ra ~30 fps (tự ứng nghiệm) | Không bật; ghi rõ trong `cmd` của CSV |
| 4 | **Đường batch cần CUDA** — `bvh_to_robot_dataset.py` hardcode `device = "cuda:0"` | Máy chỉ CPU chạy batch sẽ lỗi → tưởng "không cài được" | Dùng wrapper; không dùng batch cho phép đo chính |
| 5 | **Viewer cần display** | Headless/SSH làm script gốc chết | Wrapper không dựng viewer |
| 6 | **Trôi phiên bản repo** — PDF hướng dẫn (8/2025) dùng conda + `pip install -e .`, README hiện tại dùng `uv sync`; repo từ 12 → 19 robot | Số đo khác nhau giữa các lần | **Ghim commit `25f56db7`**; ghi `git rev-parse --short HEAD` vào mọi CSV |
| 7 | **Sai `fps_src`** — GMR hardcode 30 fps, không đọc header BVH | Nếu lỡ dùng file 120 Hz (ví dụ `assets/xsens_bvh_test/…120Hz…bvh`) thì `realtime_factor` sai **4 lần** | Chỉ dùng LAFAN1 (30 fps, theo README Ubisoft); đọc header `Frame Time` để đối chiếu và ghi cả hai vào CSV |
| 8 | **OS** — README chỉ test Ubuntu 22.04/20.04; worktree này là Windows | Cài đặt có thể tắc (MuJoCo, Mink/qpsolvers) | Nếu tắc: ghi nhật ký theo AGENTS.md (tắc ở đâu, đã thử gì); dùng WSL2 và ghi rõ |
| 9 | **Python 3.10** bắt buộc theo hướng dẫn | Lệch version → API Mink khác | Dùng đúng 3.10; lưu `requirements.txt` thực tế |
| 10 | **Máy đo có GPU** | torch/MuJoCo có thể chọn backend khác → số không so được với "CPU" | Đặt `CUDA_VISIBLE_DEVICES=""` khi đo, ghi vào `cmd` |
| 11 | **Clip quá ngắn** (Walk 2 = 5,5 s) | Ảnh hưởng warm-up lên trung bình | Dùng clip dài (Walk 1 = 33 s ≈ 990 frame); loại 30 frame đầu mỗi lần |

---

## 5. Sẽ báo cáo thế nào (tách cột, không trộn)

| Đại lượng | Bài báo | Nhóm đo được |
|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | *(điền sau khi Run chạy)* |
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
| **Code (Vỹ)** | Viết `scripts/measure_retarget_runtime.py` đúng hợp đồng §3.1 + §3.3 | `--help` chạy được; xuất đúng 2 file CSV với đủ cột |
| **Run (Mạnh)** | Dựng env `gmr` @ commit `25f56db7`, tải LAFAN1, chạy 1 warm-up + 3 lần | `results/v3_runtime.csv` có 3 dòng `run=2,3,4` |
| **Review (Trường)** | Kiểm 5 dòng: đúng file, đúng cột `cmd`, không có `--rate_limit`, có `git_head`, CV ≤ 5 % | PASS/FAIL theo mẫu 5 dòng |
| **Writing** | Điền §5 | Không ô nào ở cột "nhóm đo được" bị chép từ paper |
