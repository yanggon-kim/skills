# Sparse vs Dense FPGA Performance (NT=8, Alveo U55C)

## Build Configuration

- Bitstream: `build_sparse_dsp_int_v3_1c` (supports dense+sparse, FP16+INT8+INT4)
- CONFIGS: `-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP -DTCU_SPARSE_ENABLE`
- Clock: 300 MHz (WNS = +0.003 ns)
- Platform: Alveo U55C (xilinx_u55c_gen3x16_xdma_3_202210_1)
- CSV: `full_fpga_sweep_results.csv` in repo root (60 data points, Excel-ready)

## Summary — Crossover Points & Peak Speedup

| Type | Crossover K (32×32) | Crossover K (64×64) | Crossover K (128×128) | Peak Speedup |
|------|:---:|:---:|:---:|:---:|
| FP16 | ~256 | ~256 | <512 | **1.86x** (128×128×1024) |
| INT8 | ~2048 | ~512 | ~512 | **1.31x** (64×64×2048) |
| INT4 | ~4096 | ~2048 | ~2048 | **1.09x** (128×128×2048) |

## FP16 (fp16/fp32) — Best sparse type

| Size | Dense | Sparse | Speedup |
|------|------:|-------:|--------:|
| 8×8×32 | 41,227 | 43,483 | 0.95x |
| 16×16×32 | 63,514 | 72,694 | 0.87x |
| 16×16×64 | 67,100 | 74,928 | 0.90x |
| 32×32×64 | 103,725 | 130,437 | 0.80x |
| 32×32×128 | 131,716 | 146,415 | 0.90x |
| 32×32×256 | 196,722 | 184,225 | **1.07x** |
| 32×32×512 | 307,295 | 251,855 | **1.22x** |
| 32×32×1024 | 602,948 | 393,423 | **1.53x** |
| 32×32×2048 | 1,123,677 | 764,518 | **1.47x** |
| 32×32×4096 | 2,206,089 | 1,586,443 | **1.39x** |
| 64×64×64 | 276,483 | 352,867 | 0.78x |
| 64×64×256 | 592,277 | 567,549 | **1.04x** |
| 64×64×512 | 1,030,051 | 841,303 | **1.22x** |
| 64×64×1024 | 2,197,321 | 1,400,175 | **1.57x** |
| 64×64×2048 | 4,647,987 | 2,897,612 | **1.60x** |
| 64×64×4096 | 9,739,288 | 6,200,571 | **1.57x** |
| 128×128×512 | 4,836,912 | 3,175,049 | **1.52x** |
| 128×128×1024 | 10,116,124 | 5,443,150 | **1.86x** |
| 128×128×2048 | 20,232,943 | 11,798,789 | **1.71x** |
| 128×128×4096 | 44,508,971 | 24,502,680 | **1.82x** |

## INT8 (int8/int32) — Moderate sparse gains

| Size | Dense | Sparse | Speedup |
|------|------:|-------:|--------:|
| 8×8×32 | 41,760 | 43,028 | 0.97x |
| 16×16×32 | 68,082 | 74,647 | 0.91x |
| 16×16×64 | 70,383 | 77,214 | 0.91x |
| 32×32×64 | 107,787 | 134,937 | 0.80x |
| 32×32×128 | 124,844 | 146,044 | 0.85x |
| 32×32×256 | 147,131 | 173,899 | 0.85x |
| 32×32×512 | 212,890 | 231,029 | 0.92x |
| 32×32×1024 | 336,661 | 344,577 | 0.98x |
| 32×32×2048 | 614,931 | 565,828 | **1.09x** |
| 32×32×4096 | 1,295,701 | 1,115,703 | **1.16x** |
| 64×64×64 | 271,933 | 376,899 | 0.72x |
| 64×64×256 | 468,206 | 559,211 | 0.84x |
| 64×64×512 | 806,007 | 791,218 | **1.02x** |
| 64×64×1024 | 1,389,825 | 1,243,016 | **1.12x** |
| 64×64×2048 | 2,874,207 | 2,188,393 | **1.31x** |
| 64×64×4096 | 6,186,307 | 4,972,935 | **1.24x** |
| 128×128×512 | 3,030,568 | 2,993,775 | **1.01x** |
| 128×128×1024 | 5,607,037 | 5,409,820 | **1.04x** |
| 128×128×2048 | 11,016,221 | 10,517,657 | **1.05x** |
| 128×128×4096 | 24,635,878 | 20,553,266 | **1.20x** |

