# Kernel SASS forensics (Step 5.5 reference)

A methodology for fully deconstructing a single GPU kernel at the SASS level
and tying every observed dynamic counter back to a concrete piece of the
binary. This deepens Step 5 (high-level instruction analysis); it does not
replace it. Step 5 establishes *that* the kernel is bound by long-latency
loads (or whatever); Step 5.5 explains *which* loads, in *which* phase of the
kernel, with *which* downstream stall reason, taking *how many cycles* each.

The worked example for this methodology is
`01_suitesparse_spmv/analysis/kernel_sass_analysis.md` (519 lines, 13
sections) which applied it to cuSPARSE `csrmv_v3_kernel` (Blackwell sm_120).
Read it once before doing your own to see what the synthesis doc looks like.

---

## 1. When to use Step 5.5 (and when to skip)

Run Step 5.5 when:

- The dominant-time kernel will appear in a research report or paper.
- You want to *understand* the kernel — not just bound its performance — to
  motivate algorithmic changes, decoupled access-execute claims, custom
  kernels, or hardware proposals.
- You need stall and latency evidence at instruction granularity to back a
  specific root-cause claim that Step 5's dependency-chain analysis can't
  fully justify.
- The kernel is a vendor-library kernel (cuSPARSE / cuBLAS / cuDNN /
  CUTLASS) and you need to identify the algorithm — vendor docs rarely
  state it.

Skip Step 5.5 when:

- The workload is launch-bound (kernel runtime ≈ kernel-launch overhead).
  ncu's `Compute (SM) Throughput` < 5 % is a strong skip signal.
- The kernel is trivially memory-bound and DRAM saturation is the answer
  (≥95 % `dram__throughput.avg.pct_of_peak_sustained_elapsed`, the
  Mem-throughput pipe is the unambiguous bottleneck, no further
  instruction-level evidence is needed).
- Step 5's dependency-chain analysis already pinpoints the bottleneck
  unambiguously and the workload's report depth doesn't require more.

The phase costs ~1-2 hours of analyst time per kernel and produces a
substantial markdown artefact. Don't run it speculatively.

## 2. Methodology — dumping SASS

### 2.1 Find the kernel symbol

For vendor kernels (the common case), the mangled symbol comes from ncu's
output. The full kernel name from the per-kernel page of `--page details`
is what `cuobjdump` needs. Save it; don't paraphrase.

To browse all kernels in a vendor library and see which architectures are
compiled in:

```bash
cuobjdump --list-text /usr/local/cuda/lib64/libcusparse.so.<VERSION>
```

This prints one line per `(kernel, sm_arch)` pair like:

```
SASS text section <N> : x-_ZN8cusparse15csrmv_v3_kernelISt17integral_constantIbLb0EEiiffffvEE...sm_120.elf.bin
```

Vendor libraries ship kernels for many architectures (`sm_75`, `sm_80`,
`sm_86`, `sm_89`, `sm_90`, `sm_120`, …); pick the one matching your runtime
GPU.

### 2.2 Dump the SASS

```bash
cuobjdump --dump-sass -arch=sm_<XXX> --function <MANGLED_SYMBOL> \
    <library.so> > <kernel>_sm<XXX>.sass
```

Notes:

- The `-arch=sm_<XXX>` flag uses `=` not space (`-arch sm_120` errors).
- `cuobjdump` from the CUDA toolkit version that produced the binary; older
  toolkits don't recognise newer arches (e.g. `sm_120` needs CUDA 13+).
- For custom-compiled kernels, point at the `.cubin` produced by
  `nvcc --cubin` instead of the vendor `.so`.
- The output has **two physical lines per SASS instruction**: the
  disassembled mnemonic line (with PC, predicate, opcode, operands), plus
  a control-code/encoding hex line that begins with whitespace followed by
  `/*` and a hex pair. So `wc -l` ≈ 2 × instruction count.
- For hand-built (`nvcc`-compiled) binaries, `cuobjdump --list-text` may
  emit a benign `cuobjdump warning: '...': Function not found` line before
  the real listing — this typically means the first fatbin section is a
  PTX-only stub and the SASS lives in a later section. Ignore the warning;
  scan for the `sm_<arch>.elf.bin` line that matches your runtime arch.

### 2.3 Architecture-specific opcode catalogue

