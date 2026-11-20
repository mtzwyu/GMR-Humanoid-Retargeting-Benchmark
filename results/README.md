# Kết quả thực nghiệm

CSV/PNG do tab `gmr-lab` sinh ra. Không sửa tay số liệu trong này.

| File | Nội dung |
|---|---|
| `v3_runtime.csv` | Thời gian retarget G1 trên `walk1_subject1.bvh` bằng `bvh_to_robot.py` **không** `--rate_limit`: 1 warm-up + 5 lần đo (cột `ms_per_frame_process` = wall-clock cả tiến trình / số frame) |
| `v5_sim2sim.csv` | Cùng 1 motion → nhiều robot, mức tụt chất lượng (thời gian chạy mỗi lần) |
| `v6_quality.csv` | 4 chỉ số **chất lượng ánh xạ** trên pkl V5 (foot slide, độ cao tâm thân thấp nhất + offset nghỉ, % frame xuyên sàn, % frame bão hòa khớp) |
