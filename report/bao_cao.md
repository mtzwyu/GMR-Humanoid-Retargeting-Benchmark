# BÁO CÁO GIAI ĐOẠN 1 — GMR: ÁNH XẠ CHUYỂN ĐỘNG NGƯỜI SANG ROBOT HÌNH NGƯỜI THEO THỜI GIAN THỰC

**Trường Đại học Công Thương TP. HCM · Khoa Công nghệ Thông tin**
**Lớp 15DHTH07 · HK1 2026–2027 · Nhóm 01 · Đề tài HR04**

| Hạng mục | Giá trị |
|---|---|
| Repo / commit | `YanjieZe/GMR` @ `25f56db` (2026-10-22) · LICENSE MIT |
| Bài báo | *Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking*, arXiv:2510.02252v1, 9 trang, CC BY 4.0 |
| Dữ liệu đo | LAFAN1 (Ubisoft), BVH 30 fps, CC BY-NC-ND 4.0 — học thuật, không phân phối lại |
| Máy đo | LENOVO 83GS · i5-12450HX (8 nhân/12 luồng) · ~15,7 GiB RAM · Windows 11 · **CPU** |
| Phạm vi | Chạy retargeting có sẵn, đo tốc độ, sim2sim 3 robot + 4 phép thử nhiễu; **không** train RL, **không** robot thật |

> **Quy ước.** Mọi số của nhóm nằm ở cột "nhóm đo được", mọi số của paper nằm ở cột "bài báo". Hai cột không trộn, không suy diễn. Số không tự đo thì ghi **"không đo"** kèm lý do.

## 1. Giới thiệu bài toán và tóm tắt bài báo

### 1.1 Bài toán

**Retargeting** nhận quỹ đạo chuyển động của người (mocap) và sinh quỹ đạo khớp (`qpos`) cho robot hình người, sao cho giữ được "dáng" chuyển động gốc mà vẫn thoả ràng buộc của robot. Bài toán khó ở ba tầng:

1. **Sai khác hình thái.** Người và robot khác nhau về số bậc tự do, tỉ lệ chiều dài khâu, giới hạn khớp và tư thế nghỉ. Ánh xạ thẳng góc khớp là vô nghĩa; ánh xạ thẳng vị trí tuyệt đối thì vi phạm giới hạn khớp.
2. **Ràng buộc vật lý.** Kết quả phải không xuyên sàn, không bay, không tự cắt, không giật khớp — những lỗi mắt người thấy ngay nhưng khó gói vào một hàm mục tiêu.
3. **Thời gian thực.** Với teleoperation, retargeting phải nhanh ít nhất bằng tốc độ phát dữ liệu nguồn (LAFAN1 30 fps ⇒ 33,3 ms/frame). Chậm hơn thì chỉ phát lại được, không điều khiển được.

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

> **GMR tuyên bố retarget chuyển động người sang humanoid "theo thời gian thực trên CPU". Nhóm đo thời gian xử lý mỗi frame (`ms_per_frame`) khi retarget LAFAN1 (30 fps) sang Unitree G1 trên CPU, không bật `--rate_limit`; coi là tái lập được nếu trung vị `ms_per_frame` ≤ 33,3 ms, tức `fps_out` ≥ 30 và `realtime_factor` ≥ 1,00.**

Bốn điều bắt buộc ghi kèm:

1. **Nguồn tuyên bố là repo, không phải paper.** Paper không nói GMR real-time và không định nghĩa "real-time".
2. **Paper không có số** ⇒ giá trị gốc là **định tính**; không tồn tại sai số "so với paper", mọi so sánh tốc độ với paper là bịa.
3. **Ngưỡng 33,3 ms do nhóm đặt** (`1000/30`, từ tốc độ phát LAFAN1), chốt trước khi thấy số.
4. **Giai đoạn 1 chỉ đo `ms_per_frame_process`** bằng bản đo cũ `results/v3_runtime.csv` (13 cột, không có cột `ms_per_frame`); kết luận đi qua bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`; **cấm** quy đổi `0,92 ×`.

### 2.2 Vì sao chọn phương án C

Vì paper không có số tốc độ, nhóm cân nhắc: **A** chỉ đo real-time và ghi rõ paper không nêu (yếu chữ "trong bài báo"); **B** chuyển sang Bảng II `E_g-mpbpe = 104,1 mm` (đúng chữ "số trong paper" nhưng gần chắc chắn thất bại, không tạo số đo mới); **C** = A + trình bày ba bảng paper và lý do không tái lập. **Chọn C** (DEC-01): thoả cả hai vế, chi phí gần bằng A, vẫn kết luận dứt khoát.

### 2.3 Hai đại lượng, tên phải đúng

`bvh_to_robot.py` chạy retarget và render trong cùng vòng lặp, nên `Actual rendering FPS` không phải throughput retargeting.

| Đại lượng | Đo gì | Vai trò |
|---|---|---|
| `ms_per_frame` | **chỉ** `retarget()` từng frame (probe, không viewer) | Đại lượng của tuyên bố |
| `ms_per_frame_process` | cả tiến trình: nạp BVH + init + viewer + retarget + render + ghi pkl | Cận trên bảo thủ; giai đoạn 1 chỉ có số này |
| `realtime_factor_process` | `33,333 / ms_per_frame_process` | Đọc kèm, không thay thế |

**Bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`** (vì thiếu số Nhóm A):