When inspecting a SASS dump for an unfamiliar arch:

- **Ada (sm_89) and earlier**: `LDG`, `STG`, `RED.E.ADD`, `FFMA`, `FMUL`,
  `FADD`, `IMAD`, `IADD3`, `ISETP`, `LOP3`, `LEA`, `BRA`, `SHFL.*`, `S2R`.
- **Hopper (sm_90)**: adds `WGMMA`, descriptor-based memory ops, async
  copy variants, Tensor Memory Accelerator (TMA) opcodes.
- **Blackwell (sm_120)**: adds `WARPSYNC.COLLECTIVE`, `ENDCOLLECTIVE`,
  `REDUX.<op>` (warp-collective reduction primitives), descriptor-based
  `LD.E` / `ST.E` global memory ops, `BSSY.RECONVERGENT` /
  `BSYNC.RECONVERGENT` for warp-divergence reconvergence stack tracking.
  May omit `FFMA` in favour of split `FMUL` + `FADD` (compiler choice).

If you see opcodes the inventory script doesn't recognise, look them up in
NVIDIA's developer-forum SASS threads or in CUTLASS's SASS commentary; do
not silently put them in the "Other" bucket.

## 3. Identifying the inner loop

The inner loop — the SASS PC range that executes most frequently per warp —
is the part of the kernel that dominates dynamic instruction counts. Per-pipe
utilisation, stall reasons, and latency are all weighted by how often each
instruction executes, so finding the inner loop is a prerequisite for §5
and §9.

### 3.1 Backward-BRA enumeration

Every loop body in SASS ends with a `BRA` whose target PC is *less* than
its source PC (the "backward branch"). Count them:

```python
import re
INST_RE = re.compile(r"^\s*/\*([0-9a-fA-F]+)\*/\s+(?:@!?P[0-9TF]\s+)?(BRA)\b(.*?)(?:;|$)")
backward = []
for line in open(sass_path):
    m = INST_RE.match(line)
    if not m: continue
    pc = int(m.group(1), 16)
    rest = m.group(3)
    target = re.search(r"0x([0-9a-fA-F]+)", rest)
    if target and int(target.group(1), 16) < pc:
        backward.append((pc, int(target.group(1), 16), pc - int(target.group(1), 16)))
```

Each tuple is `(source_pc, target_pc, span_in_bytes)`. Categorise by span:

| Span | Likely role |
|---|---|
| 32-128 bytes | small-body spin: bisection, CAS retry, warp-vote loop |
| 128-512 bytes | medium-body: row_ptr walk, partition-discovery, warp-reduction shuffle ladder |
| > 1 KB | full inner loop / outer iteration loop |
| > 10 KB | outer kernel-iteration loop with a long body (typical for SpMM-style kernels accumulating across N output columns) |

A real "for j in row" inner loop usually shows up as a single long-span
backward BRA. If there are no long-span backward BRAs but several
medium-span ones, the per-element work is **fully unrolled** (e.g.
merge-path SpMV unrolls its 256-nnz tile across 8 vectorised LDGs and 8
math triples; the only loops are the row_ptr walk and the bisection).

### 3.2 Cross-reference with ncu

If your ncu profile has `--set sass-source` (collects per-instruction
sample counts), the source page of the ncu report will tell you exactly
which PCs are hot. Ada / Blackwell support this. Without it, fall back on
the BRA enumeration plus algorithm matching (§7).

### 3.3 The inner-loop PC range

Once the inner loop is identified, record the `[PC_lo, PC_hi]` range. This
range parameterises the inner-loop instruction inventory in §5.

## 4. Total-kernel instruction inventory

Run `scripts/build_inst_inventory.py` on the SASS dump. The script
parses each mnemonic line, classifies the opcode into a pipe family, and
emits a CSV plus a markdown table:

```bash
python scripts/build_inst_inventory.py <kernel>.sass > <kernel>_total_inventory.md
python scripts/build_inst_inventory.py <kernel>.sass --csv > <kernel>_total_inventory.csv
```

Pipe families:

| Family | Examples |
|---|---|
| LSU (Load) | `LDG.*`, `LDS.*`, `LDC.*`, `LDCU.*`, `LD.E`, `LDL`, `LDSM` |
| LSU (Store) | `STG.*`, `STS.*`, `ST.E`, `STL`, `STSM` |
| LSU (Atomic) | `ATOM.*`, `ATOMS.*`, `RED.*`, `REDG.*` |
| FMA | `FFMA`, `FMUL`, `FADD`, `IMAD.*`, `IMUL`, `FSEL`, `HFMA2`, `FSETP` |
| ALU | `IADD*`, `ISETP.*`, `LOP3.*`, `SHF.*`, `MOV`, `LEA.*`, `SEL`, `PRMT`, `FLO`, `POPC`, `I2I`, `F2I`, `I2F`, `F2F`, `IMNMX`, `VIMNMX`, `BMSK`, `PLOP3.*` |
| Shuffle | `SHFL.*` |
| XU | `MUFU`, FP64 (`DMUL`, `DADD`, `DFMA`, `DSETP`) |
| Reduce | `REDUX.*` (Blackwell) |
| Uniform | U-prefixed datapath: `UMOV`, `ULEA`, `UISETP`, `ULOP3`, `USHF`, `UIADD3`, `UFLO`, `ULDC`, `ULDCU`, … |
| Branch | `BRA`, `BSSY.*`, `BSYNC.*`, `EXIT`, `NOP`, `BAR.SYNC.*`, `WARPSYNC.*`, `ENDCOLLECTIVE`, `S2R`, `S2UR`, `R2UR`, `B2R`, `CS2R`, `VOTE.*`, `MATCH.*`, `CALL`, `RET`, `JMX`, `JMP`, `BRX`, `QSPC.*` |

The total-kernel table reports per-category counts and per-opcode
counts within each category (sorted descending). Worth scanning for:

- **Top-3 LSU opcodes** — which memory spaces dominate.
- **FFMA absent on Blackwell** — compiler may have split FP32 mul-add into
  separate `FMUL` + `FADD`. Don't assume `FMA = FFMA`.
- **`HFMA2` present in non-FP16 code** — the `HFMA2 R, -RZ, RZ, 0, 0`
  idiom is a register-zeroing pattern, not real FP16 work.
- **Many `ISETP.*` instructions** — typical of merge-path / partition-style
  kernels that bisect index arrays.
- **Many `BSSY.RECONVERGENT` / `BSYNC.RECONVERGENT` pairs** — warp
  divergence is being explicitly tracked; expect predicated branches.

## 5. Inner-loop instruction inventory

Pass `--inner-loop-range 0xPC_lo-0xPC_hi` to filter:

```bash
python scripts/build_inst_inventory.py <kernel>.sass \
    --inner-loop-range 0x0240-0x1300 > <kernel>_inner_inventory.md
```

The inner-loop inventory is what determines the dynamic pipe utilisation
shape, because the inner loop is what executes most often.

For a *unrolled* inner block (no backward BRA wraps it), the PC range is
the whole unrolled sequence. For a *looped* inner block (backward BRA
wraps it), the PC range is `[BRA_target, BRA_source]`.

The inner-loop counts should be related to per-iteration cost: e.g. for
merge-path SpMV the unrolled per-nonzero block has 5 LSU + 3 FMA + 0 ALU
ops per nonzero, so the inner inventory counts × 8 (× 8 nnz/lane) match
the per-warp total. Cross-check this — if the inner counts are too small
to explain the dynamic LSU%, you've identified the wrong PC range.

## 6. Decompilation to C-like pseudocode

The single most-cited section of the synthesis doc — readers want to see
the kernel they thought they understood, written in C with annotated
phases. Build it bottom-up:

1. **Identify register live ranges.** The SASS will have setup code that
   reads launch parameters from `c[0x0][...]` (constant memory) — these
   are the kernel arguments and the launch-shape registers
   (`SR_CTAID.X`, `SR_TID.X`, `SR_LANEID`).
2. **Walk the SASS in PC order**, narrating what each block does. Phases
   typically partition cleanly:
   - **Setup** — read launch parameters, compute per-block / per-warp /
     per-lane indices, set up descriptor pointers.
   - **Pre-loop bookkeeping** — load partition tuple, compute starting
     indices, possibly read row_ptr / index arrays.
   - **Inner loop body** — the hot per-element work, possibly unrolled.
   - **Reduction** — `SHFL.DOWN` butterfly across lanes, possibly
     followed by warp-vote / `REDUX` collective.
   - **Output write** — `STG.E` for interior, `RED.E.ADD` /
     `ATOM.E.ADD` for boundary, possibly preceded by a CAS-spin
     boundary-publication step.
