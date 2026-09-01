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

# Benchmark data (N=5 Cold-Cache runs: Mean and Sample Standard Deviation)
models = ["ResNet-50", "ViT-B/16", "BERT-Base"]
x = np.arange(len(models))
bar_width = 0.35

# Epoch Execution Time (s)
t_epoch_drbd_mean = [29.36, 109.80, 106.98]
t_epoch_drbd_std  = [11.90, 20.67, 12.39]

t_epoch_scratch_mean = [7.18, 20.21, 12.73]
t_epoch_scratch_std  = [0.04, 0.11, 0.11]

# Sustained Throughput (samples/s)
throughput_drbd_mean = [198.76, 46.92, 47.16]
throughput_drbd_std  = [91.07, 9.49, 5.30]

throughput_scratch_mean = [695.22, 247.08, 392.02]
throughput_scratch_std  = [3.96, 1.39, 3.42]

# Colors (accessible, high-contrast academic palette)
color_drbd = "#4A5568"     # Slate Gray
color_scratch = "#2B6CB0"  # Deep Blue

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.4), dpi=300)

# Error bar formatting
error_kw_drbd = dict(ecolor="#1A202C", lw=1.2, capsize=3.5, capthick=1.0)
error_kw_scratch = dict(ecolor="#1A365D", lw=1.2, capsize=3.5, capthick=1.0)

# -------------------------------------------------------------
# Subplot 1: Epoch Execution Time (Lower is Better)
# -------------------------------------------------------------
bars1_drbd = ax1.bar(
    x - bar_width / 2, t_epoch_drbd_mean, bar_width,
    yerr=t_epoch_drbd_std, error_kw=error_kw_drbd,
    label="DRBD-backed /data", color=color_drbd, edgecolor="black", linewidth=0.6
)
bars1_scratch = ax1.bar(
    x + bar_width / 2, t_epoch_scratch_mean, bar_width,
    yerr=t_epoch_scratch_std, error_kw=error_kw_scratch,
    label="Atlas Local Scratch", color=color_scratch, edgecolor="black", linewidth=0.6
)

ax1.set_ylabel(r"Epoch Execution Time $T_{\mathrm{epoch}}$ (s)")
ax1.set_xticks(x)
ax1.set_xticklabels(models)
ax1.grid(axis="y", linestyle="--", alpha=0.5)
ax1.set_axisbelow(True)

# Add reduction percentage annotations above scratch bars
reductions = [(1 - s / d) * 100 for d, s in zip(t_epoch_drbd_mean, t_epoch_scratch_mean)]
for idx, (bar, red, s_err) in enumerate(zip(bars1_scratch, reductions, t_epoch_scratch_std)):
    height = bar.get_height()
    ax1.text(
        bar.get_x() + bar.get_width() / 2, height + s_err + 3.0,
        f"-{red:.0f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#C53030"
    )

ax1.set_ylim(0, 150)

# -------------------------------------------------------------
# Subplot 2: Sustained Throughput (Higher is Better)
# -------------------------------------------------------------
bars2_drbd = ax2.bar(
    x - bar_width / 2, throughput_drbd_mean, bar_width,
    yerr=throughput_drbd_std, error_kw=error_kw_drbd,
    label="DRBD-backed /data", color=color_drbd, edgecolor="black", linewidth=0.6
)
bars2_scratch = ax2.bar(
    x + bar_width / 2, throughput_scratch_mean, bar_width,
    yerr=throughput_scratch_std, error_kw=error_kw_scratch,
    label="Atlas Local Scratch", color=color_scratch, edgecolor="black", linewidth=0.6
)

ax2.set_ylabel("Throughput (samples/s)")
ax2.set_xticks(x)
ax2.set_xticklabels(models)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
ax2.set_axisbelow(True)

# Add speedup annotations above scratch bars
speedups = [s / d for d, s in zip(throughput_drbd_mean, throughput_scratch_mean)]
for idx, (bar, spd, s_err) in enumerate(zip(bars2_scratch, speedups, throughput_scratch_std)):
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2, height + s_err + 18,
        f"{spd:.2f}$\\times$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#2C5282"
    )

ax2.set_ylim(0, 820)

# Unified legend at top
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.04), ncol=2, frameon=False)

plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.savefig("dl_benchmark_comparison.png", dpi=300, bbox_inches="tight")
print("[+] Plot successfully saved to dl_benchmark_comparison.png")
