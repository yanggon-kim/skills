# Instruction-Level Analysis

Systematic methodology for extracting compiled instructions (SASS/PTX), mapping them to hardware behavior, and connecting instruction-level observations to measured performance bottlenecks.

**When to use**: After profiling identifies bottleneck kernels (Step 4), before root cause analysis (Step 6). This step provides the concrete instruction-level evidence that root cause analysis builds causal chains from.

---

## 1. Extraction Tools & Commands

### cuobjdump — Primary extraction tool

```bash
# Extract SASS (actual machine instructions) from a binary
cuobjdump -sass ./executable > kernel.sass

# Extract PTX (virtual ISA) from a binary
cuobjdump -ptx ./executable > kernel.ptx

# Extract resource usage (registers, shared mem, stack)
cuobjdump -res-usage ./executable

# List all ELF sections (find kernel symbols)
cuobjdump -lelf ./executable

# List all function symbols (useful for library .so files)
cuobjdump -symbols ./executable
```

### nvdisasm — Advanced disassembly

```bash
# Extract a .cubin first, then disassemble with control flow
cuobjdump -xelf all ./executable
nvdisasm -g -sf kernel.sm_89.cubin > kernel_cfg.sass

# Options:
#   -g            Show control flow graph
#   -sf           Show function names
#   -bbnum        Number basic blocks
#   -ndf          No data flow analysis (faster)
#   -plr          Print live registers at each instruction
```

### c++filt — Demangle kernel names

```bash
# Demangle a single symbol
echo "_ZN7cutlass..." | c++filt

# Demangle all symbols in cuobjdump output
cuobjdump -symbols ./executable | c++filt

# Demangle kernel names from ncu CSV
awk -F, '{print $1}' ncu_output.csv | c++filt
```

### Extracting from library .so files (cuSPARSE, cuBLAS)

```bash
# Find the library
find /usr/local/cuda*/lib64 -name "libcusparse*.so" | head -1

# List kernels in the library
cuobjdump -symbols /usr/local/cuda-12.0/lib64/libcusparse.so | c++filt | grep -i "spmv\|csrmv"

# Extract SASS for a specific kernel
cuobjdump -sass -fun "kernel_name" /usr/local/cuda-12.0/lib64/libcusparse.so
```

---

## 2. Kernel Identification

### Step 2.1: Find the kernel symbol

Start from ncu/nsys output — get the mangled kernel name, then demangle:

```bash
# From ncu CSV, column "Kernel Name" gives the mangled name
# Demangle it:
echo "_Z18csrmv_v3_kernel..." | c++filt
# Output: csrmv_v3_kernel<float, int, ...>(...)
```

### Step 2.2: Resource usage table

Extract and tabulate per-kernel resource usage:

```bash
cuobjdump -res-usage ./executable 2>&1 | grep -A5 "kernel_name"
```

Format as:

| Kernel | Registers/Thread | Shared Mem (bytes) | Stack Frame | Spills (load/store) |
|--------|----------------:|-------------------:|------------:|--------------------:|
| kernel_name | 40 | 0 | 0 | 0/0 |

### Step 2.3: Launch configuration

Combine with ncu data:

| Kernel | Grid Size | Block Size | Regs/Thread | Theor. Occupancy | Achieved Occupancy |
|--------|----------:|-----------:|------------:|-----------------:|-------------------:|
| kernel_name | 485 | 128 | 40 | 100% | 94.3% |

---

## 3. Source-to-SASS Mapping

### Instruction pattern dictionary

Map SASS mnemonics to high-level operations:

