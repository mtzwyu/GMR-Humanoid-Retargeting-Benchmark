# Nhật ký cài đặt — GMR (Nhóm 01, HR-04)

Ghi **ngay khi gặp lỗi**, không viết lại sau. Mỗi mục: thời điểm · máy · lệnh · lỗi đầy đủ · đã thử gì · kết quả.

## Môi trường

| Mục | Giá trị |
|---|---|
| Máy | LENOVO 83GS (laptop), Windows 11 Home Single Language 10.0.26300 |
| CPU / RAM | Intel Core i5-12450HX, 8 nhân / 12 luồng · 16.873.545.728 byte (~15,7 GiB) |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU, 6144 MiB, driver 621.14 (dự án chạy CPU, GPU không dùng) |
| Conda | conda 26.7.1 (Miniconda3, `C:\Users\xpaga\miniconda3`) |
| Python | 3.10.21 (env `gmr`, tạo từ `python=3.10`) |
| Repo GMR | `third_party/GMR` · remote https://github.com/YanjieZe/GMR |
| GMR commit | `25f56db` (`25f56db79ac411258b377b6d4ccba0c8ff3372ac`, 2026-10-23, "Fix import order flagged by ruff after merging #182") |
| Giấy phép GMR | MIT — "Copyright 2025 YanjieZe", bản quyền + điều khoản chuẩn MIT, cho phép copy/sửa/phân phối kèm giữ notice |

## Nhật ký

