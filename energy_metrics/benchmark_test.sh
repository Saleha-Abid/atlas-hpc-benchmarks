#!/bin/bash
#SBATCH --job-name=atlas_tier_compare
#SBATCH --partition=chaos_ai
#SBATCH --nodelist=chaos02
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

echo "=================================================="
echo "PHASE 1: Benchmarking on DRBD-backed /data"
echo "=================================================="
for i in "${!MODELS[@]}"; do
  python3 test.py \
    --model "${MODELS[$i]}" \
    --tier "DRBD-backed /data" \
    --data-dir "${DRBD_DIR}" \
    --batch-size "${BATCH_SIZES[$i]}" \
    --workers 2 \
    --dataset-size 5000
done

echo "=================================================="
echo "Staging Data from /data to Local NVMe Scratch..."
echo "=================================================="
rsync -a "${DRBD_DIR}/" "${SCRATCH_DIR}/"

echo "=================================================="
echo "PHASE 2: Benchmarking on Atlas Local Scratch"
echo "=================================================="
for i in "${!MODELS[@]}"; do
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