| SASS Instruction | Category | High-Level Meaning | Typical Source |
|-----------------|----------|-------------------|---------------|
| `LDG.E` / `LDG.E.SYS` | Global Load | Array read from DRAM/L2 | `a[i]`, `x[col[j]]` |
| `STG.E` | Global Store | Array write to DRAM | `y[i] = ...` |
| `LDS` / `STS` | Shared Mem | Shared memory access | `__shared__` arrays |
| `IMAD` / `IMAD.WIDE` | Int Multiply-Add | Address computation, index calc | `base + idx * stride` |
| `LEA` / `LEA.HI` | Address Calc | Load effective address | Pointer arithmetic |
| `IADD3` | Int Add | Integer addition (3-input) | `i + offset` |
| `ISETP` | Int Compare | Integer set predicate | Loop bounds, `if (i < N)` |
| `FMUL` / `FADD` / `FFMA` | FP32 Arith | Single-precision compute | `a * b + c` |
| `DFMA` / `DMUL` / `DADD` | FP64 Arith | Double-precision compute | `a * b + c` (double) |
| `HFMA2` / `HMUL2` | FP16 Arith | Half-precision (packed) | Tensor core prep |
| `MUFU` | Special Func | Transcendental (sin, exp, rsqrt) | `expf()`, `rsqrtf()` |
| `SHFL.IDX` / `SHFL.BFLY` | Warp Shuffle | Cross-lane data exchange | `__shfl_sync()` |
| `S2R` | Special Reg | Read thread/block ID | `threadIdx.x`, `blockIdx.x` |
| `BAR.SYNC` | Barrier | Block-level sync | `__syncthreads()` |
| `BRA` / `BRX` | Branch | Control flow | `if/else`, loop back-edge |
| `EXIT` | Exit | Kernel return | End of kernel |
| `@P` prefix | Predication | Conditional execution | Branch-free `if` |
| `NOP` | No-op | Pipeline bubble / scheduling | Compiler-inserted |
| `DEPBAR` | Dep Barrier | Wait for memory dependency | Compiler-managed |

### Annotation format

When annotating SASS, use this format:

```
// === Phase: [Phase Name] ===
/*0090*/  S2R R0, SR_TID.X ;                    // tid = threadIdx.x
/*00a0*/  S2R R3, SR_CTAID.X ;                  // bid = blockIdx.x
/*00b0*/  IMAD R0, R3, 0x80, R0 ;               // global_id = bid * 128 + tid
/*00c0*/  ISETP.GE.AND P0, PT, R0, R8, PT ;     // if (global_id >= N) exit
/*00d0*/  @P0 EXIT ;

// === Phase: Load row pointers ===
/*00e0*/  LDG.E R2, [R4+0x0] ;                  // row_start = row_ptr[row]
/*00f0*/  LDG.E R5, [R4+0x4] ;                  // row_end = row_ptr[row+1]
```

---

## 4. Kernel Phase Breakdown

### Identifying phases by SASS address ranges

GPU kernels typically have these phases:

1. **Setup** — Thread/block ID computation (`S2R`, `IMAD`), bounds checking (`ISETP`, `@P EXIT`)
2. **Initialization** — Load constants, zero accumulators (`MOV`, `LDG` for constants)
3. **Main loop** — The hot loop with loads, compute, and loop control (`LDG`, `FFMA`, `BRA`)
4. **Reduction** — Warp/block-level reduction (`SHFL`, `FADD`, `BAR.SYNC`)
5. **Epilogue** — Store results (`STG`), exit (`EXIT`)

### Identifying the hot loop

The hot loop is where the kernel spends most time. Identify it by:
- Back-edge `BRA` instruction that jumps to an earlier address
- Contains `LDG` (memory loads) and arithmetic (`FFMA`, `IMAD`)
- The address range between the loop entry and the `BRA` back-edge

```
// Hot loop: addresses 0x0150 - 0x0250
/*0150*/  LDG.E R6, [R10] ;           // Load col_indices[j]    <-- Loop start
/*0160*/  ...
/*0240*/  IADD3 R9, R9, 0x1, RZ ;     // j++
/*0250*/  ISETP.LT.AND P1, PT, R9, R5, PT ;  // j < row_end?
/*0260*/  @P1 BRA 0x150 ;             // Loop back             <-- Back-edge
```

### Multiple code paths

Optimized kernels often have:
- **Vectorized path** — Processes 2-4 elements per iteration (uses `LDG.E.128`, wider loads)
- **Scalar path** — Handles remainder elements (single `LDG.E`)
- **Empty-row path** — Skips rows with no nonzeros

Look for divergent branches early in the kernel that select between these paths.

---

## 5. Dependency Chain Analysis

### Register def-use tracing

Trace the critical path through register dependencies in the hot loop:

```
Instruction          Dest    Sources     Dep Chain
-----------          ----    -------     ---------
LDG.E R6, [R10]     R6      R10         Start: col_index load
IMAD.WIDE R12, R6   R12     R6, ...     Waits for R6 (LDG latency: ~400 cycles)
LDG.E R14, [R12]    R14     R12         Start: value load (DEPENDENT on col_index)
FFMA R16, R14, ...  R16     R14, ...    Waits for R14 (another ~400 cycles)
```

### Critical path identification

The critical path is the longest chain of dependent instructions through the loop body. For memory-bound kernels, this is typically:

```
Total critical path = sum of all dependent memory latencies

For SpMV CSR:
  LDG col[j]  → IMAD address → LDG x[col[j]] → FFMA accumulate
  ~400 cycles  + ~4 cycles   + ~400 cycles   + ~4 cycles
  = ~808 cycles per iteration (dominated by two serial DRAM round-trips)

Compare to independent loads:
  LDG col[j] and LDG x[j] issued simultaneously
  = ~400 cycles per iteration (one DRAM round-trip, loads overlapped)
```

### ASCII pipeline diagram

Show how instructions overlap (or fail to overlap) across cycles:

```
Cycle:  0    100   200   300   400   500   600   700   800
        |-----|-----|-----|-----|-----|-----|-----|-----|
Warp 0: [LDG col[j].............]
                                 [IMAD]
                                  [LDG x[col[j]]............]
                                                            [FFMA]
                                                             → 808 cycles/iter

If loads were independent:
Warp 0: [LDG col[j].............]
        [LDG x[j]................]  ← overlapped!
                                 [IMAD + FFMA]
                                  → 404 cycles/iter (2x faster)
```

### MLP impact via Little's Law

```
Memory-Level Parallelism (MLP) = independent loads in flight simultaneously

Independent loads:  MLP = 2 (col and x loaded together)
Dependent loads:    MLP = 1 (x must wait for col)

Effective BW = MLP * single_stream_BW
             = MLP * (cache_line_size / DRAM_latency)

For dependent SpMV: BW halved because MLP drops from 2 to 1
```

---

## 6. Instruction-to-Stall Mapping

### Which SASS instructions cause which NCU stall categories

| NCU Stall Category | Primary SASS Cause | Mechanism |
|--------------------|--------------------|-----------|
| **Long Scoreboard** | `LDG.E` (global load) | Warp stalls waiting for DRAM/L2 response (~400 cycles) |
| **Short Scoreboard** | `SHFL`, `MUFU`, shared mem | Warp stalls waiting for short-latency unit (~20 cycles) |
| **Wait** | `DEPBAR`, `LEA` after `LDG` | Warp stalls on explicit dependency barrier |
| **Not Selected** | (any) | Warp is ready but scheduler picked another warp |
| **Barrier** | `BAR.SYNC` | Warp stalls waiting for other warps at `__syncthreads()` |
| **Math Pipe Throttle** | `FFMA`, `DFMA`, `HMMA` | Compute pipe is full, back-pressure |
| **LG Throttle** | `LDG` / `STG` burst | Load/store unit queue is full |
| **Tex Throttle** | `TEX` / `TLD` | Texture unit queue is full |
| **Misc** | `VOTE`, `PRMT`, misc | Other pipeline stalls |

### Mapping table format

For each bottleneck kernel, create this mapping:

| SASS (Hot Loop) | Stall Contributed | Evidence |
|----------------|-------------------|----------|
| `LDG.E R6, [R10]` (col_index load) | Long Scoreboard (40%) | First in dependent chain, ~400 cycle latency |
| `LDG.E R14, [R12]` (value load) | Long Scoreboard (44%) | Dependent on col_index, another ~400 cycles |
| `SHFL.BFLY R16, R16, 0x1` | Short Scoreboard (5%) | Warp reduction, ~20 cycle cross-lane latency |
| `IMAD.WIDE R12, R6, 0x4, R8` | Wait (3%) | Stalls until R6 from first LDG is ready |

### Critical path interpretation

