# SLIDE 13 PHÚT — GMR: KIỂM CHỨNG TUYÊN BỐ "REAL-TIME ON CPU"

**Nhóm 01 · HR-04 · 15DHTH07 · HK1 2026–2027**
Khung trình bày theo `slides` skill (chiến lược *Case Study* + nhịp Duarte *What Is → What Could Be*), 1 ý / slide, 1 slide ≈ 1 phút.
**Tổng: 13:00 · hỏi đáp: 3:00.** Số chi tiết để trong báo cáo; trên slide chỉ giữ số headline.

| Hạng mục | Quy ước |
|---|---|
| Khung | 16:9 (1280×720 hoặc 1920×1080) |
| Font | tiêu đề ≥ 32 pt, thân ≥ 24 pt, số liệu ≥ 40 pt |
| Màu | nền tối, 1 màu nhấn; đỏ chỉ dùng cho "vượt ngưỡng" |
| Ảnh | dùng `results/figures/*.png`, mỗi ảnh ≤ 1 MB |
| Video | 3 clip 60 s trong `results/media/` (không commit) — phát từ ổ ngoài |
| Dự phòng | nếu video lỗi: dùng bộ 3 khung `slide_*_f450/900/1350.png` |

---

## Bảng thời lượng

| # | Slide | Bắt đầu | Dài | Người |
|---|---|---|---|---|
| 1 | Bìa | 0:00 | 0:20 | Duy |
| 2 | Hook: một câu của repo | 0:20 | 0:40 | Duy |
| 3 | Bài toán retargeting | 1:00 | 1:00 | Duy |
| 4 | Paper làm gì (4 nguồn, 84 policy) | 2:00 | 1:00 | Duy |
| 5 | Nghịch lý: paper không có số tốc độ | 3:00 | 0:50 | Duy |
| 6 | Tuyên bố + ngưỡng 33,33 ms | 3:50 | 0:40 | Duy |
| 7 | Cài đặt: 7 sự cố, 1 quyết định | 4:30 | 1:10 | Mạnh |
| 8 | Đo cái gì: process vs retarget | 5:40 | 0:50 | Mạnh |
| 9 | Kết quả V3 | 6:30 | 0:50 | Mạnh |
| 10 | Bắc cầu: được kết luận gì | 7:20 | 0:40 | Duy |
| 11 | Sim2sim 3 robot | 8:00 | 1:00 | Trường |
| 12 | Vì sao PM01 chậm | 9:00 | 0:30 | Trường |
| 13 | Nhiễu vật lý không áp dụng → N1–N4 | 9:30 | 1:00 | Trương Thái Vỹ + Hà Mạnh Trường |
| 14 | Kết luận: tái lập một phần | 10:30 | 0:50 | Duy |
| 15 | Ba bài học + việc còn mở | 11:20 | 0:40 | Duy |
| 16 | Cầu nối Q&A | 12:00 | 1:00 | cả nhóm |

---

## 1. Bìa — 0:20

**Thông điệp:** một repo, một tuyên bố, một phép đo.

- Tiêu đề: *GMR — kiểm chứng "real-time on CPU"*
- Phụ: Nhóm 01 · HR-04 · 15DHTH07 · repo `YanjieZe/GMR` @ `25f56db` · MIT
- Ảnh nền mờ: `slide_v3_walk1_g1_f900.png`

**Lời:** "Nhóm em kiểm chứng một tuyên bố của repo GMR: retarget chuyển động người sang robot hình người theo thời gian thực, trên CPU."

---

## 2. Hook — 0:40

**Thông điệp:** tuyên bố nằm ở README, không nằm trong bài báo — và đó là chỗ bắt đầu.

- Trích nguyên văn: *"Retarget human motions into diverse humanoid robots in real time on CPU"*
- Ảnh robot G1 đang chạy (`v3_render_mujoco_g1_2026-11-20.png`)
- Câu dẫn: "Bài báo 9 trang — nhưng không có một con số ms/frame nào."

**Lời:** nêu mâu thuẫn, không giải thích vội; để slide 5 trả lời.

---

## 3. Bài toán — 1:00

**Thông điệp:** retargeting là bài toán ánh xạ hình thái, không phải copy góc khớp.

