# GMR — HR-04 · Kế hoạch tổng quát

**Môn:** Nghiên cứu và kiểm chứng một công trình về robot hình người · Lớp 15DHTH07 · HK1 2026–2027
**Nhóm 01** — ĐH Công Thương TP.HCM · Nhóm trưởng: Trần Nguyễn Khánh Duy
**Đề tài HR-04:** GMR — ánh xạ chuyển động người sang robot hình người theo thời gian thực
**Repo:** https://github.com/YanjieZe/GMR · MuJoCo, CPU, MIT, 12 cấu hình robot
**Bài báo:** arXiv:2510.02252 *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking*
**Sim2sim:** mức 3 — cùng một chuyển động → ≥ 3 robot

---

## Nguyên tắc cốt lõi: không ai chờ ai

Chia theo **chức năng**, mỗi vai trò = 1 worktree = 1 branch = 1 tab agent.

1. **Đọc chéo tự do, ghi tuyệt đối không.** Ai cũng được đọc file trong worktree người khác; chỉ chủ worktree được ghi.
2. **Không ai chờ merge để làm việc.** Merge chỉ để nộp bài, không phải điều kiện thi hành.
3. **Không chia sẻ tài nguyên có thể tắc:** env, script, số liệu. Mỗi thứ có đúng một chủ.

### Worktree = chỗ ngồi, branch = nhiệm vụ

Git chỉ cho **một worktree check out một branch tại một thời điểm**. Vì vậy:

- **Worktree** cố định theo vai trò (chỗ ngồi, không đổi).
- **Branch** đặt theo **nhiệm vụ**, mỗi nhiệm vụ = 1 branch = 1 PR.
- Xong nhiệm vụ → mở PR → chuyển sang branch nhiệm vụ kế tiếp (`git switch -c task/... main`).
- Không đặt tên branch theo người hay theo agent.

| Worktree (cố định) | Vai trò | Chủ | Branch hiện tại |
|---|---|---|---|
| *(main worktree)* | Planner / merge | Duy | `main` |
| `gmr-research` | Research | Duy | `task/v1-tuyen-bo` |
| `gmr-code` | Code | Vỹ | `task/code-scripts` |
| `gmr-run` | Run | Mạnh | `task/v2-cai-dat` |
| `gmr-review` | Review | Trường | `task/review-qa` |
| `gmr-writing` | Writing (mở ngày 7) | cả nhóm | `task/v6-bao-cao` |

### Danh sách nhiệm vụ → branch

| Nhiệm vụ | Branch | Worktree | Người | PR vào `main` khi |
|---|---|---|---|---|
| V1 chốt tuyên bố + định nghĩa phép đo | `task/v1-tuyen-bo` | `gmr-research` | Duy | V1 xong |
| Mã nhóm: script đo + test | `task/code-scripts` | `gmr-code` | Vỹ | `--dry-run` + pytest pass |
| V2 cài đặt + nhật ký | `task/v2-cai-dat` | `gmr-run` | Mạnh | env chạy `--help` không lỗi |
| V3 đo thời gian xử lý | `task/v3-runtime` | `gmr-run` | Mạnh | có CSV ≥ 3 dòng |
| V5 sim2sim 3 robot | `task/v5-sim2sim` | `gmr-run` | Mạnh | có CSV ≥ 3 robot |
| V4 vì sao không huấn luyện | `task/v4-phan-tich` | `gmr-code` | Vỹ | có kết luận |
| Review + checklist | `task/review-qa` | `gmr-review` | Trường | liên tục |
| V6 báo cáo + slide | `task/v6-bao-cao` | `gmr-writing` | cả nhóm | đủ 8 mục |

## Ma trận phụ thuộc: rỗng

| Người | Cần gì từ người khác | Được chặn bởi |
|---|---|---|
| Duy | không | — |
| Mạnh | không | — |
| Vỹ | không | — |
| Trường | không (đọc file của Mạnh, không chờ merge) | — |

## Nguồn sự thật dùng chung (chỉ đọc)

`docs/dinh_nghia_phep_do.md` — Duy chốt ngày 1: đo đại lượng gì, đơn vị, lấy trung bình mấy lần, sai số chấp nhận. Ai cũng đọc, không ai sửa. Không có file này thì 4 người đo theo 4 cách, số không ghép được.

## Vòng công việc

```
Research ──> docs/v1_tuyen_bo.md
                  │ (ai cũng đọc được, không chờ)
Code ─────> scripts/ + patches/
Run ──────> logs/ + results/*.csv   ←── Review đọc trực tiếp worktree Run
                                          │
                                          └─ FAIL → Planner (ticket fix) → Code
Writing ──> report/  (mở ngày 7, ráp số cuối)
```

## Cửa merge

Duy merge theo lô, **2 lần/ngày: 12:00 và 21:00**. Ngoài giờ đó không ai phải chờ.

Thứ tự khi merge: Code → Run → **Review PASS** → Writing. Không merge cái chưa PASS (trừ tài liệu không phải bằng chứng).

## Trạng thái ticket

`todo` → `coding` → `running` → `review` → (`fix` → quay vòng) → `passed` → `merged` → `reported`

## Mẫu báo lỗi của Review (bắt buộc đủ 5 dòng)