| Tình huống | Kết luận |
|---|---|
| `process` ≤ 33,3 ms | **Tái lập được** — điều kiện đủ (`retarget ≤ process`) |
| `process` > 33,3 **và** `ms_per_frame` ≤ 33,3 | Tái lập một phần |
| `process` > 33,3 **và** `ms_per_frame` > 33,3 | Không tái lập được (phải thử máy thứ hai) |
| `process` > 33,3, **không có** `ms_per_frame` | **Chưa kết luận được** — không được suy ra |

Ba mức chốt trước: `realtime_factor` ≥ 1,00 tái lập được · 0,80–0,99 một phần · < 0,80 không.

### 2.4 Bảng hai cột

| Đại lượng (điều kiện) | Bài báo | Nhóm đo được |
|---|---|---|
| `ms_per_frame` (ms) — G1, LAFAN1 | **không nêu** | **không đo** (bản đo cũ không có cột) |
| `ms_per_frame_process` (ms) | **không nêu** | **17,272** (trung vị, n = 5; mean 17,349; sd 0,369; CV 2,13 %) |
| `fps_out_process` (frame/s) | **không nêu** | **57,9** (suy ra `1000/17,272`) |
| `realtime_factor_process` (lần) | **không nêu** (chỉ chữ "real time") | **1,93** (`33,333/17,272`) |
| V5 · T1 29dof · `_process` (ms) | **—** | **13,034** (n = 5, CV 11,32 %) → 2,56 |
| V5 · G1 · `_process` (ms) | **—** | **17,018** (n = 3, CV 4,59 %) → 1,96 |
| V5 · PM01 · `_process` (ms) | **—** | **35,454** (n = 3, CV 3,01 %) → 0,94 |
| Success rate "Dance 5" sim2sim (%) | 51 (Bảng I, tr. 6) | **không đo** (ngoài phạm vi) |
| `E_g-mpbpe` mean GMR (mm) | 104,1 (Bảng II, tr. 6) | **không đo** (ngoài phạm vi) |
| Xuyên sàn PHC "Dance 1" (cm) | 60 (mục V-B, tr. 6) | **không đo** (ngoài phạm vi) |

Hai lưu ý: cột `realtime_factor` **trong CSV** là của từng lần chạy, không dùng để báo cáo; `walk1_subject1.bvh` dài **7.840 frame = 261,3 s**, **không phải** "Walk 1" của Bảng I (33 s).

### 2.5 Ba bảng của paper và vì sao không tái lập

| # | Bảng | Đại lượng | Giá trị GMR | Cần gì |
|---|---|---|---|---|
| 1 | I, tr. 6 | success rate (%) | 100 % "Dance 1"/"Dance 2"; **51 %** "Dance 5" sim2sim | IsaacSim + BeyondMimic + policy đã train + 100/4096/100 rollout |
| 2 | II, tr. 6 | `E_g-mpbpe`/`E_mpbpe` (mm), `E_mpjpe` (10⁻³ rad) | **104,1** / 28,1 / 561,7 | như trên, 100 rollout/policy; đo trên quỹ đạo policy |
| 3 | III, tr. 7 | success rate theo `start frame` | "Walk 2": **64 %** (frame 0) → 100 % (frame 7) | cùng policy đã train, đổi frame đầu |

**Bốn lý do không tái lập:** (1) phải train **84 policy** (21 × 4); (2) cần **IsaacSim + GPU** cho sim/sim-dr (4096 rollout); (3) sim2sim cần **node ROS + state estimation** của BeyondMimic; (4) paper **không công bố** hardware, phiên bản, commit ⇒ không dựng lại được môi trường kể cả có GPU. Ba bảng nằm ngoài phạm vi; cột "nhóm đo được" của ba dòng tương ứng để **"không đo"**.

### 2.6 Ba điều không được tuyên bố

1. Không nói "GMR nhanh hơn PHC/ProtoMotions" — paper và nhóm đều không đo tốc độ các phương pháp kia.
2. Không nói "tái lập Bảng I/II" — cần train RL.
3. Không nói "paper tuyên bố real-time" — tuyên bố ở README/mô tả repo.

## 3. Nhật ký cài đặt

Nhật ký đầy đủ: `logs/nhat_ky_cai_dat.md` (15 mục + 4 FIX + MEDIA + RV-23), 6 log thô, `logs/lenh_da_chay.md`. Dưới đây là 7 sự cố ảnh hưởng tới số liệu hoặc kết luận.

### 3.1 Môi trường cuối cùng

| Mục | Giá trị |
|---|---|
| Máy / OS | LENOVO 83GS, Windows 11 Home Single Language 10.0.26300 |
| CPU / RAM / GPU | i5-12450HX 8 nhân/12 luồng · ~15,7 GiB · RTX 4050 Laptop 6 GiB (**không dùng** khi đo) |
| Conda / Python | conda 26.7.1 · Python 3.10.21, env `gmr` |
| Gói chính | `mujoco 3.17.0`, `mink 1.3.0`, `torch 2.14.1`, `smplx 0.1.28`, `daqp 0.11.2`, **`proxsuite 0.7.2.post1` (ghim)** |
| `requirements.txt` | 45 dòng từ `pip freeze` thật, có `-e git+…GMR@25f56db…` |
| Cổng G1 | `smplx_to_robot.py --help` exit 0, in 17 robot — **ĐẠT** |

### 3.2 Bảy sự cố

