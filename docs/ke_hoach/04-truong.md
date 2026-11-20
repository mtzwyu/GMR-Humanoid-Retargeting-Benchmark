# Trường — Hà Mạnh Trường · 2045240326

**Vai:** Review + Writing mục 6
**Worktree:** `gmr-review` (chính) · `gmr-writing` (mục 6)
**Branch:** `task/review-qa` (mỗi nhiệm vụ một branch, một PR)
**Quyền riêng:** chỉ được ghi `report/review_notes.md`. Đọc mọi thứ, sửa không gì.

## Việc theo ngày

| Ngày | Việc | Sản phẩm | Verify |
|---|---|---|---|
| 1 | Viết checklist review 5 điểm; chọn 3 robot + motion cho V5 (đọc README GMR) | `report/review_notes.md` | Đúng 5 mục; 3 robot có trong Supported Robots |
| 2 | Phản biện V1 của Duy (trong `gmr-research`) | nhận xét | Chỉ ra số nào thiếu nguồn |
| 3–4 | Review `docs/dinh_nghia_phep_do.md` + script của Vỹ | PASS/FAIL | Mỗi cái 1 dòng kết luận |
| 5–7 | Đọc trực tiếp CSV trong worktree `gmr-run` (không chờ merge) | PASS/FAIL V3, V5 | Đối chiếu ≥ 3 số ngẫu nhiên với log gốc |
| 8 | Viết mục 6 (sim2sim) | mục 6 | Bảng + 1 câu “robot nào tụt nhiều nhất, vì sao” |
| 9 | Kiểm chéo toàn bộ báo cáo | danh sách lỗi | 0 lỗi CHẶN MERGE |
| 10 | Chuẩn bị hỏi đáp 3 phút | 5 câu hỏi + đáp án | — |

## Checklist 5 điểm

| # | Kiểm | Câu hỏi |
|---|---|---|
| 1 | Bản quyền | Đã ghi `git rev-parse --short HEAD` của GMR và đọc `LICENSE`? |
| 2 | Tái lập | Mỗi dòng CSV có cột lệnh chạy lại được? |
| 3 | Tách bạch | Bảng kết quả có 2 cột riêng “bài báo” và “nhóm đo được”? |
| 4 | Trung thực | Số trong báo cáo có khớp log gốc (đối chiếu ≥ 3 số)? |
| 5 | Kết luận | Mục 7 có dứt khoát: tái lập được / một phần / không? |

## Mẫu báo lỗi (gửi Planner, không gửi thẳng Code)

```
TICKET:      V5-01
KẾT LUẬN:    FAIL
LÝ DO:       <một dòng>
BẰNG CHỨNG:  <file:dòng>, <log:dòng>
ĐỀ XUẤT:     <một dòng>
MỨC:         CHẶN MERGE | CHỈNH NHỎ
```

## Cách đọc không chờ merge

Mở trực tiếp `..\gmr-run\results\v3_runtime.csv` và `..\gmr-run\logs\`. Đọc thì tự do, ghi thì không. Kết quả review ghi vào `report/review_notes.md` của mình.

## Ranh giới

- Được ghi: `report/review_notes.md` (duy nhất)
- Không chạm: mọi file khác. Không sửa code, không sửa CSV, không sửa báo cáo.
- Không tự trả việc về Code — mọi lỗi đi qua Planner.
