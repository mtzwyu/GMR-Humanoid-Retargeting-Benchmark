# Quyết định (Decision log) — GMR · Nhóm 01 · HR-04

Ghi lại các quyết định ảnh hưởng tới kết luận của báo cáo, kèm lý do. Dùng cho mục 2 và mục 7.

---

## DEC-01 · Chọn phương án C cho tuyên bố cần kiểm chứng

**Ngày:** 2026-11-20 · **Người quyết:** Nhóm trưởng (Duy) · **Bối cảnh:** RV-08

**Vấn đề.** Paper arXiv:2510.02252 **không công bố bất kỳ con số ms/frame hay FPS nào**. Ba bảng định lượng của paper (I, II, III) đều là kết quả **policy đã huấn luyện**, cần GPU + IsaacSim + khoảng 84 policy — ngoài phạm vi giai đoạn 1 (chỉ chạy retargeting trên CPU, không huấn luyện).

Tuyên bố "real-time" vì thế lấy từ **README của repo**, không phải từ một bảng trong paper — trong khi yêu cầu môn học là "kiểm chứng tuyên bố định lượng **trong bài báo**".

**Ba phương án đã cân nhắc:**

| | Nội dung | Ưu | Nhược |
|---|---|---|---|
| A | Chỉ đo real-time, ghi rõ paper không nêu | Đo được thật, đúng tinh thần đề tài | Yếu về chữ "trong bài báo" |
| B | Chuyển sang C2 (Bảng II, `E_g-mpbpe = 104,1 mm`) | Đúng nghĩa "số trong bảng paper" | Kết luận gần như chắc chắn "không tái lập được", không đo được gì thêm |
| **C** | **Tuyên bố chính A + mục trình bày 3 bảng của paper và lý do không tái lập** | **Thoả cả hai vế, chi phí gần bằng A** | Báo cáo dài thêm ~1 trang |

**Quyết định: chọn C.**

**Hệ quả cụ thể:**
1. Tuyên bố chính: GMR retarget **theo thời gian thực trên CPU**. Ngưỡng `ms_per_frame ≤ 33,3 ms` là **ngưỡng nhóm tự đặt** theo LAFAN1 30 fps — **không phải** ngưỡng của paper. Phải ghi rõ điều này ở mục 2.
2. Thêm một mục trong `docs/v1_tuyen_bo.md`: trình bày Bảng I/II/III của paper, mỗi bảng ghi rõ cần gì để tái lập, và kết luận "ngoài phạm vi giai đoạn 1 vì thiếu policy đã train / GPU / IsaacSim".
3. Kết luận mục 7 dự kiến: **"tái lập một phần"** — phần thời gian thực tái lập được, phần số trong bảng của paper thì không.
4. Không được gọi clip `walk1_subject1.bvh` (7.840 frame = 261,3 s) là "Walk 1" của Bảng I — Bảng I ghi Walk 1 chỉ **33 giây**.

**Vì sao không chọn B.** B sẽ tốn công dựng IsaacSim + policy mà kết quả đã biết trước là thất bại, và không tạo ra số đo nào của nhóm. C vẫn cho một kết luận dứt khoát ("tái lập một phần") mà không cần GPU.

---

## DEC-02 · Sim2sim: chọn phương án C (mức 3 + phép thử nhiễu)

**Ngày:** 2026-11-21 · **Người quyết:** Nhóm trưởng (Duy) · **Bối cảnh:** mục 6.1 báo cáo

**Vấn đề.** Hướng dẫn môn mô tả sim2sim tối thiểu là đổi **tham số vật lý** (khối lượng khâu ±20%, ma sát, 1–3 bước trễ điều khiển) rồi vẽ hiệu năng theo mức nhiễu. Đề tài HR-04 lại chốt sim2sim **mức 3**: cùng một chuyển động → ≥ 3 robot. Nhóm đã làm mức 3, **chưa** làm phép thử nhiễu.

**Phân tích.** GMR là retargeting **động học dựa trên tối ưu** — không có physics, không có khối lượng/ma sát trong vòng tính. Đổi khối lượng ±20% **không làm đổi một byte** `.pkl` (đã chứng minh bằng SHA256 trùng trên 40 lần chạy). Vậy phép thử "nhiễu vật lý" **không áp dụng được**, không phải nhóm bỏ qua.

**Quyết định: C** — giữ mức 3, **và** bổ sung 4 phép thử nhiễu có tác dụng thật lên đầu vào: nhiễu khớp, trễ điều khiển, mất frame, lệch tỉ lệ người. Đặc tả chi tiết: `docs/v6_noise_spec.md`.

**Hệ quả:**
1. Mục 6 báo cáo có **hai** bảng: bảng tụt hiệu năng theo robot (mức 3) + bảng độ bền theo mức nhiễu.
2. Mục 6.1 phải viết rõ vì sao nhiễu vật lý không áp dụng — kèm dẫn chứng pkl bất biến, không được lấp bằng lời.
3. Phép thử nhiễu chạy **1 lần/mức** (đo độ lệch hệ thống, không đo thời gian) — phải ghi rõ để không bị coi là vi phạm hợp đồng 1+3.
