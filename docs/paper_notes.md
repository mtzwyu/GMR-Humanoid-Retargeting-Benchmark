# Ghi chú bài báo — arXiv:2510.02252

**Nhóm 01 · HR-04 · Lớp 15DHTH07 · HK1 2026–2027**
Người ghi: Duy (tab Research) · Ngày đọc: 2026-11-20
Mọi con số dưới đây chép từ **PDF gốc arXiv v1** (9 trang), kèm số trang. Số nào bài báo không nêu thì ghi rõ **"paper không nêu"**.

---

## 1. Thông tin thư mục

| Trường | Giá trị | Nguồn |
|---|---|---|
| Tiêu đề | *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking* | trang 1 |
| arXiv | 2510.02252v1 (cs.RO), nộp 02-10-2025 | trang arXiv /abs |
| Tác giả | João Pedro Araújo, Yanjie Ze, Pei Xu, Jiajun Wu, C. Karen Liu (Stanford CS) | trang 1 |
| Giấy phép bài báo | CC BY 4.0 | khung "License" trên trang HTML arXiv |
| Số trang | 9 (2 cột, IEEE) | đếm từ PDF |
| Hội nghị | ICRA 2026 — **chỉ repo ghi**, bài báo không ghi | mô tả repo GitHub |
| Repo | https://github.com/YanjieZe/GMR · nhánh `master` | README |
| Commit đọc ngày 2026-11-20 | `25f56db7` — **2026-10-23** giờ VN (commit `2026-10-22T17:04:45Z`) | GitHub API `/commits/25f56db7…` |
| Giấy phép code | MIT | GitHub API `license.key = mit` |

> Lưu ý: bản arXiv **v1 là bản duy nhất** tính đến 2026-11-20. Nếu sau này có v2, phải đọc lại — số trong bảng có thể đổi.

---

## 2. Bài báo trả lời ba câu hỏi (trang 2, mục III)

- **Q1.** Cách chọn phương pháp retargeting có ảnh hưởng tới hiệu năng policy tracking không?
- **Q2.** Artifact nào của retargeting làm policy hỏng / không học được?
- **Q3.** Các phương pháp retargeting giữ được "dáng" (look) của chuyển động nguồn tới mức nào?

Cách tiếp cận: retarget cùng dữ liệu bằng **4 nguồn** (GMR, PHC, ProtoMotions, Unitree closed-source), rồi train policy tracking bằng **BeyondMimic** (được phát triển độc lập với các retargeter → công bằng), **không tinh chỉnh reward**.

---

## 3. Phương pháp GMR (mục IV, trang 4–5)

5 bước, mỗi frame chạy tuần tự, frame trước làm initial guess cho frame sau:

1. **Human–Robot key body matching** — người dùng khai báo ánh xạ body người ↔ body robot + trọng số position/orientation.
2. **Cartesian rest pose alignment** — chỉnh orientation (và đôi khi position) cho khớp rest pose của robot.
3. **Non-uniform local scaling** — hệ số scale chung theo chiều cao `h/h_ref`, nhân với hệ số cục bộ `s_b` cho từng body (công thức 2–3, trang 4). Đây là điểm khác biệt cốt lõi so với PHC/ProtoMotions.
4. **IK stage 1** — chỉ ràng buộc orientation toàn bộ + position của end-effector (tay/chân), giải bằng **Mink** (differential IK).
5. **IK stage 2 (fine-tune)** — thêm ràng buộc position cho **mọi** key body, trọng số khác stage 1.

Tham số solver (trang 5): dừng khi thay đổi hàm mục tiêu < **0,001** hoặc tối đa **10 vòng lặp**; ràng buộc joint limit `q⁻ ≤ q ≤ q⁺`.
Hậu xử lý (trang 5): sau khi retarget cả chuỗi, tính chiều cao mọi body bằng forward kinematics rồi **trừ chiều cao nhỏ nhất** khỏi global translation (sửa lỗi bay/xuyên sàn).