**(1) `proxsuite` không có wheel Windows.** Lần cài đầu chết ở metadata `proxsuite>=0.2.9` (dependency của `qpsolvers[proxqp]`): pip tải source 54,7 MB, CMake báo `CMAKE_C_COMPILER not set` vì máy không có MSVC. Bản 0.8.2 chỉ có sdist; conda-forge chỉ build linux/osx. **Xử lý:** ghim `proxsuite==0.7.2.post1` — bản duy nhất có wheel `cp310-win_amd64` (4,3 MB) — cài lại exit 0. Không sửa `pyproject.toml`; chấp nhận được vì solver mặc định là **daqp**.

**(2) `libstdcxx-ng` trong README chỉ có cho Linux.** `conda install -c conda-forge libstdcxx-ng` trả `PackagesNotFoundInChannelsError`. Bỏ qua có ghi chép; kiểm chứng bù bằng việc chạy thật có mở cửa sổ MuJoCo.

**(3) SMPL-X bị chặn bởi license → đổi đường dữ liệu.** Repo không kèm body model nhưng `utils/smpl.py` bắt buộc gọi `smplx.create(...)`. SMPL-X và AMASS/OMOMO đều phải đăng ký + ký license tại Max Planck, không có đường tải công khai. **Quyết định:** dùng `bvh_to_robot.py` + LAFAN1 BVH (công khai, repo có 6 config `bvh_lafan1_*`). **Hệ quả: V3/V5 đo trên đường BVH, không phải SMPL-X như paper.**

**(4) KI-01 — robot cúi gập khi phát lại.** Render `g1_walk4_no_rate_limit_1.pkl` thấy robot gập về trước, chân khuỵu. Đã loại trừ bằng số đo:

| Motion | frames | `waist_pitch` TB ± std | `hip_pitch` | `knee` | `root z` |
|---|---|---|---|---|---|
| `walk4_subject1` | 4.917 | **+29,52° ± 1,70** | −56,3 / −56,1° | +37,5 / +39,3° | 0,766 m |
| `walk3_subject1` | — | +25,19° ± 4,27 | −11,8 / −11,4° | +33,3 / +34,9° | 0,729 m |
| `dance1_subject2` | 3.944 | +18,62° ± 8,70 | −23,1 / −20,0° | +49,3 / +47,9° | 0,754 m |

Scale người→robot 1,75/1,8 = 0,972 (bình thường); viewer và retarget dùng **cùng** `g1_mocap_29dof.xml`; đổi clip thì tư thế đổi theo. **Nguyên nhân:** `walk4` là clip **đi bộ khom lưng** của LAFAN1 — retarget tái hiện trung thực, pipeline không lỗi (`waist_pitch` gần như hằng số, std 1,7° so với 6,0° và 8,7°). **Xử lý:** chuyển motion chính thức sang `walk1_subject1`, chạy lại V3; giữ walk4 làm ví dụ motion khó.

**(5) KI-02/RV-13 — cột `cmd` ghi cờ chưa từng truyền.** `measure_v3.ps1` chỉ ghép `--rate_limit` vào **chuỗi in ra CSV** (dòng 20, 23), lệnh thật (dòng 26) không có cờ. Ba nguồn xác nhận: mã script; log các lần đó ghi 64–136 fps (bộ giới hạn 30 Hz không thể); đo lại `RateLimiter(30)` × 300 = 14,004 s = **21,42 Hz (46,68 ms)** — thư viện chậm hơn 30 Hz. **Xử lý:** xoá 4 dòng, rút kết luận về `--rate_limit`; cờ này chỉ để phát lại cho mắt người, không dùng đo throughput.

**(6) RV-14 — log không chứa số đo.** Ban đầu `wall_clock_s` chỉ in ra console. Đã thêm dòng cuối vào từng log: `END wall_s=137.37 ms_per_frame=17.522 rtf=1.902 frames=7840 exit=0 …`. Lần đầu dùng `-Encoding utf8` làm vỡ file UTF-16LE → đổi `-Encoding Unicode`, **chạy lại toàn bộ**; 20/20 log đo có dòng `END`.

**(7) Hai đợt V3 lệch 14,4 % — và retarget tất định.** Đợt cũ (`c62e74f`, n = 3): 14,034/15,139/16,339 → mean **15,171**. Đợt mới (`f467075`, n = 5): mean **17,349**, median **17,272**. Chạy lại vì log hỏng (sự cố 6), không vì số xấu. Băm SHA256 **40 pkl**: mọi lần chạy cùng cặp (robot, motion) **giống nhau từng byte** — G1+walk1 ×20 `E7E3B906…`, T1+walk1 ×7 `4E716187…`, PM01+walk1 ×5 `57B693A8…`, G1+walk4 ×5 `37F0ACD2…`. ⇒ chênh do **trạng thái máy**, không do thuật toán; chọn đợt mới (chậm hơn, bảo thủ).

### 3.3 Ba bài học

1. Cài không được không phải thất bại, miễn ghi rõ tắc ở đâu và đã thử gì.
2. Review độc lập có giá trị bằng một người làm — sự cố (5) do Review phát hiện.
3. Số đo phải tự truy vết: mỗi số trong CSV lần ngược được tới dòng `END` của chính lần chạy.

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

n = 5: mean **17,349**, median **17,272**, sd 0,369, **CV 2,13 %** (≤ 5 %), biên độ 16,853–17,852; `fps_out_process` 57,9; `realtime_factor_process` **1,93**. Cả 5 giá trị đều < 20 ms nên kết luận không phụ thuộc chọn mean hay median. Không dùng cột `realtime_factor` từng dòng.

### 4.3 Bằng chứng hình ảnh

