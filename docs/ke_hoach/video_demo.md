# Kế hoạch dựng video demo (V6 · sản phẩm nộp)

**Mục tiêu:** một video **90 giây**, tự giải thích được khi không có người thuyết minh, dùng cho 2 việc:
1. Chèn vào slide 13 phút (đoạn 2–3 phút nói về kết quả)
2. **Phương án dự phòng** nếu demo trực tiếp hỏng

## Ràng buộc kỹ thuật (đã kiểm tra trên máy)

| Hạng mục | Giá trị thực tế |
|---|---|
| ffmpeg | **9.0.2** tại `C:\Users\xpaga\miniconda3\envs\gmr\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe` (không có trong PATH) |
| ⚠️ Lưu ý ffmpeg 9 | **Bỏ `-vsync`**, thay bằng `-fps_mode`; `-update 1` bắt buộc khi xuất 1 khung |
| Font cho `drawtext` | `C:\Windows\Fonts\segoeui.ttf`, `arial.ttf` (có sẵn) |
| PIL (tạo card) | 12.3.0 trong env `gmr` |
| matplotlib (đồ thị) | 3.11.2 trong Python base — env `gmr` **không có** |
| Clip gốc | 3 file 1280×720, 30 fps, đúng 60,00 s, 5,4–7,1 MB |
| Ảnh | 23 PNG trong `results/figures/` |

**Định dạng xuất:**
- `demo_90s_720p.mp4` — H.264, 1280×720, **không audio** (`-an`), mục tiêu ≤ 25 MB → bản nộp
- `demo_90s_540p.mp4` — bản nhẹ ≤ 8 MB để nhúng slide

## Kịch bản 6 cảnh (90 giây)

| # | Thời gian | Nội dung | Nguồn asset | Trạng thái |
|---|---|---|---|---|
| **S0** | 0–5 s | Card tiêu đề: tên đề tài · nhóm 01 HR-04 · GMR `25f56db` · MIT | Card PNG tự tạo | cần tạo |
| **S1** | 5–18 s | Chuyển động người đầu vào: 1 clip LAFAN1, 7.840 frame, 261,3 s | Clip "human" mới **hoặc** ảnh tĩnh + pan | **thiếu** |
| **S2** | 18–35 s | Retarget → G1, phụ đề: `17,3 ms/frame · nhanh hơn 2× thời gian thực` | `v3_walk1_g1.mp4` (cắt 10 s đẹp) | có |
| **S3** | 35–50 s | **Đối chứng KI-01**: trái = walk4 (khom, clip gốc), phải = walk1 (chuẩn) | `v3_walk4_g1` + `v3_walk1_g1` ghép cạnh nhau | có |
| **S4** | 50–68 s | Sim2sim 3 robot, phụ đề số ms từng con: T1 13,0 · G1 17,0 · PM01 35,5 | `v5_sim2sim_g1_t1_pm01.mp4` | có |
| **S5** | 68–82 s | Độ bền: nhiễu σ 0,5→5°, trễ 1–5 frame (đồ thị động hoặc pan ảnh) | `v6_noise_vs_deviation.png` | có (chờ merge PR 8) |
| **S6** | 82–90 s | Card kết luận: "tái lập một phần" + 3 số chốt | Card PNG | cần tạo |

**Nguyên tắc phụ đề:** mỗi cảnh **tối đa 1 dòng**, chữ ≥ 36 px, đặt ở dải dưới có nền mờ — người xem điện thoại vẫn đọc được. Không đặt chữ đè lên thân robot.

## Thiếu 1 asset: clip "chuyển động người"

Hiện chỉ có clip robot. Cần ~10 s cho thấy **đầu vào là người**, để người xem hiểu đây là bài toán ánh xạ.

Hai cách:
- **(a)** Quay thêm bằng viewer của GMR (có vẽ điểm khớp người, `human_point_scale=0.1`) — đúng bản chất nhất, ~15 phút
- **(b)** Dùng ảnh `results/figures/fix_dance1_*.png` + hiệu ứng pan/zoom (Ken Burns) — không cần quay, kém trực quan hơn

