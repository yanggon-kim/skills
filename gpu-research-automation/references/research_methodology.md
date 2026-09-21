# Research Methodology — How Rhu's and Zhu's Groups Define and Solve Architecture Problems

This document is a *perspective* document, not a structural one. Where `paper_structure_template.md` describes the *shape* of these papers, this one describes the *lens* — the analytical habits that make the two groups consistently produce strong work. It is intended as a "how to do research like Rhu/Zhu" reference for a graduate student or a junior architect.

The unifying claim of this document: **both groups practice quantitative-first problem definition with counter-driven root-cause analysis, and they discipline their solutions to be one-to-one responses to those root causes.** That single discipline drives most of the consistency we see across 78 papers.

---

## 1. Picking the workload

### The pattern
Both groups consistently pick workloads that are:
- **Already deployed in industry at scale** — not hypothetical, not academic-only. Recommendation models (Meta deployment), LLM serving (OpenAI/Anthropic deployment), neural rendering (Apple Vision Pro / Meta Quest), autonomous-machine perception (TuSimple / Waymo / Boston Dynamics), Gaussian splatting (Unity / Unreal pipeline integrations), PIM (Samsung / SK Hynix products).
- **Architecturally under-studied** — either no prior arch paper has profiled them on real hardware, or all prior work assumes a simulator setup that elides the property the workload actually exercises.
- **Likely to be 10× more important in 2–3 years** — they bet on workloads that are growing fast in production. The 2018-era "memory wall for DL training" bet, the 2019-era "embedding-table" bet, the 2023-era "LLM serving" bet, the 2024-era "neural rendering for XR" bet — all paid off because the industrial trajectory was visible at the time of bet-placing.

