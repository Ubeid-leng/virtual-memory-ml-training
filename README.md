# Virtual Memory Performance for Large-Model Training

How much does training slow down when a model's working set no longer fits in RAM? This group project for the Operating Systems module (BSc (Hons) Data Science, University of Mauritius, 2026) measured the cost of the latency gap between RAM and disk on a memory-intensive, training-style workload.

## Experiment

A Linux virtual machine in Oracle VirtualBox (4 vCPUs, 20 GB disk, 4 GB swap file) ran the same workload under three RAM limits:

| Scenario | VM RAM | Working set vs RAM | What it simulates |
|---|---|---|---|
| A: baseline | 4096 MB | ~70–75% | Model fits comfortably in memory |
| B: moderate pressure | 1536 MB | ~100–110% | Working set slightly exceeds RAM |
| C: thrashing | 512 MB | ~150–160% | Severe oversubscription |

No real large language model was used. [`workload.py`](workload.py) imitates a training loop: two large matrices stand in for weights and gradients, and each of 20 "epochs" runs a matrix multiply (forward pass) and an element-wise update (backward pass). This tests the OS memory subsystem rather than any particular model.

## Results

As reported in the group's report:

| Metric | A (4096 MB) | B (1536 MB) | C (512 MB) |
|---|---|---|---|
| Average iteration time | 0.42 s | 0.61 s | 5.87 s |
| I/O wait (average) | 1.2% | 8.4% | 41.3% |
| System efficiency (100% − I/O wait) | 98.8% | 91.6% | 58.7% |
| Swap used | 0 MB | 312 MB | 1,847 MB |
| Page faults per second (vmstat si + so) | 2.1 | 48.4 | 530.7 |

Once the working set was about 1.5 times the available RAM, each iteration took about **14 times longer** than the in-memory baseline (5.87 s vs 0.42 s), and the system spent over 40% of its time waiting on disk I/O. The raw monitoring logs are not included in this repository.

## Mitigations discussed

- **OS tuning:** a low `vm.swappiness` and Multi-Gen LRU, to keep frequently used model parameters resident in RAM
- **Memory pinning:** `mlock()` for critical weights, and CUDA Unified Memory with prefetch hints
- **Gradient checkpointing:** recompute activations in the backward pass instead of storing them, trading extra compute for a much smaller memory footprint
- **Hardware paths:** GPUDirect Storage and CXL memory expansion, to narrow the gap between RAM and NVMe

## Reproduce

1. Create a minimal 64-bit Linux server VM in VirtualBox with 4 vCPUs and a 20 GB disk, then enable a 4 GB swap file inside it:
   ```bash
   sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile
   sudo mkswap /swapfile && sudo swapon /swapfile
   ```
2. With the VM shut down, set its RAM for the scenario from the host: `./set_vm_ram.sh "YourVMName" 4096` (4096, 1536 or 512).
3. Inside the VM, start monitoring in one terminal (`./monitor.sh A`, which needs `sudo apt install sysstat`), then run the workload in another terminal: `python3 workload.py 8000`.

The argument to `workload.py` is the matrix size *n*. Each matrix takes about 8·*n*² bytes (8000 → ~512 MB), and the loop holds three matrices at once (weights, gradients and activations). Choose *n* so the total matches the scenario's share of RAM.

The scripts were transcribed from Section 5.2 of the report. The only changes are that the matrix size can now be passed on the command line, and that the monitoring commands write their output to files.

## Team

| Member | Role in the report |
|---|---|
| Om Noyensing | Team leader and editor: task allocation, discussion and conclusion, final document |
| Ubeid Teelhawod | Lead researcher: Section 4 (current OS implementations against performance degradation), the methodology, and sourcing 10+ academic references |
| Luv Ramrup | Technical lead: performance analysis and mitigation proposals |
| Marie Aurélie Emilie-Anne Carver | Abstract, introduction and theoretical concepts of virtual memory |

## Tools

Linux, Oracle VirtualBox, Python, NumPy, sysstat (`sar`, `iostat`), `vmstat`