The stall mapping reveals the bottleneck structure:
- **Long Scoreboard >> 50%**: Memory latency dominates. The kernel is latency-bound.
- **Long Scoreboard + dependent chain**: Each dependent load adds ~400 cycles serially. MLP is limited.
- **Barrier >> 10%**: Load imbalance between warps (common with irregular sparsity).
- **Math Pipe Throttle >> 10%**: Compute-bound region. Instruction-level optimization may help.

---

## 7. Instruction Mix Statistics

### Counting instruction classes from SASS

Extract the hot loop SASS and classify each instruction:

```bash
# Count instruction types in SASS dump
grep -oP '^\s*/\*[0-9a-f]+\*/\s+\K\S+' kernel.sass | sort | uniq -c | sort -rn
```

### Instruction mix table format

| Instruction Class | Count | % of Hot Loop | Examples |
|------------------|------:|-------------:|---------|
| Integer Arithmetic | 12 | 35% | IMAD, IADD3, ISETP, LEA |
| Global Load | 4 | 12% | LDG.E |
| Global Store | 1 | 3% | STG.E |
| FP Arithmetic | 3 | 9% | FFMA, FADD |
| Warp Shuffle | 5 | 15% | SHFL.BFLY |
| Control Flow | 3 | 9% | BRA, @P, EXIT |
| Special Register | 2 | 6% | S2R |
| Other | 4 | 12% | MOV, NOP, DEPBAR |
| **Total** | **34** | **100%** | |

### Compute-to-memory ratio

```
Compute ops = FP arithmetic + Int arithmetic (excluding address calc)
Memory ops  = Global loads + Global stores

Ratio = Compute ops / Memory ops

SpMV typical: ratio ~0.4 (2 FP ops per 5 memory ops) → heavily memory-bound
GEMM typical: ratio ~10+ (many FP ops per few memory ops) → compute-bound
```

---

## 8. Connecting to Measured Performance

### The analysis chain

```
Instruction Mix → Stall Distribution → CPI → IPC → Bandwidth Efficiency

1. Instruction mix tells you what the kernel DOES
2. Stall distribution tells you what the kernel WAITS on
3. CPI = cycles per instruction (from stalls + execution)
4. IPC = instructions per cycle = 1/CPI (from ncu)
5. Bandwidth = bytes_moved / time = f(IPC, bytes_per_instruction)
```

### Per-input variation analysis

Different inputs expose different bottleneck intensities:

| Input | IPC | Long Scoreboard % | Achieved BW (GB/s) | % Peak BW |
|-------|----:|-------------------:|--------------------:|----------:|
| Regular mesh (cant) | 0.85 | 74% | 615 | 91.5% |
| Power-law graph (webbase) | 0.63 | 83% | 489 | 72.8% |
| Large structured (cage15) | 0.81 | 78% | 598 | 89.0% |

**Interpretation**: Regular meshes achieve higher IPC because uniform row lengths mean less load imbalance (lower barrier stalls), freeing scheduler slots for memory requests.

### Floor-vs-actual gap decomposition

Connect instruction-level evidence to the gap between physical floor and actual performance:

| Gap Factor | Evidence Source | Contribution |
|-----------|----------------|-------------|
| Dependent load chain (MLP=1 vs MLP=2) | SASS: `LDG→IMAD→LDG` chain in hot loop | 45% of gap |
| L2 cache misses on irregular access | SASS: `LDG.E` with data-dependent address | 25% of gap |
| Warp load imbalance | SASS: `BAR.SYNC` + ncu barrier stalls | 15% of gap |
| Address computation overhead | SASS: `IMAD.WIDE`, `LEA` between loads | 10% of gap |
| Control flow (loop overhead) | SASS: `ISETP`, `BRA` per iteration | 5% of gap |
| **Total accounted** | | **100%** |

### Verification checklist

Before finalizing instruction-level analysis:
- [ ] Every stall category > 5% is traced to specific SASS instructions
- [ ] Dependency chain length matches theoretical prediction (e.g., 2 serial loads = ~800 cycles)
- [ ] Instruction mix ratio is consistent with memory-bound/compute-bound classification from roofline
- [ ] IPC variation across inputs is explained by structural differences (regularity, row length distribution)
- [ ] Gap decomposition percentages sum to ~100% (within 10% tolerance)
