# Duy — Trần Nguyễn Khánh Duy (NT) · 2001230120

**Vai:** Planner + Research + Writing mục 1, 2, 7
**Worktree:** `main` (merge) · `gmr-research` (V1) · `gmr-writing` (báo cáo)
**Branch:** `task/v1-tuyen-bo` → `task/v6-bao-cao` (mỗi nhiệm vụ một branch, một PR)
**Nguyên tắc:** Planner không code. Duy tự sửa code thì mất người phản biện độc lập.

## Việc theo ngày

| Ngày | Việc | Worktree | Sản phẩm | Verify |
|---|---|---|---|---|
| 1 | Đọc arXiv:2510.02252; chốt 1 tuyên bố + viết định nghĩa phép đo | `gmr-research` | `docs/v1_tuyen_bo.md`, `docs/dinh_nghia_phep_do.md` | Câu chốt đúng dạng, mỗi số có số hiệu Bảng/Hình |
| 2 | Hoàn tất V1, ghi `docs/paper_notes.md` | `gmr-research` | ghi chú paper | Mỗi con số có nguồn trang/bảng |
| 3 | Mở 6 ticket GitHub, gán người | `main` | ticket | `gh issue list` ≥ 6 |
| 4–6 | Merge lô 2 lần/ngày, review PR | `main` | comment PASS/FAIL | Mỗi PR có ≥1 comment quyết định |
| 7–8 | Dựng `report/bao_cao.md` + viết mục 1, 2 | `gmr-writing` | báo cáo khung | `grep -c '^## '` = 8 |
| 9 | Viết mục 7 kết luận | `gmr-writing` | mục 7 | Đúng 1 trong 3: tái lập được / một phần / không |
| 10 | Slide 13 phút + tập bấm giờ | `gmr-writing` | `report/slides.md` | ≤ 13 phút |

## V1 — nội dung bắt buộc

- 3–5 tuyên bố ứng viên: đại lượng, đơn vị, giá trị gốc, số hiệu Bảng/Hình, điều kiện đo (robot, dataset, phần cứng).
- Chọn **đúng một** tuyên bố chính + lý do khả thi khi đo lại trên CPU với repo này.
- Cách đo lại: lệnh cụ thể, đầu ra, sai số chấp nhận.
- Rủi ro không tái lập: khác phần cứng / dataset / commit.

## `docs/dinh_nghia_phep_do.md` — nguồn sự thật chung

Phải có ngay ngày 1, gồm: đo đại lượng nào · đơn vị · lấy trung bình mấy lần (đề xuất 3) · bỏ lần chạy đầu (warm-up) · sai số chấp nhận · cách ghi `ms_per_frame` và `fps`. Ai cũng đọc, không ai sửa.

## Điều phối

- Merge theo lô 12:00 và 21:00, thứ tự Code → Run → Review PASS → Writing.
- Nhận báo lỗi Review → mở ticket `fix` → giao Code → chờ Review PASS → merge.
- Review thiếu 1 trong 5 dòng → trả lại Review, không chuyển Code.

## Ranh giới

- Được ghi: `README.md`, `.gitignore`, `docs/v1_tuyen_bo.md`, `docs/paper_notes.md`, `docs/dinh_nghia_phep_do.md`, `report/*`
- Không chạm: `logs/`, `results/`, `scripts/`
