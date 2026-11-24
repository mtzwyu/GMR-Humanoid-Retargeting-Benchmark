# KỊCH BẢN SẢN XUẤT VIDEO DEMO — 77 GIÂY

**Nhóm 01 · HR04 · 15DHTH07 · HK1 2026–2027**

Đây là **nguồn duy nhất** để script dựng video đọc phụ đề và lời thuyết minh. Không sửa `report/video_script.md`; mọi thay đổi nội dung video làm ở file này.

| Thông số | Giá trị |
|---|---|
| Thời lượng | **77 giây** (0:00–1:17) |
| Khung hình | **1280×720**, 30 fps, H.264 |
| Âm thanh | **Lời thuyết minh tiếng Việt (voice-over), không nhạc nền** |
| Phụ đề | **Burn-in**; tối đa **2 dòng/cảnh**, mỗi dòng **≤ 60 ký tự**; chữ ≥ 36 px, dải dưới có nền mờ |
| Nguồn số liệu | `results/v3_runtime.csv` · `results/v5_sim2sim.csv` · `results/v6_noise_sweep.csv` · `results/v7_physics_perturb.csv` · `results/v7_gpu_check.csv` |
| Nguyên tắc số | **Mọi số đọc từ file, không viết tay.** Script lấy CSV → làm tròn theo quy ước dưới đây → điền phụ đề/lời đọc. |

**Quy ước làm tròn trên video:** ms và mm/s lấy **1 chữ số thập phân** (17,3 · 13,0 · 16,8 · 35,0); phần trăm lấy **1 chữ số** (87,7 %); `max|dq|` giữ dạng khoa học **1,5e-9 rad**; riêng câu “không đổi một byte” **chỉ dùng cho ma sát**, không dùng cho khối lượng.

**Quy ước thời gian:** timecode vào/ra tính bằng `phút:giây`; tổng 8 cảnh = **5 + 10 + 10 + 10 + 10 + 14 + 10 + 8 = 77 giây**. Lời đọc tối đa **2,1 từ/giây** (ước lượng); cảnh nào dài hơn thì cắt chữ ngay trong bảng này, **không tăng tốc quá 1,2×**. Đếm từ chỉ là ước lượng: phải **đo gTTS thật** vì số đọc chậm hơn chữ.

> **Cảnh báo tốc độ đọc:** ước lượng thực tế của gTTS tiếng Việt là **1,9–2,1 từ/giây**, không phải 2,6; mỗi cảnh phải **≤ 2,1 × số giây**. Đo gTTS thật (`lang='vi'`): `atempo` cao nhất **1,09×** (S1), mọi cảnh **≤ 1,2×**.

## Bảng cảnh

