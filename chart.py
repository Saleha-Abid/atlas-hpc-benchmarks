#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

# Set publication-quality styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9.5,
    "figure.titlesize": 12,
    "figure.autolayout": True,
})

# Benchmark data
models = ["ResNet-50", "ViT-B/16", "BERT-Base"]
x = np.arange(len(models))
bar_width = 0.35

t_epoch_drbd = [14.62, 61.53, 65.91]
t_epoch_scratch = [7.16, 20.08, 12.73]

throughput_drbd = [341.5, 81.1, 75.7]
throughput_scratch = [697.0, 248.6, 392.2]

# Colors (accessible, high-contrast academic palette)
color_drbd = "#4A5568"     # Slate Gray
color_scratch = "#2B6CB0"  # Deep Blue

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=300)

# -------------------------------------------------------------
# Subplot 1: Epoch Execution Time (Lower is Better)
# -------------------------------------------------------------
bars1_drbd = ax1.bar(x - bar_width / 2, t_epoch_drbd, bar_width, label="DRBD-backed /data", color=color_drbd, edgecolor="black", linewidth=0.6)
bars1_scratch = ax1.bar(x + bar_width / 2, t_epoch_scratch, bar_width, label="Atlas Local Scratch", color=color_scratch, edgecolor="black", linewidth=0.6)

ax1.set_ylabel(r"Epoch Execution Time $T_{\mathrm{epoch}}$ (s)")
ax1.set_xticks(x)
ax1.set_xticklabels(models)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.set_axisbelow(True)

# Add reduction percentage annotations above scratch bars
reductions = [(1 - s / d) * 100 for d, s in zip(t_epoch_drbd, t_epoch_scratch)]
for idx, (bar, red) in enumerate(zip(bars1_scratch, reductions)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height + 1.8, f"-{red:.0f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#C53030")

ax1.set_ylim(0, 78)

# -------------------------------------------------------------
# Subplot 2: Sustained Throughput (Higher is Better)
# -------------------------------------------------------------
bars2_drbd = ax2.bar(x - bar_width / 2, throughput_drbd, bar_width, label="DRBD-backed /data", color=color_drbd, edgecolor="black", linewidth=0.6)
bars2_scratch = ax2.bar(x + bar_width / 2, throughput_scratch, bar_width, label="Atlas Local Scratch", color=color_scratch, edgecolor="black", linewidth=0.6)

ax2.set_ylabel("Throughput (samples/s)")
ax2.set_xticks(x)
ax2.set_xticklabels(models)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
ax2.set_axisbelow(True)

# Add speedup annotations above scratch bars
speedups = [s / d for d, s in zip(throughput_drbd, throughput_scratch)]
for idx, (bar, spd) in enumerate(zip(bars2_scratch, speedups)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, height + 15, f"{spd:.2f}$\\times$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#2C5282")

ax2.set_ylim(0, 800)

# Unified legend at top
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.04), ncol=2, frameon=False)

plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.savefig("dl_benchmark_comparison.png", dpi=300, bbox_inches="tight")
print("[+] Plot successfully saved to dl_benchmark_comparison.png")