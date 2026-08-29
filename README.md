# Storage Benchmark & Energy Profiling

This repository contains benchmarking and visualization scripts designed to evaluate storage I/O performance for Atlas HPC across different mount points (`/data` vs `/scratch`) and analyze system energy consumption during workload execution versus baseline idle states.

---

## Overview

* **Storage Performance Comparison**: Evaluates throughput and training performance between network storage (`/data`) and local high-speed storage (`/scratch`).
* **Workloads Tested**:
  * ResNet-50
  * Vision Transformer (ViT-B/16)
  * BERT-Base
* **Energy Consumption Profiling**: Visualizes power draw curves to compare active benchmark runtimes against idle state metrics.

---

## Repository Structure

* `benchmark_test.py`: Python workload driver executing the benchmark suites (ResNet-50, ViT-B/16, BERT-Base) across `/data` and `/scratch`.
* `benchmark_test.sh`: Slurm script for running benchmark_test.py.
* `chart_energy.py`: Generates comparative energy plots contrasting power usage when benchmarks are actively running versus when the system is idle.
* `chart_energy.sh`: Slurm script for running chart_energy.py.

---

## Usage

### 1. Run the Benchmarks (For /data vs /scratch)

Execute the automated benchmark pipeline across the target directories:

```bash
sbatch benchmark_test.py
```
The output will be recorded for all three workloads in the log files.

### 2. Record Energy Consumption

While executing the above benchmarks across different configuration of HPC nodes (Core or Opportunistic), measure the energy consumed. Using the mean values of energy consumption, the energy chart can be plotted via:

```bash
sbatch chart_energy.sh
```