3. **Annotate PC ranges per phase** in the C-like pseudocode comments.
4. **Cross-reference with the algorithm** (§7). If you can name the
   algorithm (merge-path, row-split, etc.), the phase boundaries tend to
   match the published reference implementation; cite it.

The pseudocode does not need to be compilable C — it needs to be readable.
Use comments like `/* unrolled */`, `/* warp-collective */`,
`/* atomic on contention */` to flag what's happening at the SASS level.

## 7. Algorithm-identification cookbook

Library kernels almost always implement a known algorithm. Identify it
from structural fingerprints:

### Sparse matrix kernels (cuSPARSE)

- **`csrmv_v3` (FP32 SpMV)** = **merge-path SpMV** (Merrill–Garland 2016).
  Fingerprints:
  - 256 nonzeros per warp tile (verified by grid sizing: nnz / 256 ≈ warp count).
  - Companion `csr_partition_kernel` runs first to publish per-warp
    `(row_start, nnz_start)` tuples.
  - Shared-memory staging of `row_ptr` slices (50+ `STS` instructions).
  - Warp-level `SHFL.DOWN` reduction.
  - Mix of `STG` (interior rows) + `RED.E.ADD` (boundary rows) writes.
- **`csrmm_alg2` (FP32 SpMM)** = **row-split / CSR-Stream**. Fingerprints:
  - Long-span backward BRA (>10 KB) — per-row inner-nonzero loop.
  - Register-resident `C[m, 0..N]` accumulator across the loop.
  - Final row write via `RED.E.ADD` per output column (N writes per row).
  - No companion partition kernel.

### Dense GEMM (cuBLAS / CUTLASS)

- **Tile-based GEMM (`sgemm`, `cublasGemm*`)**. Fingerprints:
  - Outer loop over K-tile (long-span backward BRA).
  - Per-K-tile: shared-memory load of A-tile + B-tile (`LDS.128` /
    `LDSM`-via-async-copy on Hopper+).
  - Inner: `FFMA` × M_tile × N_tile (often hundreds of FFMAs unrolled).
  - Final epilogue: predicated `STG.128` for C-tile.
- **Tensor-core GEMM (`hgemm`, `wgmma`-class)**. Fingerprints:
  - `HMMA.16816.F16` / `HMMA.16816.F32` (Ampere) or `WGMMA.M64.NK.F16`
    (Hopper) tensor-core opcodes.
  - Per-tile CTA cooperative load via `BAR.SYNC` or `WARPSYNC`.
  - On Hopper+: TMA descriptor setup before the loop, async load
    barriers between K-tiles.

### Convolution (cuDNN)

- **Implicit-GEMM convolution**. Fingerprints: same as tile-based GEMM,
  plus index-arithmetic in the K-loop to compute input-tensor offsets
  from output-tile coordinates.
- **Direct convolution / FFT-based / Winograd**. Fingerprints differ
  substantially; consult cuDNN's published kernel taxonomy.

### Attention (FlashAttention-derived)

- **FlashAttention 2 / 3**. Fingerprints:
  - Tile loops over Q-block × K-block (two-deep nested loops).
  - Per-tile: GEMM(Q, K^T) → online softmax → GEMM(P, V).
  - Online softmax: `MUFU.EX2`, `MUFU.RCP`, sequential row-max /
    row-sum updates per tile.
  - Output written incrementally; `__shfl_xor` butterfly for row-reduce.

### Ray tracing / BVH traversal

- **Stack-based BVH ray traversal (Aila-Laine 2009 "while-while" / "while-if",
  software RT).** Fingerprints:
  - Two backward BRAs: an outer while-stack loop (long-span, often
    >2 KB) and an inner per-leaf-triangle loop (~1-2 KB span).
  - Three near-identical AABB slab-test blocks each combining `MUFU.RCP`
    + `FMUL` / `FADD` / `FSEL` / `FMNMX` / `FSETP`.
  - Möller-Trumbore triangle-intersection signature inside the inner
    loop: cross-product `FFMA` ladder, one `MUFU.RCP` for `1/det`, then
    predicated `u<0 / u>1 / v<0 / u+v>1` early-outs.
  - `STL` / `LDL` on local-memory traversal stack (push when entering
    internal node, pop on miss).
  - Output via plain `STG.E` to per-ray hit buffer; **no** `RED` / `ATOM`.
  - L2 latency-bound rather than DRAM-saturated: high `long_scoreboard`
    with low DRAM throughput and high L2 hit rate (BVH nodes near the
    root are L2-resident; only deep nodes hit DRAM).