- Sơ đồ 3 khối: người (mocap) → **retargeting** → robot (qpos)
- Ba tầng khó: embodiment gap · ràng buộc vật lý (sàn/tự cắt/giật) · thời gian thực
- Số nhấn: người ↔ G1 29 DoF; ngân sách **33,33 ms/frame** ở 30 fps

**Lời:** nhấn "33,33 ms là ngân sách của dữ liệu nguồn, không phải ngưỡng của paper".

---

## 4. Paper làm gì — 1:00

**Thông điệp:** paper không so retargeter bằng mắt, mà bằng policy phía sau.

- 4 nguồn: GMR · PHC · ProtoMotions · Unitree (closed)
- Cùng 21 clip LAFAN1, cùng G1, train BeyondMimic
- 21 × 4 = **84 policy**; 100 / 4096 / 100 rollout
- 3 bảng: success rate · tracking error · start frame

**Lời:** "Đây là lý do ba bảng của paper nằm ngoài phạm vi — không phải thiếu GPU, mà thiếu cả 84 policy và môi trường."

---

## 5. Nghịch lý — 0:50

**Thông điệp:** muốn "kiểm chứng bài báo" nhưng bài báo không có số tốc độ → phương án C.

- Bảng 3 dòng A / B / **C** (chỉ nêu ưu–nhược 1 dòng mỗi ô)
- C = đo real-time (tuyên bố repo) **+** trình bày 3 bảng paper và lý do không tái lập
- Ghi chú: "không gọi clip 261,3 s là Walk 1 của Bảng I (33 s)"

**Lời:** thừa nhận điểm yếu trước khi bị hỏi; đây là slide "what is".

---

## 6. Tuyên bố + ngưỡng — 0:40

**Thông điệp:** một câu chốt, một ngưỡng đặt trước, một cách đọc duy nhất.

- Câu chốt (rút gọn 2 dòng)
- `ms_per_frame ≤ 33,33 ms` ⇔ `fps_out ≥ 30` ⇔ `realtime_factor ≥ 1,00`
- Ba nhãn: ≥1,00 tái lập được · 0,80–0,99 một phần · <0,80 không

**Lời:** "Ngưỡng chốt trước, không đổi sau khi thấy số."

---

## 7. Cài đặt — 1:10

**Thông điệp:** bảy sự cố, nhưng chỉ một quyết định thay đổi toàn bộ đường đo.

- Timeline 7 chấm: proxsuite · libstdcxx · **SMPL-X license** · KI-01 · KI-02 · RV-14 · hai đợt lệch 14 %
- Quyết định lớn: bỏ SMPL-X → **BVH LAFAN1** (công khai), H1 bị chặn
- Ảnh: `slide_v3_walk4_g1_f900.png` (KI-01 — clip khom lưng) cạnh `slide_v3_walk1_g1_f900.png`

**Lời (Mạnh):** kể 1 sự cố có bài học — KI-02: cột `cmd` ghi cờ chưa từng truyền; người phát hiện là Review.

---

## 8. Đo cái gì — 0:50

**Thông điệp:** script chạy retarget và render chung một vòng lặp, nên phải tách hai đại lượng.

- Sơ đồ: `ms_per_frame` (chỉ `retarget()`) vs `ms_per_frame_process` (cả tiến trình)
- Giai đoạn 1: **chỉ có `_process`**, bản đo cũ 13 cột
- Cấm: dùng `Actual rendering FPS`; cấm nhân hệ số 0,92
- Ngưỡng áp cho `ms_per_frame`; thiếu số → dùng bảng bắc cầu

**Lời:** "Đây là chỗ dễ tự lừa mình nhất — đo cả tiến trình rồi gọi là retarget."

---

## 9. Kết quả V3 — 0:50

**Thông điệp:** 5 lần đo, tất cả dưới ngưỡng, độ tản mát thấp.

