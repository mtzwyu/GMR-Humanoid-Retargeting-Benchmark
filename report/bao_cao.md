# BÁO CÁO GIAI ĐOẠN 1 — GMR: ÁNH XẠ CHUYỂN ĐỘNG NGƯỜI SANG ROBOT HÌNH NGƯỜI THEO THỜI GIAN THỰC

**Trường Đại học Công Thương TP. HCM · Khoa Công nghệ Thông tin**
**Lớp 15DHTH07 · HK1 2026–2027 · Nhóm 01 · Đề tài HR04**

| Hạng mục | Giá trị |
|---|---|
| Repo | https://github.com/YanjieZe/GMR |
| Commit của repo dùng trong toàn bộ báo cáo | `25f56db` (`25f56db79ac411258b377b6d4ccba0c8ff3372ac`, 2026-10-22) |
| Giấy phép mã nguồn | MIT — "Copyright 2025 YanjieZe" (đã đọc file `LICENSE`) |
| Bài báo | *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking*, arXiv:2510.02252v1, 9 trang, CC BY 4.0 |
| Dữ liệu dùng để đo | LAFAN1 (Ubisoft), BVH 30 fps, giấy phép **CC BY-NC-ND 4.0** — dùng cho học thuật, không phân phối lại |
| Máy đo | LENOVO 83GS · Intel Core i5-12450HX (8 nhân/12 luồng) · ~15,7 GiB RAM · Windows 11 · **chạy CPU** |
| Phạm vi | Giai đoạn 1: chạy retargeting có sẵn, đo tốc độ, sim2sim 3 robot; **không** huấn luyện RL, **không** robot thật |

> **Quy ước đọc báo cáo.** Mọi số của nhóm nằm ở cột "nhóm đo được", mọi số của bài báo nằm ở cột "bài báo". Hai cột **không** được trộn, không suy diễn, không quy đổi. Số nào nhóm không tự đo thì ghi rõ **"không đo"** kèm lý do.

---

## 1. Giới thiệu bài toán và tóm tắt bài báo

### 1.1 Bài toán

Một robot hình người không thể "bắt chước" trực tiếp chuyển động của con người. Dữ liệu chuyển động người (mocap) mô tả một bộ xương với số khớp, chiều dài khâu và tư thế nghỉ khác hẳn robot. **Retargeting** là bước trung gian: nhận quỹ đạo của người theo thời gian rồi sinh ra quỹ đạo khớp (`qpos`) cho robot sao cho robot vừa giữ được "dáng" của chuyển động gốc, vừa thoả các ràng buộc vật lý của chính nó.

Bài toán khó ở ba tầng:

1. **Sai khác hình thái (embodiment gap).** Người và robot khác nhau về số bậc tự do, tỉ lệ chiều dài tay/chân/thân, giới hạn khớp và tư thế nghỉ. Ánh xạ thẳng theo góc khớp là vô nghĩa; ánh xạ thẳng theo vị trí tuyệt đối thì vi phạm giới hạn khớp.
2. **Ràng buộc vật lý của kết quả.** Một file retarget "đẹp" phải không xuyên sàn, không bay lên khỏi mặt đất, không để hai chân/hai tay tự cắt nhau, không có cú giật khớp. Đây là những lỗi mà mắt người thấy ngay nhưng lại khó diễn đạt thành một hàm mục tiêu duy nhất.
3. **Yêu cầu thời gian thực.** Với teleoperation hoặc điều khiển trực tiếp, retargeting phải chạy nhanh ít nhất bằng tốc độ phát của dữ liệu nguồn (LAFAN1: 30 fps, tức ngân sách 33,3 ms mỗi frame). Chậm hơn ngưỡng đó thì hệ thống chỉ phát lại được, không điều khiển được.

Điểm thứ ba chính là chỗ nhóm chọn để kiểm chứng, vì nó đo được trên CPU, không cần GPU, không cần huấn luyện.

### 1.2 Tóm tắt bài báo (viết lại bằng lời của nhóm)

**Luận điểm trung tâm.** Bài báo không đứng về phía "thuật toán retargeting nào khớp khít nhất". Tác giả lập luận rằng **cách retarget có ảnh hưởng quyết định tới việc một policy tracking phía sau có học và có sống sót được hay không**. Vì vậy, để đánh giá một retargeter, không thể chỉ nhìn file đầu ra bằng mắt; phải huấn luyện một policy trên chính file đó rồi đo tỉ lệ sống sót và sai số bám quỹ đạo. Tên bài — *Retargeting Matters* — chính là câu trả lời cho ba câu hỏi mà tác giả đặt ra: (i) chọn phương pháp retargeting có làm thay đổi hiệu năng policy không; (ii) artifact nào của retargeting làm policy hỏng; (iii) các phương pháp giữ được "dáng" chuyển động nguồn tới mức nào.

**Cách làm.** Nhóm tác giả lấy **bốn nguồn retargeting** khác nhau — GMR (phương pháp của chính bài báo), PHC, ProtoMotions và một pipeline nội bộ closed-source của Unitree — rồi cho cả bốn xử lý **cùng một bộ 21 chuỗi LAFAN1**. Sau đó, mỗi file retarget được dùng để huấn luyện **một policy riêng** bằng BeyondMimic (một phương pháp RL độc lập với các retargeter, nên phép so sánh không thiên vị bên nào), không tinh chỉnh reward cho từng phương pháp. Robot duy nhất dùng trong thí nghiệm là **Unitree G1**. Đánh giá gồm ba chế độ: mô phỏng gốc (100 rollout/policy), mô phỏng có ngẫu nhiên hoá động lực học (4096 rollout), và sim2sim trên MuJoCo qua node ROS của BeyondMimic (100 rollout). Ba nhóm chỉ số là tỉ lệ thành công, sai số vị trí/góc của body, và ảnh hưởng của frame bắt đầu. Ngoài ra có một user study 20 người để so "độ giống" bằng cảm nhận.

**Kết quả chính.** GMR đạt tỉ lệ thành công rất cao trên phần lớn chuyển động (nhiều clip 100 % ở cả ba chế độ), nhưng **không phải tốt nhất mọi mặt**: bài báo tự ghi nhận GMR chỉ đạt 51 % trên "Dance 5" ở sim2sim, do các cú giật ở khớp waist. Về sai số bám quỹ đạo, GMR đứng sau Unitree và trước PHC/ProtoMotions. Về ảnh hưởng của frame bắt đầu, bài báo cho thấy cùng một policy nhưng đổi frame khởi động có thể đổi tỉ lệ thành công từ 64 % lên 100 %. Phần artifact cũng được nêu thẳng: PHC có ca xuyên sàn tới 60 cm, ProtoMotions có ca hai chân giao nhau, GMR có sudden jump dưới 2 % độ dài dataset.

**Phương pháp GMR (để hiểu nhóm đã chạy cái gì).** GMR là một pipeline tối ưu hình học, **không huấn luyện**. Mỗi frame được xử lý tuần tự và frame trước được dùng làm điểm khởi tạo cho frame sau, gồm năm bước: khai báo ánh xạ các "key body" người ↔ robot kèm trọng số vị trí/hướng; căn rest pose bằng phép biến đổi Cartesian; **scale không đồng nhất theo từng body** (đây là điểm khác biệt cốt lõi so với các phương pháp khác — hệ số scale chung theo chiều cao được nhân thêm hệ số cục bộ cho từng khâu); IK tầng 1 ràng buộc hướng của toàn bộ khớp và vị trí của tay/chân; IK tầng 2 tinh chỉnh thêm vị trí cho mọi key body. Bộ giải dừng khi thay đổi hàm mục tiêu nhỏ hơn 0,001 hoặc sau 10 vòng lặp, luôn kèm ràng buộc giới hạn khớp. Sau khi retarget xong cả chuỗi, tác giả tính chiều cao mọi body bằng forward kinematics rồi trừ đi chiều cao nhỏ nhất — đây là cách chống bay/xuyên sàn ở mức toàn clip.