- **Persistent-warp BVH traversal.** Fingerprints: same inner-loop shape
  as Aila-Laine but the outer loop wraps a global ray-pool work-queue
  index (`ATOM.E.ADD` on a counter), and the kernel exits only when the
  pool is empty. Use this when ncu shows `not_selected` ≪ `long_scoreboard`
  at high occupancy — the kernel deliberately keeps warps alive.
- **Hardware-RT kernels (OptiX 9, RTX cores)** dispatch to a closest-hit
  / any-hit / miss program; the SASS for the user-callable program is
  typically very small (no traversal loop — the RT cores do the
  traversal). The bottleneck analysis is different — see the OptiX
  programming guide and the per-program profiling counters
  (`rt__cycles_*`).

### Stencil / structured-grid kernels

- **N-point stencil (Jacobi / red-black GS / Lattice-Boltzmann).** Fingerprints:
  - Single backward BRA over the time-step / sweep loop (long-span).
  - Inner body: 2×N or 3×N `LDG` from the input grid + N `FFMA` for the
    stencil weights + 1 `STG` to the output grid.
  - Often shared-memory tiling: 2-D or 3-D halo loaded with `BAR.SYNC`
    between the load phase and the compute phase.
  - DRAM-bound at large grid sizes; compute-bound at small grid sizes.

### Custom kernels

For kernels you wrote yourself, the algorithm is whatever you wrote — but
still write the pseudocode and cite your source file. The exercise of
writing a SASS-level pseudocode often reveals compiler choices (loop
peeling, prefetching, register spilling) that the source code doesn't.

## 8. Pipe → instruction mapping

This table is community-derived (NVIDIA forum threads, the official
`nsight-compute` documentation lists pipes but not the per-opcode mapping).

| ncu counter | SASS opcodes |
|---|---|
| `sm__inst_executed_pipe_lsu` | `LDG`, `LD`, `LDS`, `LDC`, `LDCU`, `STG`, `ST`, `STS`, `RED`, `REDG`, `ATOM`, `ATOMS`, `LDGSTS`, `TLDS` |
| `sm__inst_executed_pipe_fma` | `FFMA`, `FMUL`, `FADD`, `IMAD`, `IMUL`, `IMAD.WIDE`, `FSEL`, `HFMA2`, `FSETP`, `FCMP` |
| `sm__inst_executed_pipe_alu` | `IADD3`, `IADD`, `ISETP`, `LOP3`, `SHF`, `MOV`, `SEL`, `LEA`, `PRMT`, `FLO`, `POPC`, `I2I`, `F2I`, `I2F`, `F2F`, `IMNMX`, `BMSK`, `IDP`, `PLOP3`, `VIMNMX` |
| `sm__inst_executed_pipe_xu`  | `MUFU`, FP64 (`DMUL` / `DADD` / `DFMA`), Shuffle (`SHFL.*`) — sometimes split off as `pipe_xu_shfl` |
| `sm__inst_executed_pipe_adu` | address-generation sub-pipe — no direct SASS opcode; counts addressing work the LSU offloads |
| `sm__inst_executed_pipe_cbu` | control-block sub-pipe: `BRA`, `BSSY`, `BSYNC`, `EXIT`, `WARPSYNC`, `BAR.SYNC.*`, `S2R`, `S2UR` |
| `sm__inst_executed_pipe_fp16`| `HFMA2`, `HMUL2`, `HADD2` — overlaps with FMA-pipe accounting on some architectures |

`sm__inst_executed_pipe_<X>.avg.pct_of_peak_sustained_active` is the
**per-active-cycle issue rate** of pipe X against its own peak. The
denominator differs across pipes (LSU has 1 issue/cycle/scheduler; FMA can
dual-issue on some architectures; ALU shares an issue slot with FMA on
Ampere+ in some configurations). Therefore:

- The pipe percentages are **not summable** to 100 %.
- Comparing percentages across pipes is not the same as comparing static
  instruction counts.
- 100 % LSU is a different denominator than 100 % FMA.

## 9. LSU split apportionment (Load / Store / Atomic)

The aggregate `pipe_lsu_active_pct` covers loads, stores, atomics, and
shared-memory ops together. Splitting it requires the per-op request
counters from ncu's raw page:

```
l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum
l1tex__t_requests_pipe_lsu_mem_global_op_st.sum
l1tex__t_requests_pipe_lsu_mem_global_op_red.sum
l1tex__t_requests_pipe_lsu_mem_global_op_atom.sum
l1tex__t_requests_pipe_lsu_mem_local_op_ld.sum
l1tex__t_requests_pipe_lsu_mem_local_op_st.sum
l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum
l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum
l1tex__data_pipe_lsu_wavefronts_mem_shared_op_atom.sum
```

Apportion by request count:

```
load_pct  = pipe_lsu_active_pct × (op_ld_global + op_ld_local + op_ld_shared) / total_requests
write_pct = pipe_lsu_active_pct × (op_st_global + op_red + op_atom + op_st_local
                                    + op_st_shared + op_atom_shared) / total_requests
```

**Critical**: writes count `op_st + op_red + op_atom`, not just `op_st`.
cuSPARSE-style kernels write boundary rows via `RED.E.ADD` (atomic
add-to-global), not plain `STG`. Counting only `op_st` underreports writes
by 50–95 % on dense-row matrices and falsely suggests the kernel never
writes.

The updated `scripts/parse_ncu_results.py` emits this in the JSON's
`pipe_lsu_split` block:

```json
{
  "load_pct": 22.52,
  "write_pct": 6.54,
  "load_to_write_ratio": 3.44,
  "load_global_pct": 22.52,
  "load_shared_pct": 0.00,
  "write_global_pct": 6.54,
  "write_shared_pct": 0.00,
  "op_request_counts": {
    "global_ld": 16697432, "global_st": 15667,
    "global_red": 15656, "global_atom": 0, ...
  }
}
```

The `load_to_write_ratio` is the headline number. Compare against the
static load:store ratio from §4 — they will not match exactly (predication,
trip counts) but should agree directionally.

## 10. Static-vs-dynamic cross-check

`scripts/crosscheck_sass.py` consumes the inventory CSV (§4) and the
parsed-ncu JSON (with `pipe_lsu_split`, §9) and emits a markdown table
plus a reconciliation paragraph.

Static instruction counts predict the **direction** of pipe utilisation
(LSU-heavy / FMA-heavy / ALU-heavy) but **cannot reproduce the magnitude**.
Four sources of the gap:

1. **Predication.** Many ALU and branch ops are predicated on
   boundary-row sentinels or partition-loop exit conditions. Static count
   counts them once; dynamic execution fires them only on the small
   fraction of warps that hit the boundary case.
2. **Looped vs unrolled execution counts.** The unrolled per-element block
   executes once per warp tile; the row_ptr walk / bisection / spin loops
   execute many times. Static count is trip-count-blind. Per-warp dynamic
   instruction counts therefore over-weight the unrolled block relative
   to its static line count.
3. **Per-pipe peak issue rates differ.** `pct_of_peak_sustained_active` is
   normalised by the *maximum issuable per-active-cycle for that pipe*,
   which differs across pipes. So 100 % LSU is a different denominator
   than 100 % FMA. Dividing one dynamic % by another is not the same as
   dividing one static count by another.
4. **Per-instruction issue cost.** Some opcodes consume multiple pipe
   slots (vector LDGs count as one *instruction* but burn multiple LSU
   cycles); some consume zero (NOPs, uniform-datapath ops). The static
   count and the dynamic counter measure different things.

A worked example: cuSPARSE `csrmv_v3` static LSU/FMA = 1.50× while
dynamic LSU/FMA = 8.7-11.8× across 6 SuiteSparse matrices. The static
ratio gets the direction right (LSU-heavy); the dynamic ratio amplifies
because of (3) and (4).

Bottom line of §10: static counts give the **direction**; dynamic counters
give the magnitude.

## 11. Stall-reason → instruction-class mapping