- Số lớn: **17,349 ms** (trung bình, n = 5) · CV **2,13 %** · 1,92× · **57,6 FPS**
- Mốc repo (Speed Benchmark): 35–45 FPS (i9-13900K) · 60–70 FPS (Threadripper) — README không nêu điều kiện
- Tính toán CPU, render GPU: headless **2,36 ms**; **17,349 ms là cả tiến trình có viewer**
- Đồ thị: `v3_ms_per_frame_g1_2026-11-20.png` (đường 33,33 ms)
- Bảng nhỏ 5 điểm: 17,522 · 17,246 · 17,852 · 16,853 · 17,272
- Ghi chú: bỏ warm-up; cả 5 giá trị đều < 20 ms

**Lời:** "Con số không sát ngưỡng — nên kết luận không phụ thuộc chọn mean hay median."

---

## 10. Bắc cầu — 0:40

**Thông điệp:** `process ≤ 33,33` là điều kiện **đủ**, không phải suy diễn.

- Bất đẳng thức: `retarget ≤ process = 17,349 ≤ 33,33`
- Kết luận: tái lập được **ở mức cả tiến trình**
- Không được nói: "vòng lặp retarget đạt real-time" (không đo)
- Sai số giữa hai phiên ≈ 14 % → báo 17,3 ms, không 17,35

**Lời:** vẽ bất đẳng thức bằng tay; đây là slide ăn điểm phương pháp.

---

## 11. Sim2sim 3 robot — 1:00

**Thông điệp:** cùng motion, đổi robot, không huấn luyện lại — 2/3 robot vẫn dưới ngưỡng.

- 3 ảnh cùng frame 2000: G1 · T1 · PM01 (`v5_sim2sim_*_frame2000`)
- Bảng 3 dòng: 16,758 (1,99) · 13,034 (2,56) · **34,975 (0,95)**
- H1: bị chặn — exit 2 `invalid choice`, không có config BVH, README TBD
- Đồ thị: `v5_ms_per_frame_robots_2026-11-20.png`

**Lời (Trường):** "PM01 vượt ngưỡng, nhưng chưa được gọi là 'không real-time' — xem slide sau."

---

## 12. Vì sao PM01 chậm — 0:30

**Thông điệp:** ít khớp nhất mà chậm nhất → số DoF không giải thích được.

- 24 DoF / 34,975 ms (mean) vs 27 DoF / 13,034 ms (median); so cùng mean thì chậm 2,8× T1
- Ba giả thuyết: cấu hình IK · số vòng lặp solver · mô hình nặng
- Nhãn đỏ: "**giả thuyết**, chưa tách nguyên nhân"

**Lời:** nói rõ đã kiểm soát thermal (PM01 chạy đầu, 51–57 °C).

---

## 13. Nhiễu: tham số vật lý gần như không vào vòng tính — 1:00

**Thông điệp:** ma sát ×1,5 trùng hash tuyệt đối; khối lượng ±20 % chỉ lệch 1,5e-9 rad — bảng "tụt theo mức" vẫn là bảng giả.

- GMR = tối ưu động học, mass/friction gần như không vào vòng tính
- V7: ma sát ×1,5 (72 geom) → SHA256 trùng, `max|dq| = 0`
- V7: khối lượng ±20 % (31 body) → SHA256 khác, `max|dq| = 1,5e-9 rad`
- Thay bằng N1–N4: nhiễu khớp · trễ · mất frame · lệch tỉ lệ người (15 mức × 1 lần)
- Kết quả headline: N2/N3 vô hại · N1 hỏng từ **2°** · N4 hỏng từ **±10 %**, giãn nặng hơn co
- Cảnh báo trên slide: `dr_rmse` 719 mm của N4 là **scale quỹ đạo**, không phải sai tư thế

**Lời (Vỹ + Trường):** Vỹ nói vì sao phép thử ±20 % khối lượng không có tác dụng; Trường nói kết quả N1–N4. "Nhóm không lấp bằng một bảng đẹp; nhóm thay bằng phép thử có tác dụng thật — và nói rõ chỉ số nào không được đọc sai."

---

## 14. Kết luận — 0:50

**Thông điệp:** **tách hai vế** — tốc độ **tái lập được** trên CPU; chất lượng ánh xạ chỉ **một phần**.

