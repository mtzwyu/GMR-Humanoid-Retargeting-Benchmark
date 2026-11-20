# NOTES — API repo GMR và cách dùng script của nhóm

**Repo gốc:** https://github.com/YanjieZe/GMR
**Commit đã đọc:** `25f56db` (clone nông vào `third_party/GMR`, **không commit** — đã nằm trong `.gitignore`)
**License:** MIT (`Copyright 2025 Yanjieze`) — dùng và trích dẫn thoải mái, giữ bản quyền.
**Bài báo:** arXiv:2510.02252 — *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking*

Mọi thông tin dưới đây đọc trực tiếp từ source tại commit trên, không chép từ paper.

---

## 1. Cấu trúc repo

```
third_party/GMR/
├── scripts/                        # entry point (mỗi file là 1 lệnh chạy độc lập)
│   ├── smplx_to_robot.py           # SMPL-X (.npz) -> .pkl robot
│   ├── bvh_to_robot.py             # BVH (.bvh)   -> .pkl robot
│   ├── smplx_to_robot_dataset.py   # chạy hàng loạt
│   ├── bvh_to_robot_dataset.py
│   ├── vis_robot_motion.py         # xem lại .pkl
│   ├── batch_gmr_pkl_to_csv.py     # .pkl -> .csv (7+dof cột)
│   └── xsens_*.py / gvhmr_to_robot.py / fbx_offline_to_robot.py ...
├── general_motion_retargeting/
│   ├── motion_retarget.py          # class GeneralMotionRetargeting (IK bằng mink + MuJoCo)
│   ├── kinematics_model.py
│   ├── robot_motion_viewer.py      # cửa sổ MuJoCo, có --record_video
│   ├── data_loader.py              # load_robot_motion() — đọc .pkl
│   ├── params.py                   # ROBOT_XML_DICT, IK_CONFIG_DICT
│   ├── ik_configs/*.json           # map khớp xương người -> robot
│   └── utils/                      # smpl.py, lafan1.py, ...
├── assets/                         # MJCF robot; body_models/ KHÔNG có sẵn (phải tự tải SMPL-X)
├── pyproject.toml, uv.lock
└── README.md                       # có mục "Speed Benchmark"
```

Cài đặt (chỉ tab Run, env `gmr`): `conda create -n gmr python=3.10`, `pip install -e .`,
`conda install -c conda-forge libstdcxx-ng`. Script của Vỹ **không cần** bước này.

---

## 2. File `.pkl` đầu ra — cấu trúc chính xác

Cả `smplx_to_robot.py` (dòng 148–168) và `bvh_to_robot.py` (dòng 159–179) đều lưu **một dict** bằng `pickle`:

| Khóa | Kiểu / shape | Ý nghĩa |
|---|---|---|
| `fps` | `float` | fps của motion đã lưu (xem mục 4) |
| `root_pos` | `np.ndarray (T, 3)` | vị trí gốc (pelvis/waist…) trong hệ thế giới, mét |
| `root_rot` | `np.ndarray (T, 4)` | quaternion gốc, **thứ tự xyzw** |
| `dof_pos` | `np.ndarray (T, J)` | khớp robot; `J` = số DOF của robot (G1 = 29) |
| `local_body_pos` | `None` | 2 script này luôn ghi `None` |
| `link_body_list` | `None` | 2 script này luôn ghi `None` |

- `T` = số frame. **Số frame đọc bằng `len(motion_data["dof_pos"])`** — `measure_runtime.py` dùng đúng cách này.
- Quy ước quaternion là cái bẫy lớn nhất:
  - GMR nội bộ (`retarget()`) trả `qpos = [pos(3), quat wxyz(4), dof]`.
  - Khi lưu, script đổi sang **xyzw**: `root_rot = qpos[3:7][[1,2,3,0]]`.
  - Khi đọc, `load_robot_motion()` đổi ngược về **wxyz**: `root_rot[:, [3,0,1,2]]`.
  - → Ai đọc `.pkl` trực tiếp phải tự đổi nếu muốn wxyz.
- Đọc chuẩn bằng API repo:

```python
from general_motion_retargeting import load_robot_motion
(data, fps, root_pos, root_rot_wxyz, dof_pos, local_body_pos, link_names) = load_robot_motion(path)
```

