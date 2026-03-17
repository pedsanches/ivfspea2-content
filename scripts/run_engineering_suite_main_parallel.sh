#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/pedro/desenvolvimento/ivfspea2"
RUNNER="$ROOT/experiments/run_engineering_suite_rwmop.m"
PROCESSOR="$ROOT/experiments/process_engineering_suite.m"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
TS="$(date +%Y%m%d_%H%M%S)"

STAGE_RAW="${ENG_SUITE_STAGE:-MAIN}"
STAGE="$(printf '%s' "$STAGE_RAW" | tr '[:lower:]' '[:upper:]')"

case "$STAGE" in
  SCREEN)
    DEFAULT_RUNS=10
    DEFAULT_RUNBASE=1
    ;;
  MAIN)
    DEFAULT_RUNS=60
    DEFAULT_RUNBASE=11
    ;;
  *)
    printf 'Invalid ENG_SUITE_STAGE=%s (use SCREEN or MAIN)\n' "$STAGE_RAW" >&2
    exit 2
    ;;
esac

RUNS="${ENG_SUITE_RUNS:-$DEFAULT_RUNS}"
RUNBASE="${ENG_SUITE_RUNBASE:-$DEFAULT_RUNBASE}"
WORKERS="${ENG_SUITE_WORKERS:-6}"
PROBLEMS_FILE="${ENG_SUITE_PROBLEMS_FILE:-}"
THREAD_CAP="${THREAD_CAP:-1}"

run_group() {
  local grp="$1"
  local log_file="$LOG_DIR/engineering_suite_${STAGE,,}_${grp}_${TS}.log"

  if [[ -n "$PROBLEMS_FILE" ]]; then
    env \
      ENG_SUITE_STAGE="$STAGE" \
      ENG_SUITE_GROUP="$grp" \
      ENG_SUITE_RUNS="$RUNS" \
      ENG_SUITE_RUNBASE="$RUNBASE" \
      ENG_SUITE_WORKERS="$WORKERS" \
      ENG_SUITE_PROBLEMS_FILE="$PROBLEMS_FILE" \
      OMP_NUM_THREADS="$THREAD_CAP" \
      MKL_NUM_THREADS="$THREAD_CAP" \
      OPENBLAS_NUM_THREADS="$THREAD_CAP" \
      matlab -batch "run('${RUNNER}')" > "$log_file" 2>&1
  else
    env \
      ENG_SUITE_STAGE="$STAGE" \
      ENG_SUITE_GROUP="$grp" \
      ENG_SUITE_RUNS="$RUNS" \
      ENG_SUITE_RUNBASE="$RUNBASE" \
      ENG_SUITE_WORKERS="$WORKERS" \
      OMP_NUM_THREADS="$THREAD_CAP" \
      MKL_NUM_THREADS="$THREAD_CAP" \
      OPENBLAS_NUM_THREADS="$THREAD_CAP" \
      matlab -batch "run('${RUNNER}')" > "$log_file" 2>&1
  fi
}

(run_group G1) & p1=$!
(run_group G2) & p2=$!
(run_group G3) & p3=$!

status=0
wait "$p1" || status=1
wait "$p2" || status=1
wait "$p3" || status=1

if [[ $status -ne 0 ]]; then
  printf 'One or more group runs failed. Check logs in %s\n' "$LOG_DIR" >&2
  exit 1
fi

process_log="$LOG_DIR/engineering_suite_${STAGE,,}_process_${TS}.log"
if [[ -n "$PROBLEMS_FILE" ]]; then
  env \
    ENG_SUITE_STAGE="$STAGE" \
    ENG_SUITE_TARGET_RUNS="$RUNS" \
    ENG_SUITE_PROBLEMS_FILE="$PROBLEMS_FILE" \
    OMP_NUM_THREADS="$THREAD_CAP" \
    MKL_NUM_THREADS="$THREAD_CAP" \
    OPENBLAS_NUM_THREADS="$THREAD_CAP" \
    matlab -batch "run('${PROCESSOR}')" > "$process_log" 2>&1
else
  env \
    ENG_SUITE_STAGE="$STAGE" \
    ENG_SUITE_TARGET_RUNS="$RUNS" \
    OMP_NUM_THREADS="$THREAD_CAP" \
    MKL_NUM_THREADS="$THREAD_CAP" \
    OPENBLAS_NUM_THREADS="$THREAD_CAP" \
    matlab -batch "run('${PROCESSOR}')" > "$process_log" 2>&1
fi

printf 'Completed %s stage with grouped execution.\n' "$STAGE"
printf 'Runner logs under: %s\n' "$LOG_DIR"
printf 'Post-process log: %s\n' "$process_log"
