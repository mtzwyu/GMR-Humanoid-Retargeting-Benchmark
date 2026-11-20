# Chương 4 — Giảm chiều dữ liệu (Dimensionality Reduction)

> Bám sát slide Chương 4 (HUIT) · song ngữ · **áp dụng lên đồ án DA-17 (Rice)**.
> Đặt cạnh **Chương 3**: DA-17 buộc bạn so sánh **PCA** (chiếu tuyến tính) với **trục phổ** (eigenvectors Laplace).

---

## Mục tiêu chương

Sau chương này bạn có thể **tự**:
- Giải thích vì sao cần giảm chiều và "**curse of dimensionality**".
- Hiểu **PCA** và **tự viết PCA qua SVD** bằng NumPy.
- Đọc **đường phương sai tích lũy**, biết chọn số chiều `k`.
- Phân biệt **PCA** (giữ phương sai toàn cục, khoảng cách tuyến tính) vs **trục phổ** (bẻ cong theo láng giềng).
- (Mở rộng) **LDA** — giảm chiều có giám sát.

---

## Lesson map

| Lesson | Tên | Loại | Mastery evidence |
|---|---|---|---|
| L4.1 | Vì sao giảm chiều? Curse of dimensionality | Khái niệm | Giải thích curse; vì sao Rice "3 chiều thật" |
| L4.2 | PCA & SVD — phương sai, trị riêng | Khái niệm | Giải thích PCA tìm hướng phương sai lớn nhất |
| L4.3 | PCA tự viết + đường phương sai tích lũy | Thực hành (DA-17) | Tự viết PCA qua SVD; vẽ cumulative variance |
| L4.4 | PCA vs trục phổ (Laplace eigenvectors) | Khái niệm+So sánh | Phân biệt 2 loại giảm chiều; vẽ 2 hình cạnh nhau |
| L4.5 | (Mở rộng) LDA | Khái niệm | Phân biệt PCA (không nhãn) vs LDA (có nhãn) |

---

# Bài giảng

## L4.1 — Vì sao giảm chiều? Curse of dimensionality

Dữ liệu càng nhiều cột (chiều) càng khó học: **curse of dimensionality** — ở không gian nhiều chiều, các điểm trở nên thưa và mọi khoảng cách gần như bằng nhau, khiến phân loại/gom cụm khó. Nhiều cột còn **dư thừa** (tương quan cao) hoặc **nhiễu**.

**Giảm chiều** = biến dữ liệu `d` chiều thành ít chiều hơn `k`, **giữ càng nhiều thông tin càng tốt**, để: dễ trực quan hóa, giảm nhiễu, giảm tính toán, tránh overfit.

**DA-17 (Rice) là ví dụ sắc nét:** 7 cột nhưng **3 thành phần chính đầu giữ 99,71% phương sai**, và 6/21 cặp cột tương quan > 0.9 (cao nhất 0.9989). Tức dữ liệu **thật sự chỉ có ~3 chiều có ích** — giảm chiều không phải "thêm bước", mà lộ bản chất dữ liệu.

> 🎯 **Vận dụng:** Nếu 2 cột của Rice tương quan 0.9989, giữ cả 2 có thêm thông tin đáng kể không? Giảm bớt chúng giúp gì cho gom cụm?

---

## L4.2 — PCA & SVD

**PCA (Principal Component Analysis):** tìm các **hướng (trục) mới** mà dữ liệu **biến thiên (phương sai) nhiều nhất**, theo thứ tự giảm dần. Chiếu dữ liệu xuống `k` trục đầu → giữ phần lớn phương sai với ít chiều.

**Cách làm (2 đường tương đương):**
1. **Qua hiệp phương sai:** tính ma trận hiệp phương sai của dữ liệu (đã chuẩn hóa), lấy **eigenvector** ứng với `k` **trị riêng lớn nhất** → đó là các **principal component**.
2. **Qua SVD** (đồ án yêu cầu): phân rã ma trận dữ liệu `X = U·Σ·Vᵀ`; các cột của `V` chính là các trục PCA, trị số riêng cho biết mức phương sai. SVD **ổn định về số** hơn.

**Chuẩn hóa trước** là bắt buộc, nếu không các cột có đơn vị lớn sẽ lấn át.

> 🎯 **Vận dụng:** PCA "ưu tiên" trục có phương sai lớn. Vì sao nếu không chuẩn hóa, một cột có giá trị rất lớn (vd diện tích ~ hàng nghìn) có thể làm PCA hiểu sai?