| Ảnh | Nội dung |
|---|---|
| `v3_ms_per_frame_g1_2026-11-20.png` | ms/frame 5 lần đo + đường ngưỡng 33,33 ms |
| `v3_terminal_start_g1_2026-11-20.png` | cửa sổ lệnh đo đang chạy |
| `v3_terminal_result_g1_2026-11-20.png` | kết quả một lần chạy (thời gian, ms, rtf) |
| `v3_render_mujoco_g1_2026-11-20.png` | MuJoCo đang phát G1 |
| `slide_v3_walk1_g1_f450/f900/f1350.png` | 3 khung 25/50/75 % của clip chính thức |

### 4.4 Đối chiếu với bài báo

Paper không có mốc tốc độ (`docs/paper_notes.md` §12), nên chỉ so được với **ngưỡng nhóm đặt**: 17,272 ms ≤ 33,3 ms ⇒ theo bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md`, **tái lập được ở mức cả tiến trình** (điều kiện đủ: `retarget ≤ process`). Hai giới hạn phải nói cùng lúc: (a) **không** được nói "vòng lặp retarget đạt real-time" — bản đo cũ không có `ms_per_frame`, số 17,272 gồm init + viewer + render + ghi pkl, là **cận trên bảo thủ**; (b) sai số **giữa hai phiên ≈ 14 %**, lớn hơn CV trong phiên (2,13 %) ⇒ báo **17,3 ms** kèm sai số giữa phiên, không phải 17,35 ms chính xác đến 0,4 ms. Ba bảng paper **không đối chiếu được** và **không được đối chiếu** — chúng đo policy, không đo tốc độ.

### 4.5 Hạn chế phép đo

1. Chỉ có số **cả tiến trình**, là cận trên; không phải thời gian riêng `retarget()`.
2. Không xác minh `CUDA_VISIBLE_DEVICES` — "chạy CPU" là suy luận từ mã, không phải bằng chứng cấu hình.
3. Một máy Windows 11, trong khi README chỉ test Ubuntu 22.04/20.04.
4. Đồng hồ Windows thô (hạt `sleep` ~15,6 ms) — ảnh hưởng nhỏ với wall-clock nhưng không bằng 0.
5. T1 trong V5 có CV 11,32 % > 5 % ⇒ báo trung vị, không báo mean.

## 5. Kết quả tự huấn luyện (3 hạt giống)

GMR là **retargeting dựa trên tối ưu hình học**, không phải học tăng cường: không trọng số, không vòng huấn luyện, không hàm mất mát, **không có khái niệm seed**. Yêu cầu "train cấu hình nhỏ, 3 hạt giống, ghi đường cong" **không áp dụng** — không phải bỏ qua mà đối tượng huấn luyện không tồn tại.

Phần RL duy nhất là **policy BeyondMimic** (Bảng I/II/III). Muốn train thật phải dựng IsaacSim + BeyondMimic trên GPU, train ít nhất một policy/clip rồi chạy 3 seed. Máy chỉ có GPU laptop 6 GiB (không dùng khi đo), không đủ cấu hình; 10 ngày không đủ một vòng train + đánh giá.

**Phương án thay thế (V4):** chạy cùng pipeline với **3 cấu hình**, ghi thời gian và khác biệt. Ba cấu hình lấy từ V5 (cùng motion, khác robot) — **số tái sử dụng, không phải phép đo mới**:

| Cấu hình | DoF | `_process` (trung vị) | Khác biệt |
|---|---|---|---|
| Booster T1 29dof | 27 | 13,034 ms (n = 5) | nhanh nhất |
| Unitree G1 | 29 | 17,018 ms (n = 3) | trung gian |
| ENGINEAI PM01 | 24 | 35,454 ms (n = 3) | chậm nhất, dù ít khớp nhất |

Không có quan hệ đơn điệu giữa DoF và thời gian (PM01 24 khớp chậm 2,7× T1 27 khớp) ⇒ không được viết "nhiều khớp thì chậm". **Kết luận mục 5:** không có đường cong học để trình bày; ba seed không tồn tại để chạy; phần thay thế đã thực hiện. Muốn có 3 seed thật thì đối tượng phải là policy BeyondMimic — ngoài phạm vi.

## 6. Sim2sim: bảng tụt hiệu năng, độ bền theo nhiễu và đồ thị

### 6.1 Mức 3: đổi embodiment

Đề tài chọn **sim2sim mức 3**: giữ simulator, **cùng motion → ≥ 3 robot**, không huấn luyện lại.

| Robot | `--robot` | DoF | Trạng thái |
|---|---|---|---|
| Unitree G1 | `unitree_g1` | 29 | đo được (n = 3) |
| Booster T1 29dof | `booster_t1_29dof` | 27 | đo được (n = 5) |
| ENGINEAI PM01 | `engineai_pm01` | 24 | đo được (n = 3) |
| Unitree H1 | `unitree_h1` | — | **bị chặn** (§6.6) |

### 6.2 Vì sao không dùng nhiễu vật lý (DEC-02)

Hướng dẫn môn mô tả sim2sim tối thiểu bằng **đổi tham số vật lý** (khối lượng ±20 %, ma sát, trễ 1–3 bước). Nhóm không làm vậy vì phép thử **vô nghĩa với pipeline này**:

1. **Không có physics trong vòng tính.** Mỗi frame chỉ giải bài toán ngược trên vị trí/hướng khớp (Mink, ≤ 10 vòng); không tích phân lực, không ma sát, không lực tiếp xúc. Khối lượng khâu không xuất hiện ở bất kỳ bước nào.
2. **Đổi khối lượng không đổi một byte pkl.** Đường tính chỉ dùng qpos, chiều dài khâu, hệ số scale, giới hạn khớp. Tính tất định đã kiểm bằng SHA256: **40 pkl** thuộc các cặp (robot, motion) khác nhau, khác đợt, có/không `--rate_limit`, đều **trùng hash trong cùng cặp**. Cùng đầu vào ⇒ cùng đầu ra từng byte, không có nguồn ngẫu nhiên.
3. **Bảng "tụt theo mức nhiễu vật lý" sẽ là bảng giả.** Mọi mức ±20 % cho cùng kết quả; vẽ ra chỉ tạo cảm giác đã kiểm chứng độ bền. Nhóm từ chối làm bảng đó.

Thay bằng **bốn phép thử nhiễu có tác dụng thật lên đầu vào bài toán ngược** (DEC-02, `docs/v6_noise_spec.md`).

### 6.3 Bốn phép thử

Input cố định `walk1_subject1.bvh` → `unitree_g1`; baseline là lần chạy sạch.

| # | Phép thử | Mức | Cách làm |
|---|---|---|---|
| N1 | Nhiễu khớp | σ = 0,5 · 1 · 2 · 5° | Cộng Gaussian vào mọi kênh rotation BVH |
| N2 | Trễ điều khiển | k = 1 · 2 · 3 · 5 frame | Dịch chuỗi frame đi k |
| N3 | Mất frame | p = 1 · 5 · 10 % | Bỏ ngẫu nhiên p %, nội suy tuyến tính |
| N4 | Lệch tỉ lệ người | ±10 · ±20 % | Scale chiều cao người |

Mỗi mức chạy **1 lần** vì đo **độ lệch có hệ thống**, không đo thời gian — **không** vi phạm hợp đồng 1+3. Năm chỉ số: `dq_mean` (°), `dq_max` (°), `dr_rmse` (mm), `pct_frames_gt5deg` (%), `still_converges` (0/1). Trước khi chạy, driver được kiểm chứng: chạy lại bản sạch cho `|Δq| = 0,0000°`, `dr_rmse = 0,000 mm` so với baseline.

**Giả thuyết:** retargeting giải **gần như độc lập** từng frame — frame trước chỉ là warm start, không phải ràng buộc tích lũy — nên sai số **không tích lũy theo thời gian**. Ngoại lệ đã biết: tại **frame biên** (ngay sau điểm dịch/nối clip), warm start có thể làm lệch cục bộ vài chục độ ở đúng một frame rồi tắt nhanh. Kết quả khác giả thuyết thì ghi đúng kết quả, không sửa số.

### 6.4 Kết quả

Nguồn: `results/v6_noise_sweep.csv` (nhánh `task/v6-noise`, chờ PR 8 merge), log `results/logs/v6_*.log`, đồ thị `results/figures/v6_noise_vs_deviation.png`. Baseline `g1_walk1_subject1_run1.pkl` (`E7E3B906…`), 7.839 frame.

**N1 — nhiễu khớp:**

| σ (°) | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_gt5°` (%) | conv. |
|---|---|---|---|---|---|
| 0,5 | 0,56 | 7,56 | 1,20 | 0,51 | 1 |
| 1 | 1,10 | 14,11 | 1,56 | 5,55 | 1 |
| 2 | 2,18 | 25,80 | 2,02 | **87,74** | 1 |
| 5 | 5,41 | 63,89 | 3,52 | **100,00** | 1 |

