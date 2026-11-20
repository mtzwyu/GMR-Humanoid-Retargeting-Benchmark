# GMR-Humanoid-Retargeting-Benchmark

Giai đoạn 1 — **Nghiên cứu và kiểm chứng một công trình về robot hình người**.
Lớp 15DHTH07 · HK1 2026–2027 · ĐH Công Thương TP.HCM · **Nhóm 01 · đề tài HR04**.

## Mục tiêu

Lấy một repo mã nguồn mở về humanoid, chạy được nó, và **kiểm chứng lại một tuyên bố định lượng** trong bài báo của chính repo đó. Toàn bộ trên mô phỏng, không cần robot thật.

## Sáu bước

| Bước | Việc | Sản phẩm |
|---|---|---|
| V1 | Chốt tuyên bố cần kiểm chứng (kèm số hiệu Bảng/Hình) | Câu phát biểu + con số gốc |
| V2 | Cài đặt theo đúng lệnh trong đề tài | `logs/nhat_ky_cai_dat.md` |
| V3 | Chạy mô hình có sẵn (**bắt buộc**) | Bảng đối chiếu bài báo vs nhóm đo |
| V4 | Tự huấn luyện cấu hình nhỏ, 3 hạt giống | Đường cong học + thời gian |
| V5 | Sim2sim (khối lượng ±20%, ma sát, trễ điều khiển) | Bảng tụt hiệu năng + đồ thị |
| V6 | Kết luận dứt khoát + trình bày | Báo cáo 10–15 trang, slide 13 phút, video |

## Cấu trúc

```
AGENTS.md                  # quy ước làm việc cho agent (kế thừa global CLAUDE.md)
.agents/skills/            # skills riêng của project
docs/huong_dan/            # PDF hướng dẫn, danh sách nhóm, đề tài HR04
docs/slide_bai_giang/      # slide môn Machine Learning (chỉ commit file .md)
docs/tai_lieu_tham_khao/   # sách tham khảo (giữ local)
report/                    # báo cáo giai đoạn 1
logs/                      # nhật ký cài đặt, log chạy
```

## Nộp bài

- Báo cáo 10–15 trang (8 mục theo hướng dẫn)
- Slide 13 phút + 3 phút hỏi đáp
- Nhật ký cài đặt (ghi trong lúc làm)
- Bằng chứng chạy được: ảnh chụp màn hình / video / file log
- Mã nhóm: script, file cấu hình đã sửa, `requirements.txt`
- Bảng phân công + tự thuật từng thành viên

## Lưu ý

`docs/.mat_khau_tai_lieu.local.md` và slide bài giảng dung lượng lớn **không** được commit (xem `.gitignore`).
