# Storage Benchmark & Energy Profiling

This repository contains benchmarking and visualization scripts designed to evaluate storage I/O performance for Atlas HPC across different mount points (`/data` vs `/scratch`) and analyze system energy consumption during workload execution versus baseline idle states.

---

## Directory Structure

```text
atlas-hpc-benchmarks/
├── dynamic_scheduling/
│   ├── instructions.md        
│   └── wol.sh                  
├── energy_metrics/
│   ├── instructions.md         
│   ├── benchmark_test.py       
│   ├── benchmark_test.sh       
│   ├── chart_energy.py         
│   └── chart_energy.sh        
├── storage_benchmark/
│   ├── instructions.md        
│   └── storage.sh              
├── workload_benchmark/
│   ├── instructions.md         
│   ├── benchmark_test.py       
│   ├── benchmark_test.sh      
│   ├── chart.py                
│   └── chart.sh               
└── README.md                  
```

## Overview
Each of these different sub-directories target a particular benchmark test for Atlas HPC.
1. `storage_benchmark`: Evaluates raw storage bandwidth, IOPS, and latency using fio direct I/O (libaio) across sequential and random patterns to compare network-replicated DRBD (/data) against local NVMe PCIe 4.0 storage (/scratch) under explicit cold-cache purges.
2. `workload_benchmark`: Profiles single-GPU training throughput, per-epoch makespan ($T_{\text{epoch}}$), and I/O wait overhead ($\delta_{\text{I/O}}$) across ResNet-50, ViT-B/16, and BERT-Base to measure storage tiering impact under I/O-intensive data-loading and checkpoint serialization.
3. `energy_metrics`: Records real-time power dissipation (Watts) at 1 Hz by capturing CPU package energy via Intel RAPL (energy_uj) and GPU power via NVML (nvidia-smi), quantifying energy savings achieved through off-peak node power management.
4. `dynamic_scheduling`: Manages opportunistic node state transitions via Wake-on-LAN (WoL) broadcasts, tracking link negotiation, kernel boot, SSSD/LDAP directory registration, and Slurm partition updates to safely harvest classroom workstations off-hours.
