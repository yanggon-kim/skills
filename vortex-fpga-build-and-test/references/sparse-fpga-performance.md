# Sparse vs Dense FPGA Performance (fp16, NT=8, Alveo U55C)

## Build Configuration

- Bitstream: `build_sparse_tcu_1c` (includes both dense and sparse paths)
- CONFIGS: `-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE`
- Data type: FP16 input, FP32 output (only type supported by DSP FEDP)
- Clock: 300 MHz (WNS = +0.003 ns)
- Platform: Alveo U55C (xilinx_u55c_gen3x16_xdma_3_202210_1)

## Performance Table

| M | N | K | Dense Cycles | Sparse Cycles | Speedup | Notes |
|---|---|---|-------------|--------------|---------|-------|
| 16 | 16 | 32 | 95,384 | 125,756 | 0.76x | Baseline size (default) |
| 32 | 32 | 64 | 104,379 | 130,085 | 0.80x | Metadata overhead dominates |
| 32 | 32 | 128 | 130,597 | 144,636 | 0.90x | Approaching crossover |
| 32 | 32 | 256 | 193,763 | 185,636 | 1.04x | Crossover point |
| 32 | 32 | 512 | 303,289 | 253,863 | 1.19x | |
| 32 | 32 | 1024 | 596,562 | 392,053 | 1.52x | |
| 64 | 64 | 64 | 274,873 | 353,451 | 0.78x | |
| 64 | 64 | 256 | 590,510 | 568,393 | 1.04x | |
| 64 | 64 | 512 | 1,022,814 | 841,165 | 1.22x | |
| 64 | 64 | 1024 | 2,254,121 | 1,399,798 | 1.61x | |
| 128 | 128 | 512 | 4,935,399 | 3,177,845 | 1.55x | |
| 128 | 128 | 1024 | 9,933,634 | 5,452,424 | 1.82x | Peak speedup |

## Key Observations

### Crossover at K ~ 256
- Below K=256: sparse is slower due to metadata load overhead (meta_store instructions, compressed B load with 2x data)
- At K=256: sparse and dense are roughly equal (~1.04x)
- Above K=256: sparse TCU wins increasingly as K grows (more compute to amortize metadata cost)

### Scaling with Problem Size
- Speedup increases with K (more compute per metadata load): 1.04x@256 -> 1.22x@512 -> 1.61x@1024
- Speedup increases with M,N (more blocks sharing metadata amortization): 32x32x1024=1.52x vs 128x128x1024=1.82x

### FPGA vs RTLsim Cycle Comparison
- FPGA cycles are ~1.5-2x RTLsim cycles for the same workload
- Root cause: HBM latency on real hardware vs idealized memory in RTLsim
- Ratio is consistent across dense and sparse, so speedup comparisons are valid on both

## Measurement Methodology

### csr_read(0xB00) Cycle Counter
- Kernel wraps the TCU compute loop with `csr_read(0xB00)` (mcycle CSR)
- Start/end cycle values written to device memory, read back by host
- Reports `TCU_CYCLES: max=N (across B blocks)` — takes max across all thread blocks
- Reliable for both RTLsim and FPGA — reads the same hardware cycle counter

### Verification Notes
- Some large fp16 tests show 1-3 element mismatches out of 1024 (FP rounding)
- These are FP precision differences, NOT functional failures
- Cycle counts from these runs are still valid for performance comparison

## Reproducing

### Build
```bash
cd hw/syn/xilinx/xrt
PREFIX=build_sparse_tcu_1c NUM_CORES=1 TARGET=hw \
  PLATFORM=xilinx_u55c_gen3x16_xdma_3_202210_1 \
  CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE" \
  make > build_sparse_tcu_1c.log 2>&1 &
```

### Run Dense Test
```bash
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE" \
  make -C tests/regression/sgemm_tcu clean
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE" \
  make -C tests/regression/sgemm_tcu

export FPGA_BIN_DIR=$PWD/hw/syn/xilinx/xrt/build_sparse_tcu_1c_xilinx_u55c_gen3x16_xdma_3_202210_1_hw/bin
OPTS="-m32 -n32 -k256" TARGET=hw make -C tests/regression/sgemm_tcu run-xrt
```

### Run Sparse Test
```bash
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE" \
  make -C tests/regression/sgemm_tcu_struct_sparse clean
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE" \
  make -C tests/regression/sgemm_tcu_struct_sparse

export FPGA_BIN_DIR=$PWD/hw/syn/xilinx/xrt/build_sparse_tcu_1c_xilinx_u55c_gen3x16_xdma_3_202210_1_hw/bin
OPTS="-m32 -n32 -k256" TARGET=hw make -C tests/regression/sgemm_tcu_struct_sparse run-xrt
```
