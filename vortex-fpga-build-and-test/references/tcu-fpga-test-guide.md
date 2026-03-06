# TCU FPGA Test Guide

How to run dense, sparse, and integer-type TCU tests on the FPGA after a bitstream is built.

## Prerequisites

- A built bitstream with TCU enabled (e.g., `CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP"`)
- For sparse tests, the bitstream must also include `-DTCU_SPARSE_ENABLE`
- Environment sourced (Step 3 of SKILL.md)
- `FPGA_BIN_DIR` set to `$VORTEX_DIR/hw/syn/xilinx/xrt/<build>_hw/bin`

## Running Dense TCU Tests

Basic FP16 dense test (no extra flags needed, FP16/FP32 is the default):
```bash
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu clean
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu
OPTS="-m16 -n16 -k32" TARGET=hw make -C tests/regression/sgemm_tcu run-xrt
```

## Running Sparse TCU Tests

Rebuild the test binary with matching CONFIGS, then run via `make run-xrt`:
```bash
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu_struct_sparse clean
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu_struct_sparse
OPTS="-m16 -n16 -k32" TARGET=hw make -C tests/regression/sgemm_tcu_struct_sparse run-xrt
```

The test defaults (`common.h`) are FP16/FP32, so no extra ITYPE/OTYPE flags are needed for basic verification.

## Running Integer Type Tests

The DSP FEDP (`VX_tcu_fedp_dsp.sv`) supports FP16, BF16, INT8, UINT8, INT4, and UINT4 via a 3-stage pipelined integer dot product path. To run integer tests, pass ITYPE/OTYPE in CONFIGS when building the test binary:

```bash
# INT8 sparse test
CONFIGS="$USER_CONFIGS -DITYPE=int8 -DOTYPE=int32" \
  make -C tests/regression/sgemm_tcu_struct_sparse clean
CONFIGS="$USER_CONFIGS -DITYPE=int8 -DOTYPE=int32" \
  make -C tests/regression/sgemm_tcu_struct_sparse
OPTS="-m16 -n16 -k32" TARGET=hw make -C tests/regression/sgemm_tcu_struct_sparse run-xrt

# INT8 dense test
CONFIGS="$USER_CONFIGS -DITYPE=int8 -DOTYPE=int32" \
  make -C tests/regression/sgemm_tcu clean
CONFIGS="$USER_CONFIGS -DITYPE=int8 -DOTYPE=int32" \
  make -C tests/regression/sgemm_tcu
OPTS="-m16 -n16 -k32" TARGET=hw make -C tests/regression/sgemm_tcu run-xrt
```

The integer path adds ~18K LUTs (+1.4%) and 0 extra DSPs compared to FP16-only. It uses native-width multiplies (8×8 for INT8, 4×4 for INT4) in LUTs rather than DSP48E2 cascades. See `dsp-integer-pipeline.md` for the design details and timing data.

## Performance Sweeps

For performance comparisons, increase the `-m`, `-n`, `-k` OPTS:
```bash
# Example: 64x64 matrix with K=1024
OPTS="-m64 -n64 -k1024" TARGET=hw make -C tests/regression/sgemm_tcu run-xrt
OPTS="-m64 -n64 -k1024" TARGET=hw make -C tests/regression/sgemm_tcu_struct_sparse run-xrt
```

There is also a full sweep script at `tests/regression/sgemm_tcu_struct_sparse/run_full_sweep_fpga.sh` that runs all 3 types (FP16, INT8, INT4) across 20 sizes each, outputting CSV.

### Sparse Speedup Crossover Points

Sparse TCU only outperforms dense when K is large enough to amortize the metadata and 2x B-load overhead:

| Type | Crossover K (32×32) | Crossover K (64×64) | Peak Speedup |
|------|:---:|:---:|:---:|
| FP16 | ~256 | ~256 | 1.86x (128×128×1024) |
| INT8 | ~2048 | ~512 | 1.31x (64×64×2048) |
| INT4 | ~4096 | ~2048 | 1.09x (128×128×2048) |

FP16 benefits most because its B-load packing is lightest (halfword loads vs byte packing for INT8). See `sparse-fpga-performance.md` for the full 60-point data set.

## Common Issues

- **NUM_THREADS must be >=8** for sparse TCU (NT=4 causes static_assert failures)
- **Must `make clean` when switching ITYPE/OTYPE** — stale object files cause wrong results
- **FP16 rounding mismatches**: Large FP16 tests may show 1-3 element mismatches — these are precision differences, not functional bugs. Cycle counts are still valid.
- **NaN output with integer types**: Means the bitstream lacks the v3 integer pipeline. Rebuild with the current `VX_tcu_fedp_dsp.sv`.