ncu's warp-stall reasons attribute every warp-cycle-with-no-issue to a
cause. The mapping below is the standard interpretation:

| Stall reason | Caused by |
|---|---|
| `long_scoreboard` | Long-latency dependency, almost always a global-memory load (`LDG` / `LD.E`) or texture fetch. The warp issued the load (LSU pipe ticked), the dependent instruction can't fire until the load returns. |
| `short_scoreboard` | Short-latency dependency, typically a shared-memory load (`LDS`) or constant-cache miss. Faster than long_scoreboard but still a stall. |
| `mio_throttle` | Memory I/O pipe overflow — too many in-flight loads or stores. The LSU issue queue is full and can't accept a new instruction. Often appears with high LSU% on small matrices. |
| `lg_throttle` | Load/Store address-calculation conflict, including shared-memory bank conflicts. Distinct from data-return latency (which is `short_scoreboard`). |
| `barrier` | Waiting at a CTA-wide synchronisation: `BAR.SYNC`, `WARPSYNC.COLLECTIVE`, `__syncthreads()`. High barrier stall = load-imbalance or insufficient warps to hide the barrier. |
| `not_selected` | Scheduler had ≥2 ready warps for one issue slot; the warp that didn't get picked is "stalled" by definition. **High `not_selected` is a *good* sign** — it means the SM has plenty of warp-level parallelism. |
| `wait` | Fixed-latency operation in flight: transcendental (`MUFU.SQRT`, `MUFU.RCP`), integer divide, FP64 op on a non-FP64 SM. Distinct from memory wait. |
| `dispatch_stall` | Two warps need the same issue slot in the same cycle — usually a sign of pipe imbalance. |
| `drain` | Pipeline drain after a barrier or branch resolve — usually small. |
| `selected` | The warp *did* get picked. (Not really a stall; ncu reports it for accounting.) |
| `tex_throttle` | Texture pipe full — relevant only for kernels using `TLD4`. |
| `sleeping` | Explicit `NANOSLEEP` — almost never seen in compute kernels. |

Headline interpretation: `long_scoreboard` dominance ≥ 60 % is the
signature of a **memory-latency-bound** kernel — the SM has issued the
LSU instruction but the dependent FFMA can't fire until the load returns.
This is distinct from **memory-bandwidth-bound** (DRAM throughput at
≥90 % of peak), and the two often coexist on irregular workloads.

## 12. Per-instruction latency budget (inner-loop)

Per-instruction cycle costs (Blackwell sm_120; Ada is similar for most;
Hopper has TMA-specific variants):

| Instruction | Latency (cycles) | Notes |
|---|---:|---|
| `LDG` / `LD.E` (DRAM hit) | ~400-500 | dominant when working set > L2 |
| `LDG` / `LD.E` (L2 hit)   | ~150-200 | when working set fits in L2 (48-72 MB on consumer Blackwell) |
| `LDG` / `LD.E` (L1 hit)   | ~30-40   | rare for streaming kernels |
| `LDS` (shared)            | ~30      | bank-conflict-free; +N cycles per N-way conflict |
| `LDC` / `LDCU` (constant) | ~1-4     | broadcast-cache-served |
| `STG` / `ST.E`            | post-issue / fire-and-forget | warp doesn't stall on store completion |
| `RED.E.ADD` / `ATOM.E.*`  | atomic-contended | latency depends on contention level |
| `FFMA` / `FMUL` / `FADD`  | ~4       | can dual-issue on some architectures |
| `IMAD` / `IMAD.WIDE`      | ~4-6     | FP-pipe; integer-multiply-add |
| `IADD3` / `LOP3` / `SHF`  | ~2       | ALU pipe |
| `ISETP.*`                 | ~2       | ALU pipe; predicate-set |
| `SHFL.*`                  | ~5       | XU pipe |
| `BAR.SYNC`                | ~10-20   | + per-warp wait time if not all warps arrived |
| `BRA` (predicated, non-divergent) | ~2-4 | scheduler-folded |
| `BRA` (divergent)         | reconvergence-stack-managed | predication on most paths avoids divergence cost |
| `MUFU.RCP` / `MUFU.SQRT`  | ~16      | XU pipe |

Use these to compute the **per-iteration dependent-chain latency**:

