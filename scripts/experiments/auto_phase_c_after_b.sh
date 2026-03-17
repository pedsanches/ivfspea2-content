#!/usr/bin/env bash
set -euo pipefail

# auto_phase_c_after_b.sh
#
# Waits for current tuning jobs to finish, validates Phase B integrity,
# then launches Phase C automatically.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

CHECK_INTERVAL="${CHECK_INTERVAL:-120}"
NUM_GROUPS="${NUM_GROUPS:-3}"
WORKERS="${V2_TUNE_WORKERS:-6}"
VERIFY_FULL_METRICS="${VERIFY_FULL_METRICS:-1}"
ANALYZE_B="${ANALYZE_B:-1}"
PHASEB_ENV_FILE="${PHASEB_ENV_FILE:-results/tuning_ivfspea2v2/phaseB_center_from_phaseA.env}"
PHASE_C_ALLOW_RESUME="${PHASE_C_ALLOW_RESUME:-0}"
MAX_VERIFY_ATTEMPTS="${MAX_VERIFY_ATTEMPTS:-0}"
mkdir -p logs

# Single-instance lock (prevents duplicate Phase C launchers).
LOCK_FILE="${LOCK_FILE:-logs/auto_phase_c_after_b.lock}"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "ERROR: another auto_phase_c_after_b.sh instance is already running." >&2
  exit 3
fi

if ! [[ "$CHECK_INTERVAL" =~ ^[0-9]+$ ]] || [[ "$CHECK_INTERVAL" -lt 5 ]]; then
  echo "ERROR: CHECK_INTERVAL must be integer >= 5" >&2
  exit 2
fi
if ! [[ "$NUM_GROUPS" =~ ^[0-9]+$ ]] || [[ "$NUM_GROUPS" -lt 1 ]]; then
  echo "ERROR: NUM_GROUPS must be positive integer" >&2
  exit 2
fi
if ! [[ "$WORKERS" =~ ^[0-9]+$ ]] || [[ "$WORKERS" -lt 1 ]]; then
  echo "ERROR: V2_TUNE_WORKERS must be positive integer" >&2
  exit 2
fi
if ! [[ "$PHASE_C_ALLOW_RESUME" =~ ^[01]$ ]]; then
  echo "ERROR: PHASE_C_ALLOW_RESUME must be 0 or 1" >&2
  exit 2
fi
if ! [[ "$MAX_VERIFY_ATTEMPTS" =~ ^[0-9]+$ ]]; then
  echo "ERROR: MAX_VERIFY_ATTEMPTS must be integer >= 0" >&2
  exit 2
fi

if [[ -f "$PHASEB_ENV_FILE" ]]; then
  set -a
  source "$PHASEB_ENV_FILE"
  set +a
fi

# Phase C center defaults to the same center used in Phase B if not explicitly set.
export V2_TUNE_CENTER_R="${V2_TUNE_CENTER_R:-${V2_TUNE_FIXED_R:-0.2}}"
export V2_TUNE_CENTER_C="${V2_TUNE_CENTER_C:-${V2_TUNE_FIXED_C:-0.16}}"
export V2_TUNE_CENTER_CYCLES="${V2_TUNE_CENTER_CYCLES:-${V2_TUNE_FIXED_CYCLES:-2}}"

# Keep C runbase isolated from B using a dedicated variable.
# Defaults to 500001 (the canonical Phase C range in this tuning pipeline).
PHASE_C_RUNBASE="${V2_TUNE_C_RUNBASE:-500001}"
export V2_TUNE_RUNBASE="$PHASE_C_RUNBASE"
export V2_TUNE_PROBLEM_SET="${V2_TUNE_PROBLEM_SET:-FULL12}"
export V2_TUNE_ONLY_MISSING="${V2_TUNE_ONLY_MISSING:-1}"

