# V6 — ban do thi rieng cho slide/video: 2000x1125 (16:9), 3 panel XEP DOC, font >= 18 pt.
# So lieu giu nguyen (doc tu results/v6_noise_sweep.csv). Hinh cu v6_noise_vs_deviation.png giu nguyen.
# Dung python BASE 3.12 (co matplotlib):
#   python third_party\_run\v6_plot_slide.py
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"."
with open(os.path.join(ROOT, "results", "v6_noise_sweep.csv"), newline="", encoding="utf-8-sig") as f:
    rows = [r for r in csv.DictReader(f) if r["mode"] != "baseline"]

GROUPS = [("n1", "N1 nhiễu khớp"), ("n2", "N2 trễ điều khiển"),
          ("n3", "N3 mất frame"), ("n4", "N4 lệch tỉ lệ người")]
COLORS = {"n1": "#1f77b4", "n2": "#2ca02c", "n3": "#ff7f0e", "n4": "#d62728"}
TICK = {"n1": lambda lv: f"{lv}°", "n2": lambda lv: f"k={lv}",
        "n3": lambda lv: f"{lv}%", "n4": lambda lv: f"{float(lv):+.0f}%"}
BASELINE_SAT = int(rows[0]["baseline_n_saturated_frames"])

pos, ticks, groups_x = [], [], []
x = 0.0
for key, _ in GROUPS:
    lv = [r for r in rows if r["mode"] == key]
    xs = []
    for r in lv:
        xs.append(x)
        ticks.append(TICK[key](r["level"]))
        pos.append((x, r))
        x += 1.0
    groups_x.append((key, sum(xs) / len(xs), len(xs)))
    x += 0.9

PANELS = [("dq_mean", "Sai khớp trung bình (°)"),
          ("pct_frames_gt5deg", "Frame lệch > 5° (%)"),
          ("n_saturated_frames", "Frame bão hòa khớp")]

matplotlib.rcParams.update({"font.size": 18})
fig, axes = plt.subplots(3, 1, figsize=(20, 11.25), dpi=100)
handles = []

for pi, (ax, (key, ylab)) in enumerate(zip(axes, PANELS)):
    for k in ("n1", "n2", "n3", "n4"):
        pts = [(xx, float(r[key])) for xx, r in pos if r["mode"] == k]
        if not pts:
            continue
        (ln,) = ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", markersize=9,
                        linewidth=2.6, color=COLORS[k], label=dict(GROUPS)[k])
        if pi == 0:
            handles.append(ln)
    if key == "n_saturated_frames":
        ax.axhline(BASELINE_SAT, color="#555555", linestyle="--", linewidth=2.0)
        (bl,) = ax.plot([], [], color="#555555", linestyle="--", linewidth=2.0,
                        label=f"baseline sạch ({BASELINE_SAT} frame)")
        handles.append(bl)
    for k, xc, n in groups_x:
        ax.axvspan(xc - n / 2 - 0.35, xc + n / 2 + 0.35, color=COLORS[k], alpha=0.05)
    ax.set_xticks([p[0] for p in pos])
    ax.set_xticklabels(ticks, fontsize=18)
    ax.set_ylabel(ylab, fontsize=19, labelpad=12)
    ax.tick_params(axis="y", labelsize=18)
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(pos[0][0] - 0.8, pos[-1][0] + 0.8)
    ax.margins(y=0.24)

for k, xc, _ in groups_x:
    axes[0].text(xc, 1.03, dict(GROUPS)[k], transform=axes[0].get_xaxis_transform(),
                 ha="center", va="bottom", fontsize=19, color=COLORS[k], fontweight="bold")

fig.suptitle("GMR · walk1_subject1 → unitree_g1 · 15 mức nhiễu (mỗi mức 1 lần)", fontsize=23, y=0.985)
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=18, frameon=False,
           bbox_to_anchor=(0.5, 0.012))
fig.subplots_adjust(left=0.10, right=0.985, top=0.885, bottom=0.135, hspace=0.55)

out = os.path.join(ROOT, "results", "figures", "v6_noise_slide.png")
fig.savefig(out, dpi=100)
print("saved", out)
from PIL import Image
print("size =", Image.open(out).size)
