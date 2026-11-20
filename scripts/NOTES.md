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
   (`RobotMotionViewer`) và vẽ từng frame; đo bằng `Measure-Command`/wall-clock là đo
   **toàn bộ tiến trình**, gồm khởi tạo model + render. Vì vậy CSV tách hẳn hai nhóm cột:
   nhóm `ms_per_frame*` (chỉ `retarget()`, đúng định nghĩa `t_i`/`ms_per_frame` trong
   `docs/dinh_nghia_phep_do.md` §1.1, dùng để kết luận) và nhóm `*_process` (cả tiến
   trình, chỉ chẩn đoán). Xem §5.
4. Không có `--save_path` ⇒ không có `.pkl`; có `--loop` ⇒ không bao giờ thoát.
5. Script cần màn hình (mở cửa sổ MuJoCo). Máy không GUI phải dùng Xvfb/WSLg, hoặc
   sửa viewer — đó là phạm vi `patches/`, không phải `measure_runtime.py`.

---

## 5. `scripts/measure_runtime.py` — giao diện chính thức

Một lệnh chạy trọn giao thức (N warm-up + M lần đo, mỗi lần một process mới) và xuất
2 file: bảng tổng hợp (1 dòng/lần chạy) và bảng raw (1 dòng/frame).

### Cờ chính thức (RV-20 — Research sửa V1 theo bảng này)

| Cờ | Mặc định | Ý nghĩa |
|---|---|---|
| `--motion PATH...` | — | file motion; alias `--bvh-file`, `--bvh_file` |
| `--robot NAME...` | `unitree_g1` | robot GMR |
| `--runs N` | 4 | **tổng** số lần chạy, gồm warm-up (4 = 1 warm-up + 3 đo) |
| `--warmup-runs N` | 1 | N lần đầu bị loại khỏi mọi phép tính; alias `--warmup_runs` |
| `--warmup-frames N` | 30 | bỏ N frame đầu **trong từng lần chạy**; alias `--warmup_frames` |
| `--out PATH` | `v3_runtime.csv` | bảng tổng hợp; alias cũ `--csv` |
| `--raw-out PATH` | `<out>_raw.csv` | bảng raw từng frame; alias `--raw_out` |
| `--fps-src F` | 30 | fps phát của dữ liệu nguồn (LAFAN1 = 30); alias `--fps_src` |
| `--script {bvh,smplx}` | suy ra từ đuôi file motion | entry script GMR |
| `--gmr-dir`, `--python` | clone trong repo / python hiện tại | vị trí repo GMR, python env gmr |
| `--dry-run` | tắt | dữ liệu giả, không gọi GMR |
| `--frames N` | 300 | số frame clip giả (chỉ `--dry-run`) |
| `--work-dir` | thư mục tạm | nơi ghi `.pkl`/`.json` tạm |
| `--retarget-only`, `--out-json` | — | nội bộ: probe đo `retarget()`, do script tự gọi |

Quy ước `run`: `run = 1..--runs`; mọi `run <= --warmup-runs` có `included = 0` và bị loại
khỏi phép tính cuối. Số lần đo thực = `--runs - --warmup-runs` (phải ≥ 1).
Có thể trộn `.bvh` và `.npz` trong cùng một lệnh: mỗi motion tự suy ra entry script riêng
(bỏ trống `--script`), và `bvh_file` chỉ điền cho dòng BVH.

### Lệnh chạy (đúng V1 §3.2)

```powershell
conda run -n gmr python scripts/measure_runtime.py `
  --bvh_file <LAFAN1>/walk1_subject1.bvh `
  --robot unitree_g1 `
  --runs 4 --warmup_runs 1 --warmup_frames 30 `
  --fps_src 30 `
  --out results/v3_runtime.csv `
  --raw_out results/v3_runtime_raw.csv
```

