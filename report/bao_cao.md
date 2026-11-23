**TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG THÀNH PHỐ HỒ CHÍ MINH**

**KHOA CÔNG NGHỆ THÔNG TIN**

# BÁO CÁO GIAI ĐOẠN 1

**GMR: Ánh xạ chuyển động người sang robot hình người theo thời gian thực**

**Môn học:** Nghiên cứu và kiểm chứng một công trình về robot hình người
**Lớp:** 15DHTH07 · Học kỳ 1 · Năm học 2026–2027
**Nhóm:** 01 · Đề tài HR04
**Ngày nộp:** 21/11/2026
**Mã nguồn:** GMR @ `25f56db` (MIT) · **Bài báo:** arXiv:2510.02252v1

# MỤC LỤC

| # | Nội dung | Trang |
|---|---|---|
| 1 | Giới thiệu bài toán và tóm tắt bài báo | 2 |
| 2 | Tuyên bố cần kiểm chứng | 3 |
| 3 | Nhật ký cài đặt | 4 |
| 4 | Kết quả chạy mô hình có sẵn, đối chiếu với bài báo | 5 |
| 5 | Kết quả tự huấn luyện (3 hạt giống) | 6 |
| 6 | Sim2sim: bảng tụt hiệu năng, độ bền theo nhiễu, chất lượng ánh xạ và đồ thị | 7 |
| 7 | Kết luận | 12 |
| 8 | Phân công công việc và tự thuật từng thành viên | 13 |
|  | Tài liệu tham khảo | 15 |

**Phạm vi:** chạy retargeting có sẵn, đo tốc độ, sim2sim 3 robot + 4 phép thử nhiễu; **không** train RL, **không** robot thật. **Máy đo:** LENOVO 83GS · i5-12450HX · ~15,7 GiB · Windows 11 · **CPU**. **Dữ liệu:** LAFAN1 (Ubisoft), BVH 30 fps, CC BY-NC-ND 4.0.

> **Quy ước.** Mọi số của nhóm nằm ở cột "nhóm đo được", mọi số của paper nằm ở cột "bài báo". Hai cột không trộn, không suy diễn. Số không tự đo thì ghi **"không đo"** kèm lý do.

## 1. Giới thiệu bài toán và tóm tắt bài báo

### 1.1 Bài toán

**Retargeting** nhận quỹ đạo chuyển động của người (mocap) và sinh quỹ đạo khớp (`qpos`) cho robot hình người, sao cho giữ được "dáng" chuyển động gốc mà vẫn thoả ràng buộc của robot. Bài toán khó ở ba tầng:

1. **Sai khác hình thái.** Người và robot khác nhau về số bậc tự do, tỉ lệ chiều dài khâu, giới hạn khớp và tư thế nghỉ. Ánh xạ thẳng góc khớp là vô nghĩa; ánh xạ thẳng vị trí tuyệt đối thì vi phạm giới hạn khớp.
2. **Ràng buộc vật lý.** Kết quả phải không xuyên sàn, không bay, không tự cắt, không giật khớp — những lỗi mắt người thấy ngay nhưng khó gói vào một hàm mục tiêu.
3. **Thời gian thực.** Với teleoperation, retargeting phải nhanh ít nhất bằng tốc độ phát dữ liệu nguồn (LAFAN1 30 fps ⇒ 33,33 ms/frame). Chậm hơn thì chỉ phát lại được, không điều khiển được.

Tầng thứ ba là chỗ nhóm chọn kiểm chứng: đo được trên CPU, không cần GPU, không cần huấn luyện.

### 1.2 Tóm tắt bài báo (lời của nhóm)

**Luận điểm.** Bài báo không chọn "retargeter nào khớp khít nhất". Tác giả lập luận rằng **cách retarget quyết định việc policy tracking phía sau có học và sống sót được hay không**, nên phải đánh giá retargeter bằng chính policy chạy trên file retarget của nó. Ba câu hỏi: (i) chọn phương pháp retargeting có đổi hiệu năng policy không; (ii) artifact nào làm policy hỏng; (iii) các phương pháp giữ "dáng" nguồn tới mức nào.

**Cách làm.** Bốn nguồn retargeting — GMR, PHC, ProtoMotions, pipeline closed-source của Unitree — cùng xử lý **21 chuỗi LAFAN1**. Mỗi file retarget dùng để train **một policy riêng** bằng BeyondMimic (RL độc lập với các retargeter, không tinh chỉnh reward), trên **Unitree G1**. Đánh giá: sim gốc (100 rollout/policy), sim có ngẫu nhiên hoá động lực học (4096), sim2sim MuJoCo qua node ROS (100). Ba nhóm chỉ số: tỉ lệ thành công, sai số vị trí/góc body, ảnh hưởng frame bắt đầu; kèm user study 20 người.

**Kết quả.** GMR đạt tỉ lệ thành công rất cao (nhiều clip 100 % ở cả ba chế độ) nhưng **không tốt nhất mọi mặt**: bài báo tự ghi GMR chỉ đạt 51 % trên "Dance 5" ở sim2sim do giật khớp waist. Sai số bám quỹ đạo: GMR sau Unitree, trước PHC/ProtoMotions. Đổi frame khởi động có thể đổi tỉ lệ thành công từ 64 % lên 100 %. Artifact: PHC có ca xuyên sàn 60 cm, ProtoMotions có ca hai chân giao nhau, GMR có sudden jump dưới 2 % dataset.

**Phương pháp GMR.** Pipeline tối ưu hình học, **không huấn luyện**: mỗi frame xử lý tuần tự, frame trước làm điểm khởi tạo; khai báo ánh xạ key body người ↔ robot; căn rest pose Cartesian; **scale không đồng nhất theo từng body** (điểm khác biệt cốt lõi); IK tầng 1 ràng buộc hướng toàn bộ khớp + vị trí tay/chân; IK tầng 2 tinh chỉnh vị trí mọi key body. Solver dừng khi thay đổi hàm mục tiêu < 0,001 hoặc sau 10 vòng, kèm giới hạn khớp. Sau khi retarget cả chuỗi, tác giả trừ chiều cao body nhỏ nhất để chống bay/xuyên sàn. Hạn chế paper tự nêu: một nguồn dữ liệu, một robot, chưa xét tương tác, đôi khi vẫn phải chỉnh trọng số tay.

### 1.3 Khoảng trống nhóm bám vào

Paper **không công bố con số tốc độ nào**: không ms/frame, không FPS, không cấu hình CPU/GPU, không phiên bản IsaacSim/BeyondMimic/Mink, không commit repo. Ba bảng định lượng đều là kết quả **policy đã train**, cần GPU + IsaacSim + 84 policy — ngoài phạm vi 10 ngày, không phải "chưa làm" mà **không thể làm**. Ngược lại, README/mô tả repo tuyên bố retarget "in real time on CPU" — một tuyên bố đo được trên đúng laptop của nhóm. Nhóm chọn tuyên bố này, đồng thời trình bày đủ ba bảng paper và lý do không tái lập (phương án C, mục 2).

## 2. Tuyên bố cần kiểm chứng

### 2.1 Câu chốt

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm đo thời gian xử lý mỗi frame (`ms_per_frame`) khi retarget LAFAN1 (30 fps) sang Unitree G1 trên CPU, không bật `--rate_limit`; coi là tái lập được nếu trung vị `ms_per_frame` ≤ 33,33 ms, tức `fps_out` ≥ 30 và `realtime_factor` ≥ 1,00.**

Bốn điều bắt buộc ghi kèm:

