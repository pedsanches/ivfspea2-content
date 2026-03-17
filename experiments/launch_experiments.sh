#!/bin/bash
# launch_experiments.sh — Launch experiment phases in parallel MATLAB instances
#
# Usage:
#   chmod +x experiments/launch_experiments.sh
#   ./experiments/launch_experiments.sh [phase]
#
# Phases:
#   all         — Launch all 4 phases (3 MATLAB instances)
#   ablation    — Phase 1.1 only
#   rwmop9      — Phase 1.4 only
#   baselines   — Phase 1.2 only
#   sensitivity — Phase 1.3 only
#   validate    — Run validation checker
#
# Each phase runs in a separate nohup background process.
# Logs are saved to experiments/logs/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Find MATLAB binary (respect MATLAB_BIN if already exported)
if [ -z "$MATLAB_BIN" ]; then
    # Check PATH
    if command -v matlab &> /dev/null; then
        MATLAB_BIN=$(command -v matlab)
    fi

    # Check common install locations if not in PATH
    if [ -z "$MATLAB_BIN" ]; then
        for path in "$HOME"/MATLAB/R*/bin/matlab; do
            [ -x "$path" ] && MATLAB_BIN="$path"
        done
    fi

    if [ -z "$MATLAB_BIN" ]; then
        for path in /usr/local/MATLAB/R*/bin/matlab; do
            [ -x "$path" ] && MATLAB_BIN="$path"
        done
    fi

    if [ -z "$MATLAB_BIN" ]; then
        for path in /opt/MATLAB/R*/bin/matlab; do
            [ -x "$path" ] && MATLAB_BIN="$path"
        done
    fi
fi

if [ -z "$MATLAB_BIN" ]; then
    echo "ERROR: MATLAB not found in PATH or standard locations."
    echo "Please set MATLAB_BIN manually in this script or export it:"
    echo "  export MATLAB_BIN=/path/to/matlab"
    exit 1
fi

echo "Using MATLAB: $MATLAB_BIN"

launch() {
    local phase="$1"
    local script="$2"
    local logfile="${LOG_DIR}/${phase}_${TIMESTAMP}.log"

    echo "Launching ${phase}..."
    echo "  Script: ${script}"
    echo "  Log:    ${logfile}"

    nohup "$MATLAB_BIN" -nodisplay -nosplash -batch "run('${script}')" \
        > "$logfile" 2>&1 &

    echo "  PID:    $!"
    echo ""
}

PHASE="${1:-all}"

case "$PHASE" in
    all)
        echo "=== Launching ALL experiment phases ==="
        echo "Start time: $(date)"
        echo ""
        # Instance 1: Ablation
        launch "ablation" "${SCRIPT_DIR}/run_ablation.m"
        # Instance 2: RWMOP9
        launch "rwmop9" "${SCRIPT_DIR}/run_rwmop9.m"
        # Instance 2: Baselines (long-running)
        launch "baselines" "${SCRIPT_DIR}/run_baselines.m"
        # Instance 3: Sensitivity (long-running)
        launch "sensitivity" "${SCRIPT_DIR}/run_sensitivity.m"
        echo "All phases launched. Monitor with: tail -f ${LOG_DIR}/*_${TIMESTAMP}.log"
        ;;
    ablation)
        launch "ablation" "${SCRIPT_DIR}/run_ablation.m"
        ;;
    rwmop9)
        launch "rwmop9" "${SCRIPT_DIR}/run_rwmop9.m"
        ;;
    baselines)
        launch "baselines" "${SCRIPT_DIR}/run_baselines.m"
        ;;
    sensitivity)
        launch "sensitivity" "${SCRIPT_DIR}/run_sensitivity.m"
        ;;
    validate)
        "$MATLAB_BIN" -nodisplay -nosplash -batch "run('${SCRIPT_DIR}/validate_results.m')"
        ;;
    *)
        echo "Usage: $0 {all|ablation|rwmop9|baselines|sensitivity|validate}"
        exit 1
        ;;
esac
