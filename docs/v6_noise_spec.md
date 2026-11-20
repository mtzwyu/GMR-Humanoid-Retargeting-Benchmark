# V6 · Đặc tả phép thử độ bền (phương án C)

**Quyết định:** DEC-02 — chọn phương án **C** = giữ sim2sim mức 3 (đổi embodiment) **+** bổ sung một phép thử nhiễu định lượng.
**Lý do:** hướng dẫn môn yêu cầu "đổi tham số vật lý rồi vẽ hiệu năng theo mức nhiễu", nhưng GMR là **retargeting động học** — không có physics trong vòng tính:

- Không có khối lượng, ma sát, lực tiếp xúc → đổi ±20% khối lượng **không làm đổi một byte** file `.pkl` (đã chứng minh: SHA256 trùng giữa 40 lần chạy cùng cặp robot+motion).
- Vì vậy phép thử "nhiễu vật lý" **không áp dụng được** cho pipeline này. Thay bằng các nhiễu **có tác dụng thật** lên đầu vào của bài toán ngược.

## Bốn phép thử (mỗi phép 1 bảng con)

Đầu vào cố định: `walk1_subject1.bvh`, robot `unitree_g1`, baseline = lần chạy sạch hiện có.

| # | Phép thử | Mức | Cách làm |
|---|---|---|---|
| N1 | **Nhiễu khớp** | σ = 0,5° · 1° · 2° · 5° | Cộng Gaussian vào mọi kênh rotation của BVH trước khi retarget |
| N2 | **Trễ điều khiển** | k = 1 · 2 · 3 · 5 frame | Dịch chuỗi frame đi k (mô phỏng độ trễ truyền/nhận) |
| N3 | **Mất frame** | p = 1% · 5% · 10% | Bỏ ngẫu nhiên p% frame, nội suy tuyến tính để lấp |
| N4 | **Lệch tỉ lệ người** | ±10% · ±20% | Scale chiều cao người (đây là đại lượng "tương đương khối lượng" của bài toán động học) |

Mỗi mức chạy **1 lần** (không cần 3 lần) vì phép thử này đo **độ lệch có hệ thống**, không đo thời gian. Ghi rõ điều này trong báo cáo để không bị coi là vi phạm hợp đồng 1+3.

## Chỉ số phải ghi cho mỗi mức

| Chỉ số | Đơn vị | Ý nghĩa |
|---|---|---|
| `dq_mean` | độ | Trung bình \|Δq\| so với baseline trên toàn clip |
| `dq_max` | độ | Lệch lớn nhất tại một khớp, một frame |
| `dr_rmse` | mm | RMSE vị trí gốc so với baseline |
| `pct_frames_gt5deg` | % | Tỉ lệ frame có khớp lệch > 5° — proxy "chuyển động hỏng" |
| `still_converges` | 0/1 | Retarget có hội tụ không (không lỗi, không NaN) |

## Sản phẩm

- `results/v6_noise_sweep.csv` — mỗi dòng một mức nhiễu, đủ 5 chỉ số trên
- `results/figures/v6_noise_vs_deviation.png` — trục x = mức nhiễu, trục y = `dq_mean` và `pct_frames_gt5deg`, mỗi phép thử một đường
- 1 đoạn 4–6 câu trong báo cáo mục 6: mức nhiễu nào làm hỏng, mức nào vô hại, và **vì sao**

## Giả thuyết cần kiểm (và được phép sai)

Retargeting giải **tối ưu độc lập từng frame**, nên sai số **không tích lũy** theo thời gian. Kỳ vọng:
- N1, N3, N4: lệch tăng **tuyến tính** theo mức nhiễu, không lan sang frame khác
- N2 (trễ): không làm sai tư thế, chỉ làm **lệch pha thời gian** — nên `dq_mean` phải ≈ 0 nếu so đúng cặp frame, và khác 0 lớn nếu so lệch frame. Đây là điểm phải viết rõ kẻo kết luận sai.

Nếu kết quả khác giả thuyết, ghi đúng kết quả — **không sửa số cho khớp giả thuyết**.

## Ràng buộc

- Không đụng vào `results/v3_*`, `results/v5_*` (số chính thức đã chốt).
- Không commit file `.pkl` (đã gitignore).
- Mọi lệnh ghi vào `logs/lenh_da_chay.md` mục V6.