1. **Nguồn tuyên bố là repo, không phải paper.** Paper không nói GMR real-time và không định nghĩa "real-time".
2. **Paper không có số** ⇒ giá trị gốc là **định tính**; không tồn tại sai số "so với paper", mọi so sánh tốc độ với paper là bịa.
3. **Ngưỡng 33,33 ms do nhóm đặt** (`1000/30`, từ tốc độ phát LAFAN1), chốt trước khi thấy số.
4. **Giai đoạn 1 chỉ đo `ms_per_frame_process`** bằng bản đo cũ `results/v3_runtime.csv` (13 cột, không có cột `ms_per_frame`); kết luận đi qua bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`; **cấm** quy đổi `0,92 ×`.

### 2.2 Vì sao chọn phương án C

Vì paper không có số tốc độ, nhóm cân nhắc: **A** chỉ đo real-time và ghi rõ paper không nêu; **B** chuyển sang Bảng II `E_g-mpbpe = 104,1 mm` (đúng chữ "số trong paper" nhưng gần chắc chắn thất bại, không tạo số đo mới); **C** = A + trình bày ba bảng paper và lý do không tái lập. **Chọn C** (DEC-01): thoả cả hai vế, chi phí gần bằng A, vẫn kết luận dứt khoát.

### 2.3 Hai đại lượng, tên phải đúng

`bvh_to_robot.py` chạy retarget và render trong cùng vòng lặp, nên `Actual rendering FPS` không phải throughput retargeting.

| Đại lượng | Đo gì | Vai trò |
|---|---|---|
| `ms_per_frame` | **chỉ** `retarget()` từng frame (probe, không viewer) | Đại lượng của tuyên bố |
| `ms_per_frame_process` | cả tiến trình: nạp BVH + init + viewer + retarget + render + ghi pkl | Cận trên bảo thủ; giai đoạn 1 chỉ có số này |
| `realtime_factor_process` | `(1000 / ms_per_frame_process) / fps_src` | Đọc kèm, không thay thế |

**Bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`** (vì thiếu số Nhóm A):

| Tình huống | Kết luận |
|---|---|
| `process` ≤ 33,33 ms | **Tái lập được** — điều kiện đủ (`retarget ≤ process`) |
| `process` > 33,33 **và** `ms_per_frame` ≤ 33,33 | Tái lập một phần |
| `process` > 33,33 **và** `ms_per_frame` > 33,33 | Không tái lập được (phải thử máy thứ hai) |
| `process` > 33,33, **không có** `ms_per_frame` | **Chưa kết luận được** — không được suy ra |

Ba mức chốt trước: `realtime_factor` ≥ 1,00 tái lập được · 0,80–0,99 một phần · < 0,80 không.

### 2.4 Bảng hai cột

| Đại lượng (điều kiện) | Bài báo | Nhóm đo được |
|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | **không đo** (bản đo cũ không có cột) |
| `ms_per_frame_process` (ms) | **không nêu** | **17,349** (trung bình, n = 5; sd 0,369; CV 2,13 %; trung vị 17,272) |
| `fps_out_process` (frame/s) | **không nêu** | **57,6** (suy ra `1000/17,349`) |
| `realtime_factor_process` (lần) | **không nêu** (chỉ chữ "real time") | **1,92** (`(1000/17,349)/30`) |
| V5 · T1 29dof · `_process` (ms) | **—** | **13,034** (trung vị, n = 5, CV 11,32 %) → 2,56 |
| V5 · G1 · `_process` (ms) | **—** | **16,758** (trung bình, n = 3, CV 4,59 %) → 1,99 |
| V5 · PM01 · `_process` (ms) | **—** | **34,975** (trung bình, n = 3, CV 3,01 %) → 0,95 |
| Success rate "Dance 5" sim2sim (%) | 51 (Bảng I, tr. 6) | **không đo** (ngoài phạm vi) |
| `E_g-mpbpe` mean GMR (mm) | 104,1 (Bảng II, tr. 6) | **không đo** (ngoài phạm vi) |
| Xuyên sàn PHC "Dance 1" (cm) | 60 (mục V-B, tr. 6) | **không đo** (ngoài phạm vi) |

Hai lưu ý: cột `realtime_factor` **trong CSV** là của từng lần chạy, không dùng để báo cáo; `walk1_subject1.bvh` dài **7.840 frame = 261,3 s**, **không phải** "Walk 1" của Bảng I (33 s).

**Quy tắc thống kê:** báo **trung bình** khi CV ≤ 5 %, báo **trung vị** khi CV > 5 % (theo `docs/dinh_nghia_phep_do.md` §4). Áp dụng: V3 17,349 (CV 2,13 %), G1 16,758 (4,59 %), PM01 34,975 (3,01 %) dùng mean; **T1 13,034 dùng median vì CV 11,32 % > 5 %** — trường hợp duy nhất CV > 5 %, ghi rõ để không bị coi là chọn số có lợi. **`sd` trong toàn báo cáo là độ lệch chuẩn mẫu, `ddof = 1`.**

**Mốc đối chiếu của repo.** README (bản `25f56db`) có mục *Speed Benchmark*: **35–45 FPS** trên Intel Core i9-13900K 24 nhân và **60–70 FPS** trên AMD Threadripper 7960X 24 nhân. Nhóm đo **57,6 FPS** trên i5-12450HX — nằm giữa hai mốc, cao hơn mốc i9. Đây là so sánh **tham khảo, không kiểm soát**: README không nêu motion/robot/clip, không nói có `--rate_limit` hay có tính render; `walk1_subject1` là đi bộ (nhẹ hơn dance/kungfu); GMR chạy tuần tự từng frame nên số core ít quyết định; và số của nhóm là **cả tiến trình** (đã gồm init + render + ghi pkl), tức nếu lệch thì nhóm bị **chậm đi**. Vì vậy **không** được kết luận "GMR nhanh hơn trên CPU yếu hơn"; kết luận vẫn chỉ dựa trên ngưỡng 33,33 ms.

### 2.5 Ba bảng của paper và vì sao không tái lập

| # | Bảng | Đại lượng | Giá trị GMR | Cần gì |
|---|---|---|---|---|
| 1 | I, tr. 6 | success rate (%) | 100 % "Dance 1"/"Dance 2"; **51 %** "Dance 5" sim2sim | IsaacSim + BeyondMimic + policy đã train + 100/4096/100 rollout |
| 2 | II, tr. 6 | `E_g-mpbpe`/`E_mpbpe` (mm), `E_mpjpe` (10⁻³ rad) | **104,1** / 28,1 / 561,7 | như trên, 100 rollout/policy; đo trên quỹ đạo policy |
| 3 | III, tr. 7 | success rate theo `start frame` | "Walk 2": **64 %** (frame 0) → 100 % (frame 7) | cùng policy đã train, đổi frame đầu |

**Bốn lý do không tái lập:** (1) phải train **84 policy** (21 × 4); (2) cần **IsaacSim + GPU** cho sim/sim-dr (4096 rollout); (3) sim2sim cần **node ROS + state estimation** của BeyondMimic; (4) paper **không công bố** hardware, phiên bản, commit ⇒ không dựng lại được môi trường kể cả có GPU. Ba bảng nằm ngoài phạm vi; cột "nhóm đo được" của ba dòng tương ứng để **"không đo"**.

### 2.6 Ba điều không được tuyên bố

Ba điều **không** được tuyên bố: GMR nhanh hơn PHC/ProtoMotions (không ai đo tốc độ các phương pháp kia); tái lập Bảng I/II (cần train RL); paper tuyên bố real-time (tuyên bố nằm ở README).

## 3. Nhật ký cài đặt

Nhật ký đầy đủ: `logs/nhat_ky_cai_dat.md` (15 mục + 4 FIX + MEDIA + RV-23), 6 log thô, `logs/lenh_da_chay.md`. Dưới đây là 7 sự cố ảnh hưởng tới số liệu hoặc kết luận.

### 3.1 Môi trường cuối cùng

| Mục | Giá trị |
|---|---|
| Máy / OS | LENOVO 83GS, Windows 11 Home Single Language 10.0.26300 |
| CPU / RAM / GPU | i5-12450HX 8 nhân/12 luồng · ~15,7 GiB · RTX 4050 Laptop 6 GiB (**render OpenGL; tính toán CPU**) |
| Conda / Python | conda 26.7.1 · Python 3.10.21, env `gmr` |
| Gói chính | `mujoco 3.17.0`, `mink 1.3.0`, `torch 2.14.1`, `smplx 0.1.28`, `daqp 0.11.2`, **`proxsuite 0.7.2.post1` (ghim)** |
| `requirements.txt` | 45 dòng từ `pip freeze` thật, có `-e git+…GMR@25f56db…` |
| Cổng G1 | `smplx_to_robot.py --help` exit 0, in 17 robot — **ĐẠT** |

### 3.2 Bảy sự cố

