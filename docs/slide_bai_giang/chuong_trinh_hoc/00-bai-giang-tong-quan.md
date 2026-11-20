# Chương 1 — Tổng quan về Học máy (Machine Learning Overview)

> Bám sát slide Chương 1 (HUIT) · song ngữ · slide trang 8–52

---

## Mục tiêu chương

Sau chương này bạn có thể **tự**:
- Giải thích ML là gì bằng **định nghĩa Tom Mitchell** và chỉ ra được 3 thành phần **T–E–P** trong một bài toán cụ thể.
- Phân biệt được **classification / regression / clustering** qua **kiểu nhãn**.
- Phân biệt **supervised / unsupervised / reinforcement learning**.
- Kể đúng **7 bước pipeline** của một dự án ML.
- Giải thích vì sao phải tách **training set / test set**, và dùng được thuật ngữ *underfitting / overfitting*.

---

## Lesson map (lesson kèm mastery evidence)

| Lesson | Tên | Loại | Mastery evidence (qua bài khi) |
|---|---|---|---|
| L1.1 | ML là gì? Định nghĩa T–E–P | Khái niệm | Chỉ đúng T, E, P cho bài toán D78 / một ví dụ mới |
| L1.2 | Data point & feature | Khái niệm | Gọi đúng data point/feature/label trong D78 |
| L1.3 | Classification vs Regression vs Clustering | Khái niệm | Xếp đúng loại một bài toán cho sẵn |
| L1.4 | Supervised / Unsupervised / RL | Khái niệm | Phân loại đúng và nêu 1 ví dụ mỗi loại |
| L1.5 | Pipeline 7 bước & train/test split | Khái niệm | Sắp đúng thứ tự pipeline; nêu vì sao tách test |
| L1.6 | Underfitting / Overfitting (ý tưởng) | Khái niệm | Giải thích + nhận diện bằng đồ thị đơn giản |

*(Chương 1 chủ yếu là khái niệm nên lesson loại Khái niệm — qua bằng 1 câu vận dụng.)*

---

# Bài giảng

## L1.1 — ML là gì? Định nghĩa T–E–P

Hai định nghĩa kinh điển (trang 12):

> **Arthur Samuel (1959):** Machine Learning là ngành học cung cấp cho máy tính **khả năng học hỏi mà không cần được lập trình một cách tường minh**.

> **Tom Mitchell (CMU):** Một chương trình máy tính được gọi là **học từ kinh nghiệm E** để hoàn thành nhiệm vụ **T**, với hiệu suất đo bằng phép đánh giá **P**, nếu hiệu suất của nó khi thực hiện T, khi được đánh giá bởi P, **cải thiện theo E**.

Cách hiểu thường gặp trong slide (trang 13): ML là một nhánh của khoa học máy tính, có khả năng **tự học từ dữ liệu** mà không cần lập trình qui tắc cụ thể. Với dữ liệu lớn (big data), một nhánh mới là **Deep Learning** ra đời.

**T–E–P là "khung" quan trọng nhất của chương.** Luôn đọc một bài toán ML qua 3 chữ này:

- **T (Task — nhiệm vụ):** mục tiêu bạn muốn máy làm, diễn tả qua một **điểm dữ liệu**. Ví dụ: xác định một tin nhắn có phải SPAM.
- **E (Experience — kinh nghiệm):** dữ liệu máy "trải nghiệm" để học, tức **training data**. Ví dụ: các tin nhắn đã được gán nhãn spam/không spam.
- **P (Performance measure — phép đo):** cách đo hiệu suất. Ví dụ: % tin nhắn spam được phân loại đúng.

**Ví dụ T–E–P từ slide:**
- **SPAM filter** (trang 14): T = xác định tin nhắn có phải spam; E = các tin nhắn đã đánh dấu spam; P = % tin spam phân loại đúng.
- **Nhận dạng chữ số 0–9** (trang 15): T = nhận dạng ảnh chứa ký tự số; E = đặc trưng từ tập số cho trước; P = độ chính xác nhận dạng.
- **Chơi cờ tướng** (trang 16): T = chơi cờ; E = các ván tự chơi + chơi với người; P = % ván thắng kiện tướng.

> 🎯 **Vận dụng:** Với file D78 của bạn, bài toán phân lớp đang "học" nhiệm vụ nào, từ kinh nghiệm nào, và phép đo nào là hợp lý? *(Trả lời khi được AI hỏi — không đọc tiếp phần sau trước khi trả lời.)*

---

## L1.2 — Data point, Feature, Label

Mỗi điểm dữ liệu (data point) được mô tả bởi nhiều **đặc trưng (features)**, thường là số. Tập đặc trưng của một điểm gộp thành **vector đặc trưng** `x ∈ R^d`.

- **Trong bài toán phân loại ảnh:** mỗi ảnh là một điểm dữ liệu; mỗi pixel là một đặc trưng; vector chứa toàn bộ pixel là vector đặc trưng.
- **Trong bài toán phân loại tin nhắn:** mỗi tin nhắn là một điểm dữ liệu.
- **Label (nhãn):** "đáp án" ta muốn dự đoán cho điểm dữ liệu đó (vd: `spam`/`not spam`, chữ số `0..9`).

> 🎯 **Vận dụng:** Trong file D78 của bạn, hãy đoán: mỗi *hàng* CSV là gì, các cột `V1..V118` là gì, và cột `nhan` là gì? (Đừng mở file — suy luận từ cách đặt tên.)

---

## L1.3 — Classification vs Regression vs Clustering

