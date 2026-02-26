#!/bin/bash
# ============================================================================
# NSight Compute Profiling Wrapper (Generalized)
# ============================================================================
# Usage:
#   bash scripts/run_ncu_profile.sh [strategy]
#     strategy: nvtx (default), top, kernel, all
#
# WARNING: NCU is VERY SLOW. Each kernel is replayed 17+ times.
#
# Environment variables for configuration:
#   NCU_SET=basic|roofline|full   Metric set (default: full)
#   NCU_NVTX_RANGE=...           NVTX range to profile (default: "inference/")
#   NCU_SKIP=N                   Skip first N kernels (default: 0)
#   NCU_COUNT=M                  Capture M kernels (default: 10)
#   NCU_KERNEL_REGEX=...         Kernel name regex (default: "gemm|cutlass")
#
# ADAPT: Change SCRIPT path for your project.
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$PROJECT_DIR/profiles"

# ADAPT: Path to your NCU profiling script
SCRIPT="$SCRIPT_DIR/ncu_profile_workload.py"

# ADAPT: Path to your venv (comment out if not using venv)
# VENV="$PROJECT_DIR/venv/bin/activate"
# source "$VENV"

mkdir -p "$PROFILE_DIR"

STRATEGY="${1:-nvtx}"
SET="${NCU_SET:-full}"
NVTX_RANGE="${NCU_NVTX_RANGE:-inference/}"
SKIP="${NCU_SKIP:-0}"
COUNT="${NCU_COUNT:-10}"
KERNEL_REGEX="${NCU_KERNEL_REGEX:-gemm|cutlass}"

echo "========================================"
echo "NCU Kernel Profiling - Strategy: $STRATEGY"
echo "Metric set: $SET"
echo "========================================"
echo ""
echo "WARNING: NCU is SLOW. Expect 5-30 minutes per run."
echo ""

case "$STRATEGY" in
    nvtx)
        echo "Profiling NVTX range: $NVTX_RANGE"
        ncu --set "$SET" \
            --nvtx --nvtx-include "$NVTX_RANGE" \
            --profile-from-start off \
            -o "$PROFILE_DIR/workload_ncu_nvtx" -f \
            python "$SCRIPT" --phase all
        ;;
    top)
        echo "Skipping $SKIP kernels, capturing $COUNT"
        ncu --set "$SET" \
            -s "$SKIP" -c "$COUNT" \
            -o "$PROFILE_DIR/workload_ncu_top" -f \
            python "$SCRIPT" --phase all
        ;;
    kernel)
        echo "Filtering kernels: $KERNEL_REGEX (max $COUNT)"
        ncu --set "$SET" \
            -k "regex:${KERNEL_REGEX}" -c "$COUNT" \
            -o "$PROFILE_DIR/workload_ncu_kernel" -f \
            python "$SCRIPT" --phase all
        ;;
    all)
        echo "Profiling ALL kernels (this will be VERY slow)..."
        ncu --set "$SET" \
            --profile-from-start off \
            -o "$PROFILE_DIR/workload_ncu_all" -f \
            python "$SCRIPT" --phase all
        ;;
    *)
        echo "Unknown strategy: $STRATEGY"
        echo "Available: nvtx, top, kernel, all"
        exit 1
        ;;
esac

echo ""
echo "Profile saved to $PROFILE_DIR/"

# Export CSV
NCU_FILE="$PROFILE_DIR/workload_ncu_${STRATEGY}.ncu-rep"
if [ -f "$NCU_FILE" ]; then
    CSV_FILE="$PROFILE_DIR/workload_ncu_${STRATEGY}.csv"
    echo "Exporting CSV to: $CSV_FILE"
    ncu --import "$NCU_FILE" --csv --page details > "$CSV_FILE" 2>/dev/null || true

    echo ""
    echo "View in GUI: ncu-ui $NCU_FILE"
    echo "Parse CSV:   python scripts/parse_ncu_results.py $NCU_FILE"
    echo "Detailed:    python scripts/parse_ncu_detailed.py $NCU_FILE"
fi