**N2 — trễ (so đúng cặp frame):**

| k | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_gt5°` (%) | conv. |
|---|---|---|---|---|---|
| 1 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 2 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 3 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |
| 5 | 0,0010 | 36,08 | 0,03 | 0,013 | 1 |

**N3 — mất frame:**

| p (%) | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_gt5°` (%) | conv. |
|---|---|---|---|---|---|
| 1 | 0,0033 | 6,83 | 0,17 | 0,013 | 1 |
| 5 | 0,0158 | 6,09 | 0,36 | 0,077 | 1 |
| 10 | 0,0355 | 10,99 | 0,62 | 0,306 | 1 |

**N4 — lệch tỉ lệ người:**

| Mức (%) | `dq_mean` | `dq_max` | `dr_rmse` (mm) | `pct_gt5°` (%) | frame bão hoà (Δ) |
|---|---|---|---|---|---|
| −20 | 1,86 | 29,65 | 718,53 | 90,43 | 1.819 (−46) |
| −10 | 0,73 | 19,27 | 358,57 | **6,37** | 1.793 (−72) |
| +10 | 1,88 | 33,32 | 359,32 | **94,77** | 2.002 (+137) |
| +20 | 3,14 | 42,82 | 718,51 | 98,05 | 2.166 (+301) |

**Năm nhận xét:**