---

## 4. Thiết lập thực nghiệm (mục III, trang 2–4)

| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Robot | **Unitree G1** (duy nhất) | trang 3, mục III-B |
| Dữ liệu nguồn | **LAFAN1** (BVH), trích 21 chuỗi | trang 2 |
| Độ dài chuỗi | 5 s → 2 phút (Bảng I: 5,5 s "Walk 2" → 130,5 s "Dance 2") | trang 2, Bảng I tr.6 |
| Policy | BeyondMimic, 1 policy riêng cho từng clip | trang 2–3 |
| Simulator train | IsaacSim | Bảng I, tr.6 |
| Sim2sim | MuJoCo qua ROS node của BeyondMimic | trang 4 |
| Số rollout / policy | **100** (sim), **4096** (sim-dr), **100** (sim2sim) | trang 4, Bảng I tr.6 |
| Ngẫu nhiên hóa | sim: tắt domain randomization; sim-dr: bật | Bảng I tr.6 |
| Điểm bắt đầu | mọi rollout khởi động từ default pose của robot | trang 4 |
| Điều kiện kết thúc | robot ngã, hoặc lệch anchor height/orientation quá ngưỡng | trang 4 |
| Phần cứng (GPU/CPU) | **paper không nêu** | đã quét toàn văn: không có "GPU/A100/RTX/NVIDIA/hardware" |

Nguồn ngẫu nhiên trong sim2sim (trang 4): thời điểm/đồng bộ ROS + nhiễu của module state estimation; **không tinh chỉnh tham số simulator**; controller **không** được dùng thông tin privileged (global root pose thật).

---

## 5. Định nghĩa metric (mục III-D, trang 4)

| Ký hiệu | Đại lượng | Đơn vị |
|---|---|---|
| Success rate | số rollout chạm cuối clip / tổng rollout | % |
| `E_g-mpbpe` | sai số vị trí trung bình của body trong **hệ global** | mm |
| `E_mpbpe` | sai số vị trí trung bình của body **tương đối với root** | mm |
| `E_mpjpe` | sai số góc trung bình của joint rotation | 10⁻³ rad |

Sai số tracking chỉ tính trên các frame policy còn "sống".

---

## 6. Bảng I — Success rate (%, trang 6)

Cột: sim (100 trial) · sim-dr (4096 trial) · sim2sim (100 trial). PM = ProtoMotions, U = Unitree.

**Các con số đáng chú ý (chép nguyên):**

| Motion | Dài (s) | GMR sim | GMR sim-dr | GMR sim2sim | PHC sim | PHC sim2sim | PM sim2sim |
|---|---|---|---|---|---|---|---|
| Walk 1 | 33 | 100 | 100 | 100 | 100 | 100 | 100 |
| Walk 2 | 5,5 | 100 | 100 | 100* | 23 | 100* | 100* |
| Turn 1 | 12,3 | 100 | 99,98 | 100* | 93 | 100* | 99* |
| Dance 1 | 118 | 100 | 99,46 | 100 | **0** | **0** | 100 |
| Dance 2 | 130,5 | 100 | 99,9 | 100 | **0** | **0** | 100 |
| Dance 5 | 68,4 | 96 | 92,75 | **51** | 100 | 100 | 100 |
| Run (stop & go) | 37 | 98 | 91,24 | 100 | 17 | 74 | 26 |
| Kung fu | 8,6 | 100 | 99,95 | 100 | 100 | 100 | 100 |

\* xem mục V-D (start frame).

**Tổng hợp bằng lời của bài báo (trang 6, mục V-A):** trong 21 motion, **11** motion đạt > 98 % ở **mọi** phương pháp, **3** motion đạt 100 % tuyệt đối ("Walk 1", "Walk (old)", "Hop around"); 7 motion còn lại chênh lệch lớn giữa các phương pháp. PHC kém nhất.