| # | Sự cố | Bằng chứng và cách xử lý |
|---|---|---|
| 1 | `proxsuite` không có wheel Windows | Pip build source 54,7 MB, `CMAKE_C_COMPILER not set` vì thiếu MSVC; bản 0.8.2 chỉ có sdist. Ghim `proxsuite==0.7.2.post1` (wheel `cp310-win_amd64`, 4,3 MB), cài lại exit 0; không sửa `pyproject.toml` vì solver mặc định là **daqp** |
| 2 | `libstdcxx-ng` chỉ có cho Linux | `PackagesNotFoundInChannelsError`; bỏ qua có ghi chép, kiểm chứng bù bằng việc chạy thật có mở cửa sổ MuJoCo |
| 3 | SMPL-X bị chặn bởi license | Repo không kèm body model; SMPL-X và AMASS/OMOMO phải ký license tại Max Planck. Chuyển sang `bvh_to_robot.py` + LAFAN1 (6 config `bvh_lafan1_*`); **V3/V5 đo trên đường BVH, không phải SMPL-X như paper** |
| 4 | KI-01: robot cúi gập | `walk4` có `waist_pitch` **+29,52 ± 1,70 độ**, so với walk3 **+25,19 ± 4,27 độ** và dance1 **+18,62 ± 8,70 độ**; scale 1,75/1,8 = 0,972 và hai khâu dùng cùng `g1_mocap_29dof.xml`. Kết luận: `walk4` là clip **đi khom lưng**, pipeline tái hiện trung thực; đổi motion chính thức sang `walk1_subject1` |
| 5 | KI-02: cột `cmd` ghi cờ chưa truyền | `measure_v3.ps1` chỉ ghép `--rate_limit` vào chuỗi CSV (dòng 20, 23), lệnh thật (dòng 26) không có cờ; log ghi 64–136 fps; `RateLimiter(30)` × 300 = 14,004 s = **21,42 Hz**. Xoá 4 dòng, rút kết luận về `--rate_limit` |
| 6 | RV-14: log không chứa số đo | Thêm dòng `END wall_s=137.37 ms_per_frame=17.522 rtf=1.902 …` vào từng log; lần đầu `-Encoding utf8` làm vỡ UTF-16LE → đổi `-Encoding Unicode`, chạy lại toàn bộ; **20/20 log đo** có `END` |
| 7 | Hai đợt V3 lệch 14,4 % | 15,171 → 17,349 ms (mean); **40 file pkl**, trong đó **37 file thuộc 4 cặp trùng hash tuyệt đối** (G1+walk1 ×20 `E7E3B906…`, T1 ×7 `4E716187…`, PM01 ×5 `57B693A8…`, G1+walk4 ×5 `37F0ACD2…`), **3 file lẻ một lần chạy** ⇒ chênh do trạng thái máy, không do thuật toán; chọn đợt mới vì log đối chiếu được |

**Bài học:** Review độc lập có giá trị bằng một người làm — sự cố (5) do Review phát hiện; và mỗi số trong CSV phải lần ngược được tới dòng `END` của chính lần chạy.

## 4. Kết quả chạy mô hình có sẵn, đối chiếu với bài báo

### 4.1 Thiết lập

- Input `walk1_subject1.bvh` — **7.840 frame, 30 fps, 261,333 s**; robot `unitree_g1` (29 DoF); **không** `--rate_limit`.
- Lệnh (nguyên văn cột `cmd`): `python scripts/bvh_to_robot.py --bvh_file ..\data\lafan1\walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/g1_walk1_subject1_run2.pkl`
- 1 warm-up (bị loại) + 5 lần đo, mỗi lần một process mới; wall-clock cả tiến trình chia 7.840 frame.
- Nguồn: `results/v3_runtime.csv` (**bản đo cũ, 13 cột**, chỉ `_process`), `results/v3_raw.csv`, log `results/logs/v3_walk1_subject1_run1..6.log`.

### 4.2 Từng lần chạy

| Lần | `phase` | `wall_clock_s` | `ms_per_frame_process` | Ghi chú |
|---|---|---|---|---|
| 1 | `warmup` | 132,473 | 16,897 | **bị loại** |
| 2 | `measure_1` | 137,370 | 17,522 | log `run2`, `END wall_s=137.37` |
| 3 | `measure_2` | 135,211 | 17,246 | log `run3` |
| 4 | `measure_3` | 139,960 | 17,852 | log `run4` |
| 5 | `measure_4` | 132,128 | 16,853 | log `run5` |
| 6 | `measure_5` | 135,413 | 17,272 | log `run6` |

n = 5: mean **17,349** (số dùng để kết luận), median 17,272, sd **0,369** (mẫu, `ddof = 1`), **CV 2,13 %** (≤ 5 %), biên độ 16,853–17,852; `fps_out_process` 57,6; `realtime_factor_process` **1,92**. Cả 5 giá trị đều < 20 ms nên kết luận không phụ thuộc chọn mean hay median. Không dùng cột `realtime_factor` từng dòng.

![Hình 1](results/figures/v3_ms_per_frame_g1_2026-11-20.png)

**Hình 1 —** Thời gian xử lý mỗi frame qua 5 lần đo V3 (G1, `walk1_subject1`); đường ngưỡng 33,33 ms. Nguồn: `results/v3_runtime.csv`.

### 4.3 Bằng chứng hình ảnh

Ngoài **Hình 1** (đồ thị ms/frame) và **Hình 2** (render G1 ở §5), `results/figures/` còn giữ ảnh terminal của lần đo, ảnh mở CSV và 3 khung 25/50/75 % của clip chính thức — caption và lệnh sinh ghi trong `results/figures/README.md`.

### 4.4 Đối chiếu với bài báo