Khác nhau cốt lõi nằm ở **kiểu nhãn / mục tiêu** (trang 22–25):

- **Classification (phân lớp):** gán cho mỗi điểm một **nhãn rời rạc** trong tập C lớp. Xây hàm `f: R^d → {1,…,C}`. Vd: nhận dạng chữ số, chẩn đoán bệnh.
- **Regression (hồi quy):** dự đoán **giá trị thực (liên tục)**. Xây hàm `f: R^d → R`. Vd: ước lượng giá nhà, dự đoán tuổi.
- **Clustering (gom cụm):** **không có nhãn**, tự nhóm các điểm tương tự lại. Vd: phân nhóm khách hàng theo hành vi.

> 🎯 **Vận dụng:** Với D78, cột `nhan` nên dùng cho loại bài toán nào (classification hay regression)? Còn nếu mình muốn dự đoán giá trị số ở cột `V101` thì đó là loại nào?

---

## L1.4 — Supervised / Unsupervised / Reinforcement Learning

Phân loại theo **tính chất dữ liệu** (trang 30, 52):

- **Supervised learning (học có giám sát):** dữ liệu có **nhãn** — có cặp `(x, y)`. Gồm **classification** và **regression**. Vd: chẩn đoán bệnh, lọc spam, dự đoán giá nhà.
- **Unsupervised learning (học không giám sát):** dữ liệu **không nhãn**, chỉ có `x`. Bài toán tiêu biểu là **clustering**. Vd: phân khúc khách hàng, gom cụm tin bài, phân tích mạng xã hội.
- Ngoài ra còn có **reinforcement learning (học tăng cường)**, **semi-supervised learning (bán giám sát)**… (học chi tiết ở Ch.3 & Ch.5).

> 🎯 **Vận dụng:** Bài toán hồi quy `V101` và phân lớp `nhan` trên D78 thuộc nhóm nào? Gom cụm hạt gạo (đồ án DA-17, không dùng nhãn) thuộc nhóm nào?

---

## L1.5 — Pipeline 7 bước & train/test split

**Các bước của một dự án ML** (trang 50):
1. **Thu thập dữ liệu** (gathering data)
2. **Chuẩn bị dữ liệu** (preparing data)
3. **Chọn mô hình** (choosing a model)
4. **Huấn luyện** (training)
5. **Đánh giá** (evaluation)
6. **Tinh chỉnh siêu tham số** (hyperparameter tuning)
7. **Dự đoán** (prediction)

**Phép đánh giá P & train/test split** (trang 27):
- Dữ liệu chia **2 phần riêng biệt**: **training set** (huấn luyện) và **test set** (kiểm thử).
- Training set dùng để **tìm tham số mô hình**.
- Test set dùng để **đánh giá năng lực thật** của mô hình.
- **Quy tắc vàng:** khi tìm tham số chỉ được dùng thông tin trong training set; *không* để test set "lọt" vào quá trình huấn luyện.

**Kinh nghiệm E** (trang 29): việc huấn luyện chính là cho mô hình "trải nghiệm" trên training set. Chất lượng dữ liệu ảnh hưởng trực tiếp hiệu năng mô hình.

> 🎯 **Vận dụng:** Vì sao không thể dùng luôn test set để chọn mô hình/điều chỉnh siêu tham số? Nếu làm vậy thì phép đo P còn "thật" không?

---

## L1.6 — Underfitting / Overfitting (ý tưởng)

- **Underfitting (dưới khớp):** mô hình quá đơn giản, không nắm được cấu trúc dữ liệu → lỗi cao cả trên train lẫn test.
- **Overfitting (quá khớp):** mô hình "học thuộc lòng" training set, khớp quá mức → lỗi train rất thấp nhưng lỗi test cao (kém tổng quát với dữ liệu mới).

**Dấu hiệu trên đồ thị:** theo dõi điểm (train score) và điểm kiểm chéo (validation) khi tăng độ phức tạp — overfit khi test score bắt đầu tụt dù train vẫn tăng.

*(Kỹ thuật xử lý — điều chuẩn, validation set, cross-validation — học chi tiết ở Chương 2, vì đó chính là nội dung bạn phải làm trong BT cá nhân: đường cong kiểm chứng.)*

> 🎯 **Vận dụng:** Mô hình có lỗi train = 0.0, lỗi test rất cao. Bạn nghi ngờ underfit hay overfit? Vì sao?

---

## Tóm tắt chương

- ML = học từ dữ liệu, không cần lập trình qui tắc tường minh. Khung **T–E–P** dùng để đọc mọi bài toán.
- Điểm dữ liệu có **features**; bài toán phân biệt bởi **kiểu nhãn** → classification (nhãn rời rạc) / regression (giá trị liên tục) / clustering (không nhãn).
- Phân loại theo dữ liệu: **supervised** (có nhãn) / **unsupervised** (không nhãn) / **RL**.
- Pipeline 7 bước; luôn tách **train/test**, chỉ dùng train để tìm tham số.
- Underfitting vs overfitting là cân bằng lỗi train-test — nền cho Chương 2.

**Tự kiểm tra chương (trả lời không nhìn tài liệu):**
1. Nêu định nghĩa Mitchell và 3 chữ T–E–P.
2. Cột `V101` (số) và cột `nhan` (nhãn) trong D78 tương ứng bài toán gì?
3. Kể 7 bước pipeline.
4. Train set vs test set khác gì, vì sao phải tách?
5. Overfit là gì, dấu hiệu ra sao?