| # | Thời điểm | Bước | Lệnh | Kết quả / Lỗi | Cách xử lý |
|---|---|---|---|---|---|
| 1 | 2026-11-20 21:21 | Clone repo | `git clone https://github.com/YanjieZe/GMR third_party/GMR` | Thành công, 1938 file. PowerShell trả `Exit code: 1` nhưng đó là do git ghi tiến trình ra stderr; `git rev-parse` + `git status` sau đó sạch, không lỗi | Kiểm tra lại bằng `git rev-parse --short HEAD` → `25f56db`. Không cần xử lý |
| 2 | 2026-11-20 21:22 | Đọc LICENSE + pyproject | `Get-Content LICENSE`, `Get-Content pyproject.toml` | LICENSE = MIT (Copyright 2025 YanjieZe). `requires-python = ">=3.10,<3.14"`; dependency có `smplx @ git+https://github.com/vchoutas/smplx`, `mujoco`, `mink`, `qpsolvers[proxqp]`, `torch`… | Dùng đúng Python 3.10 theo README. Ghi nhận: repo test trên Ubuntu 22.04/20.04, máy nhóm là Windows 11 → rủi ro tương thích, theo dõi ở các bước sau |
| 3 | 2026-11-20 21:22:43 → 21:23:11 | Tạo conda env | `conda create -n gmr python=3.10 -y` | Thành công (exit 0), env `C:\Users\xpaga\miniconda3\envs\gmr`, python 3.10.21. Có 2 cảnh báo không chặn: (a) conda 26.7.1 cũ hơn 26.7.2; (b) Anaconda ngừng build package Python 3.10 mới sau 2026-10-31 | Không xử lý — cảnh báo, không ảnh hưởng cài đặt |
| 4 | 2026-11-20 21:24 → 21:31 | Cài GMR | `python -m pip install -e .` (python = `C:\Users\xpaga\miniconda3\envs\gmr\python.exe`) | **THẤT BẠI (exit 1)** ở bước chuẩn bị metadata của `proxsuite>=0.2.9` (dependency của `qpsolvers[proxqp]`). Pip không tìm được wheel Windows nên tải source `proxsuite-0.8.2.tar.gz` (54,7 MB) và build bằng CMake → `CMake Error at CMakeLists.txt:5 (project): Running 'nmake' '-?' failed with: no such file or directory` + `CMAKE_C_COMPILER not set` + `CMAKE_CXX_COMPILER not set` → `error: metadata-generation-failed`. Nguyên nhân: máy không có Visual Studio / MSVC (`where cl` rỗng), proxsuite không phát hành wheel cho win-64. Các gói khác đều resolve được (mujoco 3.17.0, mink 1.3.0, torch 2.14.1, daqp 0.11.2, smplx @ 1265df7…) | Đang thử: (1) tìm wheel proxsuite cho Windows; (2) nếu không có, cài `pip install -e . --no-deps` + cài từng dependency trừ `proxsuite` — chấp nhận được vì GMR/mink dùng solver mặc định **daqp**, `proxqp` chỉ là backend dự phòng |
| 5 | 2026-11-20 21:26 | Xử lý lỗi 4 (1) — tìm wheel proxsuite | `pip download --no-deps --only-binary=:all: proxsuite` · `conda search -c conda-forge proxsuite` | Kết quả: bản `proxsuite 0.8.2` **không có wheel win-64** (chỉ sdist). Nhưng **bản `0.7.2.post1` có wheel** `proxsuite-0.7.2.post1-0-cp310-cp310-win_amd64.whl` (4,3 MB). conda-forge chỉ build proxsuite cho linux/osx, không có win-64 | Chọn hướng ghim bản có wheel |
| 6 | 2026-11-20 21:26 → 21:29 | Cài lại GMR | `pip install "proxsuite==0.7.2.post1"` rồi `pip install -e .` | **THÀNH CÔNG (exit 0)**. Lần 1 cài proxsuite 0.7.2.post1 (kèm numpy 2.2.6, scipy 1.15.3). Lần 2 `pip install -e .` cài đủ: mujoco 3.17.0, mink 1.3.0, torch 2.14.1, smplx 0.1.28 (từ git `vchoutas/smplx`), daqp 0.11.2, qpsolvers 4.13.0, opencv-python 5.1.0.95, imageio 2.38.0… **Không sửa một dòng nào trong `pyproject.toml`** — chỉ ghim phiên bản dependency từ bên ngoài | Giữ nguyên. Đây là điểm khác README: README dùng `uv sync` (có lock `uv.lock`, chắc chắn chọn bản build được); đi đường conda+pip thì phải tự ghim proxsuite |
| 7 | 2026-11-20 21:29 | Bước 3 theo README | `conda install -n gmr -c conda-forge libstdcxx-ng -y` | **THẤT BẠI (exit 1)** — `PackagesNotFoundInChannelsError: The following packages are not available from current channels: - libstdcxx-ng`. Nguyên nhân: `libstdcxx-ng` là gói **chỉ có cho linux-64** (thư viện C++ của GCC); win-64 không có và cũng không cần. Bước này trong README nhằm sửa lỗi render trên Ubuntu | Bỏ qua có ghi chép. Đã kiểm chứng bù bằng việc chạy `--help` (mục 8) và chạy thật có mở cửa sổ MuJoCo (mục V3) — nếu render lỗi sẽ thấy ngay |
| 8 | 2026-11-20 21:30 | Cổng G1 | `conda run -n gmr python scripts/smplx_to_robot.py --help` (thực tế gọi trực tiếp `C:\Users\xpaga\miniconda3\envs\gmr\python.exe scripts/smplx_to_robot.py --help`) | **ĐẠT**: in đủ usage + danh sách 17 robot cho `--robot` (gồm `unitree_g1`, `unitree_h1`, `unitree_h1_2`, `booster_t1`, `booster_t1_29dof`), exit 0. Chỉ có 2 cảnh báo không chặn: `FutureWarning: torch.jit.script is deprecated` và `xrobotoolkit_sdk not found, skip for now` | Không xử lý — cả hai là cảnh báo, không phải lỗi |
| 9 | 2026-11-20 21:30 | Thử đường SMPL-X (ngày 2) | `python scripts/smplx_to_robot.py --smplx_file assets/body_models/none.npz --robot unitree_g1` | **KHÔNG DÙNG ĐƯỢC ĐƯỜNG SMPL-X.** Bằng chứng: (a) `assets/body_models/` **không tồn tại** — repo không kèm body model; (b) `general_motion_retargeting/utils/smpl.py:16-23` gọi `smplx.create(<assets/body_models>, "smplx", …)` nên bắt buộc phải có `SMPLX_NEUTRAL/FEMALE/MALE.pkl`; (c) chạy thử → `FileNotFoundError: [Errno 2] No such file or directory: 'assets/body_models/none.npz'`. Cả **body model SMPL-X** và **dữ liệu AMASS/OMOMO** đều phải đăng ký tài khoản + ký license tại smpl-x.is.tue.mpg.de / amass.is.tue.mpg.de, không có đường tải công khai; nhóm không có tài khoản license này | **QUYẾT ĐỊNH (ngày 2): chuyển sang `scripts/bvh_to_robot.py` với dữ liệu BVH LAFAN1.** Lý do: LAFAN1 tải công khai (không cần license điền đơn), repo có sẵn config IK `bvh_lafan1_to_{g1,t1_29dof,n1,pm01,toddy,h2}.json`, và đây là đường mà chính README hướng dẫn cho BVH. Hệ quả phải ghi rõ trong báo cáo: **V3 và V5 đo trên đường BVH, không phải đường SMPL-X như bài báo** |
| 10 | 2026-11-20 21:31 | Tải dữ liệu BVH LAFAN1 | `curl.exe -L -o third_party\data\lafan1.zip https://media.githubusercontent.com/media/ubisoft/ubisoft-laforge-animation-dataset/master/lafan1/lafan1.zip` | Thành công: 144.051.503 byte (khớp `size` trong git-lfs pointer). Lưu ý: link `raw.githubusercontent.com` chỉ trả về pointer LFS 134 byte → phải dùng host `media.githubusercontent.com`. Giải nén được **77 file .bvh**, mỗi file có `Frame Time: 0.033333` (30 fps) | **Giấy phép dữ liệu: CC BY-NC-ND 4.0** (`license.txt` của repo ubisoft-laforge-animation-dataset) — chỉ dùng phi thương mại, không phân phối lại biến thể. Nhóm dùng cho học thuật, **không commit dữ liệu** (`third_party/` đã gitignore) |
| 11 | 2026-11-20 21:33 | Chốt môi trường | `python -m pip freeze > requirements.txt` (python của env `gmr`) | 45 dòng, gồm `torch==2.14.1`, `mujoco==3.17.0`, `mink==1.3.0`, `proxsuite==0.7.2.post1` (bản ghim), `smplx @ git+…@1265df7`, `-e git+https://github.com/YanjieZe/GMR@25f56db79…` | Giữ nguyên văn output của pip freeze. Đây là requirements của **đường conda+pip trên Windows**, không phải `uv.lock` của repo |
| 12 | 2026-11-20 21:39 | Chẩn đoán KI-01 (robot cúi gập) — bước 1 | `analyze_pose.py results/pkl/g1_walk4_no_rate_limit_1.pkl assets/unitree_g1/g1_mocap_29dof.xml` | Tái lập đúng số Planner đo: `waist_pitch` **29,52° ± 1,70**, `hip_pitch` **−56,3 / −56,1°**, `knee` **+37,5 / +39,3°**, `root_z` 0,584–0,819 m (TB 0,766), `quat |dot| min 0,9981` → dữ liệu mượt, sai tư thế **có hệ thống** | Render offscreen frame 2000 xác nhận robot gập người về trước: `results/figures/fix_walk4_frame2000_g1_2026-11-20.png` |
| 13 | 2026-11-20 21:41 | Chẩn đoán KI-01 — bước 2 (scale người→robot) | Đọc `general_motion_retargeting/utils/lafan1.py:45`, `motion_retarget.py:66-75`, `ik_configs/bvh_lafan1_to_g1.json` | `actual_human_height` **hardcode = 1,75 m**, `human_height_assumption` = **1,8 m** → tỉ lệ scale = **0,972**. Chiều cao G1 ≈ 1,27 m. Tỉ lệ 0,972 **không** phải nguyên nhân gập người | Không sửa — loại trừ giả thuyết scale |
| 14 | 2026-11-20 21:42 | Chẩn đoán KI-01 — bước 3 (đổi motion) | Chạy `bvh_to_robot.py` với `dance1_subject2.bvh` (repo đánh dấu `[x]`) và `walk3_subject1.bvh` | dance1: waist **18,6° ± 8,7**, hip −23,1/−20,0°, knee 49,3/47,9°, root_z TB 0,754. walk3_subject1: waist **25,2° ± 4,3**, hip −11,8/−11,4°, knee 33,3/34,9°, root_z TB 0,729. → walk4 lệch hẳn (29,5° với std 1,7° = tư thế khom **cố định** của chính clip) | Ảnh: `fix_dance1_frame2000_g1_2026-11-20.png`, `fix_walk3_frame2000_g1_2026-11-20.png` |
| 15 | 2026-11-20 21:44 | Chẩn đoán KI-01 — bước 4 (XML của viewer) | Đọc `robot_motion_viewer.py:68-69` và `motion_retarget.py:27,30` | Cả hai lấy `ROBOT_XML_DICT[robot_type]` từ `params.py` → **cùng một file** `assets/unitree_g1/g1_mocap_29dof.xml`, cùng thứ tự 29 dof theo `qposadr`. Loại trừ giả thuyết viewer dùng XML khác | Không sửa |

