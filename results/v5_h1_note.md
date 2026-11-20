# H1 / H1_2 — vì sao V5 không có Unitree H1, và bằng chứng H1_2 chạy được qua Xsens

Ngày: 2026-11-21 · Người làm: Đặng Duy Mạnh (Run) · Nhánh: `task/h1-xsens`

## 1. Tóm tắt một dòng

**Blocker của H1 là blocker cấp (định dạng motion × robot), không phải bản thân robot H1.** Cùng một robot họ Unitree, `unitree_h1_2` **chạy được** khi đổi đầu vào sang BVH Xsens; `unitree_h1` không có cấu hình IK cho bất kỳ định dạng offline nào trong repo.

## 2. Vì sao H1 không có trong V5

V5 dùng **một motion duy nhất** `walk1_subject1.bvh` (LAFAN1) cho cả 3 robot. Trên đường đó:

| Kiểm tra | Kết quả |
|---|---|
| `scripts/bvh_to_robot.py --robot unitree_h1` | **exit 2**: `argument --robot: invalid choice: 'unitree_h1'` — danh sách hợp lệ chỉ có `booster_t1_29dof, engineai_pm01, fourier_n1, pal_talos, stanford_toddy, unitree_g1, unitree_g1_with_hands, unitree_h2` |
| `general_motion_retargeting/ik_configs/` | **không có** `bvh_lafan1_to_h1.json` (chỉ có `bvh_lafan1_to_g1/h2/t1_29dof/n1/pm01/toddy`) |
| README bảng *Supported Robots* | cột **BVH** của `unitree_h1` và `unitree_h1_2` = **TBD** |
| Đường SMPL-X (có hỗ trợ H1) | bị chặn bởi license SMPL-X (xem `logs/nhat_ky_cai_dat.md` mục 9) |

→ Vì vậy `results/v5_sim2sim.csv` giữ đúng 3 robot + 1 dòng `unitree_h1` trạng thái `blocked`, **không sửa**.

## 3. H1_2 chạy được qua Xsens — bằng chứng thật

Lệnh (chạy từ `third_party/GMR`):

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python scripts/xsens_bvh_to_robot.py `
  --bvh_file ../GMR/assets/xsens_bvh_test/251021_04_boxing_120Hz_cm_3DsMax.bvh `
  --robot unitree_h1_2 `
  --save_path ../../results/pkl/h1_2_xsens_boxing.pkl
```

| Mục | Giá trị đo được |
|---|---|
| Kết quả | **exit 0**, log `results/logs/h1_2_xsens_boxing.log` kết thúc `Saved to …h1_2_xsens_boxing.pkl` |
| Số frame | **4.249** (BVH `Frames: 4249`, `Frame Time: 0.008333` → **120 Hz**, clip 35,4 s) |
| Thời gian chạy | **82,63 s** wall (tqdm ~57–58 it/s) |
| pkl | `results/pkl/h1_2_xsens_boxing.pkl` — `fps=120`, `root_pos (4249,3)`, `dof_pos (4249,27)` |
| IK config dùng | `bvh_xsens_to_h1_2.json` (có sẵn trong repo) |

⚠️ **Không dùng thời gian của lần chạy này để so sánh tốc độ.** `xsens_bvh_to_robot.py` khai báo
`--rate_limit` với `default=True` và **không có cờ để tắt** → mọi lần chạy đều bị bộ giới hạn tốc độ bóp lại
(120 Hz danh nghĩa nhưng render thực ~57 it/s, wall 82,6 s cho clip 35,4 s).

### Ba chỗ tắc đã gặp và cách xử lý (ghi ngay khi gặp)

| # | Lỗi | Cách xử lý |
|---|---|---|
| 1 | `ModuleNotFoundError: No module named 'PyQt6'` — `general_motion_retargeting/utils/xsens.py` import `xsens_vendor/bvh_edit/CurveEditor.py`, file này cần PyQt6 | `pip install PyQt6` (6.12.1) vào env `gmr` |
| 2 | `ModuleNotFoundError: No module named 'matplotlib'` — cùng đường import trên | `pip install matplotlib` (3.10.9) vào env `gmr` |
| 3 | `UnicodeEncodeError: 'charmap' codec can't encode` — script in tiếng Trung ra console cp1258 | đặt `PYTHONIOENCODING=utf-8` trước khi chạy |

→ **PyQt6 và matplotlib chưa có trong `requirements.txt`** (requirements chốt theo đường `bvh_to_robot.py`). Nếu nhóm muốn đường Xsens tái lập được trên máy khác thì phải thêm 2 gói này; hiện chưa thêm để không đổi hợp đồng môi trường đã chốt.

## 4. Chất lượng ánh xạ của H1_2 (motion khác — không so sánh trực tiếp)

Chạy `tools/quality_metrics.py` trên pkl trên (fps đọc từ pkl = 120):

| robot | n frame | slide L / R (mm/s) | slide mean | min_body_height (mm) | % frame xuyên sàn | % frame chạm giới hạn khớp |
|---|---|---|---|---|---|---|
| `unitree_h1_2` | 4.249 | 467,78 / 737,79 | **602,79** | **+241,71** | 0,00 | 64,65 |

**Đọc số — kèm 3 cảnh báo:**
1. Đây là **motion khác** (boxing 120 Hz, định dạng Xsens), **không** so sánh trực tiếp với `walk1_subject1` của G1/T1/PM01. Foot slide 602,8 mm/s cao hơn nhiều so với đi bộ (49–118 mm/s) nhưng bài boxing có xoay/đổi trụ liên tục nên **không kết luận được gì về chất lượng tương đối**.
2. `min_body_height_mm` đo theo **gốc (origin) của body**, đúng định nghĩa đã chốt; với H1_2 gốc bàn chân nằm cao hơn mặt sàn nên con số +241,7 mm **không** đồng nghĩa "robot lơ lửng 24 cm" — muốn kết luận phải đo theo mesh/geom, việc đó ngoài phạm vi ticket này.
3. `joint_limit_violation_pct` 64,65 % cho thấy bài boxing đẩy nhiều khớp tới giới hạn — cũng là hiện tượng của motion, không phải của tốc độ.

Số thô: `results/v5_h1_quality.csv`.

## 5. Kết luận

- **Ba robot chính thức của V5 vẫn là `unitree_g1`, `booster_t1_29dof`, `engineai_pm01`** — không đổi.
- H1 (LAFAN1) bị chặn vì **thiếu cặp (định dạng × robot)**: không có `bvh_lafan1_to_h1.json`, README ghi TBD, và đường SMPL-X bị license.
- H1_2 **chạy được** ngay khi đổi sang BVH Xsens (`bvh_xsens_to_h1_2.json`) → chứng minh **robot họ H1 không phải nguyên nhân**; nguyên nhân là **cặp định dạng × robot**.
- Muốn đưa H1 vào so sánh ngang hàng với 3 robot kia thì cần **một motion chung** cho cả 4 robot: hoặc bổ sung `bvh_lafan1_to_h1(_2).json` (việc của Code, cần Review), hoặc có license SMPL-X để dùng chung nguồn AMASS.
