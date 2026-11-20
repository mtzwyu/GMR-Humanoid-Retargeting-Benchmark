# Chương 3 — Học không giám sát (Unsupervised Learning)

> Bám sát slide Chương 3 (HUIT) · song ngữ · **áp dụng lên đồ án DA-17**:
> bộ Rice (Cammeo/Osmancik), 3810 hạt × 7 cột. Trọng tâm **gom cụm phổ (spectral clustering)** + k-means.

---

## Mục tiêu chương

Sau chương này bạn có thể **tự**:
- Hiểu bản chất **clustering** khi **không có nhãn**, và khoảng cách giữa các điểm.
- **Tự viết k-means** (kèm khởi tạo k-means++) bằng NumPy.
- Đánh giá gom cụm bằng **ARI / NMI / silhouette** (không dùng nhãn khi chọn tham số).
- Hiểu & tự viết **spectral clustering** (ma trận tương đồng → Laplace → eigenvectors → k-means) — lõi của DA-17.

---

## Lesson map

| Lesson | Tên | Loại | Mastery evidence |
|---|---|---|---|
| L3.1 | Clustering & khoảng cách | Khái niệm | Giải thích gom cụm; tính khoảng cách 2 điểm |
| L3.2 | k-means & k-means++ | Khái niệm+Thực hành | Tự viết k-means++; chạy trên Rice |
| L3.3 | Đánh giá không nhãn: ARI/NMI/silhouette | Khái niệm | Giải thích ARI; khi nào dùng silhouette |
| L3.4 | Spectral clustering (Laplace, eigenvectors) | Thực hành (DA-17) | Tự viết spectral + chạy trên Rice |
| L3.5 | So sánh với baseline & số cụm | Thực hành (DA-17) | ARI spectral vs k-means thẳng; vẽ eigenvalue gap |

---

# Bài giảng

## L3.1 — Clustering & khoảng cách

**Supervised** dùng nhãn; còn **unsupervised** chỉ có đặc trưng `x`, không có `y`. Bài toán tiêu biểu là **clustering (gom cụm)**: chia dữ liệu thành các nhóm sao cho các điểm **trong cùng nhóm giống nhau**, khác nhóm thì **khác nhau**. Slide ví dụ: phân nhóm khách hàng theo hành vi mua, hoặc cho trẻ xếp mảnh ghép theo màu/hình dạng dù không nói trước nhóm nào là gì.

**Cốt lõi:** cần một cách đo "giống nhau". Thường dùng **khoảng cách** giữa 2 vector đặc trưng:
- **Euclidean:** `d = √Σ(xᵢ−zᵢ)²` — đoạn thẳng giữa 2 điểm (chuẩn L2).
- **(Mở rộng)** Manhattan (L1), cosine (hướng).

Trong đồ án Rice, mỗi hạt = 1 điểm trong không gian 7 chiều (7 đặc trưng hình học). Gom cụm sẽ tìm xem 2 "giống gạo" có **tự lộ ra** thành 2 cụm từ hình dạng hay không.

> 🎯 **Vận dụng:** Rice có 7 cột đặc trưng. Hai hạt "giống nhau" được hiểu qua đại lượng gì? Nếu cột diện tích và chu vi cùng tăng thì hai hạt có gần nhau về khoảng cách không?

---

## L3.2 — k-means & k-means++

**k-means** chia dữ liệu thành `k` cụm, mỗi cụm có một **tâm (centroid)**. Mục tiêu: giảm **tổng bình phương khoảng cách** từ mỗi điểm tới tâm cụm của nó (inertia / WCSS).

**Thuật toán (lặp):**
1. Khởi tạo `k` tâm.
2. **Gán:** mỗi điểm về tâm gần nhất.
3. **Cập nhật:** tâm mới = trung bình các điểm trong cụm.
4. Lặp 2–3 đến khi tâm không đổi.

**k-means++:** cách khởi tạo tốt — tâm đầu tiên chọn ngẫu nhiên, các tâm sau chọn **xa** các tâm đã có (xác suất tỉ lệ với bình phương khoảng cách). Giúp tránh hội tụ về cụm tệ. **Đồ án yêu cầu tự viết k-means++**, dùng cả làm bước cuối của spectral và làm baseline chạy thẳng trên dữ liệu gốc.

> 🎯 **Vận dụng:** Vì sao khởi tạo ngẫu nhiên tệ có thể dẫn tới kết quả xấu (bị kẹt ở local minimum)? k-means++ giảm rủi ro đó bằng cách nào?

---

## L3.3 — Đánh giá gom cụm không nhãn: ARI / NMI / silhouette

Khi **không có nhãn**, làm sao biết cụm "đúng"? Hai hướng:

**1) Với nhãn ẩn (ground truth) — dùng để chấm điểm cuối cùng:** đồ án Rice biết 2 giống thật (Cammeo/Osmancik) nhưng **chỉ dùng ở bước chấm cuối**, không dùng để chọn tham số.
- **ARI (Adjusted Rand Index):** đo độ khớp giữa 2 cách chia cụm, **điều chỉnh cho ngẫu nhiên** (chạy −1..1, ngẫu nhiên ~0, khớp hoàn toàn = 1). Là **độ đo chính** của DA-17.
- **NMI (Normalized Mutual Information):** đo thông tin chia sẻ, chuẩn hóa 0..1.