Paper không có mốc tốc độ (`docs/paper_notes.md` §12), nên chỉ so được với **ngưỡng nhóm đặt**: 17,349 ms ≤ 33,33 ms ⇒ theo bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`, **tái lập được ở mức cả tiến trình** (điều kiện đủ: `retarget ≤ process`). Hai giới hạn phải nói cùng lúc: (a) **không** được nói "vòng lặp retarget đạt real-time" — bản đo cũ không có `ms_per_frame`, số 17,349 gồm init + viewer + render + ghi pkl, là **cận trên bảo thủ**; (b) sai số **giữa hai phiên ≈ 14 %**, lớn hơn CV trong phiên (2,13 %) ⇒ báo **17,3 ms** kèm sai số giữa phiên, không phải 17,35 ms chính xác đến 0,4 ms. Ba bảng paper **không đối chiếu được** và **không được đối chiếu** — chúng đo policy, không đo tốc độ.

### 4.5 Hạn chế phép đo

1. Chỉ có số **cả tiến trình**, là cận trên; không phải thời gian riêng `retarget()`.
2. **GPU (V7, `results/v7_gpu_check.csv`):** tính toán chạy **CPU** — `torch 2.14.1+cpu`, `cuda.is_available() = False`, `device_count = 0`; headless **2,359 ms/frame** (≈ **424 fps**). Render chạy **GPU thật qua OpenGL**: `GL_VENDOR = NVIDIA Corporation`, `GL_RENDERER = NVIDIA GeForce RTX 4050 Laptop GPU/PCIe/SSE2` (`tools/gl_info.py`); đặt `CUDA_VISIBLE_DEVICES=""` chỉ lệch 0,8 % (2,377 so với 2,359 ms). Chênh **~15 ms/frame** giữa V3 (17,349 ms, có viewer) và headless là **chi phí render trên GPU**, không phải GPU tính toán. Vì vậy **17,3 ms là cận trên của cả tiến trình có render GPU**, không phải "CPU-only" và cũng không phải throughput thuần `retarget()`; nhiệt GPU 51–57 °C ở V5 là do chính các lần chạy có viewer.
3. Một máy Windows 11, trong khi README chỉ test Ubuntu 22.04/20.04.
4. Đồng hồ Windows thô (hạt `sleep` ~15,6 ms) ảnh hưởng nhỏ với wall-clock; T1 trong V5 có CV 11,32 % > 5 % nên báo trung vị.

## 5. Kết quả tự huấn luyện (3 hạt giống)

GMR là **retargeting dựa trên tối ưu hình học**, không phải học tăng cường: không trọng số, không vòng huấn luyện, không hàm mất mát, **không có khái niệm seed**. Yêu cầu "train cấu hình nhỏ, 3 hạt giống, ghi đường cong" **không áp dụng** — không phải bỏ qua mà đối tượng huấn luyện không tồn tại. Phần RL duy nhất là **policy BeyondMimic** (Bảng I/II/III); muốn train thật phải có IsaacSim + GPU + 84 policy, ngoài phạm vi 10 ngày.

**Thay bằng 5 lần lặp thật.** Repo không có seed, nên nhóm dùng đúng 5 lần chạy độc lập đã có trong `results/v3_runtime.csv` (cùng input `walk1_subject1`, cùng G1, mỗi lần một process mới) — trình bày đầy đủ ở bảng §4.2 — để chứng minh pipeline **ổn định và tất định**, đáp ứng vượt mức yêu cầu "3 lần lặp".

5 lần đo chính thức: mean **17,349 ms**, median 17,272, sd **0,369** (mẫu, `ddof = 1`), **CV 2,13 %**. Nếu gộp cả warm-up (16,897): mean 17,274 — không đổi kết luận. Độ biến thiên **0,999 ms** giữa lần nhanh nhất và chậm nhất (16,853–17,852), tức **5,8 %** biên độ thô.

**Bằng chứng tất định:** 20 pkl của cặp G1 + `walk1_subject1` trong lô V3/V5 (6 lần V3, 4 lần V5, bản đầu, các bản cũ) có **cùng SHA256 `E7E3B906…`** — khác thời điểm chạy nhưng đầu ra giống nhau từng byte. Vì vậy dao động thời gian là **trạng thái máy**, không phải thuật toán; và không có "seed" nào có thể đổi kết quả.

**Kết luận mục 5:** không có đường cong học để trình bày vì không có quá trình học; ba seed không tồn tại để chạy. Phần thay thế là **5 lần lặp thật** ở trên, kèm bằng chứng bất biến SHA256. Muốn có 3 seed thật thì đối tượng phải là policy BeyondMimic — ngoài phạm vi giai đoạn 1.

![Hình 2](results/figures/slide_v3_walk1_g1_f900.png)

**Hình 2 —** Unitree G1 phát lại `walk1_subject1` tại frame 900 (giữa clip) — đầu ra của pipeline retarget, không phải ảnh minh hoạ. Trích từ `results/media/v3_walk1_g1.mp4`.

## 6. Sim2sim: bảng tụt hiệu năng, độ bền theo nhiễu, chất lượng ánh xạ và đồ thị

### 6.1 Mức 3: đổi embodiment

Đề tài chọn **sim2sim mức 3**: giữ simulator, **cùng motion → ≥ 3 robot**, không huấn luyện lại.

| Robot | `--robot` | DoF | Trạng thái |
|---|---|---|---|
| Unitree G1 | `unitree_g1` | 29 | đo được (n = 3) |
| Booster T1 29dof | `booster_t1_29dof` | 27 | đo được (n = 5) |
| ENGINEAI PM01 | `engineai_pm01` | 24 | đo được (n = 3) |
| Unitree H1 | `unitree_h1` | — | **bị chặn** (§6.6) |

### 6.2 Vì sao không dùng nhiễu vật lý (DEC-02)

Hướng dẫn môn mô tả sim2sim tối thiểu bằng **đổi tham số vật lý** (khối lượng ±20 %, ma sát, trễ 1–3 bước). Nhóm không lập bảng "tụt theo mức nhiễu vật lý" vì tham số vật lý **gần như không đi vào vòng tính** — đã kiểm chứng trực tiếp ở §6.2.1:

1. **Không có physics trong vòng tính.** Mỗi frame chỉ giải bài toán ngược trên vị trí/hướng khớp (Mink, ≤ 10 vòng); không tích phân lực, không ma sát, không lực tiếp xúc. Khối lượng khâu không xuất hiện trong hàm mục tiêu hay ràng buộc của IK (chỉ ảnh hưởng ở mức epsilon số thực — V7).
2. **Tham số vật lý gần như không đổi qpos — nhưng không phải "không đổi một byte" cho mọi tham số.** V7 (§6.2.1): **ma sát ×1,5** trên 72 geom → **SHA256 trùng tuyệt đối** baseline, `max|dq| = 0`; **khối lượng ±20 %** trên 31 thẻ inertial → **SHA256 khác** baseline nhưng `max|dq| = 1,5e-9 rad` (≈ 1e-7°), tức **chuyển động không đổi**, chỉ nhiễu số thực. Tính tất định với **cùng đầu vào** vẫn đúng: **37/40 file pkl thuộc 4 cặp trùng hash tuyệt đối**, 3 file lẻ một lần chạy.
3. **Bảng "tụt theo mức nhiễu vật lý" vẫn là bảng giả, nhưng lý do phải nói đúng:** ma sát không đổi gì; khối lượng ±20 % chỉ lệch **1,5e-9 rad**, không có xu hướng tụt theo mức. Nhóm từ chối lập bảng đó và thay bằng bốn phép thử nhiễu có tác dụng thật lên đầu vào bài toán ngược (DEC-02, `docs/v6_noise_spec.md`).

### 6.2.1 Kiểm chứng trực tiếp tham số vật lý (V7)

Nguồn: `results/v7_physics_perturb.csv` (nhánh `task/physics-perturb`), cùng `walk1_subject1` → G1; baseline `g1_walk1_subject1_run1.pkl` (`e7e3b906…`). Mỗi điều kiện sửa XML rồi chạy lại `tools/v7_run.py`:

| Điều kiện | Thay đổi | SHA256 pkl (rút gọn) | Giống baseline | `max\|dq\|` (rad) |
|---|---|---|---|---|
| baseline | — | `e7e3b906…` | — | 0 |
| ma sát ×1,5 | 72 geom | `e7e3b906…` | **có, tuyệt đối** | **0** |
| khối lượng ×1,2 | 31 thẻ inertial | `597d0402…` | không | **1,5e-9** |
| khối lượng ×0,8 | 31 thẻ inertial | `eecef802…` | không | **1,5e-9** |

**Kết luận V7:** ma sát **không vào vòng tính** (hash trùng tuyệt đối); khối lượng có vào nhưng chỉ ở mức **epsilon số thực** — `1,5e-9 rad ≈ 1e-7°`, không phải thay đổi chuyển động. Câu đúng là "**gần như không đổi**", không phải "không đổi một byte" cho mọi tham số: chỉ **ma sát** mới trùng byte; **khối lượng** đổi hash nhưng không đổi qpos ở mức có nghĩa.

### 6.3 Bốn phép thử

Input cố định `walk1_subject1.bvh` → `unitree_g1`; baseline là lần chạy sạch.

| # | Phép thử | Mức | Cách làm |
|---|---|---|---|
| N1 | Nhiễu khớp | σ ∈ {0,5; 1; 2; 5} độ | Cộng Gaussian vào mọi kênh rotation BVH |
| N2 | Trễ điều khiển | k ∈ {1; 2; 3; 5} frame | Dịch chuỗi frame đi k |
| N3 | Mất frame | p = 1 · 5 · 10 % | Bỏ ngẫu nhiên p %, nội suy tuyến tính |
| N4 | Lệch tỉ lệ người | ±10 · ±20 % | Scale chiều cao người |

Mỗi mức chạy **1 lần** vì đo **độ lệch có hệ thống**, không đo thời gian — **không** vi phạm hợp đồng 1+3. Năm chỉ số: `dq_mean` (°), `dq_max` (°), `dr_rmse` (mm), `pct_frames_gt5deg` (%), `still_converges` (0/1). Trước khi chạy, driver được kiểm chứng: chạy lại bản sạch cho `|Δq| = 0,0000°`, `dr_rmse = 0,000 mm` so với baseline.

**Giả thuyết:** retargeting giải **gần như độc lập** từng frame — frame trước chỉ là warm start, không phải ràng buộc tích lũy — nên sai số **không tích lũy theo thời gian**. Ngoại lệ đã biết: tại **frame biên** (ngay sau điểm dịch/nối clip), warm start có thể làm lệch cục bộ vài chục độ ở đúng một frame rồi tắt nhanh. Kết quả khác giả thuyết thì ghi đúng kết quả, không sửa số.

### 6.4 Kết quả

Nguồn: `results/v6_noise_sweep.csv` (đã merge vào `main`), log `results/logs/v6_*.log`, đồ thị `results/figures/v6_noise_vs_deviation.png`. Baseline `g1_walk1_subject1_run1.pkl` (`E7E3B906…`), 7.839 frame.

**Hai ghi chú kỹ thuật bắt buộc:**

- **Off-by-one frame:** baseline do `bvh_to_robot.py` ghi **7.839 frame** (repo `break` trước khi `append` nên mất frame cuối), còn driver V6 lưu đủ **7.840**. Mọi so sánh dùng trên **7.839 frame chung** nên không thiên vị; không có frame nào bị so lệch.
- **Phạm vi chỉ số `dq`:** `dq_mean` và `dq_max` chỉ tính trên **29 DoF khớp**, **không** gồm root rotation (root ghi riêng ở cột `dq_rootrot_mean`). σ của N1 là **per-channel** (từng trục rotvec), nên biên độ góc khớp thực tế xấp xỉ **σ√3** — cụm "ngưỡng hỏng nằm giữa 1° và 2°" phải đọc là **per-channel**, không phải biên độ khớp. Với N4, `dq_max` bị **frame 0** (warm start) phóng đại; bảng N4 vì thế thêm cột **`dq_max` bỏ frame 0** — giá trị trên 7.838 frame còn lại.

**N1 — nhiễu khớp:**

| σ (°) | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_frames_gt5deg` (%) | conv. |
|---|---|---|---|---|---|
| 0,5 | 0,56 | 7,56 | 1,20 | 0,51 | 1 |
| 1 | 1,10 | 14,11 | 1,56 | 5,55 | 1 |
| 2 | 2,18 | 25,80 | 2,02 | **87,74** | 1 |
| 5 | 5,41 | 63,89 | 3,52 | **100,00** | 1 |

