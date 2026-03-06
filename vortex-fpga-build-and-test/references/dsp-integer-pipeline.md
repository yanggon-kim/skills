# DSP FEDP Integer Pipeline

## Supported Types

`VX_tcu_fedp_dsp.sv` supports all TCU data types on FPGA:

| Type | Status | Implementation |
|------|--------|---------------|
| FP16 | Supported | DSP48E2 FP MAC (original) |
| BF16 | Supported (with ifdef) | DSP48E2 FP MAC (original) |
| INT8 | Supported | 3-stage LUT-based pipeline (v3) |
| UINT8 | Supported | 3-stage LUT-based pipeline (v3) |
| INT4 | Supported | 3-stage LUT-based pipeline (v3) |
| UINT4 | Supported | 3-stage LUT-based pipeline (v3) |

## Integer Pipeline Design (v3)

The integer path uses a 3-stage pipeline that matches the FP path's total latency:

**Stage 1a (1 cycle):** Compute individual element products in native width, then register.
- Elements 0..3: genvar loop handles INT8/UINT8/INT4/UINT4 (8x8->16bit or 4x4->8bit multiplies)
- Elements 4..7: separate genvar loop handles INT4/UINT4 only (avoids OOB bit access for INT8 byte positions)
- Products are sign/zero-extended to 32-bit via `case(fmt_s)` mux
- Native-width multiplies (8x8 or 4x4) synthesize as pure LUT logic, NOT DSP48E2

**Stage 1b (1 cycle):** Sum all 8 element products per word, then register.

**Stage 2 (TOTAL_LATENCY-2 cycles):** Cross-word accumulate + C, piped to match FP latency.

Total: 1 + 1 + (TOTAL_LATENCY-2) = TOTAL_LATENCY cycles. Same latency as FP path.

Output mux selects between integer and FP results: `d_val = is_int_out ? int_result : fp_result`

## FPGA Resource Cost

Integer path adds minimal overhead compared to FP16-only:

| Metric | FP16-only (build_sparse_tcu_1c) | FP16+INT (build_sparse_dsp_int_v3_1c) | Delta |
|--------|------|------|-------|
| LUTs | 192,673 (14.8%) | 210,801 (16.2%) | +18K (+1.4%) |
| FFs | 254,620 (9.8%) | 258,483 (9.9%) | +4K (+0.1%) |
| BRAM | 329 (16.3%) | 329 (16.3%) | 0 |
| DSPs | 180 (2.0%) | 180 (2.0%) | 0 |
| WNS | +0.003 ns | +0.003 ns | Same |

Zero extra DSPs because native-width multiplies (8x8, 4x4) are implemented in LUTs (~2 logic levels each).

## Why Native-Width Multiplies Matter

An earlier attempt (v2) used 32-bit sign-extended operands:
```systemverilog
// v2 (FAILED — WNS=-3.073ns, 756 DSPs):
word_prod = word_prod + $signed({{24{a[8j+7]}}, a[8j+:8]}) * $signed({{24{b[8j+7]}}, b[8j+:8]});
```

This created 32x32 multiplies that Vivado mapped to DSP48E2 cascades (756 DSPs, 19 logic levels, 6.040ns data path). The v3 fix uses native widths:

```systemverilog
// v3 (PASSED — WNS=+0.003ns, 180 DSPs):
wire signed [15:0] i8_prod = $signed(a[8*j +: 8]) * $signed(b[8*j +: 8]);  // 8x8 in LUTs
```

## Historical Note

Before the v3 integer pipeline was added, the `case(fmt_s)` in `VX_tcu_fedp_dsp.sv` had `default: result = 'x` for unsupported types. Integer inputs would produce NaN (0x7fc00000) on FPGA. If you encounter NaN output with integer types, verify your bitstream includes the v3 pipeline (check `VX_tcu_fedp_dsp.sv` for the `g_int_mul` genvar loops around lines 279-405).

## FPGA Test Results (v3 bitstream)

All tested on Alveo U55C at 300 MHz:

| Test | Data Type | Mode | Result |
|------|-----------|------|--------|
| sgemm_tcu_struct_sparse | FP16 | Sparse | PASSED |
| sgemm_tcu_struct_sparse | INT8 | Sparse | PASSED |
| sgemm_tcu | INT8 | Dense | PASSED |
| sgemm_tcu | FP16 | Dense | PASSED |
| demo | - | - | PASSED |
