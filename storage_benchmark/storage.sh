#!/bin/bash
#SBATCH --job-name=atlas_fio_microbench
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --output=fio_microbench_%j.log

set -euo pipefail

# -----------------------------------------------------------------------------
# Storage target directory (adjust to benchmark /data, /scratch, or local paths)
# -----------------------------------------------------------------------------
TARGET_DIR="${1:-/scratch/testuser/fio_benchmark}"
mkdir -p "${TARGET_DIR}"

echo "========================================================================"
echo "Starting FIO Micro-benchmarks on target: ${TARGET_DIR}"
echo "Node: $(hostname) | Date: $(date)"
echo "========================================================================"

# Helper function to flush filesystem dirty buffers and purge OS page caches
flush_page_cache() {
    echo -e "\n[*] Synchronizing and purging OS page caches..."
    sync
    echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    sleep 2
}

# =============================================================================
# 1. Sequential Read & Write (Throughput in MB/s with 1MB blocks)
# =============================================================================

flush_page_cache
echo ">>> [1/4] Sequential Write (1MB block size, 16 threads, O_DIRECT)..."
fio --name=seq_write \
    --directory="${TARGET_DIR}" \
    --direct=1 \
    --rw=write \
    --bs=1M \
    --size=4G \
    --numjobs=16 \
    --time_based \
    --runtime=60 \
    --group_reporting \
    --ioengine=libaio \
    --iodepth=16

flush_page_cache
echo ">>> [2/4] Sequential Read (1MB block size, 16 threads, O_DIRECT)..."
fio --name=seq_read \
    --directory="${TARGET_DIR}" \
    --direct=1 \
    --rw=read \
    --bs=1M \
    --size=4G \
    --numjobs=16 \
    --time_based \
    --runtime=60 \
    --group_reporting \
    --ioengine=libaio \
    --iodepth=16

# =============================================================================
# 2. Random Read & Write (IOPS with 4KB blocks)
# =============================================================================

flush_page_cache
echo ">>> [3/4] Random Read IOPS (4KB block size, 16 threads, O_DIRECT)..."
fio --name=rand_read \
    --directory="${TARGET_DIR}" \
    --direct=1 \
    --rw=randread \
    --bs=4k \
    --size=1G \
    --numjobs=16 \
    --time_based \
    --runtime=60 \
    --group_reporting \
    --ioengine=libaio \
    --iodepth=32

flush_page_cache
echo ">>> [4/4] Random Write IOPS (4KB block size, 16 threads, O_DIRECT)..."
fio --name=rand_write \
    --directory="${TARGET_DIR}" \
    --direct=1 \
    --rw=randwrite \
    --bs=4k \
    --size=1G \
    --numjobs=16 \
    --time_based \
    --runtime=60 \
    --group_reporting \
    --ioengine=libaio \
    --iodepth=32

# =============================================================================
# Cleanup generated benchmark target files
# =============================================================================
echo -e "\n[*] Cleaning up benchmark files in ${TARGET_DIR}..."
rm -f "${TARGET_DIR}"/seq_write.* "${TARGET_DIR}"/seq_read.* "${TARGET_DIR}"/rand_read.* "${TARGET_DIR}"/rand_write.*

echo "========================================================================"
echo "FIO Micro-benchmarks finished successfully."
echo "========================================================================"
