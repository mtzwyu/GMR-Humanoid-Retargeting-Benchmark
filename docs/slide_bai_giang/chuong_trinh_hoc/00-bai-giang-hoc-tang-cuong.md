# Chương 5 — Học tăng cường (Reinforcement Learning)

> Bám sát slide Chương 5 (HUIT) · song ngữ.
> Chương này **không có bài tập/đồ án** — học đủ khái niệm + 1 ví dụ code đơn giản để có thể trả lời câu hỏi thi. Đặt **cuối lộ trình**, sau khi xong Chương 1–4 và deadline.

---

## Mục tiêu chương

Sau chương này bạn có thể **tự**:
- Giải thích chu trình **agent – environment – state – action – reward**.
- Phân biệt **policy** với **reward**; hiểu **return** (tổng phần thưởng có chiết khấu).
- Hiểu **Q-learning** (bảng Q, cập nhật bằng Bellman).
- Chạy 1 ví dụ đơn giản (vd gridworld / FrozenLake).

---

## Lesson map

| Lesson | Tên | Loại | Mastery evidence |
|---|---|---|---|
| L5.1 | RL là gì? MDP, agent–environment | Khái niệm | Mô tả đúng state/action/reward của 1 tình huống |
| L5.2 | Policy, return, chiết khấu γ | Khái niệm | Phân biệt policy vs reward; viết return |
| L5.3 | Q-learning & Bellman update | Khái niệm | Giải thích Q(s,a) và công thức cập nhật |
| L5.4 | Ví dụ code đơn giản | Thực hành | Chạy Q-learning trên grid nhỏ |

---

# Bài giảng

## L5.1 — RL là gì? Agent, Environment, MDP

Khác hẳn supervised/unsupervised: **reinforcement learning** không có tập (x, y) để học; thay vào đó một **agent** học bằng cách **tương tác** với **environment** (môi trường), nhận phản hồi là phần thưởng (reward) để tối ưu hành vi về lâu dài.

**Chu trình:**
```
agent ──action(a)──▶ environment
  ▲                        │
  └────state(s), reward(r)─┘
```

- **State (s):** trạng thái agent đang ở (vd vị trí trên bàn cờ).
- **Action (a):** việc agent chọn làm (vd đi nước cờ, đi lên/trái/phải).
- **Reward (r):** phần thưởng tức thì sau khi làm (thắng +1, thua −1).
- **Policy (π):** chiến lược — quy tắc chọn action từ state.

Slide ví dụ: chương trình học chơi game bằng cách tự chơi nhiều lần, không ai chỉ đúng nước đi từng bước — chỉ biết thắng/thua.

**MDP (Markov Decision Process):** khung toán học của RL — gồm tập state, action, hàm chuyển, hàm reward, và hệ số chiết khấu; "Markov" nghĩa là trạng thái tiếp theo chỉ phụ thuộc trạng thái hiện tại + action, không phụ thuộc quá khứ.

> 🎯 **Vận dụng:** Trong game cờ tướng, đâu là state, đâu là action, đâu là reward (phần thưởng tức thì) — và "thắng cả ván" khác gì reward từng nước?

---

## L5.2 — Policy, Return & chiết khấu γ

**Policy π(a|s)** là chiến lược: cho biết nên làm gì ở mỗi state. Mục tiêu RL = tìm policy **tối ưu** để nhận **nhiều phần thưởng tổng cộng nhất** theo thời gian.

**Return (G):** tổng phần thưởng tương lai, thường **có chiết khấu**:

```
G = r₁ + γ·r₂ + γ²·r₃ + …
```

- **γ (gamma, hệ số chiết khấu)** ∈ [0,1]: phần thưởng **càng xa càng bị giảm giá trị**.
- γ gần 1 → quan tâm cả tương lai xa; γ gần 0 → chỉ quan tâm lợi ích sớm.

**Phân biệt quan trọng:** **reward** = lợi ích tức thì; **policy** = chiến lược gom các reward thành hành vi. Agent không học để "tối đa reward hiện tại" mà để tối đa **return**.

> 🎯 **Vận dụng:** Một agent chọn nước đi được reward +0.1 ngay nhưng khiến sau đó thua cả ván. Reward tức thì và return khác nhau thế nào ở đây? Vì sao cần chiết khấu γ?

---

## L5.3 — Q-learning & Bellman update

**Q-value Q(s, a)** = ước lượng **tổng phần thưởng chiết khấu kỳ vọng** nếu từ state `s` làm action `a` rồi sau đó theo policy tối ưu. Q càng cao → action đó càng "tốt".

**Q-learning** học bảng Q bằng cách cập nhật sau mỗi bước (công thức **Bellman**):

```
Q(s,a) ← Q(s,a) + α · [ r + γ·maxₐ' Q(s', a') − Q(s,a) ]
```

- **α (learning rate):** mức độ cập nhật.
- `r + γ·max Q(s',a')`: **mục tiêu (target)** = reward ngay + phần thưởng tốt nhất ở state mới.
- Phần `[...]` gọi là **temporal difference (TD) error**.

Chính sách chọn action trong lúc học thường là **ε-greedy**: với xác suất ε chọn ngẫu nhiên (khám phá), còn lại chọn action có Q cao nhất (khai thác).

> 🎯 **Vận dụng:** Trong công thức Q-learning, phần `maxₐ' Q(s', a')` dùng giá trị ở state mới. Vì sao phải nhìn cả state sau đó, chứ không chỉ reward hiện tại r?

---

## L5.4 — Ví dụ code đơn giản (Q-learning trên grid nhỏ)

Ý tưởng để chạy thử (dùng numpy thuần, không cần thư viện RL):
- Dựng lưới 4×4 (gridworld), 1 ô đích (reward +1), vài ô chướng ngại (đi vào bị kẹt/−1).
- State = tọa độ ô; action = lên/xuống/trái/phải.
- Khởi tạo bảng Q = 0; lặp nhiều episode; mỗi bước cập nhật theo Bellman; dùng ε-greedy giảm dần.
- Sau khi hội tụ, in ra policy (mũi tên đi hướng nào ở mỗi ô) để kiểm tra agent tìm được đường tới đích.

> 🎯 **Vận dụng:** Sau khi Q hội tụ, làm sao để đọc ra **policy** từ bảng Q? *(Gợi ý: ở mỗi state, chọn action có Q cao nhất.)*

---

## Tóm tắt chương

- RL: agent học bằng tương tác với environment, không có nhãn (x,y).
- Thành phần: state, action, reward, policy; khung toán học là **MDP**.
- Mục tiêu = tối đa **return** (reward có chiết khấu γ), không phải reward tức thì.
- **Q-learning**: học bảng Q(s,a) bằng cập nhật Bellman; chọn action bằng ε-greedy (khám phá–khai thác).
