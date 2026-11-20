# Global Engineering Guidelines & Smart Model Router Protocol

Behavioral guidelines adapted from Andrej Karpathy's engineering principles (`CLAUDE.md`), Antigravity with ChatGPT planning standards, and Smart Model Router architecture. Applies globally across all projects and agent harnesses.

---

## 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly before implementing. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear or ambiguous, STOP. Name what is confusing. Ask.

---

## 2. Planning with Antigravity & ChatGPT (Mandatory for Multi-Step Tasks)
**Define clear success criteria. Decompose before coding using Antigravity with ChatGPT standards.**
- **Cơ chế kết hợp:**
  - **Antigravity:** Đóng vai trò Agentic Harness — quản lý workspace, sinh Artifacts kế hoạch (`implementation_plan.md` / `task.md`), điều phối ngữ cảnh và quản lý vòng lặp thực thi độc lập.
  - **ChatGPT / Advanced Reasoning:** Đóng vai trò bộ não lập luận kiến trúc — phân tích yêu cầu sâu, bóc tách module, phản biện thiết kế và đề xuất lộ trình.
- **Biến quyết định thành spec (`to-spec`):** Trước khi code tính năng lớn, chốt rõ ranh giới, seams, và quyết định kiến trúc thành tài liệu đặc tả.
- **Bóc tách thành Tracer-Bullet Tickets (`to-tickets`):** Cắt nhỏ task phức tạp thành các ticket tự chứa, có thứ tự phụ thuộc (Blocked by) và tiêu chí nghiệm thu có thể demo/verify được.
- **Cấu trúc thực thi từng bước (Bắt buộc tiêu chí xác minh):**
```
1. [Bước triển khai] -> verify: [Lệnh test / Tiêu chí nghiệm thu]
2. [Bước triển khai] -> verify: [Lệnh test / Tiêu chí nghiệm thu]
3. [Bước triển khai] -> verify: [Lệnh test / Tiêu chí nghiệm thu]
```
- Tiêu chí thành công mạnh mẽ giúp Agent tự chạy vòng lặp kiểm tra độc lập. Tránh các tiêu chí mơ hồ như "làm cho nó chạy".

---

## 3. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No defensive error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

---

## 4. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- When editing existing code:
  - Match existing style and conventions, even if you'd do it differently.
  - Don't "improve" adjacent code, comments, or formatting.
  - Don't refactor things that aren't broken.
  - If you notice unrelated dead code, mention it — don't delete it without permission.
- When your changes create orphans:
  - Remove imports/variables/functions that YOUR changes made unused.
  - Don't remove pre-existing dead code unless asked.
- The Golden Test: Every changed line in a diff should trace directly to the user's request.

---

## 5. Model Selection via Smart Model Router
**Route each task to the cheapest and fastest model that clears the quality bar.**
- **Default Working Tier:** Claude Sonnet 5 or Gemini Flash (`Model: flash`). Do NOT default to expensive models (Opus / Gemini Pro) for routine coding or lookups.
- **Tier 1 - Retrieval & Lookups (`flash_lite` / Haiku 4.5):** File lookups, regex, CSV/JSON extraction, bulk classification, status checks, market data parsing.
- **Tier 2 - Coding & Testing (`flash` / Sonnet 5 / Grok 4.5):** The default working tier for well-specified coding, unit tests (pytest, vitest), indicator math, and refactoring. Grok 4.5 is the fastest median coder (~2.5 min/task).
- **Tier 3 - Deep Reasoning & Auditing (`pro` / Opus 4.8 / Fable 5):** Multi-file architecture, mathematical modeling, cointegration/Monte Carlo, and adversarial risk audits.
- **Operating Modes:**
  - `balanced` (default): cheapest model within delta=0.10 of best pass@k with CI-low >= 0.5.
  - `fast`: lowest median latency (Grok 4.5).
  - `frugal`: lowest cost clearing quality bar (Flash-Lite / Haiku).
  - `deep`: capability ceiling (highest pass@k, tightest CI).
- **Measured Ties:** NEVER break measured ties arbitrarily. Surface options to the user.
- **Attribution & Logging:** Always attribute the model used: `> **[{Model Name}]** — {reason}` and log decisions to `logs/routing-log.jsonl`. Use `router stats` or `router review`.