**Điểm yếu của chính GMR (phải nêu trong báo cáo, không được bỏ):**
- "Dance 5": sim2sim chỉ **51 %** (thấp nhất của GMR) — nguyên nhân: sudden jumps ở waist roll (mục V-B).
- "Run (stop & go)": sim-dr **91,24 %**.

---

## 7. Bảng II — Sai số tracking (trang 6)

Đo trên **100 rollout ở chế độ sim**, thống kê trên 21 motion.

| Thống kê | `E_g-mpbpe` PHC / GMR / PM / U (mm) | `E_mpbpe` PHC / GMR / PM / U (mm) | `E_mpjpe` PHC / GMR / PM / U (10⁻³ rad) |
|---|---|---|---|
| Min | 71,8 / **59,9** / 66,0 / 51,1 | 20,9 / **18,1** / 24,1 / 18,2 | 569,5 / **362,0** / 499,0 / 355,5 |
| Median | 111,9 / 91,2 / 101,9 / **73,4** | 29,9 / 27,6 / 30,4 / **23,1** | 739,8 / 546,0 / 599,7 / **467,2** |
| **Mean** | **247,8 / 104,1 / 139,7 / 77,2** | **40,2 / 28,1 / 33,2 / 23,2** | **778,5 / 561,7 / 641,8 / 483,0** |
| Max | 1062,3 / 200,0 / 915,6 / 131,4 | 134,4 / 48,0 / 107,9 / 28,9 | 1336,1 / 1044,8 / 1397,9 / 678,5 |

Đọc: GMR mean `E_g-mpbpe` = **104,1 mm**, kém Unitree (77,2 mm) nhưng tốt hơn PHC (247,8 mm) và ProtoMotions (139,7 mm).

---

## 8. Bảng III — Ảnh hưởng của frame bắt đầu (trang 7)

Success rate sim2sim (%) theo start frame, **cùng một policy**:

| Motion | Start frame | PHC | GMR | PM | U |
|---|---|---|---|---|---|
| Walk 2 | 0 | 100 | **64** | 100 | 100 |
| Walk 2 | 7 | 100 | 100 | 100 | 100 |
| Turn 1 | 0 | 14 | 100 | 86 | 47 |
| Turn 1 | 49 | 100 | 100 | 99 | 100 |

Kết luận của bài báo (trang 7): frame đầu của reference ảnh hưởng lớn tới việc policy có bám được hay không; khuyến nghị chọn tư thế bắt đầu/kết thúc an toàn.

---

## 9. Artifact (mục V-B, trang 6)

- PHC retarget của "Dance 1" và "Dance 2": **xuyên sàn rõ rệt, 60 cm** ở một trường hợp.
- ProtoMotions retarget của "Run (stop & go)": **hai chân robot giao nhau** (self-intersection).
- GMR retarget của "Dance 5": nhiều **sudden jumps của waist roll**, xảy ra trên một đoạn **10 giây**, **< 2 %** toàn bộ dataset chuyển động.
- Ngoài ra (mục III-B, trang 4): hậu xử lý chống xuyên sàn của PHC đôi khi gây **floating ≥ 30 cm**; nhóm tác giả sửa bằng cách trừ chiều cao nhỏ nhất trung bình.

Ba loại artifact cần tránh: **sai chiều cao vật lý (floating/penetration), self-intersection, sudden jumps của joint value**.

---

## 10. User study (mục III-E + V-C, trang 4 và 7, Hình 4)

| Hạng mục | Giá trị |
|---|---|
| Số người tham gia | **20** (N = 20) |
| Clip mỗi câu hỏi | 5 giây, render từ SMPL-X fit của LAFAN1 |
| Số motion dùng | 15 (lấy ngẫu nhiên trong 21) |
| Số câu hỏi | **45** (mỗi người so 3 phương pháp × 15 motion) |
| Cách hỏi | chọn clip giống reference hơn, có lựa chọn "không thấy khác biệt"; thứ tự ngẫu nhiên, người xem không biết clip nào của ai |