`--bvh_file` là alias của `--motion`, `--script` tự suy ra `bvh`, nên lệnh V1 chạy nguyên
văn. Nếu gọi bằng python ngoài env, thêm `--python <python env gmr>`.

### Mỗi lần chạy đo hai tiến trình

1. **Entry script GMR** (`bvh_to_robot.py` / `smplx_to_robot.py`) → nhóm `_process`.
   Wall-clock bấm quanh cả process: khởi động interpreter + model + viewer + render +
   ghi `.pkl`. Vì gồm cả khởi động interpreter nên đây là **cận trên** của `T_process`
   (cùng tinh thần `Measure-Command` ở V1 §3.1). Lệnh đầy đủ nằm ở `process_cmd`.
2. **Probe `--retarget-only`** — **không dựng viewer** (docs §3 cấm) → mảng `t_i`,
   `t_init_s`, số frame, phiên bản package. Lệnh đầy đủ nằm ở `cmd`.

Cả hai tiến trình được đặt `CUDA_VISIBLE_DEVICES=""` (docs §2.2) và `PYTHONPATH` trỏ
`--gmr-dir`.

### Cột file tổng hợp

25 cột đầu **đúng nguyên văn thứ tự §5.1**:

| Nhóm | Cột | Ý nghĩa |
|---|---|---|
| định danh | `run, robot, motion, bvh_file` | `bvh_file` chỉ điền khi chạy BVH, ngược lại rỗng |
| đếm frame | `n_frames, n_warmup_frames` | `n_frames` = số frame **được tính** = tổng − warm-up frame |
| nguồn | `fps_src` | từ `--fps-src`, phải khớp header dữ liệu nguồn |
| retarget | `ms_per_frame, ms_per_frame_mean, ms_per_frame_p95` | median / mean / p95 của `t_i` sau khi bỏ warm-up |
| dẫn xuất | `fps_out, realtime_factor` | `fps_out = 1000 / ms_per_frame`; `realtime_factor = fps_out / fps_src` |
| khởi tạo | `t_init_s` | thời gian `GMR(...)` đo trong probe, không cộng vào `t_i` |
| máy | `cpu, ram_gb, os, python, numpy, mujoco, mink, torch` | bốn phiên bản package đọc trong env gmr |
| môi trường | `git_head, cuda_visible` | HEAD ngắn của repo GMR; `cuda_visible` luôn rỗng (ép CPU) |
| tái lập | `cmd, timestamp` | lệnh probe + ISO-8601 có múi giờ |

5 cột cuối là phần V1 §3.3 bắt buộc thêm (không đổi tên cột nào của §5.1):

| Cột | Ý nghĩa |
|---|---|
| `n_frames_total` | tổng frame của clip nạp vào, chưa trừ warm-up frame |
| `ms_per_frame_process` | `wall_s * 1000 / n_frames_total` của cả tiến trình entry script |
| `fps_out_process` | `n_frames_total / wall_s` |
| `realtime_factor_process` | `fps_out_process / fps_src` |
| `process_cmd` | lệnh entry script đầy đủ, để tái lập nhóm `_process` |

### RV-19 — tên đại lượng

- **Đã bỏ** hai cột trần `ms_per_frame` (process cũ) và `fps`: chúng đo cả tiến trình
  nhưng tên không nói gì, trái §1.1 và rất dễ bị chép vào báo cáo như số retargeting.
- `ms_per_frame` bây giờ **là** đại lượng retarget của §1.1 (median `t_i`); mọi số process
  đều mang hậu tố `_process`. Không suy `ms_per_frame` từ `_process`, không nhân hệ số.
- `--runs` đổi nghĩa thành **tổng số lần chạy** (trước đây là số lần đo) để khớp V1 §3.2;
  cột `run_id` đổi tên thành `run` theo §5.1.

### File raw (§5.2)

`run, motion, robot, frame, included, ms`