**Hạn chế bài báo tự nêu.** Toàn bộ dữ liệu chỉ đến từ một nguồn (LAFAN1); chỉ dùng một robot (G1) vì ràng buộc của BeyondMimic; chưa xét chuyển động có tương tác với môi trường/vật/robot khác; và chính GMR đôi khi vẫn phải tinh chỉnh trọng số tay (ví dụ "Dance 5").

### 1.3 Khoảng trống mà nhóm bám vào

Bài báo **không công bố bất kỳ con số tốc độ nào**: không có ms/frame, không có FPS, không có cấu hình CPU/GPU, không nêu phiên bản IsaacSim/BeyondMimic/Mink và không nêu commit repo. Ba bảng định lượng của bài (Bảng I, II, III) đều là kết quả của **policy đã huấn luyện**, muốn tái lập phải có GPU, IsaacSim và 84 policy (21 clip × 4 phương pháp). Với một nhóm chỉ chạy được trên CPU và có 10 ngày, ba bảng đó nằm ngoài phạm vi — không phải "chưa làm" mà là **không thể làm**.

Ngược lại, **README và phần mô tả repo** lại tuyên bố retarget "in real time on CPU". Đây là một tuyên bố định lượng có thể kiểm chứng bằng thực nghiệm trên đúng chiếc laptop của nhóm. Nhóm chọn tuyên bố này làm đối tượng kiểm chứng, đồng thời trình bày đầy đủ ba bảng của bài báo và lý do không tái lập được (phương án C — xem mục 2). Cách chọn này giữ được cả hai vế của yêu cầu môn học: có một phép đo thật của nhóm, và có đối chiếu trung thực với phần định lượng của bài báo.

---

## 2. Tuyên bố cần kiểm chứng

### 2.1 Câu chốt

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm kiểm chứng bằng cách đo thời gian xử lý mỗi frame (`ms_per_frame`) khi retarget chuyển động LAFAN1 (30 fps) sang Unitree G1 trên CPU, không bật `--rate_limit`; tuyên bố được coi là tái lập được nếu trung vị `ms_per_frame` ≤ 33,3 ms, tức `fps_out` ≥ 30 và `realtime_factor` ≥ 1,00.**

Bốn điều bắt buộc phải ghi kèm câu trên:

