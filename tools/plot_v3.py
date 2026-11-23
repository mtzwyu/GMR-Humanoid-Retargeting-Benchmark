# Vẽ đồ thị từ results/v3_runtime.csv và (nếu có) results/v5_sim2sim.csv
# Chạy bằng python BASE (3.12) vì env gmr không cài matplotlib:
#   python third_party\_run\plot_v3.py
# RV-13: chỉ còn chế độ KHÔNG --rate_limit -> đồ thị V3 chỉ 1 panel.
# RV-17: cột thời gian là ms_per_frame_process (đo cả tiến trình).
# RV-24: đồ thị V5 dùng TRUNG VỊ + thanh sai số min–max (T1 29dof có CV > 5 %).
import csv, os, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    p = os.path.join(ROOT, "results", name)
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ---------- V3 ----------
v3_path = os.path.join(ROOT, "results", "v3_runtime.csv")
if os.path.exists(v3_path):
    rows = load("v3_runtime.csv")
    meas = [r for r in rows if r["phase"].startswith("measure")]
    xs = [int(r["phase"].split("_")[1]) for r in meas]
    ys = [float(r["ms_per_frame_process"]) for r in meas]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(xs, ys, marker="o", color="#1f77b4", label="unitree_g1")
    for x, y in zip(xs, ys):
        ax.annotate(f"{y:.2f}".replace(".", ","), (x, y), textcoords="offset points", xytext=(0, 8), fontsize=8)
    ax.axhline(33.333, color="crimson", linestyle="--", linewidth=1, label="ngưỡng 33,33 ms")
    ax.set_xlabel("lần đo")
    ax.set_ylabel("ms / frame (toàn tiến trình, Measure-Command)")
    ax.set_title("V3 — G1, walk1_subject1.bvh (7840 frame), không --rate_limit")
    ax.set_xticks(xs)
    ax.margins(x=0.12)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out1 = os.path.join(ROOT, "results", "figures", "v3_ms_per_frame_g1_2026-11-20.png")
    fig.savefig(out1, dpi=130)
    print("saved", out1)

# ---------- V5: mean nếu CV <= 5 %, median nếu CV > 5 % (docs/dinh_nghia_phep_do.md §4) ----------
v5_path = os.path.join(ROOT, "results", "v5_sim2sim.csv")
if os.path.exists(v5_path):
    v5 = [r for r in load("v5_sim2sim.csv")
          if r["status"] == "ok" and r["phase"].startswith("measure")]
    order = [("engineai_pm01", "#d62728"), ("booster_t1_29dof", "#2ca02c"), ("unitree_g1", "#1f77b4")]
    labels, vals, lows, highs, kinds = [], [], [], [], []
    for rb, color in order:
        v = [float(r["ms_per_frame_process"]) for r in v5 if r["robot"] == rb]
        if v:
            mean, sd = statistics.mean(v), statistics.stdev(v) if len(v) > 1 else 0.0
            cv = 100 * sd / mean
            use_mean = cv <= 5.0
            labels.append(f"{rb}\n(n={len(v)}, CV {cv:.1f}%)")
            vals.append(mean if use_mean else statistics.median(v))
            kinds.append("mean" if use_mean else "median")
            lows.append(min(v))
            highs.append(max(v))
    fig2, ax2 = plt.subplots(figsize=(7.6, 4.4))
    bars = ax2.bar(labels, vals, color=[c for _, c in order], width=0.55)
    err_low = [m - lo for m, lo in zip(vals, lows)]
    err_high = [hi - m for m, hi in zip(vals, highs)]
    ax2.errorbar(labels, vals, yerr=[err_low, err_high], fmt="none", ecolor="black",
                 capsize=6, linewidth=1)
    for i, m in enumerate(vals):
        ax2.annotate(f"{kinds[i]} {m:.2f}".replace(".", ","), (i, highs[i]), ha="center", va="bottom", fontsize=8)
    ax2.axhline(33.333, color="crimson", linestyle="--", linewidth=1, label="ngưỡng 33,33 ms")
    ax2.set_ylabel("ms / frame (toàn tiến trình, Measure-Command)")
    ax2.set_title("V5 sim2sim — mean nếu CV ≤ 5 %, median nếu CV > 5 %\nthanh sai số = min–max (cùng walk1_subject1.bvh)")
    ax2.set_ylim(0, max(highs) * 1.18)
    ax2.legend(fontsize=8)
    ax2.grid(axis="y", alpha=0.3)
    fig2.tight_layout()
    out2 = os.path.join(ROOT, "results", "figures", "v5_ms_per_frame_robots_2026-11-20.png")
    fig2.savefig(out2, dpi=130)
    print("saved", out2)