**N2 — trễ (so đúng cặp frame):**

| k | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_frames_gt5deg` (%) | conv. |
|---|---|---|---|---|---|
| 1 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 2 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 3 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 5 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |

**N3 — mất frame:**

| p (%) | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_frames_gt5deg` (%) | conv. |
|---|---|---|---|---|---|
| 1 | 0,0033 | 6,83 | 0,17 | 0,013 | 1 |
| 5 | 0,0158 | 6,09 | 0,36 | 0,077 | 1 |
| 10 | 0,0355 | 10,99 | 0,62 | 0,306 | 1 |

**N4 — lệch tỉ lệ người:**

| Mức (%) | `dq_mean` | `dq_max` | `dq_max` bỏ frame 0 | `dr_rmse` (mm) | `pct_frames_gt5deg` (%) | frame bão hoà (Δ) |
|---|---|---|---|---|---|---|
| −20 | 1,86 | 29,65 | 29,65 | 718,53 | 90,43 | 1.819 (−46) |
| −10 | 0,73 | 19,27 | 15,82 | 358,57 | **6,37** | 1.793 (−72) |
| +10 | 1,88 | 33,32 | 18,37 | 359,32 | **94,77** | 2.002 (+137) |
| +20 | 3,14 | 42,82 | 31,91 | 718,51 | 98,05 | 2.166 (+301) |

![Hình 3](results/figures/v6_noise_slide.png)

**Hình 3 —** Độ lệch khớp trung bình, tỉ lệ frame có khớp lệch > 5°, và số frame chạm giới hạn khớp theo 15 mức nhiễu N1–N4 (baseline 1.865 frame). Nguồn: `results/v6_noise_sweep.csv`.

**Năm nhận xét:**

1. **N1 — trung bình gần tuyến tính, chỉ số ngưỡng bùng nổ phi tuyến.** `dq_mean` 0,56 → 1,10 → 2,18 → 5,41°; `pct_frames_gt5deg` 0,51 → 5,55 → 87,74 → 100 %. Vì là chỉ số **ngưỡng**: khi sai số trung bình chạm ~2° thì gần như mọi frame có ít nhất một khớp vượt 5°. **Ngưỡng hỏng nằm giữa σ = 1° và 2° (per-channel, tức biên độ khớp thực ≈ 1,7°–3,5°).** Frame bão hoà: 1.875 / 1.910 / 2.122 / 3.550 (baseline 1.865).
2. **N2 — trễ chỉ lệch pha, không sai tư thế.** `dq_mean` = 0,0010°, `dr_rmse` = 0,03 mm ≈ 0 với mọi **k ∈ {1; 2; 3; 5}**. Ngoại lệ: đúng **1 frame biên** (0,013 % ≈ 1/7.839) lệch tới 36°, rồi **tắt dần** (0,31° → 0,10° → 0,05° → 0,02°): tại frame biên IK khởi tạo từ nghiệm frame trước nên phụ thuộc trạng thái khởi tạo — **hiệu ứng biên cục bộ**, không phải tích lũy. Nếu so lệch frame, `dq_mean` sẽ rất lớn và kết luận "trễ làm hỏng tư thế" là **sai phương pháp**.
3. **N3 — mất frame gần như vô hại.** `dq_mean` 0,0033 → 0,0355°, `pct` ≤ 0,31 % vì frame thiếu được nội suy tuyến tính.
4. **N4 — nguy hiểm nhất và bất đối xứng.** ±10 %: **6,37 %** (co) vs **94,77 %** (giãn); ±20 %: 90,43 % và 98,05 %. `dq_max` sau khi **bỏ frame 0** còn **29,65 / 15,82 / 18,37 / 31,91°** (−20 / −10 / +10 / +20 %) — vẫn bất đối xứng, giãn nặng hơn co. **Đọc phần chênh, không đọc trị tuyệt đối:** bản sạch đã có **1.865/7.839 frame (23,8 %)** chạm giới hạn, chủ yếu `waist_pitch` (745 frame); so baseline, +10 % là +137, +20 % là +301, −10 % là −72, tập trung ở `ankle_roll`. Chênh cỡ 10² frame **không đủ** giải thích 6,4 % vs 94,8 %; phần còn lại là **hình học tay/chân không với tới đích khi người cao hơn robot** — định tính, chưa tách định lượng.
5. **`dr_rmse` 359/719 mm của N4 KHÔNG phải sai tư thế.** Con số **đối xứng theo |mức|** (−10: 358,57 · +10: 359,32 · −20: 718,53 · +20: 718,51), tỉ lệ với độ lớn scale, không phụ thuộc dấu ⇒ **quỹ đạo gốc bị scale**, không phải retarget hỏng dáng. Sai tư thế thật nằm ở `dq_mean`/`pct_frames_gt5deg`, và hai chỉ số đó **bất đối xứng**. **Cấm** viết "N4 làm retarget hỏng, lệch 719 mm".

**Kết luận §6.4:** IK hội tụ **15/15** mức, không NaN/phân kỳ. Vô hại: trễ đúng pha (N2), mất frame ≤ 10 % (N3). Làm hỏng: nhiễu khớp từ **σ = 2° mỗi kênh** (biên độ khớp thực ≈ 3,5°), lệch tỉ lệ từ **±10 %** (N4, giãn nặng hơn). Cơ chế: sai số **không tích lũy theo thời gian** — chỉ **một frame biên** chịu trạng thái khởi tạo của IK rồi tắt nhanh; các mức hỏng còn lại do **bão hoà giới hạn khớp** (một phần) và **hình học tay/chân không với tới đích** (phần còn lại). Kết quả này **không đổi** kết luận tốc độ ở mục 7; nó thêm trục độ bền đầu vào.

### 6.5 Tụt hiệu năng theo robot

Nguồn `results/v5_sim2sim.csv` (thô `v5_raw.csv`; log `v5_<robot>_…`), bỏ warm-up:

| Robot | DoF | n | Thống kê dùng | Giá trị ms | CV | rtf | So ngưỡng 33,33 ms |
|---|---|---|---|---|---|---|---|
| Booster T1 29dof | 27 | 5 | **trung vị** (CV > 5 %) | **13,034** | 11,32 % | **2,56** | đạt, dư 20,3 ms |
| Unitree G1 | 29 | 3 | trung bình | **16,758** | 4,59 % | **1,99** | đạt, dư 16,5 ms |
| ENGINEAI PM01 | 24 | 3 | trung bình | **34,975** | 3,01 % | **0,95** | **vượt 1,7 ms (5,0 %)** |
| Unitree H1 | — | — | — | — | — | — | bị chặn (§6.6) |

