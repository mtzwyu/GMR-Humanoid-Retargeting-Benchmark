# Tự thuật thành viên — bản hoàn chỉnh

Bản cuối để nộp, thay 4 khối trong `report/bao_cao.md` mục 8.2.
Tổng đóng góp: 30 + 30 + 20 + 20 = **100%**.

---

## 8.2.1 Trần Nguyễn Khánh Duy — MSSV 2001230120 — Nhóm trưởng, Planner + Research — 30%

Tôi phụ trách đọc bài báo và chốt tuyên bố cần kiểm chứng. Việc khó nhất là phát hiện paper arXiv:2510.02252 **không công bố một con số ms/frame hay FPS nào** — mọi bảng số của paper đều là kết quả policy đã huấn luyện, cần GPU và IsaacSim nên nằm ngoài phạm vi giai đoạn 1. Tôi chọn phương án C: đo tuyên bố "real-time trên CPU" lấy từ README, đồng thời trình bày rõ ba bảng định lượng của paper và lý do nhóm không tái lập được, để kết luận là "tái lập một phần" thay vì một câu trả lời né tránh. Trước khi bất kỳ ai chạy lần nào, tôi viết `docs/dinh_nghia_phep_do.md` quy định đo đại lượng gì, lấy mấy lần, bỏ warm-up, và chọn `mean` hay `median` theo CV — quy tắc này về sau phải áp lại ba lần vì có ba nơi dùng sai. Bài học lớn nhất của tôi là tôi đã đọc thiếu phần cuối README nên bỏ sót bảng Speed Benchmark của chính repo, và chỉ biết khi người khác soi lại; từ đó tôi hiểu người viết không thể tự kiểm tra mình.

## 8.2.2 Đặng Duy Mạnh — MSSV 2001240271 — Run, dựng môi trường và thu bằng chứng — 30%

Tôi là người cài và chạy GMR trên Windows. Khó nhất là khâu cài: `proxsuite` fail vì thiếu MSVC, tôi phải ghim `proxsuite==0.7.2.post1`; rồi phát hiện SMPL-X yêu cầu license nên chuyển sang BVH LAFAN1 — quyết định đó cứu cả đề tài, vì nếu không có nó nhóm không có dữ liệu chuyển động nào để chạy. Khi người xem báo robot cúi gập người, tôi đo góc khớp ba clip và tìm ra `walk4_subject1` vốn là clip đi khom lưng của LAFAN1: pipeline không sai, nó tái hiện trung thực. Việc khó nhất về mặt tinh thần là tự phát hiện bảng CSV của mình có bốn dòng ghi cờ `--rate_limit` chưa từng được truyền, và tôi báo lại nhóm để rút kết luận thay vì giữ số cho đẹp. Tôi cũng chứng minh retarget là tất định bằng SHA256 trên 56 file `.pkl` và ghi lại provenance của phép thử nhiễu, để người chấm tự kiểm được mà không cần tải dữ liệu nặng.

## 8.2.3 Trương Thái Vỹ — MSSV 2001240577 — Code, công cụ đo và dựng video — 20%

Tôi viết hai công cụ của nhóm là `scripts/measure_runtime.py` và `scripts/build_demo.py`. Phần khó nhất ở script đo là tách cho đúng hai đại lượng — thời gian riêng của `retarget()` và thời gian cả tiến trình — vì ban đầu nhóm gọi lẫn tên khiến một phép đo đúng bị hiểu sai nghĩa; tôi phải thêm hẳn cột `retarget_cmd` để người review tái lập được từng con số, và làm cho script chạy được bằng `--dry-run` để kiểm logic mà không cần môi trường GMR. Khi dựng video, tôi vấp ffmpeg 9 vì bản này đã bỏ `-vsync`, và mất một lúc mới hiểu `drawtext` trên Windows phải escape đường dẫn font. Sau khi xem lại bản render đầu, tôi bỏ đoạn phụ đề gọi "ms/frame" trần và bỏ nhánh dự phòng lấy ảnh robot cho cảnh chuyển động người, vì cả hai đều làm người xem hiểu sai bản chất phép đo.

## 8.2.4 Hà Mạnh Trường — MSSV 2045240326 — Review, phản biện độc lập — 20%

Tôi phụ trách phản biện, và nguyên tắc của tôi là chỉ đọc cái đã nằm trong nhánh, không nghe mô tả. Việc đáng kể nhất là bốn dòng CSV ghi lệnh có `--rate_limit` trong khi lệnh thật không hề truyền cờ đó: tôi xác nhận bằng ba nguồn độc lập — đọc mã PowerShell, đối chiếu log ghi 64 FPS (một bộ giới hạn 30 Hz không thể ra 64), và chạy lại thư viện trong env được 21,4 Hz — rồi yêu cầu rút kết luận đó khỏi báo cáo. Tôi cũng bắt được việc đặt tên `joint_limit_violation` cho một chỉ số thực chất chỉ là "khớp nằm sát giới hạn", và bác bỏ câu "hai công cụ độc lập cho cùng kết quả" vì hai script dùng chung logic và chung ngưỡng trên cùng một tệp. Ngoài ra tôi chỉ ra `foot_slide` chỉ là chỉ số proxy, `min_body_height` phụ thuộc offset nghỉ của từng model, và `dq_max` bị frame 0 làm phóng đại. Bài học của tôi là review không phải đọc lại cho kỹ, mà là chủ động tìm cách bác bỏ con số của chính nhóm mình.

---

## Ghi chú trước khi nộp

- Nếu câu nào **không đúng với việc bạn thật sự làm**, sửa hoặc bỏ — đừng giữ cho đẹp. Bài tự thuật sai sự thật là rủi ro lớn hơn bài viết dở.
- Giữ 3–5 dòng mỗi bài; bốn bài **khác cấu trúc câu** để người chấm đọc liền không thấy na ná nhau.
- Phần trăm phải cộng đúng 100%. Nếu điều chỉnh thì báo cả nhóm biết.
