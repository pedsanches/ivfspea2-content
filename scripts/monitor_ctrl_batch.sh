#!/bin/bash
# Monitor controller batch progress
total=0; complete=0
for d in data/raw/ppsn_dynamics/controller/*/; do
    n=$(ls "$d"/*.mat 2>/dev/null | wc -l)
    total=$((total+n))
    [ "$n" -eq 30 ] && complete=$((complete+1))
done
fails=$(grep -c "FAIL" logs/ctrl_batch_*.log 2>/dev/null | awk -F: '{s+=$2}END{print s}')
echo "$(date +%H:%M:%S) — Cases done: $complete/51 | Runs: $total/1530 | Failures: $fails"