## FIX — KI-01: robot cúi gập người

**Hiện tượng.** Khi phát lại `results/pkl/g1_walk4_no_rate_limit_1.pkl` trong MuJoCo, robot gập người về trước, chân khuỵu, trông như bò.

**Đo trên chính máy này (G1, 3 motion khác nhau, cùng pipeline HEAD `25f56db`):**

| Motion | waist_pitch TB ± std | hip_pitch L/R | knee L/R | root_z TB |
|---|---|---|---|---|
| `walk4_subject1` | **+29,52° ± 1,70** | −56,3 / −56,1° | +37,5 / +39,3° | 0,766 m |
| `walk3_subject1` | +25,19° ± 4,27 | −11,8 / −11,4° | +33,3 / +34,9° | 0,729 m |
| `dance1_subject2` (repo đánh dấu OK) | +18,62° ± 8,70 | −23,1 / −20,0° | +49,3 / +47,9° | 0,754 m |

**Kết luận (khớp kết luận Planner ghi ở `docs/known_issues.md` KI-01, commit `4eb082a`):** `walk4_subject1.bvh` là clip **đi bộ khom lưng** của LAFAN1; retarget tái hiện trung thực nên robot trông như cúi gập. Không phải lỗi pipeline: (a) scale người→robot = 1,75/1,8 = 0,972 — bình thường; (b) viewer và retarget dùng **cùng** `g1_mocap_29dof.xml`; (c) đổi clip thì tư thế đổi theo clip.

**Quyết định:**
1. **Đổi motion chính thức của V3/V5 sang `walk1_subject1.bvh`** (7.840 frame, 30 fps, 261,3 s) — clip đi bộ tư thế bình thường. V3 chạy lại 1 warm-up + 3 lần đo cho mỗi chế độ; `results/v3_runtime.csv` ghi rõ cột `input` đã đổi từ `walk4_subject1` sang `walk1_subject1`.
2. **Giữ `walk4_subject1` như ví dụ motion khó** — không dùng để đo.
3. Ảnh render lại bằng `vis_robot_motion.py` trên pkl mới, cùng frame index 2000 với ảnh cũ.

## Đo V3 và V5 (số đo thật, máy `LAPTOP-KQVVNV12`)