Quy tắc chọn: theo `docs/dinh_nghia_phep_do.md`, dùng **trung bình**; chỉ dùng **trung vị** khi CV > 5 % — ở đây chỉ T1 vượt ngưỡng (11,32 %), nên T1 báo trung vị 13,034 còn G1/PM01 báo trung bình. PM01 **ít khớp nhất nhưng chậm nhất**: **34,975 ms (mean)** so với **13,034 ms (median)** của T1; nếu so **cùng mean** thì PM01 chậm **2,8 lần** T1 ⇒ nguyên nhân **không phải** số DoF. Ba giả thuyết (chưa tách): cấu hình IK nhiều key body hơn; số vòng solver chạm trần 10 nhiều hơn; mô hình MJCF/mesh nặng hơn. Thứ tự chạy đã kiểm soát (PM01 chạy đầu, nhiệt GPU 51–57 °C). G1 trong V5 là **16,758 ms (−3,4 % so với V3 17,349)** — mức chênh này là **sai số giữa phiên** đã nêu ở §4.4, không phải tụt hiệu năng do đổi robot. PM01 vượt ngưỡng ở mức **cả tiến trình**; theo §6.1 của định nghĩa phép đo, vì không có `ms_per_frame`, trạng thái đúng là **"chưa kết luận được"** — không được nói "PM01 không đạt real-time".

![Hình 4](results/figures/v5_ms_per_frame_robots_2026-11-20.png)

**Hình 4 —** ms/frame theo robot trong V5 (thanh sai số min–max); đồ thị dùng **trung vị** cho T1 (CV > 5 %) và **trung bình** cho G1/PM01 (CV ≤ 5 %). **G1 trung vị 17,018 ms (rtf 1,96); bảng §6.5 dùng trung bình 16,758 ms (rtf 1,99) theo quy tắc CV.** Nguồn: `results/v5_sim2sim.csv`.

### 6.6 Vì sao H1 bị chặn

Ba nguồn: (a) `--robot unitree_h1` → `invalid choice`, **exit 2** (argparse, trước khi nạp model); (b) không có `ik_configs/bvh_lafan1_to_h1.json` (chỉ 6 config `bvh_lafan1_*`); (c) README để cột BVH của H1 là **TBD**. Đường SMPL-X có H1 nhưng bị license chặn. Lý do gốc: danh sách `--robot` sinh từ `IK_CONFIG_DICT["bvh_lafan1"]`.

### 6.7 Chất lượng ánh xạ (3 robot)

Nguồn: `results/v6_quality.csv` (đã merge vào `main`), cùng `walk1_subject1`, 3 pkl V5 `run1`, **7.839 frame** (khớp off-by-one ở §6.4).

| Robot | `foot_slide` proxy TB (mm/s) | Trái / Phải | `min_body_height` (gốc body thấp nhất, mm) | delta so vị trí nghỉ (mm) | `pct_frames_penetration` (%) | Frame khớp sát giới hạn (%) |
|---|---|---|---|---|---|---|
| Unitree G1 | **49,0** | 62,1 / 36,0 | **+9,9** | **−6,3** | **0,00** | 23,79 |
| Booster T1 29dof | 83,1 | 63,2 / 103,1 | **−7,6** | **−44,3** | **2,13** | **43,32** |
| ENGINEAI PM01 | **118,4** | 94,5 / 142,3 | +43,8 | **−1,1** | 0,00 | 24,07 |

**Công thức `foot_slide`.** Với mỗi bàn chân, một frame là **tiếp đất** khi `z_bàn_chân − min(z_bàn_chân) ≤ 30 mm`; `foot_slide` = **tổng dịch ngang `|Δxy|` trên các cặp frame liên tiếp cùng tiếp đất chia tổng thời gian tiếp đất**. Tính riêng chân trái và chân phải rồi lấy trung bình; đo tại **gốc (tâm) body bàn chân**.

**Cột `pct_frames_penetration` là % frame có ÍT NHẤT MỘT BODY có gốc dưới −1 mm** (`xpos[1:,2] < −1 mm`, lấy min trên **mọi body**, không riêng thân); đây là **proxy**, không phải đo bề mặt/mesh, nên **không được đọc là bằng chứng không xuyên sàn**.

![Hình 5](results/figures/v6_quality.png)

**Hình 5 —** `foot_slide` trung bình (chấm là trái/phải) và `min_body_height` (gốc body thấp nhất) của 3 robot; **đường đỏ nét đứt là mặt đất z = 0**; **đường chấm đen là độ cao gốc body thấp nhất ở tư thế nghỉ của từng model**. Nguồn: `results/v6_quality.csv`.

**Ngưỡng đặt trước và quyết định hậu kiểm (DEC-03).** Theo **DEC-03** (`docs/quyet_dinh.md`): `docs/dinh_nghia_phep_do.md` §1.2 đã **đặt trước ngày 2026-11-20** hai ngưỡng — `foot_slide ≤ 50 mm/s` và `min_body_height ∈ [−5, +5] mm`. Nhóm **giữ và áp** ngưỡng `foot_slide`: G1 **49,0 mm/s đạt sát**; T1 **83,1** và PM01 **118,4 mm/s không đạt**. Nhóm **rút** ngưỡng `min_body_height` bằng **quyết định hậu kiểm ngày 2026-11-21** vì đại lượng đo **gốc của body thấp nhất** trên mọi body, mà mỗi model có offset nghỉ riêng (G1 **+16,1** · T1 **+36,7** · PM01 **+45,0 mm**). Hai đại lượng thay thế — **delta so vị trí nghỉ** (G1 **−6,3** · T1 **−44,3** · PM01 **−1,1 mm**) và **`pct_frames_penetration`** (0,00 / 2,13 / 0,00 %) — là **hậu kiểm, không có ngưỡng**. Tóm lại: **một ngưỡng được áp dụng, một ngưỡng bị rút sau khi đo.**

**Xếp hạng:** **G1** — `foot_slide` thấp nhất **49,0 mm/s**, **đạt sát ngưỡng 50 mm/s**; 0,00 % frame có body nào có gốc dưới −1 mm; 23,79 % frame khớp sát giới hạn. **T1** — `foot_slide` **83,1 mm/s không đạt** ngưỡng đặt trước; **2,13 % frame có ít nhất một body có gốc dưới −1 mm**; tỷ lệ frame khớp sát giới hạn cao nhất **43,32 %**. **PM01** — `foot_slide` cao nhất **118,4 mm/s, gấp 2,4 lần G1, không đạt** ngưỡng đặt trước; 0,00 % frame có body nào có gốc dưới −1 mm.

**`foot_slide` là chỉ số proxy — hai giới hạn phải đọc kèm:** (a) "tiếp đất" được định nghĩa theo **điểm thấp nhất của chính bàn chân đó**, không theo mặt đất; (b) phép đo lấy tại **gốc (tâm) body bàn chân**, nên khi bàn chân lăn gót–mũi thì tâm vẫn dịch ngang dù chân đứng yên. Vì vậy 49 / 83 / 118 mm/s **chỉ dùng để so sánh tương đối giữa 3 robot** và để áp ngưỡng 50 mm/s đặt trước, **không** được viết là "trượt chân tuyệt đối". Độ nhạy của phép đo rất lớn: **theo phép đo lại ở `tools/README.md` (đo tại ngón chân), không lưu trong `results/`**, con số đổi thành **84,3 và 169,2 mm/s** (hai robot), tức có thể gấp đôi.

**`min_body_height` đo ở gốc của body thấp nhất, không so tuyệt đối giữa robot:** mỗi model có offset nghỉ riêng — **G1 +16,1 mm · T1 +36,7 mm · PM01 +45,0 mm**. Con số **+43,8 mm của PM01 không có nghĩa "sạch nhất"**, nó chỉ là offset nghỉ của model; tương tự, −7,6 mm của T1 phải đọc cùng offset. Báo cáo vì thế đọc thêm **delta so vị trí nghỉ** ở bảng trên, và chỉ gọi `pct_frames_penetration` là **% frame có ít nhất một body có gốc dưới −1 mm**, **không** kết luận về bề mặt/mesh.

