#!/usr/bin/env bash
# Monitoring commands run in a second terminal while workload.py runs.
# Requires sysstat:  sudo apt install sysstat
# Usage:  ./monitor.sh A      (scenario label used in the output file name)

SCENARIO="${1:-A}"

# All-in-one record: CPU (-u), memory (-r) and swap/paging (-W), every second for 120 s
sar -u -r -W 1 120 > "scenario_${SCENARIO}_results.txt" &

# I/O wait: %iowait, sampled every second for 60 s
iostat -x 1 60 > "scenario_${SCENARIO}_iostat.txt" &

# Swap-in / swap-out and page fault activity (si, so columns)
vmstat 1 60 > "scenario_${SCENARIO}_vmstat.txt" &

wait

# For a live view of memory pressure instead, run:
#   watch -n 1 "free -m && cat /proc/meminfo | grep -E 'Active|Inactive|SwapUsed'"
