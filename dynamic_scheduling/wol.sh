#!/bin/bash
TARGET_HOST="reaper05"
TARGET_MAC="CC:96:E5:08:8A:3B"  # Replace with actual MAC of argon02 physical NIC
ITERATIONS=10

echo "Run,t_wol_ping,t_ssh_ready,t_slurm_idle,t_total" > wol_benchmarks.csv

for i in $(seq 1 $ITERATIONS); do
  echo "--- Starting Iteration $i / $ITERATIONS ---"
  
  # Ensure target node is powered down (ACPI S5)
  ssh -q "admin_ultron@$TARGET_HOST" "sudo poweroff" 2>/dev/null
  echo "Waiting 20s for $TARGET_HOST to reach ACPI S5..."
  sleep 20

  T0=$(date +%s.%N)
  
  # 1. Dispatch WoL Magic Packet
  wakeonlan "$TARGET_MAC" >/dev/null 2>&1 || etherwake "$TARGET_MAC" 2>/dev/null
  
  # 2. Measure time to ICMP link negotiation
  while ! ping -c 1 -W 0.2 "$TARGET_HOST" >/dev/null 2>&1; do
    sleep 0.1
  done
  T_PING=$(date +%s.%N)
  
  # 3. Measure time to SSH / OS user-space & SSSD ready
  while ! ssh -o ConnectTimeout=1 -o StrictHostKeyChecking=no -q "admin_ultron@$TARGET_HOST" "exit" 2>/dev/null; do
    sleep 0.2
  done
  T_SSH=$(date +%s.%N)
  
  # 4. Measure time until Slurm controller marks node IDLE
  while ! sinfo -N -n "$TARGET_HOST" -h -o "%T" | grep -q "idle"; do
    sleep 0.2
  done
  T_IDLE=$(date +%s.%N)

  # Calculate intervals
  D_WOL=$(echo "$T_PING - $T0" | bc)
  D_BOOT=$(echo "$T_SSH - $T_PING" | bc)
  D_SLURM=$(echo "$T_IDLE - $T_SSH" | bc)
  D_TOTAL=$(echo "$T_IDLE - $T0" | bc)

  echo "Run $i: WoL=$D_WOL s | Boot=$D_BOOT s | Slurm=$D_SLURM s | Total=$D_TOTAL s"
  echo "$i,$D_WOL,$D_BOOT,$D_SLURM,$D_TOTAL" >> wol_benchmarks.csv
  
  sleep 5
done

