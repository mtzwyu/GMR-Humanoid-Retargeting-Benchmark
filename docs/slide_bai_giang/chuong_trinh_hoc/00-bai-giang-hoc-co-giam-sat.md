# Chương 2 — Học có giám sát (Supervised Learning)

> Bám sát slide Chương 2 (HUIT) · song ngữ · **áp dụng trực tiếp lên file D78 của bạn**:
> biến mục tiêu hồi quy = **`V101`** · biến mục tiêu phân lớp = **`nhan`** · biến độc lập = các cột còn lại trừ `nhan`.

---

## Mục tiêu chương

Sau chương này bạn có thể **tự**:
- Chạy **hồi quy tuyến tính** và **Ridge/Lasso** trên `V101`, đọc được MSE/RMSE/MAE/R².
- Giải thích vì sao (và khi nào) **điều chuẩn (regularization)** giúp.
- Chạy ≥2 thuật toán **phân lớp** khác họ trên `nhan`, dùng **cross-validation** + **ma trận nhầm lẫn**.
- Chọn **độ đo phù hợp** theo tỉ lệ lớp; vẽ **đường cong kiểm chứng** chỉ rõ under/overfit.

---

## Lesson map

| Lesson | Tên | Loại | Mastery evidence (qua bài khi) |
|---|---|---|---|
| L2.1 | Hồi quy tuyến tính & hàm lỗi MSE | Khái niệm | Viết được mô hình + hàm lỗi; biết khi nào dùng regression |
| L2.2 | Train/test split & 4 độ đo hồi quy | Thực hành (D78) | Chạy LinearRegression trên `V101`, đọc MSE/RMSE/MAE/R² |
| L2.3 | Regularization: Ridge & Lasso | Khái niệm+Thực hành | Giải thích L1 vs L2; chạy ≥3 `alpha`, nói điều chuẩn giúp không |
| L2.4 | Hồi quy logistic (phân lớp nhị phân) | Khái niệm+Thực hành | Giải thích sigmoid/quyết định; chạy trên `nhan` |
| L2.5 | Cây quyết định & kNN | Thực hành (D78) | Chạy 1 thuật toán thứ 2 khác họ trên `nhan` |
| L2.6 | Cross-validation, ma trận nhầm lẫn, chọn độ đo | Thực hành (D78) | Báo cáo mean±std CV, ma trận nhầm lẫn, biện luận độ đo |
| L2.7 | Đường cong kiểm chứng (under/overfit) | Thực hành (D78) | Vẽ curve, chỉ đúng vùng dưới khớp/quá khớp |

---

# Bài giảng

## L2.1 — Hồi quy tuyến tính & hàm lỗi

**Hồi quy (regression)** dự đoán một **giá trị thực**. Ý tưởng **tuyến tính**: giả sử biến mục tiêu `y` là tổ hợp tuyến tính của các đặc trưng:

```
ŷ = w0 + w1·x1 + w2·x2 + … + wd·xd = wᵀx
```

trong đó `w` là vector **trọng số (weights)** mà máy phải học từ dữ liệu. Có nhãn `y` rồi, máy tìm `w` sao cho `ŷ` gần `y` nhất trên **training set**.

**Hàm lỗi phổ biến — MSE (Mean Squared Error):**

```
MSE = (1/n) Σ (yi − ŷi)²
```

Lỗi càng nhỏ → mô hình càng khớp train. Học `w` = **giảm MSE** (bằng giải tích normal equation hoặc **gradient descent** — học chi tiết ở L2.4 cùng logistic).

> 🎯 **Vận dụng:** Với D78, cột `V101` được dự đoán từ ~117 cột còn lại. Mô hình tuyến tính cho `V101` sẽ có dạng gì (bao nhiêu trọng số w)? Đây là classification hay regression?

---

## L2.2 — Train/test split & 4 độ đo hồi quy

Nhắc lại từ Chương 1: **không bao giờ** để test set lọt vào huấn luyện. Quy ước của BT cá nhân bạn: chia **80/20**, `random_state = 0326` (4 số cuối MSSV).