1. **Nguồn của tuyên bố là repo, không phải bài báo.** Câu "real-time" nằm ở README (mục *Key features*) và mô tả repo GitHub (*"in real time on CPU"*). Bài báo **không** nói GMR chạy real-time và **không** định nghĩa "real-time".
2. **Bài báo không công bố số.** Vì vậy "giá trị gốc" của tuyên bố này là **định tính**. Không có sai số "so với paper" cho tuyên bố này; mọi câu so sánh tốc độ với paper đều là bịa.
3. **Ngưỡng 33,3 ms là ngưỡng của nhóm**, không phải ngưỡng của paper: `1000/30`, suy ra từ tốc độ phát của chính dữ liệu nguồn LAFAN1. Nhóm đặt trước, không đổi sau khi thấy số.
4. **Giai đoạn 1 chỉ đo `ms_per_frame_process`** (cả tiến trình), bằng **bản đo cũ** `results/v3_runtime.csv` — file 13 cột, chỉ có cột `_process`, **không có** cột `ms_per_frame`. Kết luận bắt buộc đi qua bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`; **cấm** quy đổi `ms_per_frame = 0,92 × ms_per_frame_process`.

### 2.2 Vì sao chọn phương án C

Bài báo không có số tốc độ, nên tuyên bố "real-time" lấy từ repo. Yêu cầu môn học lại là kiểm chứng một tuyên bố **trong bài báo**. Nhóm đã cân nhắc ba phương án:

| | Nội dung | Ưu | Nhược |
|---|---|---|---|
| A | Chỉ đo real-time, ghi rõ paper không nêu | Đo được thật, đúng tinh thần đề tài | Yếu về chữ "trong bài báo" |
| B | Chuyển sang Bảng II (`E_g-mpbpe` = 104,1 mm) | Đúng nghĩa "số trong bảng paper" | Kết luận gần như chắc chắn "không tái lập được", không đo được gì thêm |
| **C** | **Tuyên bố chính A + một mục trình bày 3 bảng của paper và lý do không tái lập** | **Thoả cả hai vế, chi phí gần bằng A** | Báo cáo dài thêm khoảng 1 trang |

**Nhóm chọn C** (quyết định DEC-01, `docs/quyet_dinh.md`). Hệ quả: tuyên bố chính là tốc độ; ba bảng của paper được trình bày ở §2.5 với cột "nhóm đo được" để trống và ghi rõ "không đo — ngoài phạm vi".

### 2.3 Định nghĩa phép đo (hai đại lượng, tên phải đúng)

`scripts/bvh_to_robot.py` chạy retarget và render trong **cùng một vòng lặp**, nên dòng `Actual rendering FPS` do script in ra là FPS **có render**, không phải thông lượng retargeting. Dùng số đó là đo sai đối tượng. Vì vậy nhóm tách hai đại lượng:

| Đại lượng | Đo cái gì | Dùng để |
|---|---|---|
| `ms_per_frame` | **chỉ** lời gọi `retarget()` từng frame (probe không viewer) | Kết luận tuyên bố (đại lượng chính thức) |
| `ms_per_frame_process` | **cả tiến trình**: nạp BVH + khởi tạo + viewer + retarget + render + ghi pkl | Cận trên bảo thủ; giai đoạn 1 chỉ có số này |
| `realtime_factor_process` | `33,333 / ms_per_frame_process` (ngân sách 33,3 ms mỗi frame ở 30 fps) | Đọc kèm, **không** thay `realtime_factor` |

**Bảng bắc cầu §6.1** (áp dụng vì thiếu số Nhóm A):

| Tình huống | Được kết luận |
|---|---|
| `ms_per_frame_process` ≤ 33,3 ms | **Tái lập được** — điều kiện đủ, vì `retarget ≤ process ≤ 33,3 ms` |
| `process` > 33,3 ms **và** `ms_per_frame` ≤ 33,3 ms | Tái lập một phần |
| `process` > 33,3 ms **và** `ms_per_frame` > 33,3 ms | Không tái lập được (phải thử máy thứ hai) |
| `process` > 33,3 ms, **không có** `ms_per_frame` | **Chưa kết luận được** — không được suy ra |

Ba mức kết luận đã chốt trước: `realtime_factor` ≥ 1,00 → tái lập được; 0,80–0,99 → tái lập một phần; < 0,80 → không tái lập được.

### 2.4 Bảng hai cột: bài báo và nhóm đo được

Bảng dưới là bảng kết quả tổng hợp của báo cáo. Cột "bài báo" **không** chứa số của nhóm; cột "nhóm đo được" **không** chứa số của paper.

| Đại lượng (điều kiện) | Bài báo | Nhóm đo được | Ghi chú |
|---|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | **không đo** | Bản đo cũ không có cột này; không được thay bằng số `_process` |
| `ms_per_frame_process` (ms) — G1, LAFAN1 | **không nêu** | **17,272** (trung vị, n = 5; mean 17,349; sd 0,369; CV 2,13 %) | Bản đo cũ, 1 warm-up bị loại |
| `fps_out_process` (frame/s) | **không nêu** | **57,9** (suy ra `1000/17,272`) | Chỉ là số dẫn xuất, ghi rõ |
| `realtime_factor_process` (lần) | **không nêu** (chỉ có chữ "real time" ở README) | **1,93** (`33,333/17,272`) | **Không** phải `realtime_factor` của vòng lặp retarget |
| V5 · T1 29dof · `ms_per_frame_process` (ms) | **—** | **13,034** (trung vị, n = 5, CV 11,32 %) → rtf 2,56 | Paper chỉ dùng G1, không công bố tốc độ |
| V5 · G1 · `ms_per_frame_process` (ms) | **—** | **17,018** (trung vị, n = 3, CV 4,59 %) → rtf 1,96 | như trên |
| V5 · PM01 · `ms_per_frame_process` (ms) | **—** | **35,454** (trung vị, n = 3, CV 3,01 %) → rtf 0,94 | như trên |
| Success rate "Dance 5" sim2sim (%) | 51 (Bảng I, tr. 6) | **không đo** | Ngoài phạm vi — cần policy đã train |
| `E_g-mpbpe` mean của GMR (mm) | 104,1 (Bảng II, tr. 6) | **không đo** | Ngoài phạm vi — đo trên quỹ đạo policy |
| Xuyên sàn của PHC "Dance 1" (cm) | 60 (mục V-B, tr. 6) | **không đo** | Ngoài phạm vi — phải dựng lại PHC, cần SMPL-X |

Hai lưu ý về cách đọc bảng:

- Cột `realtime_factor` **trong file CSV** là của **từng lần chạy** (`motion_duration_s / wall_clock_s`), **không** phải số tổng hợp. Số tổng hợp trong báo cáo luôn tính bằng `33,333 / median_ms`, đúng như cột cuối bảng.
- `walk1_subject1.bvh` dài **7.840 frame = 261,3 s** ở 30 fps. Đây **không phải** "Walk 1" của Bảng I (33 s). Hai clip khác nhau; gộp lại là sai số liệu.

### 2.5 Ba bảng định lượng của bài báo và vì sao không tái lập được

Bài báo có đúng ba bảng số. Cả ba đều đo **policy đã huấn luyện**, không đo retargeter:

| # | Bảng | Đại lượng (đơn vị) | Giá trị GMR trong paper | Cần gì để tái lập |
|---|---|---|---|---|
| 1 | **Bảng I**, tr. 6 | success rate (%) trên 21 motion × 4 phương pháp × 3 chế độ | 100 % ở "Dance 1"/"Dance 2"; **51 %** ở "Dance 5" sim2sim | IsaacSim + BeyondMimic + policy đã train cho từng clip × từng phương pháp + 100/4096/100 rollout |
| 2 | **Bảng II**, tr. 6 | `E_g-mpbpe` (mm), `E_mpbpe` (mm), `E_mpjpe` (10⁻³ rad) | mean **104,1 mm** / 28,1 mm / 561,7 | Như trên, chế độ sim, 100 rollout/policy; sai số đo trên **quỹ đạo policy**, không phải file retarget |
| 3 | **Bảng III**, tr. 7 | success rate sim2sim (%) theo `start frame` | "Walk 2": **64 %** (frame 0) → **100 %** (frame 7) | **Cùng một policy đã train**, chỉ đổi frame đầu + 100 rollout MuJoCo |

**Bốn lý do không tái lập được (phải nêu đủ, không được rút gọn thành "thiếu GPU"):**

1. Phải **huấn luyện 84 policy** (21 clip × 4 phương pháp) bằng BeyondMimic — mỗi policy là một quá trình RL riêng.
2. Phải có **IsaacSim + GPU** cho chế độ sim và sim-dr (4096 rollout mỗi policy).
3. Sim2sim của paper cần **node ROS + state estimation** của BeyondMimic, không chỉ một script MuJoCo.
4. Bài báo **không công bố cấu hình phần cứng**, phiên bản IsaacSim/BeyondMimic/Mink và commit repo → **không dựng lại được môi trường** kể cả khi có GPU.

**Kết luận của mục này:** ba bảng của paper nằm ngoài phạm vi giai đoạn 1. Cột "nhóm đo được" của ba dòng tương ứng trong bảng §2.4 để **"không đo"**, không có số nào của paper bị chép sang cột nhóm.

### 2.6 Ba điều nhóm không được tuyên bố

1. **Không** nói "GMR nhanh hơn PHC/ProtoMotions" — paper không đo tốc độ, nhóm cũng không đo các phương pháp kia.
2. **Không** nói "nhóm tái lập Bảng I / Bảng II" — hai bảng đó cần train RL.
3. **Không** nói "paper tuyên bố real-time" — paper không nói vậy; tuyên bố nằm ở README/mô tả repo.

---

## 3. Nhật ký cài đặt

Nhật ký đầy đủ nằm ở `logs/nhat_ky_cai_dat.md` (15 mục cài đặt + 4 mục FIX + MEDIA + RV-23), kèm 6 log thô (`_conda_create.log`, `_conda_libstdcxx.log`, `_pip_install_editable*.log`, `_pip_proxsuite.log`, `_smplx_attempt.log`) và `logs/lenh_da_chay.md`. Mục này tóm tắt **bảy sự cố đáng kể** — chọn theo tiêu chí: có ảnh hưởng tới số liệu hoặc tới kết luận, không phải sự cố vặt.

### 3.1 Môi trường cuối cùng

| Mục | Giá trị |
|---|---|
| Máy | LENOVO 83GS (laptop), Windows 11 Home Single Language 10.0.26300 |
| CPU / RAM | Intel Core i5-12450HX, 8 nhân / 12 luồng · 16.873.545.728 byte (~15,7 GiB) |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU, 6144 MiB — **không dùng** cho đường đo (chạy CPU) |
| Conda / Python | conda 26.7.1 (Miniconda3) · Python 3.10.21, env `gmr` |
| Repo | `third_party/GMR`, HEAD `25f56db`, LICENSE MIT |
| Gói chính | `mujoco 3.17.0`, `mink 1.3.0`, `torch 2.14.1`, `smplx 0.1.28`, `daqp 0.11.2`, `qpsolvers 4.13.0`, **`proxsuite 0.7.2.post1` (ghim)** |
| `requirements.txt` | 45 dòng, lấy nguyên văn từ `pip freeze` của env `gmr`, có `-e git+…GMR@25f56db…` |
| Cổng G1 | `smplx_to_robot.py --help` exit 0, in đủ usage + 17 robot — **ĐẠT** |

### 3.2 Bảy sự cố

**(1) `proxsuite` không có wheel cho Windows → `pip install -e .` thất bại.**
Lần cài đầu (21:24–21:31) chết ở bước chuẩn bị metadata của `proxsuite>=0.2.9` (dependency của `qpsolvers[proxqp]`): pip tải source 54,7 MB rồi gọi CMake, nhưng máy không có MSVC (`where cl` rỗng) nên báo `CMAKE_C_COMPILER not set` và `metadata-generation-failed`. Đã thử hai hướng: tìm wheel win-64 cho bản 0.8.2 (không có, chỉ có sdist) và tìm trên conda-forge (chỉ build cho linux/osx). **Cách xử lý:** ghim `proxsuite==0.7.2.post1` — bản duy nhất có wheel `cp310-win_amd64` (4,3 MB) — rồi cài lại `pip install -e .`, thành công exit 0. **Không sửa một dòng nào trong `pyproject.toml`**; chỉ ghim phiên bản từ bên ngoài. Chấp nhận được vì GMR/mink dùng solver mặc định **daqp**, `proxqp` chỉ là backend dự phòng.

**(2) Bước `libstdcxx-ng` trong README không áp dụng cho Windows.**
`conda install -c conda-forge libstdcxx-ng` trả `PackagesNotFoundInChannelsError`. Nguyên nhân: đây là gói **chỉ có cho linux-64** (thư viện C++ của GCC); bước này trong README nhằm sửa lỗi render trên Ubuntu. **Cách xử lý:** bỏ qua có ghi chép, và kiểm chứng bù bằng việc chạy thật có mở cửa sổ MuJoCo ở V3 — nếu render lỗi sẽ thấy ngay.

**(3) Đường SMPL-X bị chặn bởi license → phải đổi đường dữ liệu.**
Repo không kèm body model: `assets/body_models/` không tồn tại, còn `utils/smpl.py` gọi `smplx.create(<assets/body_models>, "smplx", …)` nên bắt buộc phải có `SMPLX_NEUTRAL/FEMALE/MALE.pkl`. Chạy thử ra `FileNotFoundError`. Cả body model SMPL-X và dữ liệu AMASS/OMOMO đều phải đăng ký tài khoản và ký license tại trang của Max Planck, không có đường tải công khai; nhóm không có tài khoản license này. **Quyết định:** chuyển sang `scripts/bvh_to_robot.py` với LAFAN1 BVH — dữ liệu tải công khai, repo có sẵn 6 config IK `bvh_lafan1_to_*.json`, và đây là đường chính README hướng dẫn cho BVH. **Hệ quả phải ghi rõ trong báo cáo: V3 và V5 đo trên đường BVH, không phải đường SMPL-X như bài báo.**

**(4) KI-01 — robot cúi gập người khi phát lại.**
Khi render `g1_walk4_no_rate_limit_1.pkl`, robot gập hẳn về trước, đầu cúi, chân khuỵu. Nhóm đã loại trừ bốn giả thuyết bằng số đo chứ không bằng cảm nhận:

| Motion | frames | `waist_pitch` TB ± std | `hip_pitch` | `knee` | `root z` |
|---|---|---|---|---|---|
| `walk4_subject1` | 4.917 | **+29,52° ± 1,70** | −56,3 / −56,1° | +37,5 / +39,3° | 0,766 m |
| `walk3_subject1` | — | +25,19° ± 4,27 | −11,8 / −11,4° | +33,3 / +34,9° | 0,729 m |
| `dance1_subject2` (repo đánh dấu OK) | 3.944 | +18,62° ± 8,70 | −23,1 / −20,0° | +49,3 / +47,9° | 0,754 m |

Tỉ lệ scale người→robot = 1,75/1,8 = 0,972 (bình thường); viewer và retarget dùng **cùng** file `g1_mocap_29dof.xml`; đổi clip thì tư thế đổi theo clip. **Nguyên nhân:** `walk4_subject1.bvh` là clip **đi bộ khom lưng** của LAFAN1 — retarget tái hiện trung thực, pipeline không lỗi. Bằng chứng phụ: `waist_pitch` của walk4 gần như hằng số (std 1,7° so với 6,0° và 8,7° của hai clip kia), tức tư thế cố định suốt clip chứ không phải nhiễu ngẫu nhiên. **Cách xử lý:** đổi motion chính thức sang `walk1_subject1.bvh`, chạy lại V3, giữ walk4 làm ví dụ "motion khó". Kết luận này có được nhờ so sánh **ba motion qua cùng một pipeline**, không phải nhờ nhìn một clip rồi đoán.

**(5) KI-02 / RV-13 — cột `cmd` ghi một cờ chưa từng được truyền.**
Trong `third_party/_run/measure_v3.ps1`, cờ `--rate_limit` chỉ được ghép vào **chuỗi in ra CSV** (dòng 20, 23), còn lệnh thật (dòng 26) **không** kèm cờ. Vì vậy 4 dòng `mode = rate_limit` thực chất là lần chạy **không** giới hạn tốc độ. Ba nguồn độc lập xác nhận: (a) mã script; (b) log của chính các lần đó ghi `Actual rendering FPS` 64–136, trong khi một bộ giới hạn 30 Hz không thể cho 64 fps; (c) đo riêng thư viện trong env `gmr`: `RateLimiter(30).sleep()` × 300 → 14,004 s = **21,42 Hz (46,68 ms/lần)**, tức thư viện chậm hơn 30 Hz chứ không nhanh hơn. **Cách xử lý:** xoá 4 dòng khỏi CSV, rút toàn bộ kết luận về `--rate_limit`, và ghi lại bản chất: cờ này là công cụ phát lại cho mắt người xem, **không dùng để đo throughput**. Bài học được đưa vào mục 7: cột `cmd` là **hợp đồng tái lập**, một dòng sai làm cả bảng mất giá trị — và người phát hiện là người **không viết ra nó**, đây chính là lý do phải tách vai Review.

**(6) RV-14 — log không chứa số đo, và lỗi font khi sửa.**
Ban đầu `wall_clock_s` chỉ được in ra console PowerShell, không ghi vào file log của từng lần chạy, nên `ms_per_frame` và `realtime_factor` **không thể đối chiếu ngược**. Cách sửa: mỗi lần chạy ghi thêm một dòng cuối vào chính file log:

```
END wall_s=137.37 ms_per_frame=17.522 rtf=1.902 frames=7840 exit=0 at=2026-11-20 22:50:56
```

Lần ghi đầu dùng `-Encoding utf8` nên chèn UTF-8 vào file log vốn là UTF-16LE của PowerShell, chữ bị vỡ → đổi sang `-Encoding Unicode` và **chạy lại toàn bộ**. Kết quả: **20/20 log của các lần đo** (6 log V3 + 14 log V5) có dòng `END`, khớp CSV tuyệt đối.

**(7) Chênh 14,4 % giữa hai đợt đo V3 — và bằng chứng retarget là tất định.**
Đợt cũ (`c62e74f`, n = 3): 14,034 · 15,139 · 16,339 → mean **15,171**. Đợt mới (`f467075`, n = 5): mean **17,349**, median **17,272**. Lệch **+14,36 %** trên cùng máy, cùng input, cùng commit repo. Lý do chạy lại **không phải vì số xấu** mà vì định dạng log hỏng (sự cố 6) — nhưng đợt mới là đợt duy nhất có log đối chiếu được, nên lấy làm số chính thức.

Để trả lời câu "chênh do thuật toán hay do máy", nhóm băm SHA256 toàn bộ **40 file pkl**. Kết quả: mọi lần chạy của cùng một cặp (robot, motion) cho ra file **giống nhau từng byte**, bất kể đợt đo, bất kể có/không `--rate_limit`:

| Nhóm pkl | Số file | SHA256 (rút gọn) |
|---|---|---|
| G1 + `walk1_subject1` | 20 | `E7E3B906F22D3869…` |
| T1 29dof + `walk1_subject1` | 7 | `4E7161873D508ABE…` |
| PM01 + `walk1_subject1` | 5 | `57B693A8AAC72FE8…` |
| G1 + `walk4_subject1` | 5 | `37F0ACD2DD0EFF3C…` |
| Ba file KI-01 lẻ | 3 | `7A8FFEBE…`, `C9488E53…`, `2C6498E5…` |

**Kết luận:** chênh lệch 14,4 % **không đến từ thuật toán** (đầu ra giống nhau từng byte) mà từ **trạng thái máy** (tải nền, nhiệt độ, dao động lập lịch CPU). Đây chính là bản chất của một phép đo wall-clock toàn tiến trình. Hệ quả khi viết báo cáo: **không** được viết "17,35 ms" như thể chính xác đến 0,4 ms; phải nêu sai số giữa hai phiên ≈ 14 %, lớn hơn CV trong một phiên (2,13 %).

### 3.3 Ba điều nhật ký này dạy nhóm

1. **Cài không được không phải thất bại** — miễn là ghi rõ tắc ở đâu và đã thử gì. Ba sự cố (1), (2), (3) đều kết thúc bằng một quyết định có lý do, không phải bằng cách lách.
2. **Review độc lập có giá trị bằng cả một người làm.** Sự cố (5) do Review phát hiện; nếu không tách vai, bảng kết quả sẽ chứa một kết luận không có bằng chứng.
3. **Số đo phải tự truy vết được.** Sau sự cố (6), mỗi con số trong CSV đều lần ngược được tới một dòng `END` trong log của chính lần chạy đó.

---

## 4. Kết quả chạy mô hình có sẵn, đối chiếu với bài báo

### 4.1 Đối tượng đo và lệnh chạy

- Input: `walk1_subject1.bvh` (LAFAN1), **7.840 frame, 30 fps, 261,333 s**.
- Robot: `unitree_g1` (29 DoF) — robot duy nhất bài báo dùng.
- Chế độ: **không** `--rate_limit`.
- Lệnh (nguyên văn từ cột `cmd` của CSV):

```
python scripts/bvh_to_robot.py --bvh_file ..\data\lafan1\walk1_subject1.bvh \
  --format lafan1 --robot unitree_g1 \
  --save_path ../../results/pkl/g1_walk1_subject1_run2.pkl