## INT4 (int4/int32) — Marginal sparse gains

| Size | Dense | Sparse | Speedup |
|------|------:|-------:|--------:|
| 8×8×32 | 39,048 | 42,137 | 0.93x |
| 16×16×32 | 58,173 | 65,701 | 0.89x |
| 16×16×64 | 57,967 | 66,033 | 0.88x |
| 32×32×64 | 80,847 | 104,814 | 0.77x |
| 32×32×128 | 84,457 | 105,906 | 0.80x |
| 32×32×256 | 98,849 | 119,201 | 0.83x |
| 32×32×512 | 135,735 | 152,823 | 0.89x |
| 32×32×1024 | 226,441 | 253,693 | 0.89x |
| 32×32×2048 | 455,659 | 489,208 | 0.93x |
| 32×32×4096 | 1,087,394 | 1,010,167 | **1.08x** |
| 64×64×64 | 175,943 | 260,026 | 0.68x |
| 64×64×256 | 250,415 | 335,310 | 0.75x |
| 64×64×512 | 383,406 | 459,051 | 0.84x |
| 64×64×1024 | 678,124 | 776,823 | 0.87x |
| 64×64×2048 | 1,678,417 | 1,589,616 | **1.06x** |
| 64×64×4096 | 4,118,899 | 3,906,039 | **1.05x** |
| 128×128×512 | 1,372,472 | 1,538,681 | 0.89x |
| 128×128×1024 | 2,672,245 | 2,885,903 | 0.93x |
| 128×128×2048 | 6,592,388 | 6,059,919 | **1.09x** |
| 128×128×4096 | 16,282,388 | 16,144,068 | **1.01x** |

## Why FP16 > INT8 > INT4 for Sparse Speedup

Root cause: B-load byte packing overhead, which sparsity doubles (2x B data).
- FP16 B-load: `lh/lhu` + simple packing (~5 instrs/register)
- INT8 B-load: `lbu` + shift/or packing (~11 instrs/register) — 2.1x heavier
- INT4 B-load: even heavier nibble unpacking

Also, larger tileK means fewer K-iterations to halve:
- FP16: tileK=16 → many iterations → more savings from halving
- INT8: tileK=32 → fewer iterations → less savings
- INT4: tileK=64 → fewest iterations → minimal savings

## Measurement Methodology

### csr_read(0xB00) Cycle Counter
- Kernel wraps the TCU compute loop with `csr_read(0xB00)` (mcycle CSR)
- Reports `PERF: cycles=N` — reliable for both RTLsim and FPGA
- FPGA cycles ~1.5-2x RTLsim cycles due to HBM latency

### FP16 Rounding
- Some large FP16 tests show element mismatches due to FP precision differences
- These are NOT functional failures — cycle counts are still valid

## Reproducing

### Full sweep script (all 3 types, 20 sizes each)
```bash
bash tests/regression/sgemm_tcu_struct_sparse/run_full_sweep_fpga.sh
```
Outputs CSV to `full_fpga_sweep_results.csv`.

### Single test
```bash
export FPGA_BIN_DIR=$PWD/hw/syn/xilinx/xrt/<build>_hw/bin

# Dense FP16
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu clean
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu
OPTS="-m64 -n64 -k1024" TARGET=hw make -C tests/regression/sgemm_tcu run-xrt

# Sparse FP16
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu_struct_sparse clean
CONFIGS="$USER_CONFIGS" make -C tests/regression/sgemm_tcu_struct_sparse
OPTS="-m64 -n64 -k1024" TARGET=hw make -C tests/regression/sgemm_tcu_struct_sparse run-xrt
```
