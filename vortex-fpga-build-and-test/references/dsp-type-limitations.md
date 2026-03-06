# DSP FEDP Type Limitations

## Summary

`VX_tcu_fedp_dsp.sv` only supports FP16 (and BF16 with `ifdef`) data types for the fused element-wise dot product. Integer types (INT8, INT4, UINT8, UINT4) are NOT implemented and will produce NaN output on FPGA.

## Root Cause

In `VX_tcu_fedp_dsp.sv`, the `case(fmt_s)` statement (the runtime type selector) only handles FP16 and BF16:

```systemverilog
case (fmt_s)
    `VX_TCU_FMT_FP16: begin
        // FP16 multiply-accumulate using DSP48E2
        ...
    end
`ifdef TCU_BF16_ENABLE
    `VX_TCU_FMT_BF16: begin
        // BF16 multiply-accumulate
        ...
    end
`endif
    default: begin
        result = 'x;  // <-- INT8, INT4, etc. land here
    end
endcase
```

The `'x` propagates through the pipeline and ultimately appears as `0x7fc00000` (NaN in IEEE 754) in the output matrix.

## Symptoms

- All output elements are `0x7fc00000` (NaN)
- FPGA test reports `Found N / N errors!` with every element wrong
- RTLsim and SimX pass the same test (they use `VX_tcu_fedp_dpi.sv` which supports all types)
- Build succeeds, timing MET, demo PASSES (demo doesn't use TCU)

## This is NOT sparse-specific

Dense INT8 would also fail on FPGA with DSP FEDP. The issue is that the DSP MAC implementation only covers floating-point types.

## Diagnosis

1. Check `ITYPE` in your test configuration
2. Verify it's FP16 or BF16 (the only DSP-supported types)
3. If using INT8/INT4: either switch to FP16, or implement integer MAC in VX_tcu_fedp_dsp.sv

## Workaround

Use FP16 for FPGA testing. The `sgemm_tcu` and `sgemm_tcu_struct_sparse` tests default to FP16/FP32 in `common.h`, so no extra ITYPE/OTYPE flags are needed unless you changed the defaults:
```bash
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP" make -C tests/regression/sgemm_tcu clean
CONFIGS="-DNUM_THREADS=8 -DEXT_TCU_ENABLE -DTCU_TYPE_DSP" make -C tests/regression/sgemm_tcu
```

If you did override ITYPE to int8 or int4 in common.h, revert it back to fp16 before building for FPGA.

## Future Work

To support INT8/INT4 on FPGA, add integer MAC paths to `VX_tcu_fedp_dsp.sv` using DSP48E2 integer mode. The DSP48E2 primitive supports 27x18 integer multiplication natively.
