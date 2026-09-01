# # Instructions to Collect Energy and Power Metrics

This guide provides instructions to sample, log, and plot cluster node electrical power dissipation ($P_{\text{total}} = P_{\text{CPU}} + P_{\text{GPU}}$) across active workload execution and baseline idle states.

---

## 1. Measurement Methodology

Telemetry is sampled synchronously at 1 Hz across two in-band hardware interfaces:
* **CPU Package Power ($P_{\text{CPU}}$):** Polled via the Linux Running Average Power Limit (RAPL) sysfs interface, tracking energy differentials over time.
* **GPU Power Draw ($P_{\text{GPU}}$):** Polled from onboard NVML sensors using `nvidia-smi --query-gpu=power.draw`.
* **Soft-Off Standby Baseline:** Calibrated separately via line measurement.

---

To collect the metrics for energy and power, follow these steps,

### Step 1
Run `benchmark_test.py` on Atlas HPC using `benchmark_test.sh`.

```bash
sbatch benchmark_test.sh
```

### Step 2
While it is running, run for energy sampling on the compute node running the benchmark test.

```bash
# Samples GPU power (W) + CPU RAPL package power (W)
python3 -c "
import time, subprocess

def get_gpu_power():
    try:
        out = subprocess.check_output(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'])
        return sum([float(x) for x in out.decode().strip().split('\n')])
    except:
        return 0.0

def get_cpu_energy():
    try:
        with open('/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj', 'r') as f:
            return float(f.read().strip())
    except:
        return 0.0

print('Timestamp,GPU_Watts,CPU_Watts,Total_Watts')
last_e = get_cpu_energy()
last_t = time.time()

for _ in range(30):
    time.sleep(1)
    curr_e = get_cpu_energy()
    curr_t = time.time()
    cpu_w = ((curr_e - last_e) / 1e6) / (curr_t - last_t) if last_e > 0 else 0.0
    gpu_w = get_gpu_power()
    print(f'{time.strftime(\"%H:%M:%S\")},{gpu_w:.2f},{cpu_w:.2f},{gpu_w + cpu_w:.2f}')
    last_e, last_t = curr_e, curr_t
"
```

### Step 3
Repeat the **Step 2** but without the benchmark test running.

### Step 4
From the results collected, edit the `chart_energy.py` and run the file on Atlas HPC using `chart_energy.sh`.

```bash
sbatch chart_energy.sh
```
This will have to be done twice, once for the system loaded and once idle. The plotting code also has to be edited.

### Step 5
The plot is recorded as `energy_profile.png`.