- Chuyển sang CSV (cho BeyondMimic/RL): `python scripts/batch_gmr_pkl_to_csv.py --folder <dir>`
  → mỗi dòng `[root_pos(3), root_rot xyzw(4), dof(J)]`, tự hạ xuống 30 fps nếu `fps > 30`.

Kiểm tra nhanh một file `.pkl` mà không cần env `gmr` (chỉ pickle + in shape):

```powershell
python -c "import pickle;d=pickle.load(open('out.pkl','rb'));print(d['fps'],{k:(getattr(v,'shape',v)) for k,v in d.items()})"
```

---

## 3. Cách gọi 2 script chính

### SMPL-X → robot

```bash
python scripts/smplx_to_robot.py \
  --smplx_file <path>.npz \
  --robot unitree_g1 \
  --save_path out/unitree_g1_motion.pkl
```

| Cờ | Mặc định | Ghi chú |
|---|---|---|
| `--smplx_file` | đường dẫn tuyệt đối của tác giả (không dùng được) | **luôn truyền tay** |
| `--robot` | `unitree_g1` | chỉ nhận tên có trong `IK_CONFIG_DICT["smplx"]` |
| `--save_path` | `None` | **không có cờ này thì không sinh `.pkl`** |
| `--loop` | tắt | bật thì chạy vô hạn, không bao giờ lưu file |
| `--record_video`, `--rate_limit` | tắt | |

Cần SMPL-X body model: tải từ smpl-x.is.tue.mpg.de, đặt vào `assets/body_models/smplx/`
(repo **không kèm** vì license). Thiếu thư mục này script chết ngay khi `load_smplx_file`.

### BVH → robot

```bash
python scripts/bvh_to_robot.py \
  --bvh_file <path>.bvh --format lafan1 \
  --robot unitree_g1 --motion_fps 30 \
  --save_path out/unitree_g1_walk.pkl
```

`--format` nhận `lafan1` hoặc `nokov`; `--robot` lấy từ `IK_CONFIG_DICT["bvh_lafan1"]`.

### Danh sách robot (từ `params.py`, commit `25f56db`)

`unitree_g1` (29 DOF), `unitree_g1_with_hands`, `unitree_h1`, `unitree_h1_2`, `unitree_h2`,
`booster_t1`, `booster_t1_29dof`, `stanford_toddy`, `fourier_n1`, `engineai_pm01`,
`kuavo_s45`, `hightorque_hi`, `galaxea_r1pro`, `berkeley_humanoid_lite`, `booster_k1`,
`pnd_adam_lite`, `tienkung`, `pal_talos`, `fourier_gr3`.

Không phải robot nào cũng có mặt ở mọi nguồn: `bvh_lafan1` chỉ có 8 robot, `smplx` có 17.

### Xem lại `.pkl`

```bash
python scripts/vis_robot_motion.py --robot unitree_g1 --robot_motion_path out/unitree_g1_walk.pkl
```

---

## 4. Chi tiết dễ sai khi đọc kết quả

1. **Số frame trong `.pkl` = `T_input - 1` với cả 2 script, nhưng mất frame khác nhau:**
   - `smplx_to_robot.py`: tăng `i` **trước** khi dùng (`i += 1; if i >= len: break`) → bỏ
     **frame 0**, lưu frame `1..T-1`.
   - `bvh_to_robot.py`: `break` xảy ra **trước** `qpos_list.append(qpos)` ở vòng cuối →
     bỏ **frame cuối**, lưu frame `0..T-2`.
   - → Đừng lấy số frame trong `.pkl` so trực tiếp với số frame file input, và đừng giả
     định frame nào bị mất nếu không đọc lại code.
2. **`fps` lưu trong `.pkl` không phải fps đo được.**
   - SMPL-X: `aligned_fps = tgt_fps = 30` nếu nguồn ≤ 30 fps, ngược lại ≈ 30 sau nội suy.
   - BVH: chính là `--motion_fps` bạn truyền (mặc định 30), **không đọc từ header BVH**.
   - Vì vậy fps trong `.pkl` **không dùng** để kết luận về tốc độ chạy.
3. **`retarget()` chỉ là một phần thời gian chạy.** Cả 2 script còn mở cửa sổ MuJoCo
   (`RobotMotionViewer`) và vẽ từng frame; đo bằng `Measure-Command`/`wall_s` là đo
   **toàn bộ tiến trình**, gồm khởi tạo model + render. Vì vậy `measure_runtime.py`
   tách hẳn hai cột: `ms_per_frame_retarget` (đúng định nghĩa `t_i`/`ms_per_frame`
   trong `docs/dinh_nghia_phep_do.md` §1.1, dùng để kết luận) và
   `ms_per_frame_process` (cả tiến trình, chỉ để chẩn đoán). Xem §5.