Chọn **(a)** nếu Run còn thời gian, (b) là dự phòng.

## Cách dựng

```
scripts/build_demo.py            # sinh card PNG + đồ thị, gọi ffmpeg
results/figures/demo_cards/      # S0.png, S1.png, S6.png (commit)
results/media/demo/              # mp4 trung gian + bản cuối (không commit)
```

Pipeline mỗi cảnh:
1. Cắt clip: `-ss <t> -t <dài>` (cắt sau `-i` để chính xác frame)
2. Ghép cạnh nhau (S3): `hstack` sau khi scale về 640×720 mỗi bên
3. Overlay phụ đề: `drawtext` với `fontfile` escape `C\:/Windows/Fonts/segoeui.ttf`, kèm `box=1:boxcolor=black@0.55`
4. Chuyển cảnh: `xfade` 0,4 s (ffmpeg 9 hỗ trợ)
5. Kết xuất: `-c:v libx264 -pix_fmt yuv420p -crf 23 -fps_mode cfr -an`

**Vì sao re-encode toàn bộ thay vì `-c copy`:** các cảnh khác độ phân giải/thời lượng và có overlay → copy không được. Chấp nhận mất ~1 phút render.

## Phân công

| Ai | Việc | Thời lượng |
|---|---|---|
| **Run** | Quay clip S1 (người) 10 s; cắt sẵn 3 đoạn đẹp 10 s cho S2/S3/S4 (ghi rõ timecode đã cắt) | 40 phút |
| **Code** | Viết `scripts/build_demo.py` + card PNG (PIL), chạy ffmpeg, xuất 2 bản | 60 phút |
| **Writing** | Viết 6 dòng phụ đề + card chữ S0/S6 (tiếng Việt, không dấu nếu font lỗi) | 20 phút |
| **Review** | Xem 1 lượt, kiểm phụ đề không che robot, số trên phụ đề khớp CSV | 15 phút |

## Checklist nghiệm thu

- [ ] `ffprobe` báo duration **90 ± 2 s**, 1280×720, h264, **không audio**
- [ ] Bản 720p ≤ 25 MB, bản 540p ≤ 8 MB
- [ ] Số trên phụ đề khớp `results/v3_runtime.csv` và `results/v5_sim2sim.csv` (17,3 · 13,0 · 17,0 · 35,5)
- [ ] Phụ đề không che thân robot ở cả 6 cảnh
- [ ] Cảnh S3 nói rõ **trái là clip gốc khom lưng**, không phải lỗi retarget
- [ ] Xem hết 1 lượt trên máy khác (hoặc điện thoại) — không giật, không lệch tiếng
- [ ] Có thumbnail PNG 1280×720 để làm ảnh bìa slide
- [ ] File cuối **copy ra ngoài repo** + 1 USB (dự phòng demo trực tiếp hỏng)

## Rủi ro và cách chặn

| Rủi ro | Chặn bằng |
|---|---|
| ffmpeg 9 từ chối option cũ (`-vsync`) | Dùng `-fps_mode cfr`; đã ghi trong script |
| `drawtext` lỗi vì đường dẫn `C:` | Escape `C\:/Windows/Fonts/...`; test 1 cảnh trước khi render hết |
| Cắt clip rơi vào đoạn robot đứng yên | Run chọn timecode có tư thế rõ, ghi vào manifest |
| Video quá nặng để nhúng slide | Xuất thêm bản 540p, chỉ nhúng bản nhẹ |
| Máy chiếu không có audio | Video **không audio** ngay từ đầu → không phụ thuộc loa |

## Thời lượng thực hiện

| Bước | Thời gian |
|---|---|
| Quay clip S1 + chọn timecode | 40 phút |
| Viết script + card | 60 phút |
| Render + sửa | 40 phút |
| Review + xuất bản cuối | 20 phút |
| **Tổng** | **~2,5 giờ** |
