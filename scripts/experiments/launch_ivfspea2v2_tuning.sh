#!/usr/bin/env bash
set -euo pipefail

# launch_ivfspea2v2_tuning.sh
#
# Helper launcher for parallel group execution of run_ivfspea2v2_tuning.m.
#
# Usage:
#   scripts/experiments/launch_ivfspea2v2_tuning.sh A
#   scripts/experiments/launch_ivfspea2v2_tuning.sh B 4
#
# Optional environment controls:
#   LAUNCH_MODE=print|run        (default: print)
#   V2_TUNE_RUNS=30
#   V2_TUNE_MAXFE=50000
#   V2_TUNE_PROBLEM_SET=SENTINEL|FULL12
#   V2_TUNE_WORKERS=<per process>
#
# Notes:
#   - print mode only prints commands (safe default)
#   - run mode starts one background MATLAB process per group

PHASE="${1:-A}"
NUM_GROUPS="${2:-4}"
MODE="${LAUNCH_MODE:-print}"

if [[ ! "$PHASE" =~ ^[ABC]$ ]]; then
  echo "ERROR: phase must be A, B, or C" >&2
  exit 2
fi

if ! [[ "$NUM_GROUPS" =~ ^[0-9]+$ ]] || [[ "$NUM_GROUPS" -lt 1 ]]; then
  echo "ERROR: num groups must be positive integer" >&2
  exit 2
fi

SCRIPT_PATH="scripts/experiments/run_ivfspea2v2_tuning.m"
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "ERROR: missing $SCRIPT_PATH" >&2
  exit 2
fi

echo "=== IVFSPEA2V2 tuning launcher ==="
echo "Phase: $PHASE"
echo "Groups: $NUM_GROUPS"
echo "Mode: $MODE"
echo

for ((g = 1; g <= NUM_GROUPS; g++)); do
  cmd="V2_TUNE_PHASE=$PHASE V2_TUNE_GROUP=G$g V2_TUNE_NUM_GROUPS=$NUM_GROUPS matlab -batch \"run('$SCRIPT_PATH')\""

  if [[ "$MODE" == "print" ]]; then
    echo "$cmd"
  elif [[ "$MODE" == "run" ]]; then
    log_file="logs/launch_ivfspea2v2_phase${PHASE}_g${g}_$(date +%Y%m%d_%H%M%S).log"
    nohup bash -lc "$cmd" > "$log_file" 2>&1 &
    echo "started G$g -> $log_file"
  else
    echo "ERROR: LAUNCH_MODE must be print or run" >&2
    exit 2
  fi
done

if [[ "$MODE" == "run" ]]; then
  echo
  echo "All group processes started in background."
  echo "Monitor with: ps -ef | grep matlab"
fi