1. List the inner-loop body in execution order.
2. Identify the longest dependency chain — the sequence of instructions
   where each waits for the previous (e.g. `LDG col_idx` → `IMAD addr`
   → `LDG x[col]` → `FFMA y += A * x`).
3. Sum the latencies along the chain. This is the per-iteration latency
   *if a single warp ran the loop alone with no warp-level parallelism*.
4. Divide ncu's `gpc__cycles_active.avg.per_warp` (or the inner-loop's
   active cycle count) by the inner-loop iteration count → measured
   per-iteration cycles.
5. The **gap** between (3) and (4) is what warp-level parallelism + ILP
   are hiding. The smaller the gap, the closer you are to the
   single-warp serial limit; the larger the gap, the more the SM is
   issuing other warps in parallel.

For dense-row SpMV (cant): the per-nonzero dependent chain is roughly
LDG(values) ⊻ LDG(col_idx) → IMAD(addr) → LDG(x[col]) → FMUL → FADD ≈
~410 cycles per nonzero (single-warp). Measured per-nonzero is ~1.6
cycles after warp interleaving — i.e. the SM is overlapping ~250 warps
worth of dependent chains.

**Branched / conditional chains.** Iterative-traversal kernels (BVH
traversal, graph BFS, ray-marching) have inner loops where the dependent
chain depends on a runtime condition: e.g. BVH's per-node body executes
the AABB slab test always, but only enters the leaf-intersection chain
when the AABB hit-test passes. Compute the **probability-weighted chain
latency** for these:

```
expected_chain = P(branch_taken) × chain_taken + (1 - P) × chain_not_taken
```

Estimate `P(branch_taken)` from the inner-loop control-flow counters
(ncu's `smsp__warps_eligible.sum` / `smsp__warps_active.sum` per branch)
or from the algorithm's expected hit rate. The headline number for
comparison against `gpc__cycles_active.avg.per_warp` is the
expected-chain latency, not the worst-case. This is a quantitative answer to "why doesn't
adding more warps help?": at 40 warps/SM × 84 SMs × 4 schedulers ≈ 13,000
in-flight warp-instructions, the SM is already overlapping more than
enough; the bottleneck is per-warp memory-level parallelism, not warp count.

## 13. Worked example

`/home/yanggon/02_SpMV_SpMM/01_suitesparse_spmv/analysis/kernel_sass_analysis.md`
(519 lines, 13 sections). Applied this methodology to cuSPARSE
`csrmv_v3_kernel` and `csrmm_alg2_kernel` on Blackwell sm_120. Headline
findings:

- csrmv_v3 = merge-path SpMV (Merrill-Garland 2016); 12 backward BRAs, all
  in row_ptr walk / bisection / spin paths — no backward BRA wraps the
  per-nonzero processing block.
- Total inventory: LSU 206 / FMA 137 / ALU 334 / Branch 159 / Shuffle 25.
  LSU split: Load 129 / Store 68 / Atomic 9 (static load:store = 1.9:1).
- Inner-loop per-nonzero: 4 loads + 1 store + 3 FMA + 0 ALU per nonzero.
  Static load:store = 4:1; dynamic LD:WR = 3.4-3.5:1 on dense-row
  matrices, 1.05:1 on webbase-1M (3 nnz/row average).
- Static LSU/FMA = 1.50; dynamic LSU/FMA = 8.7-11.8× across 6 matrices —
  the gap is per-pipe peak rates and trip-count weighting.
- `long_scoreboard` 30-71 % across matrices; DRAM 87-96 % saturated;
  classic memory-latency-bound + memory-bandwidth-bound coexistence.

Diff your own analysis against this artefact — the structure should match,
the numbers will be kernel-specific.

## References

- Merrill, D. & Garland, M. (2016). *Merge-Based Parallel Sparse
  Matrix-Vector Multiplication.* PPoPP'16.
- NVIDIA Nsight Compute documentation, *Pipe Utilization* and *Memory
  Workload Analysis* sections.
- NVIDIA developer-forum SASS opcode threads (Greg, NVIDIA staff, on
  pipeline issue rates; community threads on Blackwell-specific opcodes).
- CUTLASS source code and commentary (for tile-based GEMM SASS patterns).
- Worked example: `01_suitesparse_spmv/analysis/kernel_sass_analysis.md`.