1. **N1 — trung bình gần tuyến tính, chỉ số ngưỡng bùng nổ phi tuyến.** `dq_mean` 0,56 → 1,10 → 2,18 → 5,41°; `pct_gt5°` 0,51 → 5,55 → 87,74 → 100 %. Vì là chỉ số **ngưỡng**: khi sai số trung bình chạm ~2° thì gần như mọi frame có ít nhất một khớp vượt 5°. **Ngưỡng hỏng nằm giữa σ = 1° và 2°.** Frame bão hoà: 1.875 / 1.910 / 2.122 / 3.550 (baseline 1.865).
2. **N2 — trễ chỉ lệch pha, không sai tư thế.** `dq_mean` = 0,0010°, `dr_rmse` = 0,03 mm ≈ 0 với mọi k = 1…5. Ngoại lệ: đúng **1 frame biên** (0,013 % ≈ 1/7.839) lệch tới 36°, rồi **tắt dần** (0,31° → 0,10° → 0,05° → 0,02°): tại frame biên IK khởi tạo từ nghiệm frame trước nên phụ thuộc trạng thái khởi tạo — **hiệu ứng biên cục bộ**, không phải tích lũy. Nếu so lệch frame, `dq_mean` sẽ rất lớn và kết luận "trễ làm hỏng tư thế" là **sai phương pháp**.
3. **N3 — mất frame gần như vô hại.** `dq_mean` 0,0033 → 0,0355°, `pct` ≤ 0,31 % vì frame thiếu được nội suy tuyến tính.
4. **N4 — nguy hiểm nhất và bất đối xứng.** ±10 %: **6,37 %** (co) vs **94,77 %** (giãn); ±20 %: 90,43 % và 98,05 %. **Đọc phần chênh, không đọc trị tuyệt đối:** bản sạch đã có **1.865/7.839 frame (23,8 %)** chạm giới hạn, chủ yếu `waist_pitch` (745 frame); so baseline, +10 % là +137, +20 % là +301, −10 % là −72, tập trung ở `ankle_roll`. Chênh cỡ 10² frame **không đủ** giải thích 6,4 % vs 94,8 %; phần còn lại là **hình học tay/chân không với tới đích khi người cao hơn robot** — giải thích định tính, chưa tách định lượng.
5. **`dr_rmse` 359/719 mm của N4 KHÔNG phải sai tư thế.** Con số **đối xứng theo |mức|** (−10: 358,57 · +10: 359,32 · −20: 718,53 · +20: 718,51), tỉ lệ với độ lớn scale, không phụ thuộc dấu ⇒ **quỹ đạo gốc bị scale**, không phải retarget hỏng dáng. Sai tư thế thật nằm ở `dq_mean`/`pct_gt5°`, và hai chỉ số đó **bất đối xứng**. **Cấm** viết "N4 làm retarget hỏng, lệch 719 mm".

**Kết luận §6.4:** IK hội tụ **15/15** mức, không NaN/phân kỳ. Vô hại: trễ đúng pha (N2), mất frame ≤ 10 % (N3). Làm hỏng: nhiễu khớp từ **2°** (N1), lệch tỉ lệ từ **±10 %** (N4, giãn nặng hơn). Cơ chế: sai số **không tích lũy theo thời gian** — chỉ **một frame biên** chịu trạng thái khởi tạo của IK rồi tắt nhanh; các mức hỏng còn lại do **bão hoà giới hạn khớp** (một phần) và **hình học tay/chân không với tới đích** (phần còn lại). Kết quả này **không đổi** kết luận tốc độ ở mục 7; nó thêm trục độ bền đầu vào.

### 6.5 Tụt hiệu năng theo robot

Nguồn `results/v5_sim2sim.csv` (thô `v5_raw.csv`; log `v5_<robot>_…`), bỏ warm-up:

| Robot | DoF | n | Trung vị ms | CV | rtf | So ngưỡng 33,3 ms |
|---|---|---|---|---|---|---|
| Booster T1 29dof | 27 | 5 | **13,034** | 11,32 % | **2,56** | đạt, dư 20,3 ms |
| Unitree G1 | 29 | 3 | **17,018** | 4,59 % | **1,96** | đạt, dư 16,3 ms |
| ENGINEAI PM01 | 24 | 3 | **35,454** | 3,01 % | **0,94** | **vượt 2,2 ms (6,4 %)** |
| Unitree H1 | — | — | — | — | — | bị chặn (§6.6) |

PM01 **ít khớp nhất nhưng chậm nhất**, gấp 2,7 lần T1 ⇒ nguyên nhân **không phải** số DoF. Ba giả thuyết (chưa tách): cấu hình IK nhiều key body hơn; số vòng solver chạm trần 10 nhiều hơn; mô hình MJCF/mesh nặng hơn. Thứ tự chạy đã kiểm soát (PM01 chạy đầu, nhiệt GPU 51–57 °C). PM01 vượt ngưỡng ở mức **cả tiến trình**; theo §6.1 của định nghĩa phép đo, vì không có `ms_per_frame`, trạng thái đúng là **"chưa kết luận được"** — không được nói "PM01 không đạt real-time".

### 6.6 Vì sao H1 bị chặn

Ba nguồn: (a) `--robot unitree_h1` → `invalid choice`, **exit 2** (argparse, trước khi nạp model); (b) không có `ik_configs/bvh_lafan1_to_h1.json` (chỉ 6 config `bvh_lafan1_*`); (c) README để cột BVH của H1 là **TBD**. Đường SMPL-X có H1 nhưng bị license chặn. Lý do gốc: danh sách `--robot` sinh từ `IK_CONFIG_DICT["bvh_lafan1"]`.

### 6.7 Hai chỉ tiêu hình học chưa đo

`docs/dinh_nghia_phep_do.md` §1.2 yêu cầu `min_body_height` và `foot_slide`, nhưng `v5_sim2sim.csv` **không có** hai cột này — thiếu so với hợp đồng §5.3. Cần FK trên ~23.500 frame và một script chưa có người nhận; nhóm **không** suy từ ảnh render (ảnh không đo được mm hay mm/s). Đây là thiếu sót ghi ở §7.4, không lấp bằng lời.

### 6.8 Đồ thị