**Bốn độ đo hồi quy bắt buộc trong bài (đều tính trên test set):**

| Độ đo | Công thức | Ý nghĩa |
|---|---|---|
| **MSE** | (1/n)Σ(y−ŷ)² | Lỗi bình phương trung bình (phạt lỗi lớn mạnh) |
| **RMSE** | √MSE | Như MSE nhưng cùng đơn vị với y |
| **MAE** | (1/n)Σ\|y−ŷ\| | Lỗi tuyệt đối trung bình (không phạt lỗi lớn) |
| **R²** | 1 − SS_res/SS_tot | Tỉ lệ phương sai giải thích được (≤1; càng gần 1 càng tốt) |

> 🎯 **Vận dụng:** Nếu có 1 dự đoán sai rất lớn (outlier), giữa **MSE** và **MAE**, cái nào sẽ "phản ánh" lỗi đó nặng hơn, và vì sao? *(Gợi ý: bình phương.)*

---

## L2.3 — Regularization: Ridge & Lasso

**Vấn đề:** với 117 đặc trưng như D78, mô hình tuyến tính dễ **quá khớp** (bắt chước nhiễu). Giải pháp: **phạt độ lớn trọng số** khi tối ưu → gọi là **regularization (điều chuẩn)**.

Thêm vào hàm lỗi một số hạng phạt:

| Loại | Hàm mục tiêu | Số hạng phạt | Đặc điểm |
|---|---|---|---|
| **Ridge (L2)** | MSE + α·Σwⱼ² | tổng **bình phương** w | Co w về gần 0 nhưng **không bằng 0** |
| **Lasso (L1)** | MSE + α·Σ\|wⱼ\| | tổng **trị tuyệt đối** w | Có thể **đẩy w = 0** → chọn đặc trưng |
| Linear | MSE | không phạt | có thể quá khớp |

`α` (alpha) càng lớn → phạt càng mạnh → w càng nhỏ. **Chuẩn hóa đặc trưng TRƯỚC** khi điều chuẩn (vì phạt phụ thuộc đơn vị). Quan trọng: **khớp bộ chuẩn hóa chỉ trên training set**.

> 🎯 **Vận dụng:** Lasso đẩy nhiều w về đúng 0. Điều đó giúp ích gì khi bạn có 117 cột như D78? Nếu `alpha` quá lớn thì mô hình thành ra thế nào (còn ý nghĩa không)?

---

## L2.4 — Hồi quy logistic (phân lớp nhị phân)

Dù tên là "regression", **logistic regression** dùng để **phân lớp** (dự đoán nhãn rời rạc). Với `nhan` có 2 giá trị, nó tính **xác suất thuộc lớp 1**:

```
p = σ(wᵀx) = 1 / (1 + e^(−wᵀx))
```

Hàm **sigmoid** `σ` nén mọi giá trị về `(0,1)`. Quyết định: nếu `p ≥ 0.5` → lớp 1, ngược lại lớp 0. Đây là một **đường/ranh giới tuyến tính** giữa hai lớp.

Học `w` bằng **gradient descent** — lặp đi lặp lại cập nhật `w` ngược hướng đạo hàm để giảm lỗi (ở đây lỗi là **cross-entropy/log-loss**, không phải MSE).

> 🎯 **Vận dụng:** Trong D78, cột `nhan` dùng làm biến phân lớp. Nếu `nhan` chỉ có giá trị 0 và 1, mô hình logistic cho ra gì (một xác suất)? Ngưỡng 0.5 nghĩa là gì?

---

## L2.5 — Cây quyết định & kNN (thuật toán thứ 2)

Bài cá nhân yêu cầu **≥2 thuật toán khác họ**. Hai lựa chọn phổ biến bên cạnh logistic:

**Cây quyết định (decision tree):** lặp lại việc chọn đặc trưng + ngưỡng để chia dữ liệu thành các nhánh, mỗi nhánh đồng nhất hơn về nhãn. Chia theo độ đo **Gini impurity** (hoặc entropy). Sâu hơn → quá khớp; nông quá → dưới khớp.