| Mục | Kết quả |
|---|---|
| Input | `walk1_subject1.bvh` — 7.840 frame, 30 fps, 261,333 s |
| V3 không `--rate_limit` (1 warm-up bị loại + 5 lần đo) | **Số chốt: mean 17,349 ms/frame** (n = 5, CV **2,13 % ≤ 5 %** → báo mean); trung vị 17,272 chỉ là số của **một** lần chạy (measure_5) dùng làm bằng chứng |
| V3 có `--rate_limit` | **ĐÃ RÚT — không có dòng nào trong CSV** (xem mục RV-13: cờ không được truyền vào lệnh thật) |
| V5 sim2sim (cùng motion, 3 robot) | PM01 **34,975** (mean, CV 3,01 %) · G1 **16,758** (mean, CV 4,59 %) · T1 29dof **13,034** (median, CV 11,32 %) ms/frame |
| H1 | **không chạy được trên đường BVH** — `bvh_to_robot.py` từ chối `--robot unitree_h1` (exit 2); README ghi cột BVH của H1 = TBD |

**RV-14 — wall time phải nằm trong log (Review chặn merge, đã sửa):** trước đây `wall_clock_s` chỉ in ra console nên không đối chiếu ngược được. Nay mỗi lần chạy, script ghi thêm **một dòng cuối vào chính file log của lần đó**:

```
END wall_s=137.37 ms_per_frame=17.522 rtf=1.902 frames=7840 exit=0 at=2026-11-20 22:50:56
```

Lần ghi đầu bị lỗi font (`Out-File -Encoding utf8` chèn UTF-8 vào file log vốn là UTF-16LE của PowerShell) → đổi sang `-Encoding Unicode` và **chạy lại toàn bộ**; 6 file log mới `results/logs/v3_walk1_subject1_run1..6.log` đều đọc được dòng END. Các log cũ (`v3_walk1_subject1_no_rate_limit_*.log`, `v3_walk1_subject1_rate_limit_*.log`, `v3_walk1_subject1_evidence.log`) đã bị thay thế và xoá khỏi nhánh.

*Lưu ý:* lần đo đơn trong cửa sổ console (13,117 ms/frame) không thuộc lô 3 lần đo nên **không** đưa vào CSV; ảnh chụp console vẫn giữ làm bằng chứng quy trình.

**RV-16 — độ tản mát giữa các lần đo (Review yêu cầu, đã xử lý):** lô cũ có CV = 7,60 % (> 5 %). Sau khi sửa RV-14 và chạy lại, **CV của 3 lần đo = 1,73 %**. Vẫn chạy thêm 2 lần (measure_4, measure_5) theo yêu cầu để có n = 5:

| Lô | n | mean (ms/frame) | median | sd | CV |
|---|---|---|---|---|---|
| 3 lần đo | 3 | 17,540 | 17,522 | 0,303 | **1,73 %** |
| 5 lần đo (báo cáo) | 5 | **17,349** | **17,272** | 0,369 | **2,13 %** |

Cả hai lô đều ≤ 5 %, nên **số chốt là mean 17,349 ms/frame** (n = 5, CV 2,13 %); trung vị 17,272 chỉ là số của **một** lần chạy (measure_5) dùng làm bằng chứng. Biên độ thô: 16,853–17,852 ms/frame.

**Quy tắc chọn số chốt (docs/dinh_nghia_phep_do.md §4, áp dụng không có ngoại lệ):** CV ≤ 5 % → báo **mean** kèm sd; CV > 5 % → chạy thêm 2 lần rồi báo **trung vị** và ghi rõ máy không ổn định. Vì thế V3 (CV 2,13 %) dùng mean 17,349; V5 PM01 (3,01 %) và G1 (4,59 %) dùng mean 34,975 / 16,758; riêng T1 29dof (11,32 %) dùng trung vị 13,034. Đồ thị V5 (`tools/plot_v3.py`) và phụ đề video đã cập nhật theo đúng quy tắc này.

**RV-17 — tên cột (Review yêu cầu, đã sửa):** đổi `ms_per_frame` → **`ms_per_frame_process`** trong `results/v3_runtime.csv` và `results/v5_sim2sim.csv`, vì tử số là wall-clock của **toàn tiến trình** (nạp model + dựng IK + retarget từng frame + render viewer + ghi pkl), **không** phải riêng hàm `retarget()`. Số giữ nguyên, không tính lại. Đồ thị V3 cũng được vẽ lại theo đúng 5 lần đo (bỏ panel `--rate_limit` đã rút).

**RV-15 — V5 phải đủ 1 warm-up + 3 lần đo mỗi robot (Review chặn merge, đã chạy lại):** trước đây mỗi robot chỉ 1 lần. Nay chạy **PM01 trước tiên** (loại trừ ảnh hưởng nhiệt), rồi T1 29dof, rồi G1; mỗi robot 4 lần (1 warm-up + 3 đo), mỗi lần ghi dòng `END` (wall, ms/frame, rtf, nhiệt độ) vào chính file log.

