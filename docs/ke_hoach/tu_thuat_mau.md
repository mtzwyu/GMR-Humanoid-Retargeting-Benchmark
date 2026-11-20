# Mẫu tự thuật cá nhân (mục 8 báo cáo)

Hướng dẫn môn yêu cầu **"bảng phân công và tự thuật 3–5 dòng của từng thành viên"**. Đây là 33% điểm G3, và là phần duy nhất máy không viết thay được.

## Quy định khi viết

1. **Ngôi thứ nhất**, 3–5 dòng, không viết chung chung kiểu "đã tham gia cùng nhóm".
2. Mỗi bài phải có **việc cụ thể** + **một khó khăn thật** + **một điều học được**.
3. Không chép của nhau, không dùng câu mẫu — hội đồng đọc 4 bài liền nhau sẽ thấy ngay.
4. Ghi **% đóng góp**, tổng 4 người = 100%.
5. Nếu có gì chưa làm được thì ghi thật — hướng dẫn nói rõ "không làm được vẫn được điểm nếu phân tích đúng".

## Bảng phân công (đã có trong báo cáo mục 8)

| Thành viên | Vai trò | Nhánh phụ trách | Sản phẩm chính |
|---|---|---|---|
| Trần Nguyễn Khánh Duy (NT) | Planner + Research | `task/v1-tuyen-bo`, `task/v1-speed-benchmark` | `docs/v1_tuyen_bo.md`, `docs/dinh_nghia_phep_do.md`, `docs/quyet_dinh.md` |
| Đặng Duy Mạnh | Run + Evidence | `task/v2-cai-dat`, `task/v3-runtime`, `task/v5-sim2sim`, `task/v6-noise`, `task/quality` | `logs/nhat_ky_cai_dat.md`, `results/*.csv`, `tools/*` |
| Trương Thái Vỹ | Code + Video | `task/code-scripts3`, `task/code-demo` | `scripts/measure_runtime.py`, `scripts/build_demo.py` |
| Hà Mạnh Trường | Review | `task/review-qa` | `report/review_notes.md` (31 ticket RV) |

**Gợi ý %** (điều chỉnh theo thực tế, đây chỉ là khởi điểm dựa trên khối lượng sản phẩm): Duy 30% · Mạnh 30% · Vỹ 20% · Trường 20%.

## Chất liệu mỗi người có thể trích (có thật trong repo)

### Duy — Planner + Research
- Chốt **phương án C** cho tuyên bố kiểm chứng (`docs/quyet_dinh.md` DEC-01), sau khi phát hiện paper **không công bố** số FPS nào
- Phát hiện README GMR **có** bảng Speed Benchmark (35–45 FPS trên i9-13900K) mà nhóm đã bỏ sót → sửa lại V1
- Viết `docs/dinh_nghia_phep_do.md`: quy tắc **mean nếu CV ≤ 5%, median nếu CV > 5%** — quy tắc này về sau phải áp lại 3 lần
- Chặn 2 lần merge có thể **xoá repo** vì nhánh tạo từ `main` cũ

### Mạnh — Run + Evidence
- Cài GMR trên Windows: vấp `proxsuite`/MSVC, phải `pip install proxsuite==0.7.2.post1`
- Phát hiện **SMPL-X bị chặn license** → chuyển sang BVH LAFAN1 (miễn phí), cứu cả đề tài
- Truy nguyên robot **cúi gập người** (KI-01) → hoá ra clip `walk4_subject1` là clip khom lưng của LAFAN1
- Tự phát hiện **cột `cmd` ghi cờ `--rate_limit` chưa từng được truyền** (KI-02) và khai báo trung thực
- 20 lần đo có đủ dòng `END` để đối chiếu ngược; chứng minh retarget **tất định** bằng SHA256 trên 40 file `.pkl`

### Vỹ — Code + Video
- `scripts/measure_runtime.py`: 25 cột đúng hợp đồng §5.1, tách `ms_per_frame` (retarget) khỏi `_process`, có `--dry-run` không cần env
- `scripts/build_demo.py`: dựng video 67 s từ manifest, phát hiện **ffmpeg 9 bỏ `-vsync`**, `drawtext` phải escape đường dẫn Windows
- Sửa theo review: bỏ phụ đề gọi `ms/frame` trần, bỏ fallback lấy ảnh **robot** cho cảnh "người"

### Trường — Review
- 31 ticket RV; bắt được **4 nhóm lỗi chặn merge** mà người làm không thấy
- Phát hiện 4 dòng CSV ghi cờ `--rate_limit` **chưa từng chạy thật** (bằng 3 nguồn độc lập: mã, log FPS 64, đo lại thư viện 21,4 Hz)
- Bắt lỗi **thống kê**: báo cáo dùng median dù CV ≤ 5%, trái định nghĩa đã chốt
- Xác nhận `foot_slide` đo đúng định nghĩa (có trừ chuyển động root) — nếu sai thì cả bảng chất lượng vô nghĩa

## Mẫu câu (chỉ để hình dung, KHÔNG chép)

> *"Tôi phụ trách dựng môi trường và chạy thực nghiệm. Việc khó nhất là cài `proxsuite` — mất gần một buổi vì thiếu MSVC, cuối cùng phải ghim `proxsuite==0.7.2.post1`. Khi phát hiện SMPL-X cần license, tôi đề xuất chuyển sang BVH LAFAN1 và đã chạy được 3 robot. Tôi cũng tự phát hiện bảng CSV của mình ghi một cờ chưa từng được truyền và báo lại nhóm để rút kết luận. Tự đánh giá 30%."*

## Cách nộp

Điền vào `report/bao_cao.md` mục 8.2, thay 4 khối `[CHỜ TỰ THUẬT]`. Sau đó nhờ Trường đọc chéo: 4 bài phải **khác giọng**, không trùng câu nào.