echo "=== Auto Phase C after B ==="
echo "Project root: $PROJECT_ROOT"
echo "Check interval: ${CHECK_INTERVAL}s"
echo "Phase B env file: $PHASEB_ENV_FILE"
echo "Phase C center: R=$V2_TUNE_CENTER_R C=$V2_TUNE_CENTER_C Cycles=$V2_TUNE_CENTER_CYCLES"
echo "Phase C runbase: $V2_TUNE_RUNBASE"
echo "Workers/job: $WORKERS | Groups: $NUM_GROUPS"
echo "Phase C allow resume: $PHASE_C_ALLOW_RESUME"
echo "Max verify attempts: $MAX_VERIFY_ATTEMPTS (0=unlimited)"

verify_cmd=(.venv/bin/python scripts/experiments/verify_ivfspea2v2_tuning_integrity.py --phase B)
if [[ "$VERIFY_FULL_METRICS" == "1" ]]; then
  verify_cmd+=(--full-metric-scan)
fi

verify_attempt=0
while true; do
  count="$(pgrep -fc "run_ivfspea2v2_tuning.m" || true)"
  if [[ "$count" -gt 0 ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Waiting: $count tuning job(s) still running"
    sleep "$CHECK_INTERVAL"
    continue
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] No active tuning jobs found. Verifying Phase B integrity..."
  if "${verify_cmd[@]}"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase B integrity PASS."
    break
  fi

  verify_attempt=$((verify_attempt + 1))
  if [[ "$MAX_VERIFY_ATTEMPTS" -gt 0 ]] && [[ "$verify_attempt" -ge "$MAX_VERIFY_ATTEMPTS" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase B integrity failed after $verify_attempt attempts. Aborting." >&2
    exit 1
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase B integrity not ready (attempt $verify_attempt). Retrying in ${CHECK_INTERVAL}s..." >&2
  sleep "$CHECK_INTERVAL"
done

if [[ "$ANALYZE_B" == "1" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running Phase B analysis snapshot..."
  .venv/bin/python src/python/analysis/analyze_ivfspea2v2_tuning.py --phases B || true
fi

# Guard against accidental contamination of Phase C data.
shopt -s nullglob
phase_c_files=(data/tuning_ivfspea2v2/phaseC/*/*.mat)
stage_files=(src/matlab/lib/PlatEMO/Data/IVFSPEA2V2/*.mat)
phase_c_count=${#phase_c_files[@]}
stage_count=${#stage_files[@]}
shopt -u nullglob

if [[ "$PHASE_C_ALLOW_RESUME" == "0" ]] && { [[ "$phase_c_count" -gt 0 ]] || [[ "$stage_count" -gt 0 ]]; }; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Refusing to auto-launch Phase C on dirty outputs." >&2
  echo "  Existing phaseC files: $phase_c_count" >&2
  echo "  Existing staging files: $stage_count" >&2
  echo "  Set PHASE_C_ALLOW_RESUME=1 to override." >&2
  exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching Phase C..."
pre_count="$(pgrep -fc "run_ivfspea2v2_tuning.m" || true)"
LAUNCH_MODE=run V2_TUNE_WORKERS="$WORKERS" scripts/experiments/launch_ivfspea2v2_tuning.sh C "$NUM_GROUPS"

sleep 10
post_count="$(pgrep -fc "run_ivfspea2v2_tuning.m" || true)"
if [[ "$post_count" -le "$pre_count" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase C launch may have failed (process count did not increase)." >&2
  exit 1
fi

trigger_file="results/tuning_ivfspea2v2/phaseC_autostart_trigger_$(date +%Y%m%d_%H%M%S).txt"
cat > "$trigger_file" <<EOF
phase=B->C
triggered_at=$(date '+%Y-%m-%d %H:%M:%S')
phase_c_center_r=$V2_TUNE_CENTER_R
phase_c_center_c=$V2_TUNE_CENTER_C
phase_c_center_cycles=$V2_TUNE_CENTER_CYCLES
phase_c_runbase=$V2_TUNE_RUNBASE
workers=$WORKERS
groups=$NUM_GROUPS
verify_full_metrics=$VERIFY_FULL_METRICS
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase C launch command submitted."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Trigger record: $trigger_file"