- `included = 0` cho **toàn bộ** frame của các run warm-up và cho `--warmup-frames` frame
  đầu của mỗi run đo; `1` cho phần còn lại. `ms` là `t_i` của retarget, 3 chữ số thập phân.
- Tổng số dòng = `số motion × số robot × --runs × số frame`; số dòng `included = 1`
  = `số motion × số robot × (--runs − --warmup-runs) × (số frame − warm-up frame)`.

### Chạy khô (không cần env, dùng cho test/Review)

```powershell
python scripts/measure_runtime.py --dry-run
python scripts/measure_runtime.py --dry-run --out "$env:TEMP\dry.csv" --runs 4 --warmup-runs 1 --frames 200
```

`--dry-run` **không gọi GMR, không import GMR**: giả định 30 frame đầu 40 ms, phần còn lại
22 ms, `t_init_s = 0,5`, overhead process 0,5 s, phiên bản package ghi `dry-run`.
→ **Số trong CSV dry-run là số giả, tuyệt đối không được chép vào báo cáo.**
Mặc định dry-run ghi vào thư mục tạm để không rơi rác vào repo.

---

## 6. Test

```powershell
python -m pytest scripts/ -q
```

- Chỉ cần Python chuẩn + pytest; **không cần** env `gmr`, không cần mạng, không cần
  `third_party/GMR`. Test gọi CLI qua subprocess, đúng lệnh Review sẽ chạy.
- Test khoá **nguyên văn** 25 cột §5.1 ở đầu header (thứ tự + tên), 5 cột V1 thêm sau,
  và header raw §5.2.
- Test giao thức: `--runs 4 --warmup-runs 1` ⇒ 4 dòng `run=1..4`, `included = 1` đúng
  `3 × (số frame − 30)` dòng, `run=1` toàn `included = 0`.
- Test dựng một package `general_motion_retargeting` giả (thư mục tạm) trong đó `__init__`
  và bước load dữ liệu ngủ 0,1–0,3 s, chỉ `retarget()` ngủ 4 ms. Nhờ vậy test chứng minh
  `ms_per_frame` **không** cộng thời gian load/khởi tạo: nếu cộng, con số sẽ vọt lên hàng
  trăm ms; đồng thời `ms_per_frame_process` phải lớn hơn hẳn (đo cả process).
- Một test khác làm 30 lời gọi `retarget()` đầu chậm 50 ms và 30 lời gọi sau nhanh 2 ms;
  trung vị phải < 20 ms, tức là warm-up frame đã bị loại đúng.
- Test sẽ fail nếu ai đổi tên/thiếu cột CSV, đổi công thức, bỏ warm-up, đổi nghĩa `--runs`,
  hoặc để dry-run phụ thuộc GMR.

---

## 7. Tuyên bố định lượng có thể kiểm chứng (cho V1)

README repo, mục **"Speed Benchmark"** (không phải bảng trong paper):

| CPU | Retargeting Speed |
|---|---|
| AMD Ryzen Threadripper 7960X 24-Cores | 60~70 FPS |
| 13th Gen Intel Core i9-13900K 24-Cores | 35~45 FPS |

Đây là tuyên bố duy nhất về tốc độ trong repo. Theo `docs/dinh_nghia_phep_do.md` §6,
**paper không nêu bất kỳ con số thời gian nào**, nên mọi câu "nhanh/chậm hơn paper"
là bịa. Cách kiểm chứng đúng: đo bằng `ms_per_frame` (median `t_i` của retarget) trên
đúng CPU, lấy `fps_out` và `realtime_factor` do script tính, rồi so `fps_out` với khoảng
trong bảng README (ghi rõ CPU và số lõi). Cột README và cột nhóm đo phải để **hai cột
riêng** trong báo cáo. Ngưỡng kết luận C5 là `realtime_factor ≥ 1,00`, không phải so với
bảng README; nhóm `_process` chỉ dùng để bắc cầu theo `docs/dinh_nghia_phep_do.md` §6.1.
