#!/bin/bash
# ============================================================================
# NSight Systems Profiling Wrapper (Generalized)
# ============================================================================
# Usage:
#   bash scripts/run_nsys_profile.sh [mode]
#     mode: single (default), batch, custom
#
# ADAPT: Change SCRIPT and VENV paths for your project.
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$PROJECT_DIR/profiles"

# ADAPT: Path to your profiling script
SCRIPT="$SCRIPT_DIR/profile_workload.py"

# ADAPT: Path to your venv (comment out if not using venv)
# VENV="$PROJECT_DIR/venv/bin/activate"
# source "$VENV"

mkdir -p "$PROFILE_DIR"

MODE="${1:-single}"

echo "========================================"
echo "NSight Systems Profiling - Mode: $MODE"
echo "========================================"

case "$MODE" in
    single)
        echo "Profiling single inference pass..."
        nsys profile \
            -o "$PROFILE_DIR/workload_nsys_single" \
            --trace=cuda,nvtx,osrt \
            -f true \
            python "$SCRIPT" --mode single-step --num-runs 1 --num-warmup 3 --batch-size 1
        ;;
    batch)
        echo "Profiling batch size sweep..."
        nsys profile \
            -o "$PROFILE_DIR/workload_nsys_batch" \
            --trace=cuda,nvtx,osrt \
            -f true \
            python "$SCRIPT" --mode batch-sweep
        ;;
    custom)
        # ADAPT: Add custom profiling configurations here
        echo "Custom profiling mode — edit this script to configure"
        shift
        nsys profile \
            -o "$PROFILE_DIR/workload_nsys_custom" \
            --trace=cuda,nvtx,osrt \
            -f true \
            python "$SCRIPT" "$@"
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Available: single, batch, custom"
        exit 1
        ;;
esac

echo ""
echo "Profile saved to $PROFILE_DIR/"

# Extract stats
PROFILE_FILE="$PROFILE_DIR/workload_nsys_${MODE}.nsys-rep"
if [ -f "$PROFILE_FILE" ]; then
    echo ""
    echo "--- CUDA Kernel Summary ---"
    nsys stats --report cuda_gpu_kern_sum "$PROFILE_FILE" 2>/dev/null || true

    echo ""
    echo "--- NVTX Range Summary ---"
    nsys stats --report nvtx_sum "$PROFILE_FILE" 2>/dev/null || true

    echo ""
    echo "View in GUI: nsys-ui $PROFILE_FILE"
fi