- Vế tốc độ: 17,349 ms · 1,92× · 2/3 robot dưới ngưỡng — **tái lập được** (tiêu chí đặt trước)
- Vế chất lượng: 1/3 robot đạt `foot_slide ≤ 50 mm/s`; T1 xuyên sàn 2,13 % frame — **một phần**
- Ngoài phạm vi: Bảng I/II/III — 84 policy, IsaacSim, ROS, không có cấu hình trong paper
- Một câu: "Tốc độ đạt ngưỡng nhóm đặt; chất lượng ánh xạ một phần; bảng paper không tái lập."

**Lời:** nói chậm, rõ; đây là slide hội đồng sẽ hỏi.

---

## 15. Ba bài học + việc còn mở — 0:40

**Thông điệp:** giá trị nằm ở quy trình, không chỉ ở con số.

- 1: **tách vai Review** — RV-13 phát hiện cờ giả
- 2: **số phải tự truy vết** — dòng `END` trong từng log
- 3: **bất biến đầu ra** — SHA256 chứng minh chênh do máy
- Còn mở: kết quả nhiễu · `min_body_height`/`foot_slide` · `ms_per_frame`

---

## 16. Cầu nối Q&A — 1:00

**Thông điệp:** mời hỏi, và chủ động đưa 1 câu mình muốn được hỏi.

- 3 ảnh: walk1 (chuẩn) · walk4 (khom) · 3 robot — "đây là toàn bộ demo"
- Câu mời: "Nhóm sẵn sàng giải thích vì sao không đo `ms_per_frame` và vì sao không train 3 seed."
- Chuẩn bị chuyển sang phần hỏi đáp 3 phút

---

## Q&A 3 phút — 7 câu đã chuẩn bị

| # | Câu hỏi dễ bị hỏi | Trả lời ngắn (1 hơi) |
|---|---|---|
| 1 | Sao không đo `ms_per_frame`? | Bản đo cũ chỉ có `_process` (13 cột); script mới có probe nhưng Planner chốt không chạy lại. `process ≤ 33,33` là điều kiện **đủ**, nên kết luận vẫn đứng. |
| 2 | Sao không train 3 seed? | GMR không huấn luyện — không có trọng số/seed. Policy BeyondMimic cần IsaacSim + GPU + 84 policy. Nhóm thay bằng 3 cấu hình (số V5) và ghi rõ. |
| 3 | PM01 chậm vì ít khớp? | Ngược lại: 34,975 ms (mean) vs 13,034 ms (median); so cùng mean thì chậm 2,8× T1 27 DoF. Số khớp không giải thích; ba giả thuyết IK/solver/model, chưa tách. |
| 4 | Sim2sim không đúng "nhiễu vật lý"? | Ma sát ×1,5 trùng SHA256 tuyệt đối (`max\|dq\| = 0`); khối lượng ±20 % đổi hash nhưng `max\|dq\| = 1,5e-9 rad` — chuyển động không đổi. Bảng ±20 % vẫn là bảng giả; nhóm thay bằng N1–N4. |
| 5 | Hai đợt lệch 14 %, số nào tin? | pkl giống nhau từng byte → chênh do trạng thái máy. Chọn đợt chậm hơn (bảo thủ), báo 17,3 ms kèm sai số giữa phiên. |
| 6 | So với paper thế nào? | Paper không công bố ms/FPS/hardware; chỉ so được với ngưỡng nhóm đặt. Không có tỉ lệ "nhanh hơn paper". |
| 7 | Nhiễu trễ có 36° ở frame 0 — có phải lỗi tích lũy? | Không. Đó là **1 frame biên**: IK khởi tạo từ nghiệm frame trước nên phụ thuộc warm start; lệch tắt dần 0,31 → 0,10 → 0,05 → 0,02°. `dq_mean` toàn clip = 0,001°. |

---

## Checklist trước khi bấm giờ

- [ ] Xuất PDF + bản PPTX dự phòng; nhúng font
- [ ] Ảnh đã copy sang máy trình chiếu (không phụ thuộc đường dẫn worktree)
- [ ] 3 video 60 s mở sẵn, đã thử loa/màn hình
- [ ] Tập 2 lần: lần 1 bấm giờ từng slide, lần 2 bỏ slide nào vượt
- [ ] Chốt người nói từng slide theo bảng thời lượng
- [ ] In 1 bản Q&A 7 câu cho cả nhóm