**Hai đại lượng hậu kiểm (DEC-03) không có ngưỡng đặt trước:** `delta so vị trí nghỉ` và `pct_frames_penetration` được thêm **sau khi đo**, nên chỉ dùng để **so sánh giữa 3 robot**, **không** được viết "đạt" hay "không đạt". Ngược lại, `foot_slide` **có** ngưỡng đặt trước 50 mm/s và **đã được áp**; chỉ số này mới là căn cứ kết luận "đạt/không đạt" của phần chất lượng.

**Không phải kiểm chứng chéo:** tỷ lệ frame khớp sát giới hạn của G1 (**23,79 %**) trùng với baseline nhiễu V6 (**1.865/7.839 = 23,79 %**) vì `quality_metrics.py` và `v6_metrics.py` dùng **cùng logic, cùng ngưỡng 0,5°** trên **cùng một pkl** — đây là **cùng một phép đo**, không phải hai công cụ độc lập. Việc trùng khớp chỉ xác nhận hai script nhất quán với nhau.

### 6.8 Đồ thị và video

Năm hình đã chèn trong báo cáo: **H1** `v3_ms_per_frame_g1` (§4.2), **H2** render G1 `slide_v3_walk1_g1_f900` (§5), **H3** `v6_noise_slide` (§6.4), **H4** `v5_ms_per_frame_robots` (§6.5), **H5** `v6_quality` (§6.7); nguồn và nội dung ghi ngay dưới mỗi hình.

Video: `results/media/v5_sim2sim_g1_t1_pm01.mp4` (60 s, 1280×720, 30 fps) và **video demo tổng hợp 67 giây, 720p, không audio** (`results/media/demo/demo_v6_720p.mp4`); cả hai **không commit**, nộp kèm link. **Link nộp:** https://github.com/mtzwyu/GMR-Humanoid-Retargeting-Benchmark/releases/tag/v1.0-demo — release gồm **5 file**: `s1_human_input`, `v3_walk1_g1`, `v3_walk4_g1`, `v5_sim2sim_g1_t1_pm01`, `demo_v6_720p` (bản đúng 67 s).

## 7. Kết luận

### 7.1 Câu kết luận