| Cảnh | Tên cảnh | Vào | Ra | Dài | Hình ảnh (mô tả + asset) | Phụ đề trên màn hình (≤ 2 dòng, ≤ 60 ký tự/dòng) | Lời thuyết minh (1–3 câu, đọc tự nhiên) | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| **S0** | Mở đầu | 0:00 | 0:05 | 5 s | Card tiêu đề nền tối: “GMR — Ánh xạ chuyển động người / sang robot hình người”; Nhóm 01 · HR04 · 15DHTH07; GMR commit `25f56db` · MIT. Asset: `cards/S0.png` (sinh bằng PIL trong `scripts/build_demo.py`). | *(card tiêu đề — không phụ đề)* | GMR: ánh xạ chuyển động người sang robot hình người. | 10 từ / 10,5 từ tối đa (5 s × 2,1). |
| **S1** | Đầu vào người | 0:05 | 0:15 | 10 s | Bộ xương người + trục khớp (đỏ/xanh), đi bộ trên sàn phẳng. Asset: `results/media/s1_human_input.mp4` (frame 300–599 của `walk1_subject1.bvh`). | Đầu vào: walk1_subject1.bvh — 7.840 frame<br>30 fps · 261,3 giây | Clip đi bộ LAFAN1: 7.840 frame, 261,3 giây — đầu vào duy nhất cho mọi phép đo. | 17 từ / 19 từ. gTTS đo **10,49 s**; target 9,60 s; `atempo` **1,09×**. Hai dòng phụ đề dài 41 và 19 ký tự. |
| **S2** | Retarget G1 + tốc độ | 0:15 | 0:25 | 10 s | G1 đi bộ nhìn thẳng, thấy rõ sải chân. Asset: `results/media/v3_walk1_g1.mp4`, từ giây 18 (tránh T-pose đầu clip). | G1: 17,3 ms/frame cả tiến trình (cận trên)<br>Nhanh hơn thời gian thực 1,92 lần | Retarget sang G1 mất 17,3 mili-giây mỗi frame, cả tiến trình, nhanh hơn thời gian thực 1,92 lần. | 18 từ / 21 từ. Số: V3 mean 17,349 ms; 33,333 / 17,349 = 1,92. Nếu còn thời gian: tính toán CPU ~2,4 ms; 17,3 ms gồm render GPU (`v7_gpu_check.csv`). |
| **S3** | Đối chứng walk4 / walk1 | 0:25 | 0:35 | 10 s | Ghép trái/phải: trái `results/media/v3_walk4_g1.mp4` từ 10 s (clip gốc khom lưng); phải `results/media/v3_walk1_g1.mp4` từ 18 s (tư thế chuẩn). | Trái: walk4 — clip gốc khom lưng, không phải lỗi<br>Phải: walk1 — tư thế chuẩn | Trái là walk4, clip gốc khom lưng của LAFAN1 — không phải lỗi retarget. Phải là walk1 chuẩn. | 18 từ / 21 từ. Bắt buộc chữ “clip gốc” và “không phải lỗi” hiện cùng lúc với nửa trái. |
| **S4** | 3 robot sim2sim | 0:35 | 0:45 | 10 s | Ba cột G1 · T1 · PM01, cùng chuyển động. Asset: `results/media/v5_sim2sim_g1_t1_pm01.mp4`, các đoạn 5 s / 25 s / 45 s. | T1 13,0 · G1 16,8 · PM01 35,0 ms/frame<br>Cùng motion, 3 robot — cả tiến trình | Ba robot: T1 mười ba, G1 mười sáu phẩy tám, PM01 ba mươi lăm. | 14 từ / 14 từ. gTTS đo **7,66 s**; target 9,60 s; `atempo` **1,00×**. Số: T1 13,0; G1 16,8; PM01 35,0 ms — đơn vị và “cả tiến trình” giữ ở phụ đề. |
| **S5** | Nhiễu N1–N4 | 0:45 | 0:59 | 14 s | Đồ thị 3 panel, pan nhẹ. Asset: `results/figures/v6_noise_slide.png` (fallback `results/figures/v6_noise_vs_deviation.png`). | 0,5° an toàn · 2° hỏng 87,7 % frame<br>Trễ 1–5 frame vô hại | Nhiễu khớp 0,5 độ vẫn an toàn. Tăng lên 2 độ, 87,7 phần trăm frame đã lệch quá 5 độ. Trễ 1 đến 5 frame thì vô hại. | 28 từ / 29,4 từ. Số: N1 σ = 0,5° → 0,51 % frame > 5°; σ = 2° → 87,74 %; N2 `dq_mean` = 0,001°. |
| **S5b** | Bảng V7 — tham số vật lý | 0:59 | 1:09 | 10 s | Bảng sinh bằng PIL từ `results/v7_physics_perturb.csv` + `results/v7_gpu_check.csv`: baseline / ma sát ×1,5 / khối lượng ×1,2 / ×0,8, kèm SHA256 rút gọn và `max dq`. Asset: `cards/S5b.png`. | Khối lượng ±20 %: lệch 1,5e-9 rad<br>Ma sát ×1,5: không đổi một byte | Đổi khối lượng ±20 % chỉ lệch một phẩy năm nano radian; đổi ma sát không đổi một byte. | 19 từ / 21 từ. Số: ma sát 72 geom → SHA256 trùng, `max dq = 0`; khối lượng 31 thẻ inertial → SHA256 khác, `max dq = 1,5e-9 rad` (`max dq` = max trị tuyệt đối của `dq`). “Một phẩy năm nano radian” = 1,5e-9 rad. Có thể thêm dòng GPU: tính toán CPU 2,359 ms; render GPU ~15 ms. |
| **S6** | Kết luận hai vế | 1:09 | 1:17 | 8 s | Card hai vế: “Tốc độ — tái lập được (17,3 ms · 1,92×)” và “Chất lượng ánh xạ — một phần (1/3 robot đạt `foot_slide`; T1 2,13 % frame)”. Asset: `cards/S6.png`. | Tốc độ: tái lập được (17,3 ms · 1,92×)<br>Chất lượng ánh xạ: một phần | Tốc độ tái lập được: 17,3 mili-giây, 1,92 lần; chất lượng ánh xạ một phần. | 15 từ / 16,8 từ. Theo DEC-04: **không** dùng một nhãn “tái lập một phần” cho tuyên bố chính. |

## Kiểm tra trước khi render

- [ ] **Timecode cộng đúng 77 giây:** 5 + 10 + 10 + 10 + 10 + 14 + 10 + 8 = 77; S6 kết thúc đúng 1:17.
- [ ] **Không cảnh nào thiếu asset:** S1–S4 dùng 4 clip trong `results/media/` (không commit, lấy từ release/máy Run); S5 dùng figure trong `results/figures/`; S5b đọc 2 CSV V7; S0/S6 sinh card trong `scripts/build_demo.py`.
- [ ] **Lời nói vừa khung:** từng cảnh ≤ **2,1 từ/giây** theo cột Ghi chú; sau khi sửa, `atempo` mỗi cảnh ≤ **1,2×**.
- [ ] **Số liệu khớp CSV:** 17,3 ms · 1,92 lần · 13,0 / 16,8 / 35,0 ms · 0,5° an toàn · 2° hỏng 87,7 % · trễ 1–5 frame vô hại · khối lượng ±20 % lệch 1,5e-9 rad · ma sát không đổi một byte — đối chiếu đủ 5 file nguồn.
