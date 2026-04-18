#!/bin/bash
# =========================================================================
# launch_ablation_v2_phase2.sh
# =========================================================================
# Launches 3 parallel MATLAB processes for Phase 2 of the ablation study.
#
# Full 2^4 factorial design (16 combinations of H1/H2/H3/H4):
#   Process 1 (Batch A): C0-C5   (baseline + singles + H1H2)
#   Process 2 (Batch B): C6-C10  (remaining 2-factor combos)
#   Process 3 (Batch C): C11-C15 (3-factor + full factorial)
#
# Total: 16 configs × 12 instances × 60 runs = 11,520 runs
# Estimated time: 12-24 hours depending on hardware
#
# Usage:
#   chmod +x scripts/experiments/launch_ablation_v2_phase2.sh
#   ./scripts/experiments/launch_ablation_v2_phase2.sh
# =========================================================================

set -e

PROJECT_ROOT="/home/pedro/desenvolvimento/ivfspea2"
SCRIPTS_DIR="${PROJECT_ROOT}/scripts/experiments"
LOGS_DIR="${PROJECT_ROOT}/logs"

mkdir -p "${LOGS_DIR}"

# Create isolated working directories so each batch writes PlatEMO Data/ separately
WORK_A="${PROJECT_ROOT}/logs/workdir_batchA"
WORK_B="${PROJECT_ROOT}/logs/workdir_batchB"
WORK_C="${PROJECT_ROOT}/logs/workdir_batchC"
mkdir -p "${WORK_A}" "${WORK_B}" "${WORK_C}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=============================================="
echo " IVF/SPEA2 v2 Ablation Study - Phase 2"
echo " Full 2^4 Factorial Design"
echo "=============================================="
echo " Start time: $(date)"
echo " Batches: 3 parallel MATLAB processes"
echo " Workers per batch: 6"
echo " Configs: 16 (C0-C15)"
echo " Instances: 12"
echo " Runs per config-instance: 60"
echo " Total runs: 11,520"
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

# Launch Batch A: C0-C5 (6 configs)
echo "[LAUNCH] Batch A: C0-C5 (baseline + singles + H1H2)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase2_batch_A.m')" \
    > "${LOGS_DIR}/ablation_v2_phase2_batchA_${TIMESTAMP}_stdout.log" 2>&1 &
PID_A=$!
echo "  PID: ${PID_A}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase2_batchA_${TIMESTAMP}_stdout.log"

# Delay to let pool initialize before next launch
sleep 15

# Launch Batch B: C6-C10 (5 configs)
echo "[LAUNCH] Batch B: C6-C10 (remaining 2-factor combos)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase2_batch_B.m')" \
    > "${LOGS_DIR}/ablation_v2_phase2_batchB_${TIMESTAMP}_stdout.log" 2>&1 &
PID_B=$!
echo "  PID: ${PID_B}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase2_batchB_${TIMESTAMP}_stdout.log"

sleep 15

# Launch Batch C: C11-C15 (5 configs)
echo "[LAUNCH] Batch C: C11-C15 (3-factor + full factorial)"
nohup matlab -nodisplay -nosplash -r "run('${SCRIPTS_DIR}/run_ablation_v2_phase2_batch_C.m')" \
    > "${LOGS_DIR}/ablation_v2_phase2_batchC_${TIMESTAMP}_stdout.log" 2>&1 &
PID_C=$!
echo "  PID: ${PID_C}"
echo "  Log: ${LOGS_DIR}/ablation_v2_phase2_batchC_${TIMESTAMP}_stdout.log"

echo ""
echo "=============================================="
echo " All 3 Phase 2 batches launched successfully!"
echo "=============================================="
echo ""
echo " Process IDs:"
echo "   Batch A (C0-C5):   ${PID_A}"
echo "   Batch B (C6-C10):  ${PID_B}"
echo "   Batch C (C11-C15): ${PID_C}"
echo ""
echo " Monitor progress:"
echo "   tail -f ${LOGS_DIR}/ablation_v2_phase2_batchA_${TIMESTAMP}_stdout.log"
echo "   tail -f ${LOGS_DIR}/ablation_v2_phase2_batchB_${TIMESTAMP}_stdout.log"
echo "   tail -f ${LOGS_DIR}/ablation_v2_phase2_batchC_${TIMESTAMP}_stdout.log"
echo ""
echo " Check if all finished:"
echo "   ps -p ${PID_A},${PID_B},${PID_C}"
echo ""
echo " After completion, verify integrity:"
echo "   python3 ${SCRIPTS_DIR}/verify_ablation_v2_phase2_integrity.py"
echo ""
echo " Results will be saved to:"
echo "   ${PROJECT_ROOT}/data/ablation_v2/phase2/"
echo ""

# Save PIDs for later reference
echo "${PID_A}" > "${LOGS_DIR}/ablation_v2_phase2_pids_${TIMESTAMP}.txt"
echo "${PID_B}" >> "${LOGS_DIR}/ablation_v2_phase2_pids_${TIMESTAMP}.txt"
echo "${PID_C}" >> "${LOGS_DIR}/ablation_v2_phase2_pids_${TIMESTAMP}.txt"
echo " PID file: ${LOGS_DIR}/ablation_v2_phase2_pids_${TIMESTAMP}.txt"
