#!/bin/bash
#SBATCH --job-name=atlas_tier_compare
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --output=tier_comparison_%j.log

DRBD_DIR="/data/testuser/dl_bench_data"
SCRATCH_DIR="/scratch/testuser/dl_bench_data"

mkdir -p "${DRBD_DIR}" "${SCRATCH_DIR}"

MODELS=("resnet50" "vit_b_16" "bert_base")
BATCH_SIZES=(64 32 32)

source /etc/profile.d/lmod.sh
module use /opt/atlas/modulefiles/
module purge
module load 3.10/pt_base

# Helper function to clear Linux OS page cache
drop_cache() {
    echo "[*] Synchronizing and flushing Linux page caches..."
    sync
    # If using passwordless sudo for cache dropping:
    sudo /sbin/sysctl -w vm.drop_caches=3 > /dev/null 2>&1 || echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    sleep 2
}

# -------------------------------------------------------------
# STEP 0: Pre-generate all datasets on /data so generation time
# is not included in benchmark runs
# -------------------------------------------------------------
echo "=================================================="
echo "PRE-GENERATION: Creating persistent raw files on /data"
echo "=================================================="
python3 test.py --model resnet50 --tier "Pre-gen" --data-dir "${DRBD_DIR}" --batch-size 64 --dataset-size 5000 --prepare-only
python3 test.py --model bert_base --tier "Pre-gen" --data-dir "${DRBD_DIR}" --batch-size 32 --dataset-size 5000 --prepare-only

# -------------------------------------------------------------
# PHASE 1: Benchmarking on DRBD-backed /data
# -------------------------------------------------------------
echo "=================================================="
echo "PHASE 1: Benchmarking on DRBD-backed /data (Cold Cache)"
echo "=================================================="
for i in "${!MODELS[@]}"; do
  drop_cache
  python3 test.py \
    --model "${MODELS[$i]}" \
    --tier "DRBD-backed /data" \
    --data-dir "${DRBD_DIR}" \
    --batch-size "${BATCH_SIZES[$i]}" \
    --workers 2 \
    --dataset-size 5000
done

# -------------------------------------------------------------
# STAGING: Sync pre-generated data from /data to Local NVMe Scratch
# -------------------------------------------------------------
echo "=================================================="
echo "Staging Data from /data to Local NVMe Scratch..."
echo "=================================================="
rsync -a "${DRBD_DIR}/" "${SCRATCH_DIR}/"

# -------------------------------------------------------------
# PHASE 2: Benchmarking on Atlas Local Scratch
# -------------------------------------------------------------
echo "=================================================="
echo "PHASE 2: Benchmarking on Atlas Local Scratch (Cold Cache)"
echo "=================================================="
for i in "${!MODELS[@]}"; do
  drop_cache
  python3 test.py \
    --model "${MODELS[$i]}" \
    --tier "Atlas Local Scratch" \
    --data-dir "${SCRATCH_DIR}" \
    --batch-size "${BATCH_SIZES[$i]}" \
    --workers 2 \
    --dataset-size 5000
done

# Cleanup local scratch
rm -rf "${SCRATCH_DIR}"