Kết quả định tính (trang 7): GMR được coi là faithful hơn PHC và ProtoMotions; Unitree faithful hơn GMR nhưng người xem khó phân biệt GMR với Unitree hơn.
**Phần trăm cụ thể chỉ nằm trong Hình 4 (ảnh cột bar), không có trong text** → không được chép số từ hình khi chưa đọc đúng giá trị; nhóm không dùng tuyên bố này.

---

## 11. Hạn chế bài báo tự nêu (mục VI, trang 7–8)

1. Toàn bộ dữ liệu chỉ từ **một nguồn** (LAFAN1) → chưa kiểm chứng trên AMASS hay motion từ video đơn mục.
2. Chỉ dùng **một robot** (Unitree G1) — hạn chế do BeyondMimic; các retargeter khác có sẵn cho H1.
3. Chưa xét chuyển động có **tương tác** (với môi trường/vật/robot khác).
4. Thừa nhận GMR đôi khi vẫn cần tinh chỉnh trọng số (ví dụ "Dance 5").

---

## 12. Những gì bài báo **KHÔNG** nêu (đã kiểm tra toàn văn 9 trang)

Đây là phần quan trọng nhất cho V1. **Lưu ý phạm vi:** bảng này chỉ nói về **bài báo**. **Repo thì CÓ số tốc độ** — xem §13.4 (Speed Benchmark: 35~45 FPS trên i9-13900K, 60~70 FPS trên Threadripper 7960X).

| Hạng mục | Tình trạng **trong bài báo** |
|---|---|
| Thời gian retarget mỗi frame (ms/frame) | **không nêu** — không có bảng/hình nào về tốc độ |
| FPS / throughput của GMR | **không nêu** (repo thì có — §13.4) |
| Từ "real-time" | chỉ xuất hiện ở **trang 2** khi nói PHC *"time-consuming and limits its application for real-time scenarios"*, và trong **tên tài liệu tham khảo** (trang 8–9). Bài báo **không** tuyên bố GMR chạy real-time, cũng không định nghĩa "real-time" |
| Cấu hình phần cứng (CPU/GPU/RAM) | **không nêu** |
| Số vòng lặp solver thực tế / thời gian hội tụ | chỉ nêu ngưỡng (0,001) và trần 10 vòng (trang 5) |
| Commit của repo dùng trong bài | **không nêu** |
| Phiên bản IsaacSim / BeyondMimic / Mink | **không nêu** |
| Độ phân giải/tần số của state estimation trong sim2sim | **không nêu** |

→ Hệ quả: **không có "giá trị gốc" nào của bài báo để đối chiếu tốc độ.** Mọi so sánh tốc độ phải dựa trên định nghĩa real-time do nhóm đặt trước (xem `docs/dinh_nghia_phep_do.md`) hoặc trên tuyên bố của repo (mục 13).

---

## 13. Ghi chú về repo (đọc qua GitHub API, **không clone**)

| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Mô tả repo | *"[ICRA 2026] GMR: General Motion Retargeting. Retarget human motions into diverse humanoid robots **in real time on CPU**. Retargeter for TWIST."* | GitHub API `/repos/YanjieZe/GMR` |
| README, mục *Key features*, dòng 1 | *"**Real-time high-quality retargeting**, unlock the potential of real-time whole-body teleoperation"* | README `master` |
| README, mục *Speed Benchmark* | **35~45 FPS** (i9-13900K 24-Cores) · **60~70 FPS** (Threadripper 7960X 24-Cores) — chi tiết §13.4 | README `master`, dòng 562–568 |
| HEAD | `25f56db7` (**2026-10-23** giờ VN; `2026-10-22T17:04:45Z`) | `/commits/25f56db7…` |
| Kích thước repo | ~281.766 KB (≈ 275 MB) | GitHub API `size` |
| Số robot | **19 robot** (ID 0–18) + 2 TBD (AgiBot A2, OpenLoong) | README, bảng *Supported Robots* |
| Cài đặt hiện tại | `uv sync` (khuyến nghị); conda + `pip install -e .` chỉ còn trong mục "Alternative" | README, mục Installation |
| OS được test | Ubuntu 22.04/20.04 | README, mục Installation |
| Python | 3.10 (theo lệnh conda) | README + PDF hướng dẫn |