| Robot | Thứ tự chạy | wall (s) 4 lần | 3 lần đo (ms/frame) | mean | median | CV | Nhiệt GPU |
|---|---|---|---|---|---|---|---|
| `engineai_pm01` | 1 | 274,08 · 264,74 · 277,96 · 279,91 | 33,77 · 35,45 · 35,70 | **34,98** | 35,45 | 3,01 % | 51,0 → 57,4 °C |
| `booster_t1_29dof` | 2 | 109,40 · 91,19 · 110,22 · 108,31 | 11,63 · 14,06 · 13,82 | **13,17** | 13,82 | **10,15 %** | 55,0 → 54,7 °C |
| `unitree_g1` | 3 | 134,94 · 136,13 · 133,42 · 124,60 | 17,36 · 17,02 · 15,89 | **16,76** | 17,02 | 4,59 % | 54,7 → 54,7 °C |

- Nhiệt độ CPU **không đọc được** (`MSAcpi_ThermalZoneTemperature` bị từ chối) — chỉ có nhiệt GPU qua `nvidia-smi`.
- **T1 29dof có CV = 10,15 % > 5 %** (một lần 91,19 s lệch khỏi hai lần ~109 s). Không giấu: máy không ổn định ở robot này; nếu cần một số đại diện duy nhất, dùng **trung vị 13,82 ms/frame**. PM01 (3,01 %) và G1 (4,59 %) đều ≤ 5 %.
- Số cũ (G1 17,34 · T1 13,44 · PM01 34,99, mỗi robot 1 lần) **đã bị thay thế** bởi bảng trên.
- Kết luận H1 bị chặn **giữ nguyên** (Review đã PASS mục này).

**RV-24 — T1 29dof vẫn tản mát, chạy bổ sung và chuyển sang trung vị (Review yêu cầu):** thêm 2 lần đo cho T1 (`run5 = 84,13 s → 10,73 ms/frame`, `run6 = 102,19 s → 13,03 ms/frame`), nay **n = 5**:

| Robot | n | Giá trị (ms/frame) | mean | **median** | sd | CV | Kết luận |
|---|---|---|---|---|---|---|---|
| `booster_t1_29dof` | 5 | 11,63 · 14,06 · 13,82 · **10,73** · **13,03** | 12,65 | **13,03** | 1,43 | **11,32 %** | vẫn > 5 % → **máy không ổn định ở robot này, dùng trung vị** |
| `engineai_pm01` | 3 | 33,77 · 35,45 · 35,70 | 34,98 | **35,45** | 1,05 | 3,01 % | đạt |
| `unitree_g1` | 3 | 17,36 · 17,02 · 15,89 | 16,76 | **17,02** | 0,77 | 4,59 % | đạt |

→ **Số chốt của V5 theo quy tắc §4**: PM01 **34,975** (mean, CV 3,01 %) · G1 **16,758** (mean, CV 4,59 %) · T1 29dof **13,034** (median, CV 11,32 %). Đồ thị `results/figures/v5_ms_per_frame_robots_2026-11-20.png` đã vẽ lại đúng quy tắc (mean cho PM01/G1, median cho T1) + thanh sai số min–max. T1 không đạt ngưỡng CV 5 % — ghi rõ là hạn chế của phép đo trên máy này, không phải của thuật toán (pkl tất định, xem RV-23).

**RV-13 — sai sót của chính nhóm khi đo (Review chặn merge, đã sửa):** trong `tools/measure_v3.ps1`, cờ `--rate_limit` chỉ được ghép vào **chuỗi `cmd` in ra CSV**, còn lệnh thật thiếu cờ. Vì vậy 4 dòng `mode=rate_limit` trong `results/v3_runtime.csv` thực chất là lần chạy **không** giới hạn tốc độ; bằng chứng phụ: log của chúng ghi `Actual rendering FPS` 64–136, không thể là băng 30 Hz. **Đã xoá 4 dòng đó khỏi CSV và rút toàn bộ kết luận về `--rate_limit`.**

Đo riêng thư viện để hiểu bản chất cờ này (tự đo, 300 lần gọi `sleep()`):

```
RateLimiter(frequency=30): n=300 total=14.004s -> 21.42 Hz, 46.68 ms/lan
```

→ Trên Windows, `RateLimiter(30)` chỉ đạt **21,42 Hz (46,68 ms/lần)** vì `sleep` của Windows có độ phân giải timer thô. **Kết luận: cờ `--rate_limit` không dùng để đo throughput** — nó là công cụ phát lại cho mắt người xem, không phải bộ đo. Mọi số V3/V5 báo cáo đều ở chế độ **không** `--rate_limit`.

**Ghi chú về đơn vị đo:** cột `ms_per_frame_process` (trước RV-17 tên là `ms_per_frame`) = wall-clock của cả tiến trình (Measure-Command) chia số frame, nên bao gồm cả khởi tạo model, IK và render — không phải riêng thời gian IK. Con số `Actual rendering FPS` mà script in ra là FPS render, **không** dùng làm kết quả (theo bàn giao V1).

**Cột `realtime_factor` đọc cho đúng (RV-27):** trong CSV, `realtime_factor` là của **từng lần chạy** (`motion_duration_s / wall_clock_s` của chính lần đó), **không** phải số tổng hợp. Số tổng hợp dùng trong báo cáo phải tính bằng **33,333 ms / median_ms** (33,333 ms = ngân sách thời gian mỗi frame ở 30 fps):
- T1 29dof: 33,333 / 13,034 = **2,56**
- G1: 33,333 / 17,018 = **1,96**
- PM01: 33,333 / 35,454 = **0,94**

