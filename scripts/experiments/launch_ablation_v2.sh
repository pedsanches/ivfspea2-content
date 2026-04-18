#!/bin/bash
# =========================================================================
# launch_ablation_v2.sh
# =========================================================================
# Launches 3 parallel MATLAB processes for the IVF/SPEA2 v2 ablation study.
#
# Each process uses 6 parpool workers:
#   Process 1 (Batch A): Baseline + V1 (dissimilar father)
#   Process 2 (Batch B): V2 (collective criterion) + V3 (eta_c=10)
#   Process 3 (Batch C): V4 (adaptive trigger) + V5 (post-SBX mutation)
#
# Total: 6 configs × 12 instances × 30 runs = 2,160 runs
# Estimated time: 4-8 hours depending on hardware
#
# Usage:
#   chmod +x scripts/experiments/launch_ablation_v2.sh
#   ./scripts/experiments/launch_ablation_v2.sh
# =========================================================================

set -e

PROJECT_ROOT="/home/pedro/desenvolvimento/ivfspea2"
SCRIPTS_DIR="${PROJECT_ROOT}/scripts/experiments"
LOGS_DIR="${PROJECT_ROOT}/logs"

mkdir -p "${LOGS_DIR}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=============================================="
echo " IVF/SPEA2 v2 Ablation Study - Phase 1"
echo "=============================================="
echo " Start time: $(date)"
echo " Batches: 3 parallel MATLAB processes"
echo " Workers per batch: 6"
echo " Total runs: 2,160"
echo "=============================================="
echo ""

# Detect MATLAB binary
MATLAB_BIN=$(which matlab 2>/dev/null || echo "")
if [ -z "$MATLAB_BIN" ]; then
    echo "[ERROR] MATLAB not found in PATH"
    echo "Please ensure MATLAB is installed and accessible."
    exit 1
fi
echo "[OK] MATLAB found: ${MATLAB_BIN}"
echo ""

# Launch Batch A (background)
echo "[LAUNCH] Batch A: Baseline + V1 (dissimilar father)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_batch_A.m')" \
    > "${LOGS_DIR}/ablation_v2_batchA_${TIMESTAMP}_stdout.log" 2>&1 &
PID_A=$!
echo "  PID: ${PID_A}"
echo "  Log: ${LOGS_DIR}/ablation_v2_batchA_${TIMESTAMP}_stdout.log"

# Small delay to avoid PlatEMO path conflicts
sleep 5

# Launch Batch B (background)
echo "[LAUNCH] Batch B: V2 (collective) + V3 (eta_c=10)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_batch_B.m')" \
    > "${LOGS_DIR}/ablation_v2_batchB_${TIMESTAMP}_stdout.log" 2>&1 &
PID_B=$!
echo "  PID: ${PID_B}"
echo "  Log: ${LOGS_DIR}/ablation_v2_batchB_${TIMESTAMP}_stdout.log"

sleep 5

# Launch Batch C (background)
echo "[LAUNCH] Batch C: V4 (adaptive) + V5 (mutation)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_batch_C.m')" \
    > "${LOGS_DIR}/ablation_v2_batchC_${TIMESTAMP}_stdout.log" 2>&1 &
PID_C=$!
echo "  PID: ${PID_C}"
echo "  Log: ${LOGS_DIR}/ablation_v2_batchC_${TIMESTAMP}_stdout.log"

echo ""
echo "=============================================="
echo " All 3 batches launched successfully!"
echo "=============================================="
echo ""
echo " Process IDs:"
echo "   Batch A: ${PID_A}"
echo "   Batch B: ${PID_B}"
echo "   Batch C: ${PID_C}"
echo ""
echo " Monitor progress:"
echo "   tail -f ${LOGS_DIR}/ablation_v2_batchA_${TIMESTAMP}_stdout.log"
echo "   tail -f ${LOGS_DIR}/ablation_v2_batchB_${TIMESTAMP}_stdout.log"
echo "   tail -f ${LOGS_DIR}/ablation_v2_batchC_${TIMESTAMP}_stdout.log"
echo ""
echo " Check if all finished:"
echo "   ps -p ${PID_A},${PID_B},${PID_C}"
echo ""
echo " Results will be saved to:"
echo "   ${PROJECT_ROOT}/data/ablation_v2/phase1/"
echo ""

# Save PIDs for later reference
echo "${PID_A}" > "${LOGS_DIR}/ablation_v2_pids_${TIMESTAMP}.txt"
echo "${PID_B}" >> "${LOGS_DIR}/ablation_v2_pids_${TIMESTAMP}.txt"
echo "${PID_C}" >> "${LOGS_DIR}/ablation_v2_pids_${TIMESTAMP}.txt"
echo " PID file: ${LOGS_DIR}/ablation_v2_pids_${TIMESTAMP}.txt"
