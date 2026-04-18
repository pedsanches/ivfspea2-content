#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/src/matlab/lib/PlatEMO/Data/IVFSPEA2"

RUN_START="${1:-2001}"
RUN_END="${2:-2100}"
EXPECTED_CONFIGS="${3:-52}"
EXPECTED_RUNS_PER_CONFIG=$((RUN_END - RUN_START + 1))
EXPECTED_TOTAL=$((EXPECTED_CONFIGS * EXPECTED_RUNS_PER_CONFIG))

if [[ ! -d "$DATA_DIR" ]]; then
  echo "Data directory not found: $DATA_DIR"
  exit 1
fi

read -r TOTAL_FILES COMPLETE_CONFIGS PARTIAL_CONFIGS EMPTY_CONFIGS <<EOF
$(find "$DATA_DIR" -maxdepth 1 -type f -name 'IVFSPEA2_*.mat' | \
  awk -v lo="$RUN_START" -v hi="$RUN_END" -v expectedCfg="$EXPECTED_CONFIGS" '
    {
      fn = $0
      sub(/^.*\//, "", fn)
      if (match(fn, /_([0-9]+)\.mat$/, m)) {
        run = m[1] + 0
        if (run >= lo && run <= hi) {
          key = fn
          sub(/_[0-9]+\.mat$/, "", key)
          total++
          cfg[key]++
        }
      }
    }
    END {
      done = 0
      partial = 0
      for (k in cfg) {
        if (cfg[k] == (hi - lo + 1)) done++
        else partial++
      }
      empty = expectedCfg - done - partial
      if (empty < 0) empty = 0
      printf "%d %d %d %d\n", total, done, partial, empty
    }')
EOF

PCT=$(awk -v n="$TOTAL_FILES" -v d="$EXPECTED_TOTAL" 'BEGIN { if (d>0) printf "%.2f", (100*n)/d; else print "0.00" }')

echo "submission_range=${RUN_START}..${RUN_END}"
echo "expected_configs=${EXPECTED_CONFIGS}"
echo "expected_total_files=${EXPECTED_TOTAL}"
echo "found_total_files=${TOTAL_FILES}"
echo "progress_pct=${PCT}%"
echo "configs_complete=${COMPLETE_CONFIGS}"
echo "configs_partial=${PARTIAL_CONFIGS}"
echo "configs_empty=${EMPTY_CONFIGS}"
