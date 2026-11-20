# Đóng gói & nộp bài — checklist cuối

Dùng khi mọi PR đã merge. Mỗi mục có **cách kiểm** để không nộp nhầm bản cũ.

## 1. Trạng thái `main` phải sạch

```bash
git switch main && git pull --ff-only
git status --short          # phải rỗng
git log --oneline -5
```

## 2. Kiểm bản báo cáo trước khi in

| Kiểm | Cách |
|---|---|
| Đúng 15 trang | mở `report/bao_cao.pdf`, đếm trang |
| 8 mục đủ | mục lục trang 2 phải khớp nội dung |
| Không còn `CHỜ`/placeholder | `grep -c "CHỜ\|TODO\|XXX" report/bao_cao.md` → 0 |
| 5 hình hiện đúng | mở PDF, xem Hình 1–5 không bị cắt |
| 4 tự thuật đúng tên + % | mục 8.2, tổng = 100% |
| Số khớp nguồn | V3 17,3 ms · T1 13,0 · G1 16,8 · PM01 35,0 · foot_slide 49,0/83,1/118,4 |

**In 1 bản để đọc trên giấy** trước khi in nộp — lỗi ngắt trang và bảng tràn chỉ thấy khi cầm giấy.

## 3. Video: đưa lên GitHub Release

Video `.mp4` bị `.gitignore` nên phải nộp qua Release. Chạy tại worktree có file video (`gmr-run/results/media/`):

```bash
gh release create v1.0-demo \
  results/media/v3_walk1_g1.mp4 \
  results/media/v3_walk4_g1.mp4 \
  results/media/v5_sim2sim_g1_t1_pm01.mp4 \
  results/media/s1_human_input.mp4 \
  results/media/demo/demo_v6_720p.mp4 \
  --title "Giai đoạn 1 — video demo" \
  --notes "4 clip cảnh + 1 bản dựng 67 s. Tất cả 1280x720, 30 fps, không audio."
```

Sau đó **dán link Release vào báo cáo** (mục 6 hoặc phụ lục) và vào `README.md` mục Kết quả.

**Sao lưu kép:** copy cả 5 file vào 1 USB. Nếu mạng hội trường hỏng, vẫn demo được.

## 4. Slide

| Kiểm | Cách |
|---|---|
| 16 slide, 13:00 | mở `slides.pptx`, đếm slide; notes ghi tổng thời lượng |
| Không tràn chữ | đã QA bằng ảnh — nhưng **mở lại trên máy trình chiếu thật** |
| Font không bị thay | mở trên máy khác hoặc xuất PDF `slides.pdf` làm bản dự phòng |
| Có bản PDF | `report/slides.pdf` — dùng khi máy chiếu lỗi font |

**Chuẩn bị 3 bản:** `.pptx` (bản chính) · `.pdf` (dự phòng font) · USB.

## 5. Bộ hồ sơ nộp

| # | Thành phần | Ở đâu |
|---|---|---|
| 1 | Báo cáo PDF 15 trang | `report/bao_cao.pdf` |
| 2 | Slide `.pptx` + `.pdf` | `report/` |
| 3 | Nhật ký cài đặt | `logs/nhat_ky_cai_dat.md` (in ra hoặc PDF) |
| 4 | Bằng chứng chạy: ảnh + log | `results/figures/`, `results/logs/` |
| 5 | Video | GitHub Release + USB |
| 6 | Mã nhóm | `scripts/`, `tools/` (đã trong repo) |
| 7 | Bảng phân công + tự thuật | mục 8 báo cáo |
| 8 | Link repo | https://github.com/mtzwyu/GMR-Humanoid-Retargeting-Benchmark |

Nếu trường yêu cầu nộp qua LMS/Drive: nén `report/` + `logs/` + `results/figures/` thành 1 file zip (bỏ `.mp4`, `.pkl`), kèm file `LINK.txt` ghi link repo và link Release.

## 6. Trước giờ báo cáo 18:13

| Thời điểm | Việc |
|---|---|
| T-60 phút | Mở thử slide trên máy sẽ dùng, kiểm âm thanh (video không audio nên không cần loa) |
| T-30 phút | Chạy thử 1 lần đủ 13 phút, bấm giờ |
| T-15 phút | Copy báo cáo + slide + video sang USB, kiểm mở được |
| T-5 phút | Mở sẵn: slide, video, terminal có `results/` để trả lời "cho xem log" |

**Câu hội đồng chắc chắn hỏi** — chuẩn bị sẵn 1 câu trả lời 2 dòng cho mỗi câu:
1. Vì sao không tái lập được bảng của paper? → thiếu policy đã train + GPU + IsaacSim
2. Vì sao chọn đo "cả tiến trình" thay vì chỉ `retarget()`? → điều kiện đủ, bảo thủ
3. `foot_slide` 49 mm/s là tốt hay xấu? → chỉ so sánh tương đối, ngưỡng 50 mm/s đã đặt trước và G1 đạt sát
4. Sao không huấn luyện 3 hạt giống? → GMR không có training, không có seed
5. 12 robot trong README mà chỉ chạy 3? → 6 robot có config BVH, 3 chạy được trên LAFAN1, H1 bị chặn
6. Số 17,3 ms tin được không? → log `END` từng lần, hash pkl bất biến, 5 lần lặp CV 2,13%
7. Nếu có GPU thì làm gì tiếp? → chạy policy tracking của paper, đo success rate như Bảng I

## 7. Việc còn lại của con người

- [ ] 4 bạn đọc lại tự thuật, sửa câu không đúng với mình
- [ ] Chốt % đóng góp (hiện 30/30/20/20)
- [ ] Tập bấm giờ 13 phút, phân ai nói slide nào
- [ ] Tạo GitHub Release + copy USB
- [ ] In báo cáo, kiểm bản giấy
