# Instructions to Collect Dynamic Scheduling Benchmark Results

This guide provides the protocol to measure, collect, and analyze the operational overhead and state transition latencies when dynamically provisioning opportunistic classroom workstations (`argon01`–`argon10`) into the active Slurm compute fabric.

---

## 1. Experimental Overview

Dynamic cycle harvesting transitions dormant workstations across three discrete phases:

$$\text{Total Transition Latency: } t_{\text{total}} = t_{\text{wol}} + t_{\text{boot}} + t_{\text{slurm}}$$

* **$t_{\text{wol}}$ (NIC Link & BIOS Handshake):** Time from Magic Packet broadcast to Ethernet physical link negotiation, motherboard POST, and UEFI handoff.
* **$t_{\text{boot}}$ (OS Kernel & Directory Authorization):** Time from Linux kernel bootstrap to centralized LDAP/SSSD user authentication synchronization.
* **$t_{\text{slurm}}$ (Daemon Registration):** Time from `slurmd` initialization to active `IDLE` state registration in the `slurmctld` controller tables.

---

Since dynamic scheduling involves only opportunistic nodes, the following steps are only to be followed for these nodes.

### Step 1
Run `wol.sh`. 

```bash
chmod +x wol.sh #make it executable
./wol.sk #run the script
```

### Step 2
Record the results from the WOL sequence. Then repeat the experiment for multiple computers by changing the value `TARGET_HOST`. Collect the results and tabulate them.