Writing **không** lấy trực tiếp cột `realtime_factor` của một dòng bất kỳ để báo cáo.

## MEDIA — video demo và ảnh trích cho slide

**Yêu cầu:** 3 clip ≤ 60 s, khung 16:9; mỗi clip trích 3 khung 25/50/75 % thành PNG ≤ 1 MB; video **không commit**, PNG **có commit**.

**Rào cản gặp phải và cách xử lý (ghi ngay khi gặp):**

1. `scripts/vis_robot_motion.py` chạy `while True`, reset `frame_idx` về 0 khi hết motion → **không bao giờ gọi `env.close()`** nên writer MP4 không được đóng (file hỏng) và không có cách dừng sạch. Script cũng không có tham số kích thước (mặc định **640×480 = 4:3**) và không giới hạn số frame.
   → Viết `tools/record_clip.py`: **chỉ gọi đúng lớp `RobotMotionViewer` của repo**, thêm `video_width=1280, video_height=720`, số frame và frame bắt đầu. **Không sửa một dòng nào trong `scripts/`.**
2. `ffmpeg` của `imageio-ffmpeg` (bản 9.0.2) từ chối `-vsync 0` và yêu cầu `-update 1` khi xuất 1 ảnh từ video → sửa `extract_frames.py` dùng `-frames:v 1 -update 1`, sau đó trích được đủ 9 ảnh (143–217 KB/ảnh).

**Kết quả đo bằng ffmpeg (thật):** cả 3 clip `Duration: 00:01:00.00`, `1280x720`, `30 fps`, h264.

| Clip | Nguồn | Dung lượng | Khung đã trích |
|---|---|---|---|
| `results/media/v3_walk1_g1.mp4` | pkl G1 `walk1_subject1` (V3) | 7.437.270 byte | 450 / 900 / 1350 |
| `results/media/v3_walk4_g1.mp4` | pkl G1 `walk4_subject1` (minh hoạ KI-01) | 5.704.724 byte | 450 / 900 / 1350 |
| `results/media/v5_sim2sim_g1_t1_pm01.mp4` | 3 pkl V5, mỗi robot 600 frame | 7.431.439 byte | 450 (G1) / 900 (T1) / 1350 (PM01) |

Ảnh: `results/figures/slide_*.png`; caption + vị trí chèn slide ghi ở `results/figures/README.md`; bảng nguồn/lệnh/thời lượng ở `results/media/README.md`.

## RV-23 — Hai đợt đo V3 và tính tất định của retarget

Mục này là **căn cứ số cho Writing viết mục 7** (độ tin cậy của phép đo).

### (a) So sánh hai đợt đo V3 (cùng input `walk1_subject1.bvh`, cùng G1, đều **không** `--rate_limit`)

| Đợt | Commit | n | Giá trị đo (ms/frame) | Đại diện | Vì sao phải chạy lại |
|---|---|---|---|---|---|
| Đợt cũ | `c62e74f` | 3 | 14,034 · 15,139 · 16,339 | mean **15,171** | log thiếu dòng `END` (wall time chỉ in ra console) → Review chặn merge ở RV-14 |
| Đợt mới | `f467075` | 5 | 17,522 · 17,246 · 17,852 · 16,853 · 17,272 | **median 17,272** (mean 17,349) | sau khi sửa định dạng dòng `END` (UTF-8 → UTF-16) và chạy lại toàn bộ |

Chênh lệch: **+14,36 %** nếu so mean với mean (17,349 / 15,171); **+13,85 %** nếu so median mới với mean cũ. Nguyên nhân chạy lại **không** phải vì số xấu mà vì **định dạng log hỏng** (RV-14) — nhưng đợt mới là đợt duy nhất có log đối chiếu được, nên **lấy đợt mới làm số chính thức**: median **17,272 ms/frame** (n = 5, CV 2,13 %). Số đợt cũ chỉ giữ để đối chiếu.

### (b) Retarget là tất định — bằng chứng SHA256 trên 40 file pkl

Băm toàn bộ `results/pkl/*.pkl` (SHA256, sau khi đã chạy thêm `run5`/`run6` cho T1 theo RV-24). Kết quả: **mọi lần chạy của cùng một cặp (robot, motion) cho ra file pkl giống nhau từng byte**, bất kể đợt đo, bất kể có/không `--rate_limit`:

| Nhóm pkl | Số file | SHA256 (rút gọn) | Gồm |
|---|---|---|---|
| G1 + `walk1_subject1` | **20** | `E7E3B906F22D3869…` | 6 pkl V3 mới (`run1..run6`), 1 pkl console (`…_evidence`), 4 pkl V3 cũ (`…_no_rate_limit_1..4`), 4 pkl cũ có cờ (`…_rate_limit_1..4`), 4 pkl V5 G1 (`run1..4`), 1 pkl V5 G1 bản đầu |
| T1 29dof + `walk1_subject1` | **7** | `4E7161873D508ABE…` | V5 `run1..4` + bản đầu + `run5`/`run6` (đo bổ sung theo RV-24) |
| PM01 + `walk1_subject1` | 5 | `57B693A8AAC72FE8…` | V5 `run1..4` + bản đầu |
| G1 + `walk4_subject1` | 5 | `37F0ACD2DD0EFF3C…` | warmup + `no_rate_limit_1..4` |
| G1 + `dance1_subject2` | 1 | `7A8FFEBE9C2BAE6F…` | KI-01 |
| G1 + `walk3_subject1` | 1 | `C9488E53DD93B7C8…` | KI-01 |
| T1 29dof + `walk4_subject1` | 1 | `2C6498E50CDBE0EF…` | KI-01 |