```
TICKET:      V3-02
KẾT LUẬN:    FAIL
LÝ DO:       CSV có FPS nhưng không có cột lệnh tái lập
BẰNG CHỨNG:  results/v3_runtime.csv:1 (header thiếu "cmd")
             logs/run_v3_02.log:44
ĐỀ XUẤT:     Code thêm cột cmd; Run chạy lại 3 lần
MỨC:         CHẶN MERGE
```

Thiếu 1 trong 5 dòng → Planner trả lại Review, không chuyển Code.

## Ba cổng

| Cổng | Hạn | Điều kiện qua | Nếu không qua |
|---|---|---|---|
| **G1** | Ngày 3 | `conda run -n gmr python scripts/smplx_to_robot.py --help` không lỗi | Họp ngay, chuyển `bvh_to_robot.py` |
| **G2** | Ngày 7 | Có `results/v3_runtime.csv` + `results/v5_sim2sim.csv` do Review chấm PASS | Dồn điểm sang mục 3 (nhật ký tắc) |
| **G3** | Ngày 9 | Báo cáo đủ 8 mục, 0 lỗi CHẶN MERGE | Trường kiểm chéo, Duy chốt |

## Bằng chứng hình ảnh

Sản phẩm nộp cần "bằng chứng chạy được"; ảnh là bằng chứng rẻ nhất và không thể làm giả bằng lời.

- Lưu vào `results/figures/`, định dạng **PNG**, mỗi ảnh ≤ 1 MB (chụp đúng vùng, không chụp nguyên màn hình 4K).
- Tên tệp: `<nhiệm vụ>_<nội dung>_<yyyy-mm-dd>.png` — ví dụ `v3_runtime_g1_2026-11-21.png`.
- Mỗi ảnh phải có **1 dòng caption** trong `results/figures/README.md`: ảnh gì · lệnh nào sinh ra · ngày · người chụp.
- Bắt buộc có 4 loại:
  1. Ảnh terminal chạy lệnh đo (thấy rõ lệnh + thời gian)
  2. Ảnh kết quả render robot trong MuJoCo (nếu viewer chạy được)
  3. Đồ thị `ms_per_frame` theo robot/lần chạy
  4. Ảnh mở `results/*.csv` (bằng chứng số liệu tồn tại)
- Video demo: `.mp4` **không commit** (đã gitignore) — để ngoài repo và nộp kèm link.
- Ảnh phải do máy chạy ra, không dùng ảnh minh hoạ lấy từ repo gốc.

## Media cho slide

Ảnh và video dùng lại cho slide 13 phút — làm **ngay khi có kết quả**, không để cuối kỳ đi tìm.

**Video** (để xem lại và chèn slide):
- Lưu ở `results/media/`, `.mp4`, **không commit** (đã gitignore) — giữ local, nộp bằng link.
- Mỗi clip ≤ 60 giây, khung 16:9, quay đúng đoạn cao trào (không quay cả 164 giây).
- Bắt buộc có 3 clip: `v3_walk1_g1` (tư thế chuẩn) · `v3_walk4_g1` (clip khom — minh hoạ motion khó) · `v5_sim2sim_g1_t1_pm01` (cùng motion, 3 robot).
- Lệnh sinh video ghi vào `results/media/README.md` để tái tạo được.

**Ảnh trích từ video** (để chèn slide, commit được):
- Mỗi clip trích **3 khung hình** tại cùng frame index (ví dụ 25%, 50%, 75%) → `results/figures/`, PNG ≤ 1 MB.
- Đặt tên: `slide_<clip>_f<frame>.png`.
- Ảnh cần: 1 khung tư thế chuẩn, 1 khung clip khom (để so), 1 khung 3 robot cạnh nhau, 1 đồ thị `ms_per_frame`, 1 ảnh terminal có lệnh + thời gian.

`results/media/README.md` ghi bảng: tệp · pkl nguồn · lệnh sinh · thời lượng · frame index đã trích.

## Quy tắc cứng

1. `main` chỉ Planner merge. Không ai push thẳng, không ai chạy thử trên `main`.
2. **Chỉ Mạnh tạo/sửa conda env `gmr`.** Env là tài sản riêng của `gmr-run`; không ai khác cần env (Vỹ test `--dry-run`, Trường/Duy chỉ đọc).
3. Repo GMR clone vào `third_party/GMR` trong worktree của Mạnh, **không commit**.
4. Không bịa số. Cột “bài báo” và “nhóm đo được” tách bạch.
5. Luôn ghi `git rev-parse --short HEAD` của GMR và đọc `LICENSE` (MIT).
6. Commit nhỏ, message dạng `v3: đo runtime g1 lần 1`.

## Sáu bước khởi động

1. Thêm `third_party/` vào `.gitignore` (Planner)
2. Tạo `gmr-research` + tab Research
3. Tạo `gmr-code` + tab Code
4. Tạo `gmr-run` + tab Run
5. Tạo `gmr-review` + tab Review
6. Đóng tab `V2-V5 - GMR Lab` cũ (thao tác UI)

## Sản phẩm nộp

- Báo cáo 10–15 trang, 8 mục
- Slide 13 phút + 3 phút hỏi đáp
- Nhật ký cài đặt (file riêng)
- Bằng chứng: ảnh chụp / video / log
- Mã nhóm: script, cấu hình, `requirements.txt`
- Bảng phân công + tự thuật 3–5 dòng mỗi người