4. Không có `--save_path` ⇒ không có `.pkl`; có `--loop` ⇒ không bao giờ thoát.
5. Script cần màn hình (mở cửa sổ MuJoCo). Máy không GUI phải dùng Xvfb/WSLg, hoặc
   sửa viewer — đó là phạm vi `patches/`, không phải `measure_runtime.py`.

---

## 5. `scripts/measure_runtime.py`

### Hai đại lượng, hai mục đích

| Cột | Đo cái gì | Dùng để |
|---|---|---|
| `ms_per_frame_retarget` | `median(t_i)` với `t_i = perf_counter() sau − trước` **chỉ** quanh `retargeter.retarget(frame)`; bỏ `--warmup-frames` frame đầu | **Kết luận tuyên bố tốc độ** (`fps_out = 1000 / cột này`, `realtime_factor = fps_out / fps_src`) |
| `ms_per_frame_process` | `wall_s * 1000 / frames` của **cả tiến trình** entry script: khởi tạo model, dựng viewer, render từng frame, ghi `.pkl` | Chẩn đoán "chạy một lệnh GMR mất bao lâu"; **không** dùng để kết luận |

Vì sao phải tách: `docs/dinh_nghia_phep_do.md` §1.1 định nghĩa `ms_per_frame` là trung vị
`t_i` chỉ bọc `retarget()`, còn §3 **cấm** dựng `RobotMotionViewer` trong lúc đo và cấm
dùng FPS render. Nếu chỉ có một cột wall-clock thì con số vừa sai định nghĩa vừa không
so sánh được giữa các máy (GPU/display/render khác nhau). Cột process được giữ lại vì
CSV cũ đã có và vì nó trả lời câu hỏi vận hành khác.

### Chạy thật (tab Run, env `gmr`)

```powershell
conda run -n gmr python scripts/measure_runtime.py `
  --motion <file>.npz `
  --robot unitree_g1 `
  --script smplx --runs 3 `
  --csv measure_runtime.csv
```

- `conda run -n gmr` để `sys.executable` là python của env; nếu gọi bằng python ngoài,
  truyền thêm `--python <đường dẫn python env gmr>`.
- Với BVH: `--script bvh --motion <file>.bvh`.
- Mỗi dòng CSV chạy **hai tiến trình**:
  1. entry script GMR (`smplx_to_robot.py` / `bvh_to_robot.py`) → `wall_s`, `frames`, `cmd`;
  2. probe `measure_runtime.py --retarget-only` → mảng `t_i` từng frame, **không dựng
     viewer**, có `--warmup-frames 30` bỏ 30 frame đầu theo §3. `retarget_cmd` là lệnh
     tái lập đúng probe này.
- Cả hai tiến trình được đặt `CUDA_VISIBLE_DEVICES=""` (docs §2.2) và `PYTHONPATH` trỏ
  `--gmr-dir`.
- `--warmup-frames` mặc định **30** (≈ 1 s ở 30 fps) theo §3; nếu motion ngắn hơn, script
  báo lỗi chứ không lặng lẽ lấy mẫu rỗng.

### Cách đọc `fps` và `frames`

- `fps` = `frames / wall_s` — thông lượng **cả tiến trình**, **không phải** `fps_out`.
  `fps_out` phải tính từ `1000 / ms_per_frame_retarget`.
- `frames` lấy từ `.pkl` nên vẫn là `T-1` so với input (§4.1) và **không** trừ 30 frame
  warm-up. Chỉ `ms_per_frame_retarget` bị trừ warm-up.

### Còn thiếu so với hợp đồng `results/v3_runtime.csv` (§5.1)

Script này là công cụ đo/chẩn đoán, **chưa** phát ra đúng hợp đồng §5.1. Các cột còn
thiếu: `ms_per_frame_mean`, `ms_per_frame_p95`, `fps_src`, `realtime_factor`, `t_init_s`,
`n_warmup_frames`, `bvh_file`, đánh dấu `run=1` là warm-up rồi loại khỏi phép tính,
thông tin máy (`cpu, ram_gb, os, python, numpy, mujoco,
mink, torch, git_head, cuda_visible`), `timestamp`, và file raw từng frame (§5.2).
Đừng trỏ `--csv` vào `results/v3_runtime.csv` rồi coi là đã đạt §5.1 — việc đó thuộc
ticket riêng.