---

## L4.3 — PCA tự viết + đường phương sai tích lũy

**Các bước tự viết PCA qua SVD (DA-17):**
1. Chuẩn hóa từng cột (trừ mean, chia std) — khớp trên dữ liệu.
2. `U, s, Vt = np.linalg.svd(X, full_matrices=False)`.
3. Các cột của `Vt.T` (hay `V`) = principal components.
4. Chiếu: `X_k = X @ V[:, :k]`.
5. **Phương sai giải thích** tỉ lệ với bình phương trị số riêng `s²`; chia cho tổng để ra phần trăm.

**Hình bắt buộc — đường phương sai tích lũy:** vẽ phần trăm phương sai tích lũy theo số thành phần; ghi rõ `k` cần cho **80%, 90%, 95%, 99%**. Tham chiếu của Rice: `k = 2, 3, 3, 3` (tức 3 thành phần đã đủ 99.71%).

> 🎯 **Vận dụng:** Đường tích lũy của Rice đạt ~80% ở thành phần 2, ~99.71% ở thành phần 3 rồi gần như không tăng. Điều đó nói gì về "số chiều thật" của dữ liệu? Bạn chọn `k` bao nhiêu khi chiếu để trực quan hóa (mắt người xem được 2 chiều)?

---

## L4.4 — PCA vs trục phổ (eigenvectors Laplace)

**Điểm trung tâm của đồ án — 2 phép giảm chiều khác bản chất:**

| | **PCA** | **Trục phổ (Spectral)** |
|---|---|---|
| Tìm gì | hướng **phương sai lớn nhất** trong không gian gốc | eigenvectors của **ma trận Laplace** |
| Bản chất | **chiếu tuyến tính** | bẻ cong không gian theo **quan hệ láng giềng** |
| Giữ gì | khoảng cách **toàn cục** (Euclidean) | cấu trúc **cục bộ / cụm** |
| Vai trò | bước chuẩn bị cho thuật toán khác | **chính là thuật toán** (gom cụm phổ) |

**Hình trung tâm của báo cáo (bắt buộc):** 3810 hạt chiếu lên **2 thành phần chính** đầu, và cùng 3810 hạt lên **2 trục phổ** đầu, cả hai **tô theo giống thật** — đặt cạnh nhau. Câu hỏi nghiên cứu: khi PCA nói dữ liệu chỉ 3 chiều thật, trục phổ có tìm được cấu trúc mà PCA không thấy không, và nếu có thì cấu trúc đó **cong hay thẳng**?

> 🎯 **Vận dụng:** PCA chiếu xuống mặt phẳng 2 PC đầu. Nếu 2 giống gạo tách được bằng một đường **cong** trong không gian gốc, PCA (chiếu thẳng) có tách được rõ không? Trục phổ thì sao, và vì sao?

---

## L4.5 — (Mở rộng) LDA

**LDA (Linear Discriminant Analysis):** khác PCA — nó **có giám sát** (dùng nhãn). Thay vì tối đa phương sai, LDA tìm hướng chiếu sao cho **giữa các lớp càng tách nhau càng tốt, trong lớp càng gom nhau càng tốt**. Với bài 2 lớp, LDA cho 1 hướng chiếu; với C lớp cho tối đa C−1 chiều.

Dùng khi bạn có nhãn và muốn chiếu để phân biệt lớp (khác PCA chỉ nhìn phương sai, không biết lớp).

> 🎯 **Vận dụng:** Nếu bạn muốn giảm chiều **để phân biệt Cammeo vs Osmancik** (có nhãn), PCA hay LDA hợp lý hơn về lý thuyết? Vì sao? *(Trong DA-17 bạn vẫn phải dùng PCA/spectral vì phần gom cụm chính không dùng nhãn.)*

---

## Tóm tắt chương

- Giảm chiều chống curse of dimensionality, lộ bản chất dữ liệu.
- PCA tìm trục phương sai lớn; tự viết qua SVD; đường phương sai tích lũy chọn `k`.
- **PCA vs trục phổ**: chiếu tuyến tính giữ phương sai toàn cục vs eigenvectors Laplace bẻ cong theo láng giềng — là lõi so sánh của DA-17.
- LDA = giảm chiều **có giám sát** (dùng nhãn).
