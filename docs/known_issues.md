# Known Issues — GMR (Nhóm 01, HR-04)

Lỗi đang mở, có bằng chứng đo được. Mỗi mục: hiện tượng · bằng chứng · giả thuyết · người xử lý · trạng thái.

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

**Người xử lý:** Mạnh (`gmr-run`)
**Trạng thái:** đang sửa ([dispatch `msg_7a35d2367ee5`](docs/ke_hoach/00-tong-quan.md))

**Ảnh hưởng tới báo cáo:** nếu phải đổi motion input thì V3 phải đo lại 3 lần trên input mới; ghi rõ trong `results/v3_runtime.csv` là input đã đổi. Đây vẫn là nội dung tốt cho mục 3 (nhật ký) và mục 7 (vì sao chênh).
