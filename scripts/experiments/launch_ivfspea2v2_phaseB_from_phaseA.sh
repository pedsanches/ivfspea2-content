#!/usr/bin/env bash
set -euo pipefail

# launch_ivfspea2v2_phaseB_from_phaseA.sh
#
# Loads Phase B center selected from Phase A analysis and launches jobs.
#
# Usage:
#   scripts/experiments/launch_ivfspea2v2_phaseB_from_phaseA.sh
#   LAUNCH_MODE=run scripts/experiments/launch_ivfspea2v2_phaseB_from_phaseA.sh 3

NUM_GROUPS="${1:-3}"
ENV_FILE="${PHASEB_ENV_FILE:-results/tuning_ivfspea2v2/phaseB_center_from_phaseA.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: missing env file: $ENV_FILE" >&2
  echo "Generate it with: python3 scripts/experiments/prepare_ivfspea2v2_phase_b.py" >&2
  exit 2
fi

if ! [[ "$NUM_GROUPS" =~ ^[0-9]+$ ]] || [[ "$NUM_GROUPS" -lt 1 ]]; then
  echo "ERROR: num groups must be positive integer" >&2
  exit 2
fi

set -a
source "$ENV_FILE"
set +a

echo "Loaded Phase B center from: $ENV_FILE"
echo "  V2_TUNE_FIXED_R=${V2_TUNE_FIXED_R:-unset}"
echo "  V2_TUNE_FIXED_C=${V2_TUNE_FIXED_C:-unset}"
echo "  V2_TUNE_FIXED_CYCLES=${V2_TUNE_FIXED_CYCLES:-unset}"
echo "  V2_TUNE_RUNBASE=${V2_TUNE_RUNBASE:-unset}"
echo

scripts/experiments/launch_ivfspea2v2_tuning.sh B "$NUM_GROUPS"