**Lệch giữa PDF hướng dẫn của môn và repo hiện tại** (phải ghi vào nhật ký cài đặt):

1. PDF ghi "12 cấu hình robot"; README hiện tại liệt kê **19** — repo đã thêm robot sau tháng 8/2025.
2. PDF ghi `conda create` + `pip install -e .`; README hiện tại ưu tiên `uv sync`.
3. README mới có thêm Xsens, PICO streaming (TWIST2), Fourier GR3… — không cần cho đề tài.

### 13.1 Hành vi code ảnh hưởng trực tiếp tới phép đo

Đọc `scripts/bvh_to_robot.py` (bản `master`):

- Vòng lặp chính gọi `qpos = retargeter.retarget(smplx_data)` rồi `robot_motion_viewer.step(...)`. Tức **retarget và render nằm chung một vòng lặp**.
- Script tự in `print(f"Actual rendering FPS: {actual_fps:.2f}")` — đây là **FPS của vòng lặp có render**, **không phải** throughput retargeting. Dùng số này để kiểm chứng tuyên bố là **sai đối tượng đo**.
- `--rate_limit` được truyền vào `robot_motion_viewer.step(..., rate_limit=args.rate_limit)`, tức **giới hạn nhịp phát theo chuyển động người**. Bật cờ này thì thời gian bị áp theo motion fps → đo ra ≈ 30 fps bất kể máy nhanh/chậm (**tự ứng nghiệm**). README: *"If you want it as fast as possible, remove `--rate_limit`"*.
- `--motion_fps` mặc định **30**; script **không đọc frame rate từ header BVH** mà chỉ in ra `mocap_frame_rate: 30`.
- Script **không** tính `local_body_pos` (`= None` khi lưu pkl).

Đọc `scripts/bvh_to_robot_dataset.py` (bản `master`):

- Có dòng `device = "cuda:0"` khi khởi tạo `KinematicsModel` → **đường batch yêu cầu CUDA**, không chạy được trên máy chỉ có CPU.
- Hardcode `src_fps = 30  # LAFAN1 data is typically 30 FPS`.
- Theo README: batch **không có visualization** → hấp dẫn để đo, nhưng vì `cuda:0` nên **không dùng được** cho tuyên bố "trên CPU".

### 13.2 Robot nào retarget được từ BVH LAFAN1 — đếm theo `ik_configs`, không theo README

Đếm thực tế trong `general_motion_retargeting/ik_configs` (bản `25f56db7`, chỉ đọc): có **6** file `bvh_lafan1_to_*.json`:

`bvh_lafan1_to_g1.json` · `..._h2.json` · `..._n1.json` · `..._pm01.json` · `..._t1_29dof.json` · `..._toddy.json`

→ **6 robot**: `unitree_g1`, `unitree_h2`, `fourier_n1`, `engineai_pm01`, `booster_t1_29dof`, `stanford_toddy`.

⚠ **README và `ik_configs` lệch nhau 1 robot:** README đánh ✅ ở cột BVH(LAFAN1) cho **`unitree_g1_with_hands`**, nhưng **không có** file `bvh_lafan1_to_g1_with_hands.json`. Lấy `ik_configs` làm chuẩn (đó là file script thực sự nạp); muốn dùng G1-có-tay qua BVH thì phải tự viết config. Vì vậy con số đúng là **6, không phải 7**.

