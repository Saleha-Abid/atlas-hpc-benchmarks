#!/bin/bash
#SBATCH --job-name=chart
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --time=01:30:00
#SBATCH --output=chart_%j.log


source /etc/profile.d/lmod.sh
module use /opt/atlas/modulefiles/
module purge
module load 3.10/pt_base

python3 chart.py \
  --input-file "tier_comparison_*.log" \
  --output-file "tier_comparison_chart.png"