> **Tuyên bố thời gian thực tái lập được trên CPU (1,92× ngưỡng đặt trước); chất lượng ánh xạ chỉ tái lập một phần (1/3 robot đạt ngưỡng `foot_slide`, một robot xuyên sàn 2,13% frame).** Phần **thời gian thực** kiểm chứng được ở mức **cả tiến trình**: `ms_per_frame_process` = **17,3 ms** (trung bình, n = 5, CV 2,13 %), `realtime_factor_process` = **1,92**, theo **bản đo cũ 13 cột**. Áp bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md` với ngưỡng 33,33 ms → **tái lập được ở mức cả tiến trình** (điều kiện đủ). `ms_per_frame` (chỉ vòng retarget) **không đo được** vì bản đo cũ không có cột đó. Phần **bảng số của paper** (I, II, III) **không tái lập được** — đo policy đã train trong IsaacSim, cần GPU + 84 policy; số 104,1 mm của Bảng II chỉ nằm ở cột "bài báo", không đối chiếu với số nào nhóm đo.

**Vì sao không dùng một nhãn chung (DEC-04).** Tiêu chí **đặt trước** chỉ phủ vế **tốc độ** (`realtime_factor ≥ 1,00`), nên vế đó giữ nguyên nhãn **"tái lập được"**. Vế **chất lượng ánh xạ** được đo **sau**, trong hai ngưỡng đặt trước ngày 2026-11-20 chỉ có `foot_slide ≤ 50 mm/s` áp cho cả 3 robot, và kết quả chỉ **1/3 robot đạt** — T1 xuyên sàn **2,13 % frame** — nên vế này là **"một phần"**. Dùng một nhãn chung sẽ hoặc hạ nhãn tuyên bố chính, hoặc nâng nhãn vế chất lượng; cả hai đều sai. V5 củng cố vế tốc độ: 2/3 robot dưới ngưỡng (T1 13,034 → 2,56; G1 16,758 → 1,99); PM01 34,975 → 0,95 nhưng **"chưa kết luận được"** theo §6.1. Vế chất lượng (§6.7): `foot_slide` là ngưỡng **duy nhất còn giữ và đã áp** — G1 **49,0 mm/s đạt sát**, T1 **83,1** và PM01 **118,4 mm/s không đạt**; `min_body_height ±5 mm` đã **rút bằng DEC-03 (2026-11-21)**, thay bằng delta so vị trí nghỉ (**−6,3 / −44,3 / −1,1 mm**) và `pct_frames_penetration` (**0,00 / 2,13 / 0,00 %**).

### 7.2 Điều kiện để câu trên đứng vững

1. Số 17,349 (trung bình, CV 2,13 % ≤ 5 %) lấy từ bản đo cũ đã Review PASS; không trộn đợt cũ `c62e74f` (15,171).
2. Ngưỡng 33,33 ms chốt trước, không đổi sau khi thấy số.
3. Không dùng "tái lập được" cho toàn bộ paper — chỉ vế tốc độ; ba bảng I/II/III của paper ngoài phạm vi.
4. Không nói "retarget đạt real-time"; muốn chắc phải chạy probe `measure_runtime.py` (@`5f9cdd5`) — **chưa làm**. Tính toán chạy CPU (headless **2,36 ms/frame**); **17,3 ms là cả tiến trình có render GPU**, nên là cận trên.
5. Kết quả nhiễu (§6.4) không đổi kết luận tốc độ; nó chỉ thêm nhận định về độ bền.
6. V7 (§6.2.1) xác nhận trực tiếp: ma sát ×1,5 trùng hash tuyệt đối; khối lượng ±20 % chỉ lệch `1,5e-9 rad` — tham số vật lý gần như không vào vòng tính, nên không có bảng tụt theo mức.

**Vì sao tách nhãn thay vì hạ nhãn tuyên bố chính?** `realtime_factor_process` = 1,92 ≥ 1,00 nên theo tiêu chí đặt trước, vế tốc độ **tái lập được**; hạ xuống "một phần" sẽ là sửa tiêu chí sau khi thấy kết quả. Vế chất lượng chỉ đạt một phần vì **1/3 robot đạt `foot_slide`** và T1 xuyên sàn **2,13 % frame** — hai vế mang hai nhãn riêng (DEC-04).

### 7.3 Ba câu "chênh thì vì sao"

**(a) Hai đợt V3 lệch 14,4 % — do máy, không do thuật toán.** 15,171 → 17,349 ms (mean), cùng máy/input/commit. **37/40 file pkl thuộc 4 cặp trùng SHA256 tuyệt đối** (3 file lẻ một lần chạy) ⇒ cùng đầu ra từng byte mà thời gian khác 14 % ⇒ môi trường chạy. Đợt mới chậm hơn nên chọn là bảo thủ.

**(b) PM01 chậm nhất dù ít khớp nhất.** 24 DoF / 34,975 ms vs 27 DoF / 13,034 ms. Số DoF không giải thích; ba giả thuyết IK/solver/model chưa tách. Đã kiểm soát thermal (PM01 chạy đầu).

**(c) Nhóm vs paper — không có mốc.** Paper không công bố ms/FPS/hardware, nên câu đúng là "không có số của paper để chênh"; mốc duy nhất là ngưỡng nhóm đặt.

### 7.4 Thiếu sót phải nêu

- Chất lượng ánh xạ: **hai ngưỡng đặt trước ngày 2026-11-20**; `foot_slide ≤ 50 mm/s` **được giữ và áp** (G1 49,0 đạt sát; T1 83,1 và PM01 118,4 không đạt), `min_body_height ±5 mm` **rút hậu kiểm** (DEC-03, 2026-11-21) vì đo gốc body và offset nghỉ khác nhau; `pct_frames_penetration` chỉ là proxy gốc body, không phải bề mặt/mesh. Hai đại lượng hậu kiểm không có ngưỡng đặt trước (§6.7).
- `ms_per_frame` **chưa đo**; chỉ có số cả tiến trình (§4.5).
- Bản đo cũ V3 **không ghi** `CUDA_VISIBLE_DEVICES`; V7 đã kiểm lại (đặt rỗng, lệch 0,8 %, cùng SHA256).
- Kết quả trên **một máy Windows**, không đại diện Linux.
- Bất đối xứng N4 mới giải thích **định tính**, chưa định lượng phần đóng góp.
- Ba bảng I/II/III của paper **ngoài phạm vi**.

## 8. Phân công công việc và tự thuật từng thành viên

### 8.1 Bảng phân công

| # | Thành viên | MSSV | Vai trò | Nhánh đã làm | Sản phẩm chính | Bằng chứng |
|---|---|---|---|---|---|---|
| 1 | Trần Nguyễn Khánh Duy | 2001230120 | Planner · Research · Writing | `task/v1-tuyen-bo`, `task/v1-speed-benchmark`, `task/dinh-nghia-v14`, `task/v6-bao-cao`, `task/pdf-build` | `v1_tuyen_bo.md`, `paper_notes.md`, `dinh_nghia_phep_do.md` (v1.5), `quyet_dinh.md` (DEC-01…04), mục 1–2–7 | 4 quyết định có ngày; Review PASS |
| 2 | Đặng Duy Mạnh | 2001240271 | Run · Evidence · Writing 3 | `task/v2-cai-dat`, `v3-runtime`, `v5-sim2sim`, `v6-noise`, `quality`, `h1-xsens`, `tools-va-evidence`, `physics-perturb`, `provenance-utf8`, `demo-video` | nhật ký 15 mục, `lenh_da_chay.md`, `requirements.txt`, CSV V3/V5/V6/V7, ảnh, video | 20/20 log `END`; hash 56 pkl; V7 |
| 3 | Trương Thái Vỹ | 2001240577 | Code · Video · Writing 5 | `task/code-scripts` → `code-scripts3`, `code-demo`, `demo-v6table`, `readme`, `slide-fix` | `scripts/measure_runtime.py`, `scripts/build_demo.py`, `NOTES.md`, mục 5, slide 13 | 12 test PASS; video 77 s |
| 4 | Hà Mạnh Trường | 2045240326 | Review · Writing 6 | `task/review-qa` | `review_notes.md`, checklist 5 điểm, **50 mã RV** (RV-01…RV-50) | 23 PR; RV-13 phát hiện cờ giả |

### 8.2 Tự thuật

Bản nháp được viết lại từ nhật ký làm việc và lịch sử commit của nhóm.

#### 8.2.1 Trần Nguyễn Khánh Duy — MSSV 2001230120 — Nhóm trưởng, Planner + Research — 30%

Tôi phụ trách đọc bài báo và chốt tuyên bố cần kiểm chứng. Khó nhất là phát hiện paper arXiv:2510.02252 **không công bố số ms/frame hay FPS nào** — mọi bảng số đều là kết quả policy đã huấn luyện, cần GPU và IsaacSim. Tôi chọn phương án C: đo tuyên bố "real-time trên CPU" lấy từ README, trình bày rõ ba bảng định lượng của paper và tách kết luận thành hai vế thay vì né tránh. Trước khi ai chạy lần nào, tôi viết `docs/dinh_nghia_phep_do.md` quy định đo gì, lấy mấy lần, và chọn `mean` hay `median` theo CV — quy tắc đó về sau phải áp lại ba lần vì có ba nơi dùng sai. Bài học lớn nhất: tôi đọc thiếu phần cuối README nên bỏ sót bảng Speed Benchmark của chính repo, và chỉ biết khi người khác soi lại.

#### 8.2.2 Đặng Duy Mạnh — MSSV 2001240271 — Run, dựng môi trường và thu bằng chứng — 30%

Tôi là người cài và chạy GMR trên Windows. Khó nhất là `proxsuite` fail vì thiếu MSVC nên phải ghim `0.7.2.post1`, rồi phát hiện SMPL-X yêu cầu license và chuyển sang BVH LAFAN1 — quyết định đó cứu cả đề tài. Khi người xem báo robot cúi gập người, tôi đo góc khớp ba clip và tìm ra `walk4_subject1` vốn là clip đi khom lưng của LAFAN1: pipeline không sai, nó tái hiện trung thực. Việc khó nhất về tinh thần là tự phát hiện bốn dòng CSV ghi cờ `--rate_limit` chưa từng được truyền và báo lại để rút kết luận. Sau đó tôi chạy thật phép thử đổi khối lượng ±20% và ma sát; kết quả buộc nhóm bỏ câu "không đổi một byte" cho khối lượng, vì hash đổi dù chuyển động chỉ lệch 1,5e-9 rad.

#### 8.2.3 Trương Thái Vỹ — MSSV 2001240577 — Code, công cụ đo và dựng video — 20%

Tôi viết `scripts/measure_runtime.py` và `scripts/build_demo.py`. Khó nhất ở script đo là tách đúng hai đại lượng — thời gian riêng của `retarget()` và thời gian cả tiến trình — vì ban đầu nhóm gọi lẫn tên khiến một phép đo đúng bị hiểu sai; tôi thêm cột `retarget_cmd` để người review tái lập được, và làm `--dry-run` để kiểm logic mà không cần môi trường GMR. Khi dựng video, tôi vấp ffmpeg 9 vì bản này đã bỏ `-vsync`, và mất một lúc mới hiểu `drawtext` trên Windows phải escape đường dẫn font. Sau khi xem lại bản render đầu, tôi bỏ phụ đề gọi "ms/frame" trần và bỏ nhánh dự phòng lấy ảnh robot cho cảnh chuyển động người, vì cả hai đều làm người xem hiểu sai bản chất phép đo.

#### 8.2.4 Hà Mạnh Trường — MSSV 2045240326 — Review, phản biện độc lập — 20%

Tôi phụ trách phản biện, và nguyên tắc là chỉ đọc cái đã nằm trong nhánh, không nghe mô tả. Việc đáng kể nhất là bốn dòng CSV ghi lệnh có `--rate_limit` trong khi lệnh thật không hề truyền: tôi xác nhận bằng ba nguồn độc lập — đọc mã PowerShell, đối chiếu log ghi 64 FPS, và chạy lại thư viện được 21,4 Hz. Tôi cũng bắt việc đặt tên `joint_limit_violation` cho một chỉ số thực chất chỉ là "khớp nằm sát giới hạn", và bác bỏ câu "hai công cụ độc lập cho cùng kết quả" vì hai script dùng chung logic trên cùng tệp. Ngoài ra tôi chỉ ra `foot_slide` chỉ là proxy, `min_body_height` phụ thuộc offset nghỉ, và `dq_max` bị frame 0 làm phóng đại. Bài học: review không phải đọc lại cho kỹ, mà là chủ động tìm cách bác bỏ con số của chính nhóm mình.

Mọi số truy ngược được tới `results/` và dòng `END`; mọi số paper nằm ở cột "bài báo"; video/pkl/LAFAN1 không commit.

# TÀI LIỆU THAM KHẢO

1. J. P. Araújo, Y. Ze, P. Xu, J. Wu, C. K. Liu. *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking*. arXiv:2510.02252v1, 2025. https://arxiv.org/abs/2510.02252
2. YanjieZe. *GMR: General Motion Retargeting*, commit `25f56db`, 2026-10-22 UTC, giấy phép MIT. https://github.com/YanjieZe/GMR
3. Ubisoft La Forge. *LAFAN1 Animation Dataset*, CC BY-NC-ND 4.0. https://github.com/ubisoft/ubisoft-laforge-animation-dataset
4. Thư viện dùng trong pipeline: MuJoCo 3.17 (Todorov et al., IROS 2012), Mink 1.3 (https://github.com/kevinzakka/mink), BeyondMimic (https://github.com/HybridRobotics/BeyondMimic), QPSolvers 4.13 với `daqp` 0.11.2 và `proxsuite` 0.7.2.post1.
5. Tài liệu nội bộ: `docs/v1_tuyen_bo.md`, `docs/dinh_nghia_phep_do.md`, `docs/paper_notes.md`, `docs/quyet_dinh.md`, `docs/v6_noise_spec.md`, `logs/nhat_ky_cai_dat.md`.
