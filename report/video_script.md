# VIDEO DEMO 90 GIÂY — PHỤ ĐỀ VÀ CARD CHỮ

**Nhóm 01 · HR04 · 15DHTH07 · HK1 2026–2027**
Nguồn kịch bản: `docs/ke_hoach/video_demo.md` (commit `05cd5da`).
Định dạng: 1280×720, H.264, **không audio**, 90 ± 2 giây; bản 540p để nhúng slide.
Quy ước phụ đề: **mỗi dòng ≤ 60 ký tự**, tiếng Việt có dấu, không viết tắt, chữ ≥ 36 px, dải dưới có nền mờ, không đè lên thân robot. Cảnh dài thì xuống tối đa 3 dòng, ngắt theo cụm nghĩa.

| Cảnh | Thời gian | Nội dung hình | Số dòng phụ đề |
|---|---|---|---|
| S0 | 0–5 s | Card tiêu đề | (card, không phụ đề) |
| S1 | 5–18 s | Chuyển động người đầu vào | 1 |
| S2 | 18–35 s | G1 retarget `v3_walk1_g1.mp4` | 2 |
| S3 | 35–50 s | Đối chứng walk4 (trái) / walk1 (phải) | 2 |
| S4 | 50–68 s | 3 robot `v5_sim2sim_g1_t1_pm01.mp4` | 2 |
| S5 | 68–82 s | Đồ thị nhiễu `v6_noise_vs_deviation.png` | 3 |
| S6 | 82–90 s | Card kết luận | (card, không phụ đề) |

---

## S1 — 5–18 s

```
Một clip chuyển động người: 7.840 frame, 261,3 giây
```

- 1 dòng, 51 ký tự.
- Ghi chú: nếu dùng ảnh tĩnh + pan (phương án b), giữ nguyên dòng này.

## S2 — 18–35 s

```
Retarget sang Unitree G1: 17,3 ms/frame
Nhanh hơn thời gian thực 2 lần
```

- Dòng 1: 39 ký tự · Dòng 2: 30 ký tự.
- Số chốt: 17,3 ms/frame (trung vị 17,272 của V3) và 2 lần (làm tròn từ 1,93).

## S3 — 35–50 s

```
Trái: clip gốc khom lưng (không phải lỗi retarget)
Phải: clip đi bộ chuẩn
```

- Dòng 1: 50 ký tự · Dòng 2: 22 ký tự.
- Bắt buộc: chữ "clip gốc" và "không phải lỗi retarget" phải hiện cùng lúc với cảnh trái, tránh bị hiểu là robot hỏng.

## S4 — 50–68 s

```
Cùng một chuyển động, 3 robot:
T1 13,0 · G1 17,0 · PM01 35,5 ms/frame
```

- Dòng 1: 30 ký tự · Dòng 2: 38 ký tự.
- Số chốt: trung vị `ms_per_frame_process` — T1 13,034 · G1 17,018 · PM01 35,454.

## S5 — 68–82 s

```
Nhiễu khớp 0,5 độ vẫn an toàn
2 độ đã hỏng 88 phần trăm frame
Trễ 1–5 frame vô hại
```

- Dòng 1: 29 · Dòng 2: 31 · Dòng 3: 20 ký tự.
- Số chốt: σ = 0,5° → 0,51 % frame vượt 5°; σ = 2° → 87,74 % (làm tròn 88 %); N2 (trễ 1–5 frame) có `dq_mean` 0,001°.
- Không đưa `dr_rmse` lên phụ đề; nếu người xem hỏi, trả lời theo báo cáo §6.4: đó là do quỹ đạo gốc bị scale, không phải sai tư thế.

## S6 — 82–90 s

```
Kết luận: tái lập một phần
Phần thời gian thực tái lập được
Số trong bảng của paper thì không
```

- Dòng 1: 26 · Dòng 2: 32 · Dòng 3: 33 ký tự.

---

## CARD S0 — 0–5 s

**Bố cục:** nền tối, tiêu đề lớn giữa khung, 4 dòng thông tin nhỏ dưới.

```
GMR — Ánh xạ chuyển động người
sang robot hình người theo thời gian thực

Nhóm 01 · HR04 · 15DHTH07
GMR commit 25f56db · Giấy phép MIT
```

- Dòng tiêu đề 1: 30 ký tự · dòng 2: 41 ký tự (font tiêu đề ≥ 48 px).
- Dòng thông tin: "Nhóm 01 · HR04 · 15DHTH07" (25) và "GMR commit 25f56db · Giấy phép MIT" (34), font ≥ 28 px.
- Có thể thêm logo trường ở góc trên trái; không thêm text khác để tránh rối trong 5 giây.

## CARD S6 — 82–90 s

**Bố cục:** 3 số lớn trên một hàng, dòng kết luận bên dưới.

```
17,3 ms          2×                3 robot
ms/frame         thời gian thực    sim2sim

TÁI LẬP MỘT PHẦN
```

- Ba số: `17,3 ms` (trung vị V3) · `2×` (1,93 làm tròn) · `3 robot` (G1, T1 29dof, PM01).
- Dòng kết luận "TÁI LẬP MỘT PHẦN" font ≥ 44 px, cùng màu nhấn với S0.
- Không thêm số khác lên card; chi tiết để trong báo cáo.

---

## Ghi chú dựng hình

- Phụ đề đặt ở dải dưới 20 % chiều cao, `box=1:boxcolor=black@0.55`, chừa 40 px an toàn hai bên.
- S3 dùng `hstack` hai clip 640×720; phụ đề đặt dưới **cả khung**, không đặt riêng từng bên.
- S5 dùng pan ảnh đồ thị (Ken Burns) để tránh cảnh tĩnh 14 giây; phụ đề hiện lần lượt theo 3 dòng.
- Chuyển cảnh `xfade` 0,4 s; tổng thời lượng kiểm bằng `ffprobe` phải 90 ± 2 s.
- Font: `C:\Windows\Fonts\segoeui.ttf`; nếu `drawtext` lỗi dấu tiếng Việt thì chuyển sang render phụ đề bằng PIL thành PNG trong suốt rồi overlay.

## Đối chiếu số trước khi render

| Số trên video | Nguồn | Giá trị gốc |
|---|---|---|
| 7.840 frame / 261,3 giây | header BVH `walk1_subject1` | 7.840 frame, 30 fps |
| 17,3 ms/frame | `results/v3_runtime.csv` — trung vị n = 5 | 17,272 ms |
| 2 lần | `33,333 / 17,272` | 1,93 (làm tròn 2) |
| T1 13,0 · G1 17,0 · PM01 35,5 | `results/v5_sim2sim.csv` — trung vị | 13,034 · 17,018 · 35,454 |
| 0,5 độ an toàn | `results/v6_noise_sweep.csv` N1 σ = 0,5 | 0,51 % frame > 5° |
| 2 độ hỏng 88 phần trăm | N1 σ = 2 | 87,74 % |
| Trễ 1–5 frame vô hại | N2 k = 1…5 | `dq_mean` 0,001° |

**Không được đổi số trên phụ đề/card nếu chưa đối chiếu lại bảng này.**
