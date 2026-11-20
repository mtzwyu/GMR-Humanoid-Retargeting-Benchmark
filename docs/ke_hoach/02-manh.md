# Mạnh — Đặng Duy Mạnh · 2001240271

**Vai:** Run + Writing mục 3
**Worktree:** `gmr-run` (chính) · `gmr-writing` (mục 3)
**Branch:** `task/v2-cai-dat` → `task/v3-runtime` → `task/v5-sim2sim` (mỗi nhiệm vụ một branch, một PR)
**Quyền riêng:** chỉ Mạnh được tạo/sửa conda env `gmr`. Không ai khác cần env.

## Việc theo ngày

| Ngày | Việc | Sản phẩm | Verify |
|---|---|---|---|
| 1 | Clone GMR vào `third_party/GMR`, ghi `git rev-parse --short HEAD`, đọc `LICENSE`; cài 4 lệnh; ghi log **ngay khi lỗi** | `logs/nhat_ky_cai_dat.md` | ≥ 3 mục thực tế |
| 2 | Thử đường SMPL-X; nếu thiếu license → chuyển `bvh_to_robot.py` | 1 dòng quyết định trong log | Ghi rõ đường chạy được + vì sao |
| 3 | Chốt env, `pip freeze`; báo Planner | `requirements.txt` | **G1**: `conda run -n gmr python scripts/smplx_to_robot.py --help` không lỗi |
| 4–5 | Đo V3: chạy `--rate_limit` ≥ 3 lần, đo bằng `Measure-Command` (không cần script của Vỹ) | `results/v3_runtime.csv` | ≥ 3 dòng, có cột lệnh tái lập |
| 6–7 | V5 sim2sim: cùng 1 motion → G1, H1, T1 | `results/v5_sim2sim.csv` | ≥ 3 robot, mỗi robot 1 file log |
| 8 | Viết mục 3 từ log | mục 3 | Có lỗi + cách sửa |
| 9–10 | Quay video demo, chạy lại số nếu Review yêu cầu | `.mp4` ngoài repo | Phát lại được |

## Lệnh chính thức (theo README, đúng thứ tự)

```
conda create -n gmr python=3.10 -y
conda activate gmr
pip install -e .
conda install -c conda-forge libstdcxx-ng -y
```

```
python scripts/smplx_to_robot.py --smplx_file <path> --robot <robot_name> --save_path <out.pkl> --rate_limit
```

## Đo độc lập, không chờ script

```
Measure-Command { python scripts/smplx_to_robot.py --smplx_file <path> --robot g1 --save_path out.pkl --rate_limit }
```

Script `measure_runtime.py` của Vỹ là **sản phẩm nộp** (mã nhóm), không phải điều kiện để Mạnh chạy. Có thì dùng, chưa có thì vẫn đo được.

## Sản phẩm bắt buộc

- `logs/nhat_ky_cai_dat.md` — ghi trong lúc làm
- `logs/lenh_da_chay.md` — mọi lệnh tái lập được
- `requirements.txt` — từ `pip freeze` thực tế
- `results/v3_runtime.csv`, `results/v5_sim2sim.csv`
- `results/figures/*.png` + `results/figures/README.md` — ảnh bằng chứng theo quy ước trong `00-tong-quan.md`:
  1. terminal chạy lệnh đo · 2. render robot trong MuJoCo · 3. đồ thị `ms_per_frame` · 4. ảnh mở CSV

## Ranh giới

- Được ghi: `logs/*`, `results/*`, `requirements.txt`, `third_party/` (không commit)
- Không chạm: `scripts/`, `docs/`, `report/`
- Không phán đúng/sai — chỉ ghi số. Kết luận là của Review.
