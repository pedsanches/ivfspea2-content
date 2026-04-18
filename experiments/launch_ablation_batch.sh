#!/bin/bash
# launch_ablation_batch.sh — Launch 6 parallel MATLAB runners for one ablation batch
#
# Usage:
#   ./experiments/launch_ablation_batch.sh 1   # Launch batch 1 (6 runners)
#   ./experiments/launch_ablation_batch.sh 2   # Launch batch 2 (6 runners)
#   ./experiments/launch_ablation_batch.sh 3   # Launch batch 3 (6 runners)

BATCH=${1:?Usage: $0 <batch_number 1|2|3>}
LOGDIR="logs/ablation_batch${BATCH}"
mkdir -p "$LOGDIR"

SCRIPT="experiments/run_ablation_batch${BATCH}.m"

if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: $SCRIPT not found"
    exit 1
fi

echo "=== Launching Ablation Batch ${BATCH} — 6 runners ==="
echo "Logs in: $LOGDIR/"

for RUNNER in 1 2 3 4 5 6; do
    LOGFILE="${LOGDIR}/runner${RUNNER}_$(date +%Y%m%d_%H%M%S).log"
    echo "  Starting runner ${RUNNER} → ${LOGFILE}"
    RUNNER_ID=${RUNNER} nohup matlab -batch "run('${SCRIPT}')" > "${LOGFILE}" 2>&1 &
done

echo ""
echo "All 6 runners launched in background."
echo "Monitor with: tail -f ${LOGDIR}/runner*.log"
echo "Check progress: ps aux | grep matlab"