| Ảnh | Nội dung |
|---|---|
| `v5_ms_per_frame_robots_2026-11-20.png` | trung vị ms/frame 3 robot, thanh min–max, ngưỡng 33,33 ms |
| `v5_sim2sim_{g1,t1,pm01}_frame2000_2026-11-20.png` | 3 robot tại cùng frame 2000 |
| `slide_v5_sim2sim_f450/f900/f1350.png` | 3 khung từ clip ghép 3 robot |
| `v6_noise_vs_deviation.png` | `dq_mean` + `pct_gt5°` theo 15 mức N1–N4 |

Video `results/media/v5_sim2sim_g1_t1_pm01.mp4` — 60 s, 1280×720, 30 fps; **không commit**, nộp kèm link.

## 7. Kết luận

### 7.1 Câu kết luận

> **Tái lập một phần.** Phần **thời gian thực** kiểm chứng được ở mức **cả tiến trình**: `ms_per_frame_process` = **17,272 ms** (trung vị, n = 5, CV 2,13 %), `realtime_factor_process` = **1,93**, theo **bản đo cũ 13 cột**. Áp bảng bắc cầu §6.1 của `docs/dinh_nghia_phep_do.md` với ngưỡng 33,3 ms → **tái lập được ở mức cả tiến trình** (điều kiện đủ). `ms_per_frame` (chỉ vòng retarget) **không đo được** vì bản đo cũ không có cột đó. Phần **bảng số của paper** (I, II, III) **không tái lập được** — đo policy đã train trong IsaacSim, cần GPU + 84 policy; số 104,1 mm của Bảng II chỉ nằm ở cột "bài báo", không đối chiếu với số nào nhóm đo.

Vì sao "một phần": tuyên bố "real-time" đúng ở mức đo được nhưng là tuyên bố **của repo**, không phải bảng của paper; ba bảng định lượng — phần đúng nghĩa "kiểm chứng bài báo" — ngoài phạm vi. V5 củng cố: 2/3 robot dưới ngưỡng (T1 13,034 → 2,56; G1 17,018 → 1,96); PM01 35,454 → 0,94 nhưng **"chưa kết luận được"** theo §6.1.

### 7.2 Điều kiện để câu trên đứng vững

1. Số 17,272 lấy từ bản đo cũ đã Review PASS; không trộn đợt cũ `c62e74f` (15,171).
2. Ngưỡng 33,3 ms chốt trước, không đổi sau khi thấy số.
3. Không dùng "tái lập được" cho toàn bộ paper — chỉ phần thời gian thực.
4. Không nói "retarget đạt real-time"; muốn chắc phải chạy probe `measure_runtime.py` (@`5f9cdd5`) — **chưa làm**.
5. Kết quả nhiễu (§6.4) không đổi kết luận tốc độ; nó chỉ thêm nhận định về độ bền.

### 7.3 Ba câu "chênh thì vì sao"

**(a) Hai đợt V3 lệch 14,4 % — do máy, không do thuật toán.** 15,171 → 17,349 ms (mean), cùng máy/input/commit. 40 pkl trùng SHA256 tuyệt đối theo cặp ⇒ cùng đầu ra từng byte mà thời gian khác 14 % ⇒ môi trường chạy. Đợt mới chậm hơn nên chọn là bảo thủ.

**(b) PM01 chậm nhất dù ít khớp nhất.** 24 DoF / 35,454 ms vs 27 DoF / 13,034 ms. Số DoF không giải thích; ba giả thuyết IK/solver/model chưa tách. Đã kiểm soát thermal (PM01 chạy đầu).

**(c) Nhóm vs paper — không có mốc.** Paper không công bố ms/FPS/hardware, nên câu đúng là "không có số của paper để chênh"; mốc duy nhất là ngưỡng nhóm đặt.

### 7.4 Thiếu sót phải nêu

- `min_body_height` / `foot_slide` **chưa đo** (§6.7).
- `ms_per_frame` **chưa đo**; chỉ có số cả tiến trình (§4.5).
- `CUDA_VISIBLE_DEVICES` **chưa xác minh** trên bản đo cũ.
- Kết quả trên **một máy Windows**, không đại diện Linux.
- Bất đối xứng N4 mới giải thích **định tính**, chưa định lượng phần đóng góp.
- Ba bảng I/II/III của paper **ngoài phạm vi**.

## 8. Phân công công việc và tự thuật từng thành viên

### 8.1 Bảng phân công

| # | Thành viên | MSSV | Vai trò | Worktree / nhánh | Sản phẩm chính | Bằng chứng |
|---|---|---|---|---|---|---|
| 1 | Trần Nguyễn Khánh Duy | 2001230120 | Planner · Research · Writing 1, 2, 7 | `main` · `gmr-research` · `gmr-writing` | `v1_tuyen_bo.md`, `paper_notes.md`, `dinh_nghia_phep_do.md`, `quyet_dinh.md`, mục 1–2–7 | commit `f0a8fff`; Review PASS 5/5 |
| 2 | Đặng Duy Mạnh | 2001240271 | Run · Writing 3 | `gmr-run` (`task/v2-cai-dat` → `v3-runtime` → `v5-sim2sim` → `v6-noise`) | nhật ký, `lenh_da_chay.md`, `requirements.txt`, CSV V3/V5/V6, ảnh, video | `f467075`, `5c05497`, `4e23df0`; 20/20 log `END` |
| 3 | Trương Thái Vỹ | 2001240577 | Code · Writing 5 | `gmr-code` (`task/code-scripts` → `code-scripts3` → `v4-phan-tich`) | `measure_runtime.py`, test, `NOTES.md`, mục 5 | `5f9cdd5`; 12 test PASS |
| 4 | Hà Mạnh Trường | 2045240326 | Review · Writing 6 | `gmr-review` (`task/review-qa`) | `review_notes.md`, checklist 5 điểm, 29 ticket RV | 7 PR; RV-13 phát hiện cờ giả |