Ngoài LAFAN1, thư mục còn 4 file BVH cho định dạng khác: `bvh_nokov_to_g1.json`, `bvh_xsens_to_g1.json`, `bvh_xsens_to_h1_2.json`, `bvh_to_talos.json`.

TBD (không có config LAFAN1): `unitree_h1`, `unitree_h1_2`, `booster_t1`, `booster_k1`, `hightorque_hi`, `galaxea_r1pro`, `kuavo_s45`, `berkeley_humanoid_lite`, `pnd_adam_lite`, `tienkung`, `pal_talos`, `fourier_gr3`.

→ V5 (sim2sim mức 3) **không được** chọn H1 nếu đi đường BVH; dùng **G1 + T1-29dof + PM01**.

### 13.3 Dữ liệu mẫu có sẵn trong repo

- `assets/xsens_bvh_test/251021_04_boxing_120Hz_cm_3DsMax.bvh` (~2,9 MB) — BVH **120 Hz**, dùng để smoke-test.
- `assets/hard_motions/{0,1}.txt`, `assets/<robot>/…` (MJCF/URDF + mesh).
- Không có sẵn file LAFAN1 → phải tải `lafan1.zip` từ repo Ubisoft (LAFAN1 là **30 fps**, 77 sequence, 496.672 frame — theo README của Ubisoft).
- **Cảnh báo tên clip:** `walk1_subject1.bvh` dài **7840 frame = 261,3 s** ở 30 fps. Đây **không phải** "Walk 1" của Bảng I (33 s, trang 6). Hai clip khác nhau — không được gộp khi lập bảng so sánh.

---

### 13.4 Speed Benchmark trong README — số định lượng **duy nhất** của repo

README `master` @ `25f56db7`, mục **"Speed Benchmark"** (nằm ngay trước mục "Citation"):

| CPU | Retargeting Speed |
|---|---|
| AMD Ryzen Threadripper 7960X 24-Cores | **60~70 FPS** |
| 13th Gen Intel Core i9-13900K 24-Cores | **35~45 FPS** |
| TBD | TBD |

Ghi chú bắt buộc khi trích:

- README **không nêu điều kiện đo**: motion nào, robot nào, clip dài bao nhiêu, có `--rate_limit` hay không, có tính khởi tạo + render hay không → **không tái lập chính xác được**.
- Đây là **số của repo**, **không phải** của paper (paper không có bảng tốc độ — §12). Không được ghi lẫn nguồn.
- Là mốc đối chiếu duy nhất; khi so sánh phải nêu **cả hai** CPU, không chọn mốc có lợi.
- Nhóm đo được **57,6 FPS** (i5-12450HX, `walk1_subject1` + `unitree_g1`, đo cả tiến trình). Phân tích vì sao nhanh hơn i9-13900K: `docs/v1_tuyen_bo.md` §3.6.

---

## 14. Nguồn (đều là nguồn gốc, truy cập 2026-11-20)

1. Bài báo PDF: https://arxiv.org/pdf/2510.02252v1 (bản HTML: https://arxiv.org/html/2510.02252v1)
2. Trang arXiv: https://arxiv.org/abs/2510.02252
3. Repo: https://github.com/YanjieZe/GMR (nhánh `master`, HEAD `25f56db7`)
4. README: https://raw.githubusercontent.com/YanjieZe/GMR/master/README.md
5. `scripts/bvh_to_robot.py`, `scripts/bvh_to_robot_dataset.py` (raw, `master`)
6. GitHub API: `/repos/YanjieZe/GMR`, `/repos/YanjieZe/GMR/commits?per_page=1`
7. LAFAN1 (Ubisoft): https://github.com/ubisoft/ubisoft-laforge-animation-dataset — README nêu 30 fps
8. Đề tài giai đoạn 1 (PDF của môn): `docs/huong_dan/De_tai_giai_doan_1_Nhom_01_HR04_15DHTH07.pdf`, trang 2
