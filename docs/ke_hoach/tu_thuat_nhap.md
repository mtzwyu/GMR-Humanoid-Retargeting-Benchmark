# Tự thuật 4 thành viên (bản nháp để các bạn sửa)

Viết theo ngôi thứ nhất, dựa trên việc có thật trong repo. **Đây là bản nháp** — mỗi bạn đọc lại, sửa cho đúng giọng mình, rồi thay vào `report/bao_cao.md` mục 8.2. Không nên nộp nguyên văn nếu thấy câu nào không đúng với trải nghiệm của mình.

Tổng %: 30 + 30 + 20 + 20 = 100.

---

## 8.2.1 Trần Nguyễn Khánh Duy — Nhóm trưởng, Planner + Research — 30%

Tôi phụ trách đọc bài báo và chốt tuyên bố cần kiểm chứng. Việc khó nhất là phát hiện paper arXiv:2510.02252 không công bố một con số ms/frame hay FPS nào, nên tôi phải chọn giữa bám chữ "số trong bài báo" và đo được thứ có thật — cuối cùng nhóm chọn phương án C: đo tuyên bố real-time lấy từ README, đồng thời trình bày rõ ba bảng số của paper và lý do không tái lập được. Tôi cũng viết định nghĩa phép đo trước khi ai chạy lần nào, gồm quy tắc chọn mean hay median theo CV, và quy tắc đó về sau phải áp lại ba lần vì có ba nơi dùng sai. Bài học lớn nhất của tôi là tôi đã đọc thiếu sáu nghìn ký tự cuối README nên bỏ sót bảng Speed Benchmark của chính repo, và chỉ phát hiện khi người khác soi lại. Tôi tự đánh giá 30%.

## 8.2.2 Đặng Duy Mạnh — Run, dựng môi trường và thu bằng chứng — 30%

Tôi là người cài và chạy GMR trên Windows. Việc khó nhất là cài đặt: `proxsuite` fail vì thiếu MSVC, tôi phải ghim `proxsuite==0.7.2.post1`, rồi phát hiện SMPL-X yêu cầu license nên chuyển sang BVH LAFAN1 và nhờ đó chạy được cả ba robot. Khi người xem báo robot cúi gập người, tôi đo góc khớp của ba clip và tìm ra clip `walk4_subject1` vốn là clip đi khom lưng của LAFAN1 — pipeline không sai, nó tái hiện trung thực. Việc khó nhất về mặt tinh thần là tự phát hiện bảng CSV của mình có bốn dòng ghi cờ `--rate_limit` chưa từng được truyền, và tôi đã báo lại nhóm để rút kết luận đó thay vì giữ số cho đẹp. Tôi cũng chứng minh retarget là tất định bằng SHA256 trên bốn mươi file pkl, để người chấm tự kiểm được. Tôi tự đánh giá 30%.

## 8.2.3 Trương Thái Vỹ — Code, công cụ đo và dựng video — 20%

Tôi viết hai công cụ của nhóm: `measure_runtime.py` và `build_demo.py`. Phần khó nhất ở script đo là tách cho đúng hai đại lượng — thời gian riêng của `retarget()` và thời gian cả tiến trình — vì ban đầu nhóm gọi lẫn tên khiến một số đo đúng bị hiểu sai nghĩa, và tôi phải thêm hẳn một cột `retarget_cmd` để người review tái lập được con số. Khi dựng video, tôi vấp ffmpeg 9 vì bản này đã bỏ `-vsync`, và mất một lúc mới hiểu `drawtext` trên Windows phải escape đường dẫn font. Sau khi xem lại bản render đầu, tôi bỏ luôn đoạn phụ đề gọi "ms/frame" trần và bỏ nhánh dự phòng lấy ảnh robot cho cảnh chuyển động người, vì cả hai đều làm người xem hiểu sai. Tôi tự đánh giá 20%.

## 8.2.4 Hà Mạnh Trường — Review, phản biện độc lập — 20%

Tôi phụ trách phản biện, và nguyên tắc của tôi là chỉ đọc cái đã nằm trong nhánh, không nghe mô tả. Việc đáng kể nhất là bốn dòng CSV ghi lệnh có `--rate_limit` trong khi lệnh thật không hề truyền cờ đó; tôi xác nhận bằng ba nguồn độc lập — đọc mã PowerShell, đối chiếu log ghi 64 FPS (một bộ giới hạn 30 Hz không thể ra 64), và chạy lại thư viện trong env được 21,4 Hz — rồi yêu cầu rút kết luận đó khỏi báo cáo. Tôi cũng bắt được báo cáo dùng trung vị trong khi định nghĩa đã chốt là dùng mean khi CV dưới 5%, và phải nêu lại ba lần vì lỗi lặp ở ba tài liệu khác nhau. Bài học của tôi là review không phải đọc lại cho kỹ, mà là chủ động tìm cách bác bỏ con số của chính nhóm mình. Tôi tự đánh giá 20%.

---

## Ghi chú khi sửa

- Nếu bạn thấy câu nào **không đúng với việc mình làm**, sửa hoặc bỏ — đừng giữ cho đẹp.
- Giữ 3–5 dòng, ngôi thứ nhất, có **một khó khăn thật** và **một điều học được**.
- Bốn bài không nên trùng cấu trúc câu; người chấm đọc liền bốn bài sẽ thấy ngay.