### 8.2 Tự thuật

> ✍️ **CHỜ NỘI DUNG — mỗi người 3–5 dòng, ngôi thứ nhất: đã làm gì · khó nhất ở đâu · học được gì · % đóng góp.**

**Duy (Planner/Research/Writing 1–2–7)**
- `[CHỜ TỰ THUẬT: việc đã làm — đọc paper, chốt tuyên bố, viết định nghĩa phép đo, điều phối merge, viết mục 1–2–7]`
- `[CHỜ TỰ THUẬT: khó nhất — chọn tuyên bố khi paper không có số tốc độ]`
- `[CHỜ TỰ THUẬT: học được — vì sao phải tách vai phản biện]`
- `[CHỜ TỰ THUẬT: % đóng góp]`

**Mạnh (Run/Writing 3)**
- `[CHỜ TỰ THUẬT: việc đã làm — cài env, 7 sự cố, V3/V5/V6, video, nhật ký]`
- `[CHỜ TỰ THUẬT: khó nhất — proxsuite trên Windows; KI-01; log UTF-16]`
- `[CHỜ TỰ THUẬT: học được — log phải chứa chính con số mình báo cáo]`
- `[CHỜ TỰ THUẬT: % đóng góp]`

**Vỹ (Code/Writing 5)**
- `[CHỜ TỰ THUẬT: việc đã làm — measure_runtime.py, 12 test, hợp đồng CSV 30 cột]`
- `[CHỜ TỰ THUẬT: khó nhất — tách ms_per_frame / _process; đổi tên cột]`
- `[CHỜ TỰ THUẬT: học được — test trước giúp đổi hợp đồng không vỡ]`
- `[CHỜ TỰ THUẬT: % đóng góp]`

**Trường (Review/Writing 6)**
- `[CHỜ TỰ THUẬT: việc đã làm — checklist, 7 PR, 29 RV, đối chiếu CSV–log]`
- `[CHỜ TỰ THUẬT: khó nhất — phát hiện --rate_limit chưa từng truyền]`
- `[CHỜ TỰ THUẬT: học được — người viết số không phải người kiểm số]`
- `[CHỜ TỰ THUẬT: % đóng góp]`

### 8.3 Cam kết

Mọi số lần ngược được tới `results/` và dòng `END`; mọi số paper nằm ở cột "bài báo"; video/pkl/LAFAN1 không commit.

# PHỤ LỤC A — Nhật ký phản biện (rút gọn)

Bản đầy đủ: `report/review_notes.md` (nhánh `task/review-qa`).

| Ticket | Phát hiện | Xử lý |
|---|---|---|
| RV-13 | 4 dòng `rate_limit` ghi cờ chưa từng truyền | Xoá 4 dòng, rút kết luận |
| RV-14 | `wall_clock_s` không có trong log | Thêm dòng `END`, 20/20 log |
| RV-15/16 | V5 1 lần/robot; CV 7,6 % | Chạy lại n=3/5, báo trung vị |
| RV-17 | Tên cột `ms_per_frame` trần | Đổi `_process` |
| RV-18 | Thiếu bảng 2 cột | §2.4 của báo cáo |
| RV-23 | Hai đợt lệch 14,4 % | Mục 3 (7) + §7.3 |
| RV-26 | rtf trong mô tả PR tính sai | Báo cáo luôn `33,333/median` |

# PHỤ LỤC B — Tự kiểm theo hướng dẫn

| # | Điều kiện | Trạng thái |
|---|---|---|
| 1 | Tuyên bố + số hiệu bảng/hình | ✅ mục 1–2 (Bảng I/II/III, tr. 6–7) |
| 2 | Nhật ký cài đặt đầy đủ | ✅ mục 3 |
| 3 | Chạy mô hình có sẵn, có số so | ✅ mục 4 |
| 4 | Train 3 hạt giống | ✅ không áp dụng — mục 5 giải thích + 3 cấu hình |
| 5 | Sim2sim + bảng tụt hiệu năng | ✅ mục 6: 3 robot + nhiễu N1–N4 |
| 6 | Bảng tách 2 cột | ✅ §2.4 |
| 7 | Kết luận dứt khoát | ✅ mục 7: tái lập một phần |
| 8 | Commit + LICENSE | ✅ đầu báo cáo |
| 9 | Phân công + tự thuật | ⚠️ bảng xong, tự thuật chờ |
| 10 | Tập trình bày + video | ⚠️ video có, slide mới có khung |

# PHỤ LỤC C — Việc còn mở

| # | Việc | Người |
|---|---|---|
| 1 | Merge PR 8 (`task/v6-noise`) để CSV + ảnh vào `main` | Duy → Trường |
| 2 | Bổ sung `min_body_height` / `foot_slide` hoặc chốt "không đo" | Mạnh/Vỹ |
| 3 | 4 tự thuật + % đóng góp | 4 thành viên |
| 4 | Hoàn thiện `slides.md`, tập bấm giờ ≤ 13 phút | Duy + nhóm |
| 5 | Cập nhật `results/README.md` (còn mô tả bản cũ) | Mạnh |
| 6 | Định lượng phần bất đối xứng N4 còn lại | Mạnh + Trường |
