#!/bin/bash
# =========================================================================
# launch_ablation_v2_phase3.sh
# =========================================================================
# Launches Phase 3 full-suite validation for ablation v2 winner (P2_C05).
#
# Batches:
#   - Batch A: round-robin subset A of 51 problems
#   - Batch B: round-robin subset B of 51 problems
#   - Batch C: round-robin subset C of 51 problems
#
# Total: 51 problems x 60 runs = 3,060 runs
#
# Usage:
#   chmod +x scripts/experiments/launch_ablation_v2_phase3.sh
#   ./scripts/experiments/launch_ablation_v2_phase3.sh
# =========================================================================

set -e

PROJECT_ROOT="/home/pedro/desenvolvimento/ivfspea2"
SCRIPTS_DIR="${PROJECT_ROOT}/scripts/experiments"
LOGS_DIR="${PROJECT_ROOT}/logs"

mkdir -p "${LOGS_DIR}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=============================================="
echo " IVF/SPEA2 v2 Ablation - Phase 3"
echo " Winner-only full-suite validation (P2_C05)"
echo "=============================================="
echo " Start time: $(date)"
echo " Batches: 3 parallel MATLAB processes"
echo " Workers per batch: 6"
echo " Problems: 51"
echo " Runs per problem: 60"
echo " Total runs: 3,060"
echo " Run-ID range: 300001..300060"
echo "=============================================="
echo ""

MATLAB_BIN=$(which matlab 2>/dev/null || echo "")
if [ -z "$MATLAB_BIN" ]; then
    echo "[ERROR] MATLAB not found in PATH"
    exit 1
fi
echo "[OK] MATLAB found: ${MATLAB_BIN}"

PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
if [ ! -x "${PYTHON_BIN}" ]; then
    PYTHON_BIN="python3"
fi
echo "[OK] Python for checks: ${PYTHON_BIN}"
echo ""

echo "[CHECK] Running preflight checks..."
"${PYTHON_BIN}" "${SCRIPTS_DIR}/preflight_ablation_v2_phase3.py" --project-root "${PROJECT_ROOT}" --python-exec "${PYTHON_BIN}"
echo "[OK] Preflight checks passed."
echo ""

echo "[LAUNCH] Batch A"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase3_batch_A.m')" \
    > "${LOGS_DIR}/ablation_v2_phase3_batchA_${TIMESTAMP}_stdout.log" 2>&1 &
PID_A=$!
echo "  PID: ${PID_A}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase3_batchA_${TIMESTAMP}_stdout.log"

sleep 15

echo "[LAUNCH] Batch B"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase3_batch_B.m')" \
    > "${LOGS_DIR}/ablation_v2_phase3_batchB_${TIMESTAMP}_stdout.log" 2>&1 &
PID_B=$!
echo "  PID: ${PID_B}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase3_batchB_${TIMESTAMP}_stdout.log"

sleep 15

echo "[LAUNCH] Batch C"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase3_batch_C.m')" \
    > "${LOGS_DIR}/ablation_v2_phase3_batchC_${TIMESTAMP}_stdout.log" 2>&1 &
PID_C=$!
echo "  PID: ${PID_C}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase3_batchC_${TIMESTAMP}_stdout.log"

echo ""
echo "=============================================="
echo " Phase 3 batches launched successfully"
echo "=============================================="
echo ""
echo "Process IDs:"
echo "  Batch A: ${PID_A}"
echo "  Batch B: ${PID_B}"
echo "  Batch C: ${PID_C}"
echo ""
echo "Monitor logs:"
echo "  tail -f ${LOGS_DIR}/ablation_v2_phase3_batchA_${TIMESTAMP}_stdout.log"
echo "  tail -f ${LOGS_DIR}/ablation_v2_phase3_batchB_${TIMESTAMP}_stdout.log"
echo "  tail -f ${LOGS_DIR}/ablation_v2_phase3_batchC_${TIMESTAMP}_stdout.log"
echo ""
echo "Check active processes:"
echo "  ps -p ${PID_A},${PID_B},${PID_C}"
echo ""
echo "After completion, validate integrity:"
echo "  ${PYTHON_BIN} ${SCRIPTS_DIR}/verify_ablation_v2_phase3_integrity.py"
echo "  ${PYTHON_BIN} ${SCRIPTS_DIR}/verify_ablation_v2_phase3_integrity.py --check-metrics"
echo ""
echo "Results target:"
echo "  ${PROJECT_ROOT}/data/ablation_v2/phase3/"

PID_FILE="${LOGS_DIR}/ablation_v2_phase3_pids_${TIMESTAMP}.txt"
echo "${PID_A}" > "${PID_FILE}"
echo "${PID_B}" >> "${PID_FILE}"
echo "${PID_C}" >> "${PID_FILE}"
echo ""
echo "PID file: ${PID_FILE}"
