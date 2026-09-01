#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

# Publication-grade typography
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9.0,
    "figure.autolayout": True,
})

# Hardware telemetry constants
P_ARGON_LOAD = 89.17 * 10
P_ARGON_IDLE = 10.37 * 10

P_REAPER_LOAD = 115.35 * 8
P_REAPER_IDLE = 18.64 * 8
P_REAPER_OFF  = 1.80 * 8

P_CHAOS_LOAD  = 103.88 * 4
P_CHAOS_IDLE  = 11.33 * 4
P_CHAOS_OFF   = 1.80 * 4

# Power levels (in kW)
P_FULL_LOAD = (P_ARGON_LOAD + P_REAPER_LOAD + P_CHAOS_LOAD) / 1000.0  # ~2.23 kW
P_STATIC_IDLE = (P_ARGON_IDLE + P_REAPER_IDLE + P_CHAOS_IDLE) / 1000.0 # ~0.30 kW
P_ATLAS_DAY_IDLE = (P_ARGON_IDLE + P_REAPER_OFF + P_CHAOS_OFF) / 1000.0 # ~0.13 kW

hours = np.linspace(0, 24, 288)

# Construct 24-hour time series
p_baseline = np.zeros_like(hours)
p_atlas = np.zeros_like(hours)

for i, h in enumerate(hours):
    # Night compute window: 16:00 to 07:00 (active distributed training)
    if h >= 16.0 or h < 7.0:
        p_baseline[i] = P_FULL_LOAD
        p_atlas[i] = P_FULL_LOAD
    # Day lab window: 07:00 to 16:00
    else:
        p_baseline[i] = P_FULL_LOAD
        p_atlas[i] = P_ARGON_LOAD/1000.0

fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=300)

# Plot curves
ax.plot(hours, p_baseline, label="Static Continuous (24/7 Under-Load Baseline)", color="#E53E3E", linestyle="--", linewidth=1.8)
ax.plot(hours, p_atlas, label="Atlas Dynamic Scheduling (Under-Load)", color="#2B6CB0", linewidth=2.0)

# Fill energy savings region
day_mask = (hours >= 7.0) & (hours <= 16.0)
ax.fill_between(hours[day_mask], p_atlas[day_mask], p_baseline[day_mask], 
                color="#48BB78", alpha=0.3, label="Daytime Energy Saved (60.0% Under-Load Reduction)")

# Annotate lab hours
ax.axvspan(7.0, 16.0, color="gray", alpha=0.08)
ax.text(11.5, 0.45, "Laboratory Hours (07:00 - 16:00)\nWorkstations in Standby Mode", 
        ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#2D3748")

ax.set_xlabel("Time of Day (24-Hour Cycle)")
ax.set_ylabel("Cluster Power Draw (kW)")
ax.set_xlim(0, 24)
ax.set_xticks(np.arange(0, 25, 4))
ax.set_xticklabels(["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"])
ax.set_ylim(0, 3.5)
ax.grid(True, linestyle=":", alpha=0.6)

ax.legend(loc="upper right", framealpha=0.95)

plt.tight_layout()
plt.savefig("energy_profile.png", dpi=300, bbox_inches="tight")
print("[+] Publication figure successfully generated and saved to energy_profile.png")