### Concrete signals they use
- Production blog posts and earnings-call mentions from major companies.
- Open-source releases (PyTorch, vLLM, OctaneRender, Gaussian Splatting reference impls) that hit non-trivial GitHub-star velocity.
- Hardware vendor announcements (Samsung HBM-PIM, Intel Gaudi, NVIDIA Blackwell Transformer Engine, Apple's R1 / M-series) — they track hardware moves to find what *will become* the dominant load.

### What this means for *you*
Before committing to a project, you should be able to answer:
> "If I succeed, what production system at what company gets faster, and how do I know that company actually cares?"

If you can't name the company and the metric, the workload is too academic. This is the strongest single discipline that distinguishes Rhu/Zhu workload selection from typical paper-driven workload selection.

---

## 2. Quantitative-first problem definition

### The pattern
**No claim about a bottleneck appears without a number attached.** A Rhu/Zhu paper never says "performance is poor" — it says "performance is 23% of peak; 41% of cycles are stalled on DRAM; 78% of memory traffic is sparse activation reads."

This carries through three habits:

1. **Magnitude-based prioritization.** Bottlenecks below ~30% of total are not pursued. If activation-reads are 22% of latency but address translation is 38%, the paper attacks address translation first. This sounds obvious but most papers fail to do it — they pursue what is intellectually interesting rather than what is numerically dominant.

2. **Multiple workload-scale points.** The dominant-stage finding is established across 3–5 model sizes / batch sizes / input resolutions, not at a single point. This guards against "the bottleneck moves at scale" reviewer attacks. (See *Centaur*'s sweep across RM1/RM2/RM3, *OliVe*'s LLaMA-7/13/30/70B sweep, *Cicero*'s scene-resolution sweep.)

3. **The breakdown is reproducible.** The methodology section names the exact tool (`nsys profile`, `ncu --metrics dram__bytes`, GPGPU-Sim trace), exact model checkpoint, exact input. A reader (or reviewer) could in principle re-run the breakdown.

### Quantitative *and* qualitative — they're not in tension
The user's intuition was sharp here: these groups use both. The quantitative measurement establishes magnitude; the qualitative reasoning explains *why the architecture does that*. For instance:

- *Quantitative:* "Embedding lookups achieve 12% of HBM peak BW."
- *Qualitative:* "Because each lookup is a sparse, random gather of 64-byte rows, the GPU memory hierarchy never coalesces — every access is a unique row activation, defeating any prefetching the L2 might do."

The qualitative half is what makes the paper usable to other architects. The quantitative half is what makes the qualitative claim non-hand-wavy.

### What this means for *you*
For every claim in your motivation section, ask:
- *Did I measure this, or am I relying on someone else's measurement?*
- *Did I measure it on the workload I actually care about, or on a proxy?*
- *Did I measure it across enough scale points that the dominant-finding is robust?*
- *Did I qualitatively explain why the hardware behaves this way?*

If you say "performance is poor" without all four, your motivation is weaker than a Rhu/Zhu paper's would be.

---

## 3. Counter-driven root-cause analysis

### The pattern
A breakdown plot identifies *which stage* dominates. That is necessary but **not sufficient.** Both groups always go one level deeper to identify *which architectural property* of the dominant stage causes its dominance. This is the move that most distinguishes their work from generic systems papers.

The mechanism is:

1. Pick the dominant stage from the breakdown.
2. Profile *that stage in isolation* using counter-level tools:
   - **Real silicon (Nsight Compute):** `dram__bytes`, `dram__throughput`, `l1tex__t_bytes_pipe_lsu_mem_global`, `lts__t_sectors_srcunit_tex`, `sm__cycles_active`, `smsp__inst_executed`, `smsp__warp_issue_stalled_*`, `tlb_utilization` proxies, etc.
   - **Cycle-accurate sim (GPGPU-Sim / Accel-Sim):** L2 MSHR occupancy, NoC injection rate, partition utilization, DRAM bank conflicts, address-translation latency.
   - **Memory-traffic traces:** captured via Nsight Systems with `--gpu-metrics-device=all` or via simulator instrumentation, then post-processed to identify reuse distance distributions, hot/cold ratios, etc.
3. Match the counter signal to a *named architectural property*: low arithmetic intensity, irregular access pattern, TLB pressure, NoC asymmetry, cache thrashing, warp serialization, etc.
4. State the property as the root cause in plain English and as a counter value.

### A cross-paper inventory of root causes they've identified

The table below grounds the abstraction in concrete summaries. Each row is one paper, with the *probe* used in §3 and the *architectural property* that probe exposed. Numbers are pulled from the per-paper summaries in `01_papers/`.

| Paper | Summary file | Probe | Root cause |
|-------|--------------|-------|------------|
| *Compressing DMA* (HPCA 2018) | `00_rhu/2018_HPCA_CompressingDMA.md` | PCIe transfer profile + activation sparsity histogram | Post-ReLU activations have very high zero-density but are offloaded densely across PCIe → DMA transfers mostly zeros. |
| *TensorDIMM* (MICRO 2019) | `00_rhu/2019_MICRO_TensorDIMM.md` | DLRM stage timing + system memory BW utilization | Embedding lookups want capacity (tens of GB) and BW (random reads), not FLOPS — GPU is wrong substrate. |
| *Centaur* (ISCA 2020) | `00_rhu/2020_ISCA_Centaur.md` | FC vs embedding stage profile + on-chip utilization | Dense MLP and sparse embedding have *opposing* hardware preferences — a monolithic die wastes silicon on whichever phase doesn't match. |
| *NeuMMU* (ASPLOS 2020) | `00_rhu/2020_ASPLOS_NeuMMU.md` | NPU access trace + page-walker queue depth | Address translation can be >50% of NPU stall time; CPU-style MMUs serialize batched (tensor-strided) TLB misses through one page-walker. |
| *Mesorasi* (MICRO 2020) | `01_zhu/2020_MICRO_Mesorasi.md` | Per-stage timing on Jetson TX2; tensor-size accounting | Aggregation stage expands data K× before MLP; F(A(N(p))) ≈ A(F(N(p))) approximate-distributive property is the lever. |
| *Tigris* (MICRO 2019) | `01_zhu/2019_MICRO_Tigris.md` | Design-space sweep across registration variants | KD-tree search >50% of time across *all* design points; recursive traversal hides node-level parallelism. |
| *Pathfinding PIM* (HPCA 2024) | `00_rhu/2024_HPCA_PIMpath.md` | uPIMulator cycle-level model + real UPMEM measurement | Production PIM has slower cores, no inter-DPU communication, no HW caches — the academic PIM literature had over-assumed. |
| *OliVe* (ISCA 2023) | `01_zhu/2023_ISCA_OliVe.md` | Outlier-magnitude histogram of LLM activations + neighbor-magnitude analysis | <0.1% of values are outliers determining quantization quality; their *immediate neighbors* are low-magnitude, hence sacrificeable. |
| *Cicero* (ISCA 2024) | `01_zhu/2024_ISCA_Cicero.md` | NeRF roofline; per-frame stage trace; SRAM bank-conflict count | Three coupled causes: per-ray MLP redundancy across nearby rays (≤88% redundant); pixel-centric ray order tours voxels in scatter; feature-major SRAM layout collides on every gather. |
| *vTrain* (MICRO 2024) | `00_rhu/2024_MICRO_vTrain.md` | Cluster-scale per-op time + comm time + memory footprint | DP × TP × PP × micro-batch parallelization choices interact non-monotonically with hardware; heuristic search misses optima → 30–70% utilization spread. |
| *S2TA* (HPCA 2022) | `01_zhu/2022_HPCA_S2TA.md` | Energy breakdown of conventional INT8 systolic array | Buffers (49%) eclipse MAC (20%); prior unstructured-sparse accelerators add ~50% buffer overhead chasing cheap MAC savings. |
| *LazyDP* (ASPLOS 2024) | `00_rhu/2024_ASPLOS_LazyDP.md` | Per-stage profile of DP-SGD on RecSys + per-example gradient timing | Noise-tensor must match gradient-tensor shape; for embedding tables this is enormous, but most rows have zero gradient — wasted noise + BW. |
| *Thales* (HPCA 2023) | `01_zhu/2022_HPCA_Thales.md` | RTL fault simulation (>2.6 B injections) vs SW fault injection | Software-vulnerability-factor mismatches architectural-vulnerability-factor by 100× because SW fault injection ignores FF-reuse and control-FF corruption. |
| *Debunking the CUDA Myth* (ISCA 2025) | `00_rhu/2025_ISCA_Gaudi.md` | Side-by-side Gaudi-2 vs A100 microbenchmarks (HabanaPerf + Nsight) | Gaudi's TPC engines and HBM are competitive on raw throughput; software-ecosystem maturity (compiler, framework integration) is the gap. |
| *LLM-PRISM* (arXiv 2026) | `01_zhu/2026_arXiv_LLMPRISM.md` | RTL fault sim + signature replay across 7,664 Megatron-LM training runs | Permanent / intermittent GPU faults are routine in hyperscale training; specific (datapath × precision) combinations (notably FP8) catastrophically diverge; deployed NaN/Inf detectors have blind spots. |
| *Trident* (HPCA 2021) | `00_rhu/2021_HPCA_Trident.md` | Real-silicon timing measurement on Kepler / Maxwell / Pascal / Volta + cache-loading probabilistic model | 32 B sectored cache + small T4-table changes the *sign* of the timing/#unique-line correlation by load-index; prior correlation attack assumed monotonic positive correlation, hence collapses on modern GPUs. |
| *TRiM* (MICRO 2021) | `00_rhu/2021_MICRO_TRiM.md` | DDR5 cycle-level sim + tCCD/tFAW timing model + internal-vs-channel BW accounting per tree depth | Rank-level NDP wastes internal BW because partitioned vectors fall below 64 B read granularity at v_len=32; deeper-level (bank-group / bank) NDP can recover ~8× headroom but is gated by C/A bandwidth and DRAM timing. |
| *SEAL* (ISCA 2025) | `01_zhu/2025_ISCA_SEAL.md` | Stage-by-stage pJ/pixel/frame energy accounting + sensor-host MIPI cost | ADC + DSP + SRAM all operate on multi-bit binary, forcing wide datapaths; the chain costs ~132 pJ/pixel/frame with MIPI dominating (100 pJ); race-logic *delay-encoding* is complete-and-causal, so the entire pipeline can drop to single-event-per-wire. |

### What this means for *you*
A "memory-bound" claim is not a root cause — it is a class. The root cause is *which counter, on which device, under which workload step*. Replace every adjective with a counter and you will have a Rhu/Zhu-grade root-cause section.

---

## 4. Solution-by-targeting-the-cause

### The pattern
Their proposed solutions read as if reverse-engineered from the §3 finding. The shape is always:

> **Root cause:** ⟨counter X on device Y is at level Z, because of property P⟩.
> **Solution:** ⟨a mechanism that *eliminates* or *amortizes* property P⟩.
> **Validation:** ⟨§7's first plot re-measures counter X and shows level Z' ≪ Z⟩.

This is the same one-to-one discipline that lets §5 subsections be tagged with §3 findings (see `paper_structure_template.md`). Concretely:

| Root cause | Targeted solution |
|------------|-------------------|
| Activation sparsity wastes DMA BW | Compress in the DMA engine itself (*Compressing DMA Engine*). |
| Embedding lookups are DRAM-bound | Move compute *into* DRAM via near-memory PE (*TensorDIMM*, *Centaur*). |
| TLB miss dominates NPU memory access | Custom MMU with NPU-aware page table walker (*NeuMMU*). |
| Outliers determine LLM quantization quality | Pair-quantize outlier+victim at fine granularity (*OliVe*). |
| NeRF cannot reuse rays in GPU memory hierarchy | Architect-visible radiance warping (*Cicero*). |
| Recommendation training has GPU memory pressure | Look-forward staging from CPU host memory (*Look Forward Not Backwards*, `00_rhu/2022_ISCA_ScratchPipe.md`). |
| Inference servers idle on long-tail latency | SLA-aware lazy batching (*Lazy Batching*, `00_rhu/2021_HPCA_LazyBatching.md`). |
| Multi-tenant inference servers waste GPU partitions | Heterogeneity-aware scheduling on MIG (*Hera*, `00_rhu/2025_PACT_Hera.md`). |
| DP-SGD wastes work + BW on zero-gradient embedding rows | Aggregated noise sampling that preserves DP guarantee — *no hardware change needed* (*LazyDP*, `00_rhu/2024_ASPLOS_LazyDP.md`, 119× throughput). |
| Aggregation expands point-cloud features K× before MLP | Operator commutation: apply MLP first, then aggregate the smaller results (*Mesorasi*, `01_zhu/2020_MICRO_Mesorasi.md`). |
| KD-tree search hides parallelism behind recursion | Two-stage data-structure restructuring + parallel PEs that exploit query- *and* node-level parallelism (*Tigris*, `01_zhu/2019_MICRO_Tigris.md`, 77.2×). |
| Outlier indices break SIMD/systolic memory alignment | Outlier-victim pair encoding so outliers fit in the same memory slot as two normal values (*OliVe*, `01_zhu/2023_ISCA_OliVe.md`, 4.5× over GOBO). |
| NeRF redundancy invisible to GPU memory hierarchy | Architect-visible radiance warping + memory-centric loop reorder + channel-major SRAM layout (*Cicero*, `01_zhu/2024_ISCA_Cicero.md`, 28.2× with HW). |
| Buffers eclipse MAC in mobile INT8 systolic | Density-Bound Block sparsity that eliminates gather/scatter staging FIFOs entirely (*S2TA*, `01_zhu/2022_HPCA_S2TA.md`). |

### Discipline rules they enforce
1. **No solution without an attached root cause.** Every architectural change in §5 references at least one §3 finding.
2. **No root cause without an attached solution component.** If §3 surfaces a finding that §5 ignores, that finding is either folded into a sensitivity study or removed from §3.
3. **The solution must be the *minimum* mechanism that fixes the cause.** They resist adding complexity uncorrelated with the diagnosed problem. Their papers are notably *not* "kitchen-sink" architecture proposals.

### What this means for *you*
When you draft your solution, write each subcomponent as a sentence: "Subcomponent X eliminates property P from finding F." If you can't write that sentence, the subcomponent doesn't belong in the paper. If multiple subcomponents address the same finding, you have over-engineered; pick one.

---

## 5. Quantitative + qualitative interplay

This is the user's own observation and worth emphasizing as a standalone principle.

- **Quantitative measurement** answers *how big*. It establishes which problem to attack.
- **Qualitative reasoning** answers *why this happens*. It establishes which mechanism to design.
- **Together** they make a paper unfalsifiable in the right way: the breakdown can be re-measured, the architectural reasoning can be re-derived, and the solution must move both.

A pure-quantitative paper without architectural reasoning ("we measured X is 70%, here's a fix") feels like an engineering report. A pure-qualitative paper without numbers ("memory is the bottleneck for this workload, our hardware fixes it") feels like hand-waving. Both groups balance the two: nearly every paragraph in §3 is a measurement followed by an architectural interpretation.

### Concrete tactic
Write §3 paragraphs in a strict alternating template:

> **Measurement:** "We profiled stage S on device D and observed counter C at value V (Fig. X)."
> **Interpretation:** "This indicates property P, which arises because ⟨architectural reason⟩."

Two-sentence measurement + two-sentence interpretation, repeated. The discipline forces both halves into every claim.

---

## 6. Closing the loop in evaluation

### The pattern
The first plot of §7 is, almost without exception, a *re-measurement of the same counter from §3*, this time including the proposed system. This visually demonstrates that the diagnosed cause was eliminated, not just that overall performance went up.

If §3 said "TLB miss dominates at 95%," §7's first plot is "TLB miss rate before/after." Then comes overall speedup. Then comes ablation. Then sensitivity. Then comparison to prior work.

### Why it matters
A reader who only looks at speedup numbers might believe an unrelated optimization happened. The counter re-measurement is the causal proof that the §3 diagnosis was correct *and* that the §5 mechanism actually addressed it. Without it, the paper's causal story is unverified.

### What this means for *you*
Plan §7 backwards from §3: list the counters you measured in §3, and require that each one be re-measured under the proposed system. If the re-measurement is missing, your causal claim is a hypothesis.

---

## 7. Reusable habits — a checklist

A condensed list of concrete rituals. If you adopt these, your papers will start to feel structurally similar to a Rhu/Zhu paper, even if the topic and authors are different.

- [ ] **Industry-relevance hook in paragraph 1.** Name the company, the deployment, and the metric.
- [ ] **The bottleneck under examination is ≥ 30% of the total.** If smaller, find a different problem.
- [ ] **Breakdown across ≥ 3 scale points.** Not a single workload point.
- [ ] **Root cause stated as a counter and a property.** Not "memory-bound" alone.
- [ ] **Roofline plot when the problem is BW-vs-compute.** Skip when it isn't, but use it when it is.
- [ ] **Single-paragraph insight section.** One paragraph. No more.
- [ ] **Each design subcomponent maps back to a §3 finding.** Tag them in subsection titles if it helps.
- [ ] **Methodology covers ≥ 3 workload scales and ≥ 2 baselines.** Document the simulator/profiler version.
- [ ] **First plot of §7 = §3's counter, re-measured.** Always.
- [ ] **Ablation removes each contribution one at a time.** No bundled ablations.
- [ ] **Real-hardware corroboration when possible.** If you simulated, run on closest-available silicon and report agreement/disagreement.
- [ ] **Treat workload characterization as a contribution.** List it as a contribution bullet in §1.
- [ ] **Compress Background and Related Work.** Reclaim that space for §3.
- [ ] **Resist adding any subcomponent that does not trace to a §3 finding.** Cut, don't fold in.

---

## 8. Anti-patterns to avoid

A list of habits these groups *do not* practice — useful as a negative checklist.

- ❌ **"The community has neglected workload X."** They never argue from neglect; they argue from numbers.
- ❌ **"We propose a unified framework for ⟨A, B, C⟩."** Their proposals are surgically narrow.
- ❌ **"Our system improves performance and energy and area and programmability."** They pick the metric that matches the §3 root cause and report sensitivity on the others.
- ❌ **"We use a representative model X to evaluate."** Always plural.
- ❌ **"Roofline analysis (Fig. 1) shows..." without specifying device peaks.** They always cite peaks for the actual silicon.
- ❌ **Speedup plots without a counter re-measurement plot.** Always paired.
- ❌ **Speculation about future hardware without a real-hardware baseline.** When real silicon exists, they measure it (e.g. *Pathfinding PIM* on UPMEM, *Debunking the CUDA Myth* on Gaudi).

---

## 9. Evolution over time (2018 → 2026)

Worth noting because the methodology has shifted:

- **2018–2019:** Heavier reliance on cycle-accurate simulators (GPGPU-Sim) for both characterization and evaluation. Real-hardware profiling existed (e.g. *Compressing DMA Engine* on PCIe BW) but was less central.
- **2020–2022:** Hybrid era. Real hardware (Nsight Compute, HabanaPerf, Jetson TX2 traces) becomes the primary characterization tool; simulator is reserved for *proposed* architecture evaluation only. *Mesorasi*'s use of TX2 timing (`01_zhu/2020_MICRO_Mesorasi.md`) and *S2TA*'s real-silicon energy breakdown (`01_zhu/2022_HPCA_S2TA.md`) typify this era.
- **2023–2026:** Real-hardware-first across the board. Multiple papers — *Pathfinding PIM* (`00_rhu/2024_HPCA_PIMpath.md`), *Debunking the CUDA Myth* (`00_rhu/2025_ISCA_Gaudi.md`), *Real GPU NoC* (`00_rhu/2024_MICRO_GPUNoC.md`) — treat measuring production silicon as the contribution itself. Simulators (uPIMulator, vTrain, CamJ) are now *validated against real-hardware ground truth* before being used; CamJ explicitly validates against 9 real CIS chips with MAPE 7.5%.

The 2026 frontier (per *LLM-PRISM*, `01_zhu/2026_arXiv_LLMPRISM.md`) introduces a new methodological invention: **decouple slow hardware fidelity from fast workload scale** by running RTL once to extract per-fault-site error signatures, then replaying signatures inside Megatron-LM at full training speed (7,664 runs / ~11,500 GPU-hours). This is a generalizable pattern beyond reliability — any time a paper wants high-fidelity microarchitectural truth at hyperscale workload size, the same RTL→signature decoupling is available.

---

## 10. Recurring methodological inventions worth naming

Beyond the canonical pipeline, both groups have introduced *named methodological moves* that other architects can borrow. The list below is short on purpose — each is a portable technique, not a one-off finding:

1. **Approximate-distributive operator commutation** — `01_zhu/2020_MICRO_Mesorasi.md`. If `F(A(x)) ≈ A(F(x))` to within workload tolerance, swap order to put expensive `F` *before* cheap-but-bandwidth-explosive `A`. The right-hand cost can be orders of magnitude lower.
2. **Sacrifice-the-unimportant-in-place encoding** — `01_zhu/2023_ISCA_OliVe.md`. When a small fraction of values dominates quality, *consume the unimportant adjacent slot* to encode the important value, preserving memory alignment. Generalizes beyond outliers (e.g. block-sparse, mixed-precision).
3. **Workload-tolerance-justified approximation** — `01_zhu/2019_MICRO_Tigris.md`, `01_zhu/2024_ISCA_Cicero.md`. When the input is itself noisy (point clouds, ray-traced radiance, autonomous-machine sensor data), claim an *approximation budget* before designing — this unlocks data-structure restructurings that exact algorithms cannot afford.
4. **Three-tier deployment evaluation** — `01_zhu/2020_MICRO_Mesorasi.md`. Report perf at (a) algorithm-only on commodity hardware, (b) minor existing-accelerator extension, (c) full custom hardware. Reviewers see deployable wins at every adoption-cost tier.
5. **Tool-as-primary-contribution** — `00_rhu/2024_HPCA_PIMpath.md` (uPIMulator), `00_rhu/2024_MICRO_vTrain.md` (vTrain), `01_zhu/2023_ISCA_CamJ.md` (CamJ), `01_zhu/2026_arXiv_LLMPRISM.md` (LLM-PRISM injection framework). The deliverable is a measurement instrument that other architects can adopt; validation against real silicon is over-emphasized to compensate for the lack of a "speedup" headline.
6. **RTL-signature decoupling** — `01_zhu/2026_arXiv_LLMPRISM.md`. Run high-fidelity RTL once per fault/op site to extract output-perturbation signatures; replay signatures in software at workload scale. Decouples *fidelity* (RTL) from *scale* (workload); generalizable beyond reliability.
7. **Design-space-exploration first, specialization second** — `01_zhu/2019_MICRO_Tigris.md`. Sweep the workload's algorithmic configuration space to find the *universal* dominant stage *before* picking an algorithm to specialize. Avoids "we sped up algorithm X, but X may not be the one production picks."
8. **Equivalence proof when proposing algorithmic redesign** — `00_rhu/2024_ASPLOS_LazyDP.md`. When the proposal alters mathematical behavior (e.g. differential privacy), prove formal equivalence to the unmodified version. Pre-empts reviewer "but does it still satisfy the guarantee?" attacks.
9. **Comparative microbenchmark + end-to-end evaluation** — `00_rhu/2025_ISCA_Gaudi.md`, `00_rhu/2024_MICRO_GPUNoC.md`. When characterizing a new device, layer microbenchmarks (per-primitive) and end-to-end workloads (production-scale) so readers can attribute gaps to either substrate, software stack, or workload scaling.
10. **Two-regime hybrid mechanism with a controller that crosses between regimes** — `00_rhu/2021_HPCA_Trident.md`. When a microarchitectural change has *split* the workload's behavior into two regimes (e.g. positive-correlation vs negative-correlation; compute-bound vs memory-bound at different scales), the right design is also two-regime: one mechanism per regime, plus a *controller* (in Trident: a chosen-plaintext attacker) that *places the workload into the regime where each mechanism shines*. Generalizes beyond security: any time a §3 finding shows a sign-change or phase transition, this pattern applies.
11. **Walk-the-memory-hierarchy quantification** — `00_rhu/2021_MICRO_TRiM.md`. Quantify internal-vs-channel bandwidth at *every level* of a hierarchical interconnect (channel → rank → bank-group → bank, or NoC tile → router → link). Place compute at the deepest level where (a) data-access granularity, (b) control-path bandwidth, and (c) timing-window constraints all permit utilization. Name each constraint quantitatively before placing.
12. **Port-a-paradigm from an adjacent sub-field** — `01_zhu/2025_ISCA_SEAL.md` (race logic from sequence-alignment / brain-inspired computing into in-sensor vision); cf. `00_rhu/2022_ISCA_BTS.md` (NTT/cryptography number-theoretic transforms into memory-hierarchy aware accelerators). The portability claim is itself a contribution: identify a paradigm whose primitives (in SEAL: {min, max, increment, threshold} under delay-encoding) are complete-and-causal for your workload, then re-implement the workload natively in that paradigm rather than approximating it inside CMOS-binary.

---

## 11. How to apply this guide to your own work

A condensed loop, derived from the above:

1. **Pick a workload your industry contact is bleeding from.** If you can't name the company, picked wrong.
2. **Profile it on real silicon first.** Generate the §3.1 stage breakdown.
3. **Identify the dominant stage (≥30%).** Below that, find a different problem.
4. **Probe *that* stage at counter level.** Name the architectural property — not "memory-bound" but "TLB miss = 38% per the page-walk-queue counter."
5. **Decide solution class** by matching root cause to the inventory above (§4 here, plus §10's named techniques). Resist scope creep.
6. **If you propose hardware,** plan a tool (simulator, energy model) early, because §6 will need it.
7. **Build the §7 first plot before writing §1.** The first plot of evaluation must re-measure the §3 counter under your system. If it doesn't move, your story is wrong.
8. **Add an ablation per contribution.** No bundled ablations.
9. **Frame §1 last.** With the §3 number and §7 number in hand, the industrial-importance hook writes itself.

---

*This document is intended to be read alongside `paper_structure_template.md`. The structural template gives you the section layout; this methodology doc gives you the perspective that makes those sections load-bearing instead of ceremonial.*

*Per-paper supporting evidence is in `01_papers/{00_rhu,01_zhu}/` — 78 summaries (47 Rhu, 31 Zhu), one per CSV row, with 63 of the 78 PDFs locally available. Each summary uses the structured template (§1 Workload & Importance / §2 Bottleneck / §3 Root Cause / §4 Solution / §5 Evaluation / §6 Methodology Notes), so the abstractions in this doc can be drilled-down to specific numbers in any paper.*
