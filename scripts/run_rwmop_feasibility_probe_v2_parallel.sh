#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/pedro/desenvolvimento/ivfspea2"
RUNNER="$ROOT/experiments/probe_rwmop_feasibility_v2.m"
LOG_DIR="$ROOT/logs"
OUT_DIR="$ROOT/results/engineering_screening"
mkdir -p "$LOG_DIR" "$OUT_DIR"

TS="$(date +%Y%m%d_%H%M%S)"
ALGO="${PROBE_ALGO:-IVFSPEA2V2}"
RUNS="${PROBE_RUNS:-1}"
MAXFE="${PROBE_MAXFE:-50000}"
WORKERS="${PROBE_WORKERS:-6}"
THREAD_CAP="${THREAD_CAP:-1}"
M_SET="${PROBE_M_SET:-2,3}"

# 3 shards x 6 workers = 18 workers total on a 20-thread host.
SHARD_1_FROM="${SHARD_1_FROM:-1}"
SHARD_1_TO="${SHARD_1_TO:-17}"
SHARD_2_FROM="${SHARD_2_FROM:-18}"
SHARD_2_TO="${SHARD_2_TO:-34}"
SHARD_3_FROM="${SHARD_3_FROM:-35}"
SHARD_3_TO="${SHARD_3_TO:-50}"

run_shard() {
  local label="$1"
  local from_id="$2"
  local to_id="$3"
  local log_file="$LOG_DIR/rwmop_probe_${ALGO,,}_${label}_${TS}.log"

  env \
    PROBE_ALGO="$ALGO" \
    PROBE_FROM="$from_id" \
    PROBE_TO="$to_id" \
    PROBE_RUNS="$RUNS" \
    PROBE_MAXFE="$MAXFE" \
    PROBE_WORKERS="$WORKERS" \
    PROBE_PARALLEL="PROBLEMS" \
    PROBE_OUTPUT_SUFFIX="$label" \
    PROBE_M_SET="$M_SET" \
    OMP_NUM_THREADS="$THREAD_CAP" \
    MKL_NUM_THREADS="$THREAD_CAP" \
    OPENBLAS_NUM_THREADS="$THREAD_CAP" \
    matlab -batch "run('${RUNNER}')" > "$log_file" 2>&1
}

(run_shard shard1 "$SHARD_1_FROM" "$SHARD_1_TO") & p1=$!
(run_shard shard2 "$SHARD_2_FROM" "$SHARD_2_TO") & p2=$!
(run_shard shard3 "$SHARD_3_FROM" "$SHARD_3_TO") & p3=$!

status=0
wait "$p1" || status=1
wait "$p2" || status=1
wait "$p3" || status=1

if [[ $status -ne 0 ]]; then
  printf 'One or more probe shards failed. Check logs in %s\n' "$LOG_DIR" >&2
  exit 1
fi

OUT_FILE="$OUT_DIR/rwmop_feasibility_probe_${ALGO,,}.csv"
SHARD_A="$OUT_DIR/rwmop_feasibility_probe_${ALGO,,}_shard1.csv"
SHARD_B="$OUT_DIR/rwmop_feasibility_probe_${ALGO,,}_shard2.csv"
SHARD_C="$OUT_DIR/rwmop_feasibility_probe_${ALGO,,}_shard3.csv"

python3 - "$SHARD_A" "$SHARD_B" "$SHARD_C" "$OUT_FILE" <<'PY'
import csv
import pathlib
import re
import sys

inputs = [pathlib.Path(p) for p in sys.argv[1:4]]
output = pathlib.Path(sys.argv[4])

rows = []
header = None
for path in inputs:
    if not path.exists():
        raise SystemExit(f"Missing shard file: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        file_header = next(reader)
        if header is None:
            header = file_header
        elif header != file_header:
            raise SystemExit(f"Header mismatch in {path}")
        rows.extend(reader)

def pid(row):
    m = re.search(r"(\d+)$", row[0])
    return int(m.group(1)) if m else 10**9

rows.sort(key=pid)

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)
PY

printf 'Merged probe CSV: %s\n' "$OUT_FILE"
printf 'Shard logs under: %s\n' "$LOG_DIR"
