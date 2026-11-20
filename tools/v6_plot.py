# V6 — do thi: dq_mean, pct_frames_gt5deg, n_saturated_frames theo muc nhieu (moi phep thu 1 duong).
# Dung python BASE 3.12 (co matplotlib):
#   python third_party\_run\v6_plot.py
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\xpaga\orca\workspaces\GMR-Humanoid-Retargeting-Benchmark\gmr-run"
csv_path = os.path.join(ROOT, "results", "v6_noise_sweep.csv")

with open(csv_path, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))


def label(r):
    m, lv = r["mode"], r["level"]
    if m == "n1":
        return f"N1 {lv}°"
    if m == "n2":
        return f"N2 k={lv}"
    if m == "n3":
        return f"N3 {lv}%"
    return f"N4 {float(lv):+.0f}%"


order = [r for r in rows if r["mode"] != "baseline"]
xs = list(range(1, len(order) + 1))
labels = [label(r) for r in order]
colors = {"n1": "#1f77b4", "n2": "#2ca02c", "n3": "#ff7f0e", "n4": "#d62728"}
names = {"n1": "N1 nhiễu khớp", "n2": "N2 trễ điều khiển",
         "n3": "N3 mất frame", "n4": "N4 lệch tỉ lệ người"}
baseline_sat = int(order[0]["baseline_n_saturated_frames"])

fig, axes = plt.subplots(1, 3, figsize=(17.5, 4.9))
panels = (("dq_mean", "dq_mean (°)", "độ lệch khớp trung bình"),
          ("pct_frames_gt5deg", "pct_frames_gt5deg (%)", "tỉ lệ frame có khớp lệch > 5°"),
          ("n_saturated_frames", "n_saturated_frames", "số frame có ≥ 1 khớp chạm giới hạn (±0,5°)"))

for ax, (key, ylab, title) in zip(axes, panels):
    for m in ("n1", "n2", "n3", "n4"):
        pts = [(x, float(r[key])) for x, r in zip(xs, order) if r["mode"] == m]
        if pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o",
                    color=colors[m], label=names[m])
    if key == "n_saturated_frames":
        ax.axhline(baseline_sat, color="gray", linestyle="--", linewidth=1,
                   label=f"baseline sạch ({baseline_sat} frame)")
        ax.set_ylim(min(baseline_sat, 1500) * 0.9, max(float(r[key]) for r in order) * 1.06)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=8)
    ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xlim(0.5, len(xs) + 0.5)

axes[0].legend(fontsize=7.5)
axes[2].legend(fontsize=7.5, loc="lower right")
fig.suptitle("GMR · walk1_subject1 → unitree_g1 · 15 mức nhiễu, mỗi mức 1 lần (đo độ lệch hệ thống, không đo thời gian)", fontsize=9)
fig.tight_layout()
out = os.path.join(ROOT, "results", "figures", "v6_noise_vs_deviation.png")
fig.savefig(out, dpi=130)
print("saved", out)