**2) Không nhãn — dùng để chọn tham số:** chỉ nhìn cấu trúc nội tại.
- **Silhouette score:** mỗi điểm so độ dính cụm mình với độ tách khỏi cụm gần nhất, trung bình ra −1..1. Dùng chọn số cụm / tham số σ.

**Quy tắc kết luận của DA-17 (chốt TRƯỚC khi chạy):** spectral chỉ được coi là *hơn* k-means khi **ΔARI > 0.02** VÀ **Wilcoxon paired p < 0.05**. Kết quả "không hơn" vẫn là câu trả lời đúng nếu chứng minh được.

> 🎯 **Vận dụng:** Vì sao DA-17 không dùng nhãn giống để chọn σ cho spectral? (Gợi ý: nếu chọn tham số bằng nhãn rồi mới chấm bằng nhãn thì kết quả còn khách quan không?)

---

## L3.4 — Spectral clustering (lõi của đồ án)

Ý tưởng: k-means chỉ tách cụm **"lồi"** theo khoảng cách Euclid. **Spectral clustering** nhìn **quan hệ láng giềng** để tách cụm có hình dạng bất kỳ. 4 bước (đồ án yêu cầu **tự viết bằng NumPy**):

1. **Ma trận tương đồng** theo nhân Gauss:
   `Wᵢⱼ = exp(−‖xᵢ−xⱼ‖² / (2σ²))` — hai điểm gần nhau có W lớn.
2. **Ma trận bậc** `D`: ma trận chéo, `Dᵢᵢ = Σⱼ Wᵢⱼ`.
3. **Ma trận Laplace chuẩn hóa đối xứng:**
   `L = I − D^(−1/2)·W·D^(−1/2)`.
4. Lấy `k` **eigenvector** ứng với `k` trị riêng **nhỏ nhất** (`np.linalg.eigh`), **chuẩn hóa từng hàng** về độ dài 1, rồi chạy **k-means** trên toạ độ mới đó.

**Tham số σ quan trọng:** không có giá trị mặc định đúng. Đồ án yêu cầu cài **ít nhất 2 cách chọn σ** — một theo **trung vị khoảng cách**, một theo **khoảng cách tới láng giềng thứ 7** — rồi so.

**Điểm mấu chốt của đề tài:** ở đây **giảm chiều chính là thuật toán**, bỏ eigenvector đi thì không còn gì (khác với PCA là bước chuẩn bị).

> 🎯 **Vận dụng:** Nếu hai điểm xa nhau, trị Wᵢⱼ của chúng lớn hay nhỏ? σ quá lớn so với khoảng cách thật thì mọi W gần bằng nhau — hậu quả gì cho việc tách cụm?

---

## L3.5 — Baseline, số cụm, và trả lời bằng số

**Baseline bắt buộc (phải tinh chỉnh nghiêm túc):**
- Gán mọi hạt vào 1 cụm → ARI = 0 (baseline sàn).
- **k-means chạy thẳng** trên 7 cột đã chuẩn hóa (không qua trục phổ) — **mốc chính**.
- (Đối chiếu) `sklearn.cluster.SpectralClustering` và `KMeans` — chỉ mở ra SAU khi bản tự viết chạy được.

**Số cụm:** vẽ **đường trị riêng nhỏ nhất** của Laplace theo thứ tự tăng dần, tìm **chỗ gãy (eigen-gap)** — cách spectral "tự nói" số cụm. Đối chiếu với kết luận từ **silhouette**. Đây là hình bắt buộc trong báo cáo.

**Phương pháp kiểm chứng (bắt buộc):** mỗi cấu hình chạy **≥5 lần với 5 seed công bố** cho bước k-means cuối; mọi bảng báo cáo **trung bình ± std**. Phần phân lớp làm mốc trên thì chia 80/20 phân tầng + CV 5×5.

**Câu trả lời phải nêu dứt khoát bằng số:** trục phổ có hơn PCA không, hơn bao nhiêu, và nếu không hơn thì nói gì về hình dạng thật của dữ liệu.

> 🎯 **Vận dụng:** Nếu ARI của k-means thẳng và spectral đều ~0.5 như nhau, theo quy tắc chốt trước (ΔARI>0.02 + Wilcoxon p<0.05) bạn kết luận gì? Có phải "thất bại" không?

---

## Tóm tắt chương

- Clustering gom dữ liệu **không nhãn** bằng độ tương tự/khoảng cách.
- k-means = gán–cập nhật tâm; k-means++ khởi tạo tốt hơn.
- Đánh giá: **ARI/NMI** (khi có nhãn ẩn để chấm) và **silhouette** (chọn tham số, không nhãn).
- **Spectral clustering**: tương đồng → Laplace → eigenvectors → k-means; giảm chiều là lõi thuật toán. Chọn σ cẩn thận, xác định số cụm bằng eigen-gap.
- So sánh với baseline theo quy tắc chốt trước (ΔARI, Wilcoxon).
