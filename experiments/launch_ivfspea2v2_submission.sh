#!/bin/bash
# launch_ivfspea2v2_submission.sh — Launch 3 parallel MATLAB instances for v2 submission
#
# Each instance gets ~17-18 problem configs and uses 6 parpool workers.
# Total: 3 instances × 6 workers = 18 cores.
#
# Usage:
#   chmod +x experiments/launch_ivfspea2v2_submission.sh
#   ./experiments/launch_ivfspea2v2_submission.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"

SCRIPT="${SCRIPT_DIR}/run_ivfspea2v2_submission.m"

if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: $SCRIPT not found"
    exit 1
fi

echo "=== Launching IVFSPEA2V2 Submission (config C26) — 3 runners × 6 workers ==="
echo "Start time: $(date)"
echo "Logs in: $LOG_DIR/"
echo ""

for RUNNER in 1 2 3; do
    LOGFILE="${LOG_DIR}/ivfspea2v2_submission_runner${RUNNER}_$(date +%Y%m%d_%H%M%S).log"
    echo "  Starting runner ${RUNNER} → ${LOGFILE}"
    RUNNER_ID=${RUNNER} nohup matlab -batch "run('${SCRIPT}')" > "${LOGFILE}" 2>&1 &
    echo "  PID: $!"
done

echo ""
echo "All 3 runners launched in background."
echo "Monitor with: tail -f ${LOG_DIR}/ivfspea2v2_submission_runner*.log"
echo "Check progress: ps aux | grep matlab"
