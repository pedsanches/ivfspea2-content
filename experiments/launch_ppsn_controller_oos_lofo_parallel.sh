#!/bin/bash
# Launch the OOS controller rerun in the historical free-trial pattern:
# 3 independent MATLAB clients, each with its own 6-worker parpool.
#
# Safety:
# - Uses a timestamped output root, so it never reuses an existing result tree.
# - Uses independent /tmp job-storage roots per batch.
# - Writes a launch manifest with PIDs, logs, manifests, and thresholds.

set -euo pipefail

PROJECT_ROOT="/home/pedro/desenvolvimento/ivfspea2"
EXPERIMENTS_DIR="${PROJECT_ROOT}/experiments"
LOGS_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

MATLAB_SCRIPT="${EXPERIMENTS_DIR}/run_ppsn_controller.m"
MATLAB_BIN="$(which matlab 2>/dev/null || true)"

MANIFEST_A="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_A.csv"
MANIFEST_B="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_B.csv"
MANIFEST_C="${PROJECT_ROOT}/config/ppsn_ctrl_oos_batch_C.csv"

THRESHOLD_COMMON="0.2158040201005025"
THRESHOLD_WFG="0.2478894472361809"
WORKERS="6"

OUTPUT_ROOT="${PROJECT_ROOT}/data/raw/ppsn_dynamics/controller_oos_lofo_parallel_${TIMESTAMP}"
LAUNCH_CSV="${LOGS_DIR}/ppsn_controller_oos_parallel_${TIMESTAMP}.csv"
SUMMARY_TXT="${LOGS_DIR}/ppsn_controller_oos_parallel_${TIMESTAMP}.txt"

if [ -z "${MATLAB_BIN}" ]; then
    echo "[ERROR] MATLAB not found in PATH"
    exit 1
fi

if [ -e "${OUTPUT_ROOT}" ]; then
    echo "[ERROR] Refusing to reuse existing output root: ${OUTPUT_ROOT}"
    exit 1
fi

mkdir -p "${LOGS_DIR}" "${OUTPUT_ROOT}"

JOB_A="/tmp/ppsn_ctrl_oos_parallel_A_${TIMESTAMP}"
JOB_B="/tmp/ppsn_ctrl_oos_parallel_B_${TIMESTAMP}"
JOB_C="/tmp/ppsn_ctrl_oos_parallel_C_${TIMESTAMP}"
mkdir -p "${JOB_A}" "${JOB_B}" "${JOB_C}"

cat > "${SUMMARY_TXT}" <<EOF
PPSN Controller OOS LOFO Parallel Launch
Timestamp: ${TIMESTAMP}
MATLAB: ${MATLAB_BIN}
Output root: ${OUTPUT_ROOT}
Workers per batch: ${WORKERS}
Mode: 3 independent MATLAB clients in parallel
EOF

printf "batch,pid,manifest,threshold,job_storage,logfile,output_root\n" > "${LAUNCH_CSV}"

echo "=============================================="
echo " PPSN Controller OOS LOFO Parallel Launch"
echo "=============================================="
echo " Start time: $(date)"
echo " MATLAB: ${MATLAB_BIN}"
echo " Output root: ${OUTPUT_ROOT}"
echo " Workers per batch: ${WORKERS}"
echo "=============================================="
echo ""

launch_batch() {
    local batch="$1"
    local manifest="$2"
    local threshold="$3"
    local job_storage="$4"
    local run_tag="ctrl_oos_${batch}_${TIMESTAMP}"
    local logfile="${LOGS_DIR}/ppsn_controller_oos_parallel_${batch}_${TIMESTAMP}.log"

    echo "[LAUNCH] Batch ${batch}"
    echo "  Manifest: ${manifest}"
    echo "  Threshold: ${threshold}"
    echo "  Job storage: ${job_storage}"
    echo "  Output root: ${OUTPUT_ROOT}"
    echo "  Log: ${logfile}"

    TMPDIR=/tmp TMP=/tmp TEMP=/tmp \
    PPSN_MANIFEST="${manifest}" \
    PPSN_WORKERS="${WORKERS}" \
    PPSN_RUN_TAG="${run_tag}" \
    PPSN_JOB_STORAGE="${job_storage}" \
    CTRL_OUTPUT_ROOT="${OUTPUT_ROOT}" \
    CTRL_TURNOVER_THRESHOLD="${threshold}" \
    nohup "${MATLAB_BIN}" -batch "run('${MATLAB_SCRIPT}')" > "${logfile}" 2>&1 &

    local pid=$!
    echo "  PID: ${pid}"
    printf "%s,%s,%s,%s,%s,%s,%s\n" \
        "${batch}" "${pid}" "${manifest}" "${threshold}" "${job_storage}" "${logfile}" "${OUTPUT_ROOT}" \
        >> "${LAUNCH_CSV}"
}

launch_batch "A" "${MANIFEST_A}" "${THRESHOLD_COMMON}" "${JOB_A}"
launch_batch "B" "${MANIFEST_B}" "${THRESHOLD_COMMON}" "${JOB_B}"
launch_batch "C" "${MANIFEST_C}" "${THRESHOLD_WFG}" "${JOB_C}"

echo ""
echo "All 3 OOS controller batches launched."
echo "Launch manifest: ${LAUNCH_CSV}"
echo "Summary: ${SUMMARY_TXT}"
