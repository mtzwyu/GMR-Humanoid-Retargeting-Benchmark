# Ve do thi chat luong anh xa: 2 panel (foot_slide theo robot, min_body_height theo robot).
# Dung python BASE 3.12 (co matplotlib):
#   python tools\quality_plot.py
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "results", "v6_quality.csv"), newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

labels = [r["robot"] for r in rows]
colors = ["#1f77b4", "#2ca02c", "#d62728"]

fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8))

# panel 1: foot slide
ax = axes[0]
means = [float(r["foot_slide_mean"]) for r in rows]
bars = ax.bar(labels, means, color=colors, width=0.55)
for i, r in enumerate(rows):
    ax.plot([i, i], [float(r["foot_slide_L"]), float(r["foot_slide_R"])], color="black",
            linewidth=1.2, marker="o", markersize=5, zorder=3)
    ax.annotate(f"{means[i]:.1f}".replace(".", ","), (i, means[i]), ha="center", va="bottom", fontsize=9)
ax.set_ylabel("foot slide (mm/s)")
ax.set_title("foot_slide: cột = trung bình 2 chân, chấm = trái/phải")
ax.grid(axis="y", alpha=0.3)

# panel 2: min body height
ax = axes[1]
heights = [float(r["min_body_height_mm"]) for r in rows]
bars = ax.bar(labels, heights, color=colors, width=0.55)
ax.axhline(0, color="crimson", linestyle="--", linewidth=1.2, label="mặt đất z = 0")
for i, h in enumerate(heights):
    rest = float(rows[i]["rest_offset_mm"])
    ax.plot([i - 0.27, i + 0.27], [rest, rest], color="black", linewidth=1.4, linestyle=":",
            zorder=4)
    ax.annotate(f"{h:.1f}".replace(".", ","), (i, h), ha="center", va="bottom" if h >= 0 else "top", fontsize=9)
ax.plot([], [], color="black", linestyle=":", linewidth=1.4, label="offset nghỉ của model")
ax.set_ylabel("min body height (mm)")
ax.set_title("Độ cao gốc body thấp nhất (âm = gốc body dưới mặt đất)")
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.3)

for a in axes:
    a.tick_params(axis="x", labelrotation=12, labelsize=9)
fig.suptitle("Chất lượng ánh xạ — cùng walk1_subject1.bvh, pkl V5 run1", fontsize=10)
fig.tight_layout()
out = os.path.join(ROOT, "results", "figures", "v6_quality.png")
fig.savefig(out, dpi=130)
print("saved", out)
