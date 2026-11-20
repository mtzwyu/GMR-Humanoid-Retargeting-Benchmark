# Known Issues — GMR (Nhóm 01, HR-04)

Lỗi đang mở, có bằng chứng đo được. Mỗi mục: hiện tượng · bằng chứng · giả thuyết · người xử lý · trạng thái.

---

## KI-02 · Cột `cmd` trong CSV ghi một cờ chưa từng được truyền

**Mức độ: nghiêm trọng.** Đây là lỗi tính trung thực của số liệu, không phải lỗi kỹ thuật — phát hiện bởi Review, không phải bởi người làm ra nó.

**Hiện tượng.** `results/v3_runtime.csv` có 4 dòng `mode = rate_limit` với cột `cmd` chứa `--rate_limit`. Nhưng lệnh thật đã chạy **không có cờ đó**.

**Bằng chứng** (3 nguồn độc lập):
1. Mã: `third_party/_run/measure_v3.ps1:20,23` chỉ đưa cờ vào **chuỗi in ra CSV**; dòng `:26` gọi lệnh thật **không** kèm `$flag`.
2. Log của chính các lần đó: `Actual rendering FPS: 64,61 … 136,41`, tqdm `64,25 it/s` — một bộ giới hạn 30 Hz không thể cho 64 fps.
3. Chạy lại thư viện trong env `gmr`: `RateLimiter(frequency=30).sleep()` × **300 lần** → 46,68 ms/lần ≈ **21,4 Hz** (tổng 14,0 s cho 300 lần). Nếu cờ có tác dụng, một clip **7.840 frame** phải mất ≈ **366 s** (7.840 × 46,68 ms ≈ 370 s), thực tế chỉ **124–136 s**.

**Hệ quả.**
- Bốn dòng đó phải **xoá khỏi CSV**; kết luận "`--rate_limit` không ép 30 fps" trong PR #4 **không có bằng chứng** và phải rút.
- Bảng so sánh có/không `--rate_limit` trong báo cáo sẽ là **số bịa** nếu giữ lại.

**Cách xử lý.**
1. Xoá 4 dòng `rate_limit` khỏi `v3_runtime.csv`.
2. Ghi lại phát hiện đúng bản chất trong nhật ký: *"đo riêng thư viện `RateLimiter(30)` = 21,4 Hz trên Windows (hạt sleep ~15,6 ms) → cờ này không dùng để đo throughput"*, kèm lệnh đo.
3. Rà các CSV khác xem còn cột nào mô tả điều lệnh không làm.

**Bài học cho mục 3 và mục 7 của báo cáo.** Cột `cmd` là **hợp đồng tái lập**. Một dòng `cmd` sai làm cả bảng mất giá trị, và người phát hiện là người **không viết ra nó**. Đây là lý do phải tách vai Review.

**Người xử lý:** Mạnh (`gmr-run`)
**Trạng thái:** đang sửa


---

## KI-01 · Robot cúi gập người và di chuyển bất thường khi phát lại

**Hiện tượng.** Khi render `results/pkl/g1_walk4_no_rate_limit_1.pkl` trong MuJoCo (`g1_mocap`), robot gập người về trước, đầu cúi, hai tay buông trước bụng, chân khuỵu — trông như đang bò/chạy loạn.

**Bằng chứng đo trên pkl** (4.917 frame, 29 dof, fps 30):

| Đại lượng | Giá trị | Nhận xét |
|---|---|---|
| `waist_pitch` (dof 14) | trung bình **+29,5°**, std **1,7°** | Gần như hằng số → sai tư thế gốc, không phải nhiễu |
| `hip_pitch` (dof 0 và 6) | trung bình **−56°**, std 17° | Gập hông quá mức |
| `knee` (dof 3 và 9) | trung bình **+37° / +39°** | Khuỵu gối |
| `root z` | 0,584 – 0,819 m (trung bình 0,766) | Hạ thấp hơn tư thế đứng |
| Quaternion `root_rot` | dot min 0,998 · 0 frame bị lật dấu | Dữ liệu mượt, không nhiễu |
| Góc quay mỗi frame | trung bình 1,6° · max 7,0° | Không có cú giật |
| Nhảy vị trí mỗi frame | max 3,6 cm (≈1,08 m/s) | Hợp lý cho đi bộ |

→ **Kết luận sơ bộ:** dữ liệu không "loạn xạ"; nó là một tư thế gập **có hệ thống**. Lỗi nằm ở khâu retarget (hoặc tỉ lệ scale người→robot), không phải ở khâu phát lại.

**Giả thuyết, theo thứ tự ưu tiên:**
1. File `walk4_subject1.bvh` hoặc subject có rest pose khác với giả định của IK config → thử `dance1_subject2.bvh` mà repo đánh dấu `[x]` trong `TEST_MOTIONS.md`
2. `actual_human_height` / `human_scale_table` tính sai → in giá trị thật, so với chiều cao G1 ≈ 1,27 m
3. IK config của `unitree_g1` lệch → thử `booster_t1_29dof` để loại trừ
4. Viewer dùng XML khác với lúc retarget → so `g1_mocap_29dof.xml` với model của `RobotMotionViewer`

## KI-01 · KẾT LUẬN (đã tìm ra nguyên nhân)

Pipeline **không lỗi**. So sánh 3 motion qua cùng một pipeline, cùng robot `unitree_g1`, cùng HEAD `25f56db`:

| Motion | frames | `waist_pitch` | `hip_pitch` | `knee` | `root z` | Nhận xét |
|---|---|---|---|---|---|---|
| `walk4_subject1.bvh` (đang dùng) | 4.917 | **29,5° ± 1,7** | **−56°** | 37–39° | 0,766 | Gập hông quá mức, gối khuỵu, thân gập |
| `walk1_subject1.bvh` | 7.840 | 18,9° ± 6,0 | −11° | 27–29° | 0,781 | Đi bộ bình thường |
| `dance1_subject2.bvh` (repo đánh dấu `[x]`) | 3.944 | 18,6° ± 8,7 | −23° | 48–49° | 0,754 | Nhảy, gối gập nhiều là bình thường |

**Nguyên nhân:** `walk4_subject1.bvh` là clip **đi bộ khom lưng** của LAFAN1 (hông gập −56°, không phải tư thế đi thường). Retargeting tái hiện **trung thực** chuyển động đó — robot không sai, chỉ là replay đúng một clip khom.

Bằng chứng phụ: `waist_pitch` của walk4 gần như hằng số (std 1,7° so với 6,0° và 8,7° của hai clip kia) → tư thế cố định suốt clip, đúng đặc điểm clip khom lưng chứ không phải lỗi ngẫu nhiên.

**Cách sửa:** đổi motion đo chính thức sang `walk1_subject1.bvh`; đo lại V3 (3 lần) trên input mới; chụp lại ảnh render cùng frame index. `walk4` giữ lại làm ví dụ "motion khó" trong báo cáo nếu cần.

**Người xử lý:** Mạnh (`gmr-run`)
**Trạng thái:** đã xác định nguyên nhân, chờ chạy lại V3

**Ảnh hưởng tới báo cáo:** ghi rõ trong `results/v3_runtime.csv` là input đã đổi từ `walk4_subject1` sang `walk1_subject1`. Đây là nội dung tốt cho mục 3 (nhật ký) và mục 7 (vì sao chênh).

> Ghi chú: con số **7.839** xuất hiện trong phép so sánh V6 là do `bvh_to_robot.py` của repo có off-by-one (break trước khi append) nên baseline mất frame cuối; độ dài clip là **7.840 frame** như trong `results/v3_runtime.csv`.
