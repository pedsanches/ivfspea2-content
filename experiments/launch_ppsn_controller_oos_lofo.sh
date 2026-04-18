#!/bin/bash
# Launch the OOS controller rerun as 3 MATLAB batch executions.
#
# Batching strategy:
# - Batch A: ZDT + DTLZ subset, threshold 0.2158040201005025
# - Batch B: remaining DTLZ + all MaF, threshold 0.2158040201005025
# - Batch C: all WFG, threshold 0.2478894472361809
#
# Each batch uses 6 MATLAB workers.

set -euo pipefail

PROJECT_ROOT="/home/pedro/desenvolvimento/ivfspea2"
EXPERIMENTS_DIR="${PROJECT_ROOT}/experiments"
LOGS_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

MATLAB_SCRIPT="${EXPERIMENTS_DIR}/run_ppsn_controller.m"
OUTPUT_ROOT="${PROJECT_ROOT}/data/raw/ppsn_dynamics/controller_oos_lofo"

MANIFEST_A="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_A.csv"
MANIFEST_B="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_B.csv"
MANIFEST_C="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_C.csv"

THRESHOLD_COMMON="0.2158040201005025"
THRESHOLD_WFG="0.2478894472361809"
WORKERS="6"

mkdir -p "${LOGS_DIR}" "${OUTPUT_ROOT}"

JOB_A="/tmp/ppsn_ctrl_oos_jobs_A_${TIMESTAMP}"
JOB_B="/tmp/ppsn_ctrl_oos_jobs_B_${TIMESTAMP}"
JOB_C="/tmp/ppsn_ctrl_oos_jobs_C_${TIMESTAMP}"
mkdir -p "${JOB_A}" "${JOB_B}" "${JOB_C}"

MATLAB_BIN="$(which matlab 2>/dev/null || true)"
if [ -z "${MATLAB_BIN}" ]; then
    echo "[ERROR] MATLAB not found in PATH"
    exit 1
fi

echo "=============================================="
echo " PPSN Controller OOS LOFO Rerun"
echo "=============================================="
echo " Start time: $(date)"
echo " MATLAB: ${MATLAB_BIN}"
echo " Output root: ${OUTPUT_ROOT}"
echo " Workers per batch: ${WORKERS}"
echo " Launch mode: serial batches"
echo "=============================================="
echo ""

launch_batch() {
    local batch="$1"
    local manifest="$2"
    local threshold="$3"
    local job_storage="$4"
    local logfile="${LOGS_DIR}/ppsn_controller_oos_${batch}_${TIMESTAMP}.log"
    local prefdir="/tmp/matlab_pref_ctrl_oos_${batch}_${TIMESTAMP}"

    mkdir -p "${prefdir}"

    echo "[RUN] Batch ${batch}"
    echo "  Manifest: ${manifest}"
    echo "  Threshold: ${threshold}"
    echo "  Job storage: ${job_storage}"
    echo "  Prefdir: ${prefdir}"
    echo "  Log: ${logfile}"

    if TMPDIR=/tmp TMP=/tmp TEMP=/tmp MATLAB_PREFDIR="${prefdir}" OMP_NUM_THREADS=1 KMP_INIT_AT_FORK=FALSE \
        PPSN_MANIFEST="${manifest}" \
        PPSN_WORKERS="${WORKERS}" \
        PPSN_RUN_TAG="ctrl_oos_${batch}" \
        PPSN_JOB_STORAGE="${job_storage}" \
        CTRL_OUTPUT_ROOT="${OUTPUT_ROOT}" \
        CTRL_TURNOVER_THRESHOLD="${threshold}" \
        "${MATLAB_BIN}" -batch "run('${MATLAB_SCRIPT}')" > "${logfile}" 2>&1; then
        echo "  Status: completed"
    else
        local status=$?
        echo "  Status: failed (${status})"
        echo "  See log: ${logfile}"
        return "${status}"
    fi
}

launch_batch "A" "${MANIFEST_A}" "${THRESHOLD_COMMON}" "${JOB_A}"
launch_batch "B" "${MANIFEST_B}" "${THRESHOLD_COMMON}" "${JOB_B}"
launch_batch "C" "${MANIFEST_C}" "${THRESHOLD_WFG}" "${JOB_C}"

echo ""
echo "All 3 controller OOS batches completed."
echo "Monitor logs:"
echo "  tail -f ${LOGS_DIR}/ppsn_controller_oos_A_${TIMESTAMP}.log"
echo "  tail -f ${LOGS_DIR}/ppsn_controller_oos_B_${TIMESTAMP}.log"
echo "  tail -f ${LOGS_DIR}/ppsn_controller_oos_C_${TIMESTAMP}.log"