```

- Quy trình: 1 lần warm-up (bị loại) + 5 lần đo, mỗi lần một process mới; đo bằng wall-clock của cả tiến trình (`Measure-Command`), chia cho 7.840 frame.
- Nguồn số: `results/v3_runtime.csv` — **bản đo cũ, 13 cột**, chỉ có `ms_per_frame_process`; bản thô `results/v3_raw.csv`; log từng lần `results/logs/v3_walk1_subject1_run1..6.log`.

### 4.2 Bảng từng lần chạy

> ⛔ **CHỜ SỐ LIỆU — mục 4.2**
> - **Nguồn:** `results/v3_runtime.csv`, các cột `phase`, `wall_clock_s`, `ms_per_frame_process`, `realtime_factor`, `log`; **chỉ** các dòng `phase = measure_1..measure_5`, bỏ dòng `phase = warmup`.
> - **Cần điền:** bảng 5 dòng (wall_clock_s, ms/frame) + 1 dòng thống kê (mean, median, sd, CV, min–max).
> - **Quy tắc tính:** mean/median/sd (ddof = 1)/CV tính trên **cả 5** giá trị; `realtime_factor_process` tổng hợp = `33,333 / median`, **không** lấy cột `realtime_factor` của một dòng bất kỳ.
> - **Người xác nhận:** Run (Mạnh) đối chiếu dòng `END` trong từng log; Review (Trường) chấm PASS.
> - **Số tổng hợp đã có ở bảng §2.4** (17,272 ms; mean 17,349; CV 2,13 %); mục này chỉ trình bày chi tiết từng lần và đồ thị.

### 4.3 Đồ thị và bằng chứng hình ảnh

| Ảnh | Nội dung | Nguồn |
|---|---|---|
| `results/figures/v3_ms_per_frame_g1_2026-11-20.png` | ms/frame theo 5 lần đo, có đường ngưỡng 33,33 ms | sinh bằng `third_party/_run/plot_v3.py` từ CSV |
| `results/figures/v3_terminal_start_g1_2026-11-20.png` | cửa sổ lệnh đo đang chạy (thấy lệnh + thời điểm) | chụp màn hình |
| `results/figures/v3_terminal_result_g1_2026-11-20.png` | kết quả một lần chạy: `TotalSeconds`, `ms_per_frame`, `realtime_factor` | chụp màn hình |
| `results/figures/v3_render_mujoco_g1_2026-11-20.png` | cửa sổ MuJoCo đang phát G1 | chụp màn hình |
| `results/figures/slide_v3_walk1_g1_f450/f900/f1350.png` | 3 khung 25/50/75 % của clip chính thức | trích từ `results/media/v3_walk1_g1.mp4` |

### 4.4 Đối chiếu với bài báo

> ⛔ **CHỜ SỐ LIỆU — mục 4.4**
> - **Cần:** một đoạn 5–7 dòng trả lời "chênh bao nhiêu và vì sao", đối chiếu với cột "bài báo" của bảng §2.4.
> - **Nguồn bắt buộc:** `docs/paper_notes.md` §12 (paper không nêu ms/frame, FPS, cấu hình) — để khẳng định **không có mốc so sánh**, không được viết "gần với paper".
> - **Nguồn số của nhóm:** bảng §2.4 + `results/v3_runtime.csv`.
> - **Nội dung phải có:** (a) paper không công bố tốc độ nên chỉ so được với ngưỡng nhóm đặt; (b) kết quả `_process` ≤ 33,3 ms → theo §6.1 là **điều kiện đủ** để kết luận tái lập ở mức cả tiến trình; (c) `ms_per_frame` (vòng lặp retarget) **không đo được** nên không được nói "retarget đạt real-time"; (d) cảnh báo sai số giữa hai phiên ≈ 14 %.

### 4.5 Hạn chế của phép đo (phải ghi, không được bỏ)

1. **Chỉ có số cả tiến trình.** `ms_per_frame_process` gồm cả khởi động interpreter, nạp model, khởi tạo viewer, render và ghi pkl — nên là **cận trên bảo thủ**, không phải thời gian của riêng `retarget()`.
2. **Không xác minh được `CUDA_VISIBLE_DEVICES`.** Bản đo cũ không có cột `cuda_visible`. Việc "chạy CPU" hiện là suy luận từ mã (đường BVH không tham chiếu `cuda`), không phải bằng chứng cấu hình.
3. **Một máy, một hệ điều hành.** Windows 11, trong khi README chỉ test Ubuntu 22.04/20.04. Kết quả không đại diện cho Linux.
4. **Đồng hồ Windows thô.** Hạt `sleep` ~15,6 ms là lý do `RateLimiter(30)` chỉ đạt 21,4 Hz; với wall-clock thì ảnh hưởng nhỏ hơn nhưng không bằng 0.
5. **CV của T1 trong V5 vượt ngưỡng** (11,32 % > 5 %) → theo luật nhóm phải báo **trung vị**, không báo mean; bảng §2.4 đã làm đúng.

---

## 5. Kết quả tự huấn luyện (3 hạt giống)

> ⛔ **CHỜ SỐ LIỆU — toàn mục 5. Người phụ trách: Vỹ (mục 5), dữ liệu: chưa có.**

**Tình trạng thật:** GMR là **retargeting dựa trên tối ưu hình học**, không phải học tăng cường. Pipeline không có trọng số, không có vòng huấn luyện, không có hàm mất mát và **không có khái niệm hạt giống (seed)**. Vì vậy yêu cầu "tự huấn luyện cấu hình nhỏ, 3 hạt giống, ghi đường cong và thời gian" **không áp dụng trực tiếp** cho repo này — không phải nhóm bỏ qua, mà là đối tượng huấn luyện không tồn tại trong repo.

Phần RL duy nhất của công trình là **policy tracking của BeyondMimic** (dùng trong Bảng I/II/III của paper). Muốn "tự huấn luyện" đúng nghĩa thì phải dựng IsaacSim + BeyondMimic trên GPU, train ít nhất một policy cho một clip, rồi chạy 3 seed. Máy đo chỉ có GPU laptop 6 GiB (không dùng cho đường đo), không đủ cấu hình để dựng IsaacSim + BeyondMimic; nhóm cũng không có phiên bản IsaacSim phù hợp, và 10 ngày không đủ cho một vòng train + đánh giá.

**Phương án thay thế đã chốt trong kế hoạch (V4):** chạy lại **cùng một pipeline tối ưu** với **3 cấu hình** (3 robot hoặc 3 motion), ghi thời gian và khác biệt đầu ra, và giải thích rõ vì sao không có đường cong học. Đây là nội dung được điểm theo tinh thần "không huấn luyện được thì ghi rõ vì sao".

> ⛔ **CHỜ SỐ LIỆU — mục 5 chi tiết**
> - **Nguồn cần lấy:** Vỹ (`gmr-code`, nhánh `task/v4-phan-tich`) — bảng 3 cấu hình (robot × motion), thời gian chạy và nhận xét khác biệt; nếu không có bảng riêng thì **dùng lại V5** (`results/v5_sim2sim.csv`, 3 robot cùng motion) làm 3 cấu hình, ghi rõ là tái sử dụng.
> - **Cần điền:** bảng 3 dòng (cấu hình · thời gian · khác biệt quan sát được) + kết luận 2–3 dòng.
> - **Cấm:** mô tả "3 seed" như thể đã chạy; không vẽ đường cong học giả.
> - **Người chốt:** Vỹ viết, Duy duyệt.

---

## 6. Sim2sim: bảng tụt hiệu năng và đồ thị

### 6.1 Nhóm đã làm gì (và chưa làm gì)

Đề tài HR04 chọn **sim2sim mức 3**: giữ nguyên simulator, **cùng một chuyển động → ≥ 3 robot**, chạy lại chính sách **không huấn luyện lại**. Nhóm đã chạy đúng mức này với 3 robot trên cùng `walk1_subject1.bvh`:

| Robot | `--robot` | DoF | Trạng thái |
|---|---|---|---|
| Unitree G1 | `unitree_g1` | 29 | đo được (n = 3) |
| Booster T1 29dof | `booster_t1_29dof` | 27 | đo được (n = 5) |
| ENGINEAI PM01 | `engineai_pm01` | 24 | đo được (n = 3) |
| Unitree H1 | `unitree_h1` | — | **bị chặn** (xem §6.3) |

**Điểm phải nói thẳng:** hướng dẫn môn học mô tả cách làm sim2sim tối thiểu là **đổi tham số vật lý** (khối lượng khâu ±20 %, hệ số ma sát, thêm 1–3 bước trễ điều khiển) rồi vẽ hiệu năng theo mức nhiễu. Nhóm **chưa làm** phần nhiễu vật lý này; cái nhóm làm là **đổi embodiment** (3 robot) — đúng định nghĩa "mức 3" mà kế hoạch đề tài đã chốt, nhưng **không thay thế** được phép thử độ bền vật lý. Đây là thiếu sót phải ghi ở mục 7, không được lấp bằng lời.

> ⛔ **CHỜ QUYẾT ĐỊNH — mục 6.1**
> - **Cần:** Planner (Duy) chốt một trong hai: (a) giữ mức 3 và ghi rõ "chưa làm nhiễu vật lý, đề xuất cho giai đoạn 2"; (b) bổ sung một lượt nhiễu vật lý (khối lượng ±20 %, ma sát, trễ 1–3 bước) trên G1 nếu còn thời gian.
> - **Nguồn để quyết:** PDF hướng dẫn tr. 1 (định nghĩa sim2sim) vs `docs/ke_hoach/00-tong-quan.md` dòng 8 (mức 3).

### 6.2 Bảng tụt hiệu năng

> ⛔ **CHỜ SỐ LIỆU — mục 6.2**
> - **Nguồn:** `results/v5_sim2sim.csv` (bản thô `results/v5_raw.csv`; log `results/logs/v5_<robot>_walk1_subject1_run*.log`).
> - **Chọn dòng:** bỏ `phase = warmup`; T1 lấy `measure_1..3 + measure_5 + measure_6` (n = 5), G1 và PM01 lấy `measure_1..3` (n = 3).
> - **Quy tắc:** báo **trung vị** (T1 CV 11,32 % > 5 %, G1 4,59 %, PM01 3,01 %); `realtime_factor_process = 33,333 / median`, **không** lấy cột `realtime_factor` từng dòng.
> - **Cần điền:** bảng `robot | DoF | n | median ms/frame | CV | rtf | so với ngưỡng 33,3 ms` + 1 câu "robot nào tụt nhiều nhất, vì sao".
> - **Số tổng hợp đã có ở §2.4:** T1 13,034 (2,56) · G1 17,018 (1,96) · PM01 35,454 (0,94).
> - **Người xác nhận:** Trường (mục 6) đối chiếu log; Mạnh xác nhận thứ tự chạy và nhiệt độ.

### 6.3 Vì sao H1 bị chặn

Ba nguồn độc lập: (a) `bvh_to_robot.py` từ chối `--robot unitree_h1` với `invalid choice` và **exit 2** — lỗi argparse xảy ra **trước** khi nạp model, nên không thể nhầm với lỗi runtime; (b) không có file `ik_configs/bvh_*_to_h1.json` (chỉ có 6 config `bvh_lafan1_*`); (c) README để cột BVH của `unitree_h1`/`unitree_h1_2` là **TBD**. Đường SMPL-X có H1 nhưng bị license SMPL-X chặn (mục 3, sự cố 3). Lý do gốc là danh sách `--robot` sinh từ `IK_CONFIG_DICT["bvh_lafan1"]`, README chỉ là bằng chứng phụ.

### 6.4 Chất lượng ánh xạ: hai chỉ tiêu nhóm tự định nghĩa

`docs/dinh_nghia_phep_do.md` §1.2 yêu cầu đo `min_body_height` (m, kỳ vọng ≈ 0) và `foot_slide` (mm/s, ngưỡng nhóm đặt ≤ 50 mm/s) để chứng minh "ánh xạ không bị hỏng".

> ⛔ **CHỜ SỐ LIỆU — mục 6.4 (số liệu CHƯA TỒN TẠI)**
> - **Hiện trạng:** `results/v5_sim2sim.csv` **không có** hai cột `min_body_height` và `foot_slide`. Đây là thiếu so với hợp đồng §5.3, không phải lỗi đánh máy.
> - **Cần:** một lượt tính FK trên các pkl V5 (`results/pkl/v5_*_run1.pkl`) để điền hai cột; người thực hiện: Mạnh (Run) hoặc Vỹ (Code) — **chưa có người nhận**.
> - **Nếu không kịp:** ghi rõ "không đo được trong giai đoạn 1" và dùng ảnh render 3 robot ở cùng frame 2000 làm bằng chứng định tính duy nhất. **Cấm** suy ra từ ảnh.

### 6.5 Đồ thị

| Ảnh | Nội dung |
|---|---|
| `results/figures/v5_ms_per_frame_robots_2026-11-20.png` | trung vị ms/frame 3 robot (thanh sai số min–max), có ngưỡng 33,33 ms |
| `results/figures/v5_sim2sim_g1_frame2000_2026-11-20.png` | G1 tại frame 2000, cùng motion |
| `results/figures/v5_sim2sim_t1_frame2000_2026-11-20.png` | T1 29dof tại frame 2000 |
| `results/figures/v5_sim2sim_pm01_frame2000_2026-11-20.png` | PM01 tại frame 2000 |
| `results/figures/slide_v5_sim2sim_f450/f900/f1350.png` | 3 khung từ clip ghép 3 robot (mỗi robot 20 s) |

Video: `results/media/v5_sim2sim_g1_t1_pm01.mp4` — 60,00 s, 1280×720, 30 fps, h264; **không commit** (`*.mp4` bị gitignore), nộp kèm link.

---

## 7. Kết luận

> ⛔ **CHỜ SỐ LIỆU + CHỜ CHỐT CÂU — toàn mục 7. Người chốt: Duy (mục 7).**

### 7.1 Khung kết luận (điền sau khi mục 4 và 6 chốt số)

Kết luận phải là **đúng một** trong ba mức, không được viết "vừa tái lập vừa không":

> **Tái lập một phần.** Phần **thời gian thực** kiểm chứng được ở mức **cả tiến trình**: `ms_per_frame_process` = `[CHỜ SỐ LIỆU: median n = 5 từ results/v3_runtime.csv]` ms (`realtime_factor_process` = `[33,333/median]`, CV = `[từ CSV]`), theo **bản đo cũ**; áp bảng bắc cầu §6.1 với ngưỡng 33,3 ms → `[tái lập được / chưa kết luận được]`. Số `ms_per_frame` (chỉ vòng lặp retarget) **không đo được** trong giai đoạn 1 vì bản đo cũ không có cột đó. Phần **bảng số của paper** (Bảng I, II, III) **không tái lập được**, vì các bảng đó đo policy đã train trong IsaacSim trên GPU — nhóm không có GPU phù hợp để dựng IsaacSim/BeyondMimic và không thể train 84 policy trong 10 ngày; con số 104,1 mm của Bảng II chỉ được ghi ở cột "bài báo" và **không** được đối chiếu với bất kỳ số nào nhóm tự đo.

### 7.2 Bốn điều kiện để câu trên đúng

1. Chỉ điền số khi `results/v3_runtime.csv` (bản đo cũ) đã được Review chấm PASS.
2. Không đổi ngưỡng 33,3 ms sau khi thấy số.
3. Không dùng từ "tái lập được" cho **toàn bộ bài báo** — chỉ cho phần thời gian thực.
4. Không viết "retarget đạt real-time" như thể đã đo riêng vòng lặp retarget. Nếu muốn nói chắc hơn thì phải chạy probe (`scripts/measure_runtime.py` @`5f9cdd5`) — việc này **chưa làm**.

### 7.3 Ba câu trả lời bắt buộc cho "chênh thì vì sao"

> ⛔ **CHỜ SỐ LIỆU — mục 7.3**
> - **Chênh giữa hai đợt đo (≈ 14 %):** nguồn `logs/nhat_ky_cai_dat.md` mục RV-23 + SHA256 40 pkl. Câu phải viết: chênh do **trạng thái máy**, không do thuật toán; đầu ra giống nhau từng byte.
> - **Chênh giữa 3 robot (PM01 chậm nhất):** nguồn `results/v5_sim2sim.csv` + ảnh 3 robot. Câu phải viết: PM01 24 DoF nhưng chậm hơn T1 27 DoF — nên **không** quy kết "nhiều khớp thì chậm"; cần nêu giả thuyết (cấu hình IK/khối lượng/điều kiện solver) ở mức **giả thuyết**, không phải kết luận.
> - **Chênh giữa nhóm và paper:** paper **không có số** → câu trả lời là "không có mốc so sánh", không được bịa tỉ lệ.

### 7.4 Thiếu sót phải nêu (không được giấu)

- Chưa làm **nhiễu vật lý** cho sim2sim (khối lượng ±20 %, ma sát, trễ điều khiển) — xem §6.1.
- Chưa đo **`min_body_height` / `foot_slide`** — xem §6.4.
- Chưa đo **`ms_per_frame`** (vòng lặp retarget) — xem §4.5.
- Chưa xác minh **`CUDA_VISIBLE_DEVICES`** trên bản đo cũ.
- Toàn bộ kết quả trên **một máy Windows**, không đại diện cho Linux/Ubuntu như README giả định.

---

## 8. Phân công công việc và tự thuật từng thành viên

> Bảng dưới là **khung**. Cột "tự thuật" do từng thành viên tự viết 3–5 dòng, không ai viết thay. Nội dung tự thuật phải trả lời: đã làm gì · khó nhất ở đâu · học được gì · tự đánh giá mức đóng góp (%).

### 8.1 Bảng phân công

| # | Thành viên | MSSV | Vai trò | Worktree / nhánh | Sản phẩm chính | Bằng chứng |
|---|---|---|---|---|---|---|
| 1 | Trần Nguyễn Khánh Duy | 2001230120 | Planner · Research · Writing mục 1, 2, 7 | `main` · `gmr-research` (`task/v1-tuyen-bo`) · `gmr-writing` | `docs/v1_tuyen_bo.md`, `docs/paper_notes.md`, `docs/dinh_nghia_phep_do.md`, `docs/quyet_dinh.md`, mục 1–2–7 | commit `f0a8fff`; review PASS 5/5 |
| 2 | Đặng Duy Mạnh | 2001240271 | Run · Writing mục 3 | `gmr-run` (`task/v2-cai-dat` → `task/v3-runtime` → `task/v5-sim2sim`) | `logs/nhat_ky_cai_dat.md`, `logs/lenh_da_chay.md`, `requirements.txt`, `results/v3_runtime.csv`, `results/v5_sim2sim.csv`, `results/figures/*`, `results/media/*` | commit `f467075`, `5c05497`; 20/20 log đo có dòng `END` |
| 3 | Trương Thái Vỹ | 2001240577 | Code · Writing mục 5 | `gmr-code` (`task/code-scripts` → `task/code-scripts3` → `task/v4-phan-tich`) | `scripts/measure_runtime.py`, `scripts/test_measure_runtime.py`, `scripts/NOTES.md`, mục 5 | commit `5f9cdd5`; 12 test PASS |
| 4 | Hà Mạnh Trường | 2045240326 | Review · Writing mục 6 | `gmr-review` (`task/review-qa`) | `report/review_notes.md`, checklist 5 điểm, 29 ticket RV | 7 PR được chấm; RV-13 phát hiện sai cột `cmd` |

### 8.2 Tự thuật từng thành viên

> ✍️ **CHỜ NỘI DUNG — mỗi người 3–5 dòng, viết ở ngôi thứ nhất.**

**Trần Nguyễn Khánh Duy (Nhóm trưởng · Planner/Research/Writing 1–2–7)**
- `[CHỜ TỰ THUẬT: việc đã làm — đọc paper, chốt tuyên bố, viết định nghĩa phép đo, điều phối merge, viết mục 1–2–7]`
- `[CHỜ TỰ THUẬT: khó nhất — chọn tuyên bố khi paper không có số tốc độ; cân bằng giữa "đúng yêu cầu môn" và "đo được thật"]`
- `[CHỜ TỰ THUẬT: học được — vì sao phải tách vai phản biện; cách viết bảng 2 cột]`
- `[CHỜ TỰ THUẬT: tự đánh giá % đóng góp]`

**Đặng Duy Mạnh (Run · Writing mục 3)**
- `[CHỜ TỰ THUẬT: việc đã làm — cài env, 7 sự cố, chạy V3/V5, quay video, viết nhật ký]`
- `[CHỜ TỰ THUẬT: khó nhất — proxsuite trên Windows; KI-01; sửa định dạng log UTF-16]`
- `[CHỜ TỰ THUẬT: học được — log phải chứa chính con số mình báo cáo]`
- `[CHỜ TỰ THUẬT: tự đánh giá % đóng góp]`

**Trương Thái Vỹ (Code · Writing mục 5)**
- **[CHỜ TỰ THUẬT: việc đã làm — `measure_runtime.py` có `--dry-run`, 12 test, hợp đồng CSV 30 cột]**
- **[CHỜ TỰ THUẬT: khó nhất — tách hai đại lượng `ms_per_frame` / `_process`; giữ tương thích CLI khi hợp đồng đổi tên cột]**
- `[CHỜ TỰ THUẬT: học được — viết test trước giúp đổi hợp đồng không vỡ]`
- `[CHỜ TỰ THUẬT: tự đánh giá % đóng góp]`

**Hà Mạnh Trường (Review · Writing mục 6)**
- `[CHỜ TỰ THUẬT: việc đã làm — checklist 5 điểm, chấm 7 PR, 29 ticket RV, đối chiếu CSV với log]`
- **[CHỜ TỰ THUẬT: khó nhất — phát hiện cờ `--rate_limit` chưa từng được truyền; chứng minh bằng 3 nguồn độc lập]**
- `[CHỜ TỰ THUẬT: học được — người viết ra số không phải người kiểm số]`
- `[CHỜ TỰ THUẬT: tự đánh giá % đóng góp]`

### 8.3 Cam kết của nhóm

- Mọi số trong báo cáo đều lần ngược được tới file trong `results/` và dòng `END` trong log tương ứng.
- Mọi số của paper nằm ở cột "bài báo" kèm số hiệu bảng/trang; không số nào bị chép sang cột "nhóm đo được".
- Video demo và dữ liệu nặng (LAFAN1, pkl) **không** commit; nộp kèm link ngoài.

---

# PHỤ LỤC A — Nhật ký phản biện (dùng làm phụ lục chất lượng)

Bản đầy đủ: `report/review_notes.md` (nhánh `task/review-qa`, do Trường viết). Dưới đây là các mục ảnh hưởng trực tiếp tới báo cáo:

| Ticket | Phát hiện | Ảnh hưởng tới báo cáo | Trạng thái |
|---|---|---|---|
| **RV-13** | 4 dòng `rate_limit` trong CSV ghi cờ chưa từng được truyền | Cấm mọi bảng so sánh có/không `--rate_limit`; đã ghi ở mục 3 sự cố (5) | ĐÓNG — 4 dòng đã xoá |
| **RV-14** | `wall_clock_s` không có trong log | Mỗi log phải có dòng `END`; đã sửa và chạy lại toàn bộ | ĐÓNG — 20/20 log đo |
| **RV-15** | V5 chỉ 1 lần/robot | Bảng V5 phải n = 3 hoặc n = 5; PM01/T1/G1 đã chạy lại | ĐÓNG |
| **RV-16** | CV đợt cũ 7,60 % > 5 % | Phải có n = 5 và báo trung vị (17,272) | ĐÓNG |
| **RV-17** | Tên cột `ms_per_frame` trần nhưng đo cả tiến trình | Mọi số đầu-cuối phải có hậu tố `_process` | ĐÓNG |
| **RV-18** | Chưa có bảng 2 cột bài báo/nhóm đo | Chính là bảng §2.4 của báo cáo | ĐÓNG bởi mục 2 |
| **RV-23** | Hai đợt V3 lệch 14,4 %; thiếu bằng chứng tất định | Mục 3 sự cố (7) + mục 7.3 | ĐÓNG |
| **RV-24** | T1 CV > 5 %, đồ thị vẽ mean | Mục 6 bắt buộc báo trung vị | ĐÓNG |
| **RV-26** | rtf trong mô tả PR tính sai (1,92 / 1,54) | Báo cáo luôn tính `33,333/median` → 2,56 / 1,96 / 0,94 | ĐÓNG |
| **RV-29** | V1 mô tả sai "V3 đo cả hai đại lượng" | Mục 2 ghi rõ V3 chỉ có `_process` | ĐÓNG |

# PHỤ LỤC B — Tự kiểm theo danh mục của hướng dẫn

| # | Điều kiện | Trạng thái |
|---|---|---|
| 1 | Đọc bài báo, ghi tuyên bố + số hiệu bảng/hình | ✅ mục 1, 2 (Bảng I/II/III, tr. 6–7) |
| 2 | Nhật ký cài đặt đầy đủ, kể cả lỗi | ✅ mục 3 + `logs/nhat_ky_cai_dat.md` |
| 3 | Chạy được mô hình có sẵn, có số để so | ✅ mục 4 (V3), số ở §2.4 |
| 4 | Tự huấn luyện ≥ 1 cấu hình nhỏ, 3 hạt giống | ⛔ **không áp dụng** — GMR không huấn luyện; mục 5 ghi rõ lý do + phương án thay thế |
| 5 | Sim2sim + bảng tụt hiệu năng | ⚠️ mục 6 có 3 robot; **thiếu nhiễu vật lý** và 2 chỉ tiêu hình học |
| 6 | Bảng tách cột "bài báo" / "nhóm đo được" | ✅ §2.4 |
| 7 | Kết luận dứt khoát | ⛔ mục 7 chờ số; khung đã chốt "tái lập một phần" |
| 8 | Ghi commit + đọc LICENSE | ✅ đầu báo cáo (`25f56db`, MIT) |
| 9 | Bảng phân công + tự thuật | ⚠️ bảng xong, tự thuật chờ 4 thành viên |
| 10 | Tập trình bày, có video dự phòng | ⚠️ 3 clip đã có (`results/media/`), slide 13 phút **chưa làm** |

# PHỤ LỤC C — Việc còn mở trước khi nộp

| # | Việc | Người | Chặn gì |
|---|---|---|---|
| 1 | Điền mục 4.2 / 4.4 từ CSV + log | Mạnh → Trường | "Kết quả chạy mô hình" chưa đủ |
| 2 | Chốt mục 5 (V4) | Vỹ | Tiêu chí 4 của hướng dẫn |
| 3 | Điền mục 6.2, quyết định mục 6.1, bổ sung 6.4 | Trường + Duy (+ Mạnh/Vỹ) | Tiêu chí 5 |
| 4 | Chốt câu kết luận mục 7 | Duy | Tiêu chí 7 |
| 5 | 4 tự thuật + % đóng góp | 4 thành viên | Tiêu chí 9 |
| 6 | `report/slides.md` 13 phút + tập bấm giờ | Duy + cả nhóm | Sản phẩm nộp |
| 7 | Cập nhật `results/README.md` (còn mô tả bản cũ `smplx_to_robot.py --rate_limit`) | Mạnh | Không chặn, nhưng dễ gây hiểu sai |