Tổng: 20 + 7 + 5 + 5 + 1 + 1 + 1 = **40 file**, và `run5`/`run6` của T1 cũng cho đúng `4E716187…` — chạy thêm không phá tính tất định.

Đọc bảng: **hash chỉ trùng trong cùng cặp (robot, motion)**; khác robot thì khác hash vì số dof khác nhau (G1 29 · T1 29dof 27 · PM01 24), khác motion cũng khác hash. (Lưu ý: không phải "15 pkl đều `E7E3B906…`" — con số đúng là **20 pkl** thuộc nhóm G1 + `walk1_subject1`.)

**Kết luận:** chênh lệch 14,4 % giữa hai đợt đo **không** đến từ thuật toán (đầu ra giống nhau từng byte) mà từ **trạng thái máy** (tải nền, nhiệt độ, dao động lập lịch CPU) — đúng bản chất của phép đo wall-clock toàn tiến trình.

## V6 — phép thử nhiễu (DEC-02): 4 phép thử, 15 mức

Đặc tả: `docs/v6_noise_spec.md` (DEC-02, phương án C). Input cố định `walk1_subject1.bvh` → `unitree_g1`; baseline = pkl của lần chạy sạch `g1_walk1_subject1_run1.pkl` (SHA256 `E7E3B906…`). Mỗi mức chạy **1 lần** — phép thử này đo **độ lệch có hệ thống**, **không** đo thời gian, nên không vi phạm hợp đồng 1 warm-up + 3 lần đo của V3/V5.

Kiểm chứng trước khi chạy: driver `v6_run.py` chạy lại bản sạch cho ra **|Δq| = 0,0000° · dr_rmse = 0,000 mm** so với pkl baseline → driver trung thực với `bvh_to_robot.py` (chỉ bỏ phần viewer).

| Phép thử | Mức | dq_mean (°) | dq_max (°) | dq_max **bỏ frame 0** (°) | dr_rmse (mm) | pct_frames_gt5deg (%) | converges |
|---|---|---|---|---|---|---|---|
| N1 nhiễu khớp | σ = 0,5° | 0,56 | 7,56 | 7,56 | 1,20 | 0,51 | 1 |
| N1 | σ = 1° | 1,10 | 14,11 | 14,11 | 1,56 | 5,55 | 1 |
| N1 | σ = 2° | 2,18 | 25,80 | 25,80 | 2,02 | 87,74 | 1 |
| N1 | σ = 5° | 5,41 | 63,89 | 63,89 | 3,52 | 100,00 | 1 |
| N2 trễ | k = 1 | 0,0010 | 36,08 | **0,31** | 0,03 | 0,013 | 1 |
| N2 | k = 2 | 0,0010 | 36,08 | **0,40** | 0,03 | 0,013 | 1 |
| N2 | k = 3 | 0,0010 | 36,08 | **0,44** | 0,03 | 0,013 | 1 |
| N2 | k = 5 | 0,0010 | 36,08 | **0,46** | 0,03 | 0,013 | 1 |
| N3 mất frame | p = 1 % | 0,0033 | 6,83 | 6,83 | 0,17 | 0,013 | 1 |
| N3 | p = 5 % | 0,0158 | 6,09 | 6,09 | 0,36 | 0,077 | 1 |
| N3 | p = 10 % | 0,0355 | 10,99 | 10,99 | 0,62 | 0,306 | 1 |
| N4 lệch tỉ lệ | −20 % | 1,86 | 29,65 | 29,65 | 718,53 | 90,43 | 1 |
| N4 | −10 % | 0,73 | 19,27 | **15,83** | 358,57 | 6,37 | 1 |
| N4 | +10 % | 1,88 | 33,32 | **18,37** | 359,32 | 94,77 | 1 |
| N4 | +20 % | 3,14 | 42,82 | **31,92** | 718,51 | 98,05 | 1 |

**RV-31 — `dq_max` bị frame 0 thổi lên:** cột `dq_max` (giữ nguyên, khớp CSV) tính cả frame 0; cột mới **`dq_max_excl_frame0`** tính lại trên các frame 1…N−1. Khác biệt chỉ đáng kể ở **N2** (36,08° → 0,31–0,46°) và **N4** (−10 %: 19,27 → **15,83**; +10 %: 33,32 → **18,37**; +20 %: 42,82 → **31,92**; −20 % không đổi vì frame 0 không phải chỗ lệch lớn nhất). `dq_mean` và `dr_rmse` **không đổi** (frame 0 chỉ là 1/7.839 nên không dịch chuyển trung bình). Cả hai cột đều nằm trong `results/v6_noise_sweep.csv`; khi trích vào báo cáo phải ghi rõ đang dùng cột nào.