**k-NN (k láng giềng gần nhất):** để phân loại một điểm mới, nhìn `k` điểm huấn luyện **gần nhất** (khoảng cách Euclidean), lấy nhãn đa số. Không "học" ra mô hình tham số — gọi là **instance-based / lazy learning**. `k` nhỏ → quá khớp; `k` lớn → dưới khớp.

> 🎯 **Vận dụng:** Nếu bạn chọn cặp *logistic regression + kNN*, hai thuật toán này khác nhau ở điểm gì cơ bản (một cái tìm ranh giới tuyến tính qua huấn luyện, một cái nhớ dữ liệu để so khoảng cách)? Với 117 cột, kNN có khó khăn gì về khoảng cách không?

---

## L2.6 — Cross-validation, ma trận nhầm lẫn, chọn độ đo

**Cross-validation (kiểm định chéo):** thay vì 1 lần chia train/test, chia thành `k` phần, mỗi lượt lấy 1 phần làm validation, phần còn lại train; lặp `k` lượt. Báo cáo **trung bình ± độ lệch chuẩn** → ước lượng độ ổn định của mô hình. BT yêu cầu **CV phân tầng 5 phần** (giữ tỉ lệ lớp trong mỗi phần).

**Ma trận nhầm lẫn (confusion matrix):** bảng đếm 4 trường hợp:

| | Dự đoán Dương (1) | Dự đoán Âm (0) |
|---|---|---|
| **Thật Dương (1)** | TP | FN |
| **Thật Âm (0)** | FP | TN |

→ Tính **precision, recall, F1, accuracy**. 

**Chọn độ đo theo tỉ lệ lớp (quan trọng cho bài):** nếu `nhan` **mất cân bằng** (vd 90% lớp 0), riêng **accuracy** dễ "lừa" (cứ đoán 0 cũng đúng 90%). Khi đó dùng **F1 / precision-recall** hoặc nói rõ vì sao vẫn dùng accuracy nếu lớp cân bằng.

> 🎯 **Vận dụng:** Trong D78, trước tiên phải đếm tỉ lệ 2 lớp của `nhan`. Nếu lớp 1 chỉ chiếm 5%, bạn có dùng riêng accuracy làm độ đo chính không? Nếu không thì chọn gì?

---

## L2.7 — Đường cong kiểm chứng (validation curve)

**Ý tưởng:** quét một **siêu tham số** (vd `k` của kNN, độ sâu cây, `alpha`), vẽ 2 đường trên cùng 1 hình: điểm **train** và điểm **validation (CV)**.

```
Điểm
 ↑            ·· train luôn tăng
 │        ·
 │   ··────·  ← validation
 │ ·
 └─────────────→ độ phức tạp
   underfit     overfit
```

- Bên trái (phức tạp thấp): **cả train lẫn validation thấp** → *underfitting*.
- Bên phải (phức tạp cao): **train cao, validation tụt** → *overfitting*.
- Điểm chọn: nơi validation **cao nhất** (cân bằng bias-variance).

Đây chính là "nội dung Chương 1 áp dụng vào dữ liệu của bạn" mà BT cá nhân yêu cầu ở Phần D.

> 🎯 **Vận dụng:** Nhìn một validation curve: khi `k` của kNN tăng từ 1 lên 50, train score giảm dần còn validation tăng rồi giảm. Vùng `k` rất nhỏ thuộc underfit hay overfit? Bạn chọn `k` ở đâu và vì sao?

---

## Tóm tắt chương

- Hồi quy dự đoán giá trị thực (`V101`); phân lớp dự đoán nhãn (`nhan`).
- Điều chuẩn Ridge/Lasso chống quá khớp; Lasso còn chọn đặc trưng. Chuẩn hóa chỉ khớp trên train.
- Cần ≥2 thuật toán khác họ; đánh giá bằng CV phân tầng ± std + ma trận nhầm lẫn.
- Chọn độ đo theo tỉ lệ lớp; đường cong kiểm chứng để tìm siêu tham số và nhận diện under/overfit.