---

## 6. Execution Safety Floor & Risk Guardrails
**Non-negotiable controls for trading, financial, and production code:**
1. **Zero Unsupervised Live Orders:** No model has autonomous authority to execute real-capital transactions or submit live orders. Live execution requires explicit human authorization (`HOLD_FOR_APPROVAL`).
2. **Deterministic Lookahead Bias Prevention:** Lookahead bias (e.g. `df['close'].shift(-1)`, forward indexing `iloc[i+1]`) is strictly forbidden in backtesting and time-series pipelines. Signals at $t$ execute at $t+1$.
3. **Mandatory Friction & Stop-Loss:** Backtests must model realistic fees (0.05% - 0.10%) and slippage. Position entries must define a deterministic stop-loss price.
4. **Secret Isolation:** Never hardcode, display, or commit API keys, private keys, or credentials.
5. **Deterministic Pre-Execution Audit:** Audit code before execution: `router check-safety <file>`.

---

## 7. Bối cảnh dự án — GMR-Humanoid-Retargeting-Benchmark

**Môn:** Nghiên cứu và kiểm chứng một công trình về ROBOT HÌNH NGƯỜI · Lớp 15DHTH07 · HK1 2026-2027 (ĐH Công Thương TP.HCM).
**Nhóm 01 — đề tài HR04.** Nhiệm vụ giai đoạn 1: lấy một repo mã nguồn mở về humanoid, chạy được nó, và **kiểm chứng lại một tuyên bố định lượng** trong bài báo của chính repo đó. Không sáng tạo thuật toán mới, không cần robot thật — toàn bộ trên mô phỏng.

### Cấu trúc thư mục
```
docs/huong_dan/            # PDF hướng dẫn, danh sách nhóm, đề tài HR04
docs/slide_bai_giang/      # slide + chương trình học môn Machine Learning
docs/tai_lieu_tham_khao/   # sách tham khảo
.agents/skills/            # skills riêng của project
report/                    # báo cáo 10-15 trang (giai đoạn 1)
logs/                      # nhật ký cài đặt, routing-log.jsonl
```

### Quy tắc riêng của đề tài
- **V1–V6 là hợp đồng nộp bài:** V1 chốt tuyên bố cần kiểm chứng kèm số hiệu Bảng/Hình → V2 nhật ký cài đặt → V3 chạy mô hình có sẵn (bắt buộc) → V4 tự huấn luyện 3 hạt giống → V5 sim2sim → V6 kết luận dứt khoát.
- **Không báo cáo con số không tự đo.** Bảng kết quả luôn tách cột `bài báo` và `nhóm đo được`. Chép số từ paper là gian lận.
- **Kết luận phải dứt khoát:** tái lập được / tái lập một phần / không tái lập được. Không tái lập được vẫn là kết quả tốt nếu phân tích đúng nguyên nhân.
- **Cài không được không phải thất bại:** ghi rõ tắc ở đâu, đã thử gì (Isaac Gym đã bị NVIDIA ngừng hỗ trợ).
- **Luôn ghi `git rev-parse --short HEAD`** của repo gốc và đọc file `LICENSE` trước khi dùng.
- **Sim2sim bắt buộc:** giữ nguyên simulator, đổi tham số vật lý (khối lượng khâu ±20%, ma sát, 1–3 bước trễ điều khiển), chạy lại chính sách **không huấn luyện lại**, vẽ hiệu năng theo mức nhiễu.
- **Tái lập có kiểm soát:** ghim seed, ghi phiên bản Python/CUDA/torch, lưu `requirements.txt` đã dùng thực tế.
- **Tài liệu và báo cáo viết bằng tiếng Việt**, thuật ngữ kỹ thuật giữ nguyên tiếng Anh khi cần.

### Không được commit
- `docs/.mat_khau_tai_lieu.local.md` và mọi file `*.local.md` chứa mật khẩu/khoá.
- Slide bài giảng dung lượng lớn (`*.ppsx`, PDF > 50 MB) — giữ local, đã nằm trong `.gitignore`.
- Checkpoint, dataset, video demo nặng: để ngoài repo hoặc dùng link ngoài.