**Đối chiếu giả thuyết (ghi đúng kết quả đo, không sửa số):**
1. **N1:** `dq_mean` tăng **gần tuyến tính** theo σ (0,56 → 1,10 → 2,18 → 5,41 ứng với 0,5/1/2/5°) — khớp kỳ vọng. Nhưng `pct_frames_gt5deg` bùng nổ **phi tuyến** (0,5 % → 5,5 % → 87,7 % → 100 %) vì đây là chỉ số ngưỡng: khi sai số trung bình chạm ~2° thì gần như mọi frame đều có ít nhất một khớp vượt 5°.
2. **N2:** so **đúng cặp frame** (dịch kết quả đi k frame) → `dq_mean` = **0,0010°**, `dr_rmse` = **0,03 mm** ≈ 0 — đúng giả thuyết "trễ chỉ làm lệch pha thời gian, không làm sai tư thế". Ngoại lệ **1 frame** (pct 0,013 % = 1/7839) lệch 36,08°, đã truy ra: đó là **frame đầu tiên ngay sau điểm dịch** — cùng một frame đầu vào (frame 0) được retarget lần thứ hai. **Lần giải đầu chưa hội tụ trong trần 10 vòng lặp; các lần giải lại sau đó hội tụ dần.** Bằng chứng: `out[0]` vs `base[0]` = **0,0000°**; `out[1]` vs `base[0]` = **36,08°**; rồi **0,307° → 0,094° → 0,044° → 0,021°** (giảm đơn điệu, không tích lũy). **Kết luận: đúng là frame biên sau warm-start, không phải sai số tích lũy**; IK có phụ thuộc warm-start ở frame biên (không hoàn toàn độc lập từng frame như giả thuyết).

**Ghi chú thêm (RV-30):** **frame 0 của mỗi clip chưa hội tụ ở khâu tay** — vì thế mọi chỉ số `dq_max` đều bị frame 0 thổi lên; xem cột `dq_max_excl_frame0` ở mục RV-31 bên dưới để đọc đúng mức lệch thực của phần còn lại của clip.
3. **N3:** ảnh hưởng **rất nhỏ** (dq_mean 0,0033 → 0,0355°; pct ≤ 0,31 %) và tăng theo p — vì frame thiếu được lấp bằng nội suy tuyến tính nên tư thế gần như giữ nguyên.
4. **N4:** lệch lớn và **bất đối xứng** (pct 6,4 % ở −10 % nhưng 94,8 % ở +10 %). `dr_rmse` 359/719 mm **chủ yếu do quỹ đạo gốc bị scale** (người cao hơn đi xa hơn), không phải sai tư thế — cần nói rõ khi viết báo cáo.
5. `still_converges = 1` ở **cả 15 mức** → không mức nhiễu nào làm IK phân kỳ hay sinh NaN.

### Bão hòa khớp — lời giải cho bất đối xứng của N4

Đếm số frame có **ít nhất 1 khớp nằm trong 0,5° so với giới hạn** (`qpos_lo`/`qpos_hi` của `g1_mocap_29dof.xml`), cột `n_saturated_frames`; cột `n_frames_hit_limit_max` = số khớp tối đa cùng bão hòa trong một frame.

| Điều kiện | n_saturated_frames | n_frames_hit_limit_max | Khớp bão hòa nhiều nhất |
|---|---|---|---|
| Baseline sạch | 1.865 / 7.839 (23,8 %) | 3 | waist_pitch 745 · ankle_roll 452/412 |
| N4 **−10 %** | 1.793 | 2 | waist_pitch 807 · shoulder_yaw 398 · ankle_roll 344/310 |
| N4 **+10 %** | **2.002** | 3 | waist_pitch 783 · **ankle_roll 534/489** · shoulder_yaw 392 |
| N4 **+20 %** | **2.166** | 3 | waist_pitch 843 · **ankle_roll 589/541** |
| N1 σ = 5° | 3.550 | 5 | — |

**Kết luận (3 câu):** Ở +10 %/+20 % (người cao hơn robot) số frame bão hòa **cao hơn** −10 % (2.002 / 2.166 so với 1.793), và phần tăng tập trung ở `ankle_roll` (534/489 so với 310/344) — hướng đúng giả thuyết "robot không với tới nên khớp bị ghì ở giới hạn". Tuy vậy mức chênh (≈200–370 frame) **không đủ lớn** để giải thích trọn vẹn khoảng cách `pct_frames_gt5deg` (6,4 % so với 94,8 %), nên bão hòa chỉ là **một phần** lời giải; phần còn lại là hình học tay/chân không với tới đích. Lưu ý `dr_rmse` 359/719 mm của N4 **chủ yếu do quỹ đạo gốc bị scale** (người cao hơn đi xa hơn) chứ **không phải sai tư thế** — chỉ số này không dùng để kết luận về tư thế.

Số thô: `results/v6_noise_sweep.csv` (thêm 2 cột bão hòa + `max_dev_frame_index`); đồ thị: `results/figures/v6_noise_vs_deviation.png` (3 panel); lệnh: `logs/lenh_da_chay.md` mục 11.