### Chạy khô (không cần env, dùng cho test/Review)

```powershell
python scripts/measure_runtime.py --dry-run
python scripts/measure_runtime.py --dry-run --csv "$env:TEMP\dry.csv" --robot unitree_g1 --runs 3 --frames 120
```

`--dry-run` **không gọi GMR, không import GMR**: nó sinh `.pkl` giả đúng cấu trúc, đếm
frame từ đó, giả định retarget 22 ms/frame và overhead 0,5 s cho cả tiến trình (nên
`ms_per_frame_process` luôn lớn hơn `ms_per_frame_retarget`).
→ **Số trong CSV dry-run là số giả, tuyệt đối không được chép vào báo cáo.**
Mặc định dry-run ghi vào thư mục tạm để không rơi rác vào repo.

### Cột CSV (hợp đồng với Review)

| Cột | Ý nghĩa |
|---|---|
| `run_id` | lần chạy thứ mấy, 1..`--runs`, lặp lại cho từng cặp (robot, motion) |
| `robot` | tên robot GMR |
| `motion` | file motion đầu vào, đúng như đã truyền |
| `wall_s` | tổng thời gian tiến trình entry script, giây (3 chữ số thập phân) |
| `frames` | số frame đọc từ `.pkl` đầu ra |
| `ms_per_frame` | `wall_s * 1000 / frames` (cột cũ, giữ nguyên) |
| `fps` | `frames / wall_s` (thông lượng cả tiến trình) |
| `cmd` | lệnh entry script đầy đủ đã chạy |
| `ms_per_frame_retarget` | trung vị `t_i` sau khi bỏ warm-up, ms, 1 chữ số thập phân |
| `ms_per_frame_process` | `ms_per_frame` làm tròn 1 chữ số thập phân (đại lượng chẩn đoán) |
| `retarget_cmd` | lệnh probe `--retarget-only` đầy đủ đã chạy, để tái lập cột retarget |

Thứ tự dòng: motion → robot → run. Một dòng = một lần chạy (2 tiến trình).

---

## 6. Test

```powershell
python -m pytest scripts/ -q
```

- Chỉ cần Python chuẩn + pytest; **không cần** env `gmr`, không cần mạng, không cần
  `third_party/GMR`. Test gọi CLI qua subprocess, đúng lệnh Review sẽ chạy.
- Test dựng một package `general_motion_retargeting` giả (thư mục tạm) trong đó `__init__`
  và bước load dữ liệu ngủ 0,1–0,3 s, chỉ `retarget()` ngủ 4 ms. Nhờ vậy test chứng minh
  `ms_per_frame_retarget` **không** cộng thời gian load/khởi tạo: nếu cộng, con số sẽ vọt
  lên hàng trăm ms.
- Một test khác làm 30 lời gọi `retarget()` đầu chậm 50 ms và 30 lời gọi sau nhanh 2 ms;
  trung vị phải < 20 ms, tức là warm-up đã bị loại đúng.
- Test sẽ fail nếu ai đổi tên/thiếu cột CSV, đổi công thức, bỏ warm-up, hoặc để dry-run
  phụ thuộc GMR.

---

## 7. Tuyên bố định lượng có thể kiểm chứng (cho V1)

README repo, mục **"Speed Benchmark"** (không phải bảng trong paper):

| CPU | Retargeting Speed |
|---|---|
| AMD Ryzen Threadripper 7960X 24-Cores | 60~70 FPS |
| 13th Gen Intel Core i9-13900K 24-Cores | 35~45 FPS |

Đây là tuyên bố duy nhất về tốc độ trong repo. Theo `docs/dinh_nghia_phep_do.md` §6,
**paper không nêu bất kỳ con số thời gian nào**, nên mọi câu "nhanh/chậm hơn paper"
là bịa. Cách kiểm chứng đúng: đo bằng `ms_per_frame_retarget` trên đúng CPU, tính
`fps_out = 1000 / ms_per_frame_retarget`, rồi so `fps_out` với khoảng trong bảng README
(ghi rõ CPU và số lõi). Cột README và cột nhóm đo phải để **hai cột riêng** trong báo cáo.
Ngưỡng kết luận C5 là `realtime_factor ≥ 1,00`, không phải so với bảng README.
