# Paper Structure Template — Rhu / Zhu Style

A generalized section-by-section template extracted from 78 computer-architecture papers by Minsoo Rhu's group (KAIST VIA Lab) and Yuhao Zhu's group (Univ. of Rochester / Horizon Lab). The template is descriptive, not prescriptive — both groups deviate from it situationally — but the canonical pipeline below recurs in well over 80% of their conference-length papers (ISCA / MICRO / HPCA / ASPLOS).

Per-paper summaries grounding the patterns below live in `01_papers/00_rhu/*.md` (47 papers) and `01_papers/01_zhu/*.md` (31 papers). Each per-section reference exemplar below cites a specific summary file so you can drill into the concrete numbers behind the abstraction.

---

## The canonical 8-section flow

| # | Section | Typical length (12-page paper) | Distinctive Rhu/Zhu trait |
|---|---------|--------------------------------|---------------------------|
| 1 | Introduction | 1.0–1.5 pages | Industry-importance hook in the *first paragraph*; ends with a numeric "punchline" claim. |
| 2 | Background | 0.5–1.5 pages | Compresses the ML/graphics/robotics primer into the minimum needed to read the bottleneck section. Often folded into Section 3. |
| 3 | Workload Characterization / Motivation | **2.0–3.0 pages — disproportionately large** | Quantitative breakdown + counter-driven root-cause. The *load-bearing* section. |
| 4 | Key Insight / Design Principle | 0.25–0.5 page | One-paragraph "insight box" linking the measured root cause to the proposed mechanism. |
| 5 | Design / Architecture | 2.0–3.0 pages | Algorithm + microarchitecture, organized so each subcomponent maps to a counter from §3. |
| 6 | Implementation / Methodology | 0.5–1.0 page | Cycle-accurate sim setup, RTL synthesis numbers, real-hardware fallback when applicable. |
| 7 | Evaluation | 2.5–3.5 pages | Headline plot is a *re-measurement of the same counter from §3* showing the cause is gone, then perf/energy plots, then an ablation. |
| 8 | Related Work + Conclusion | 0.5–1.0 page | Compact; rarely the most novel section. |

The visual signature of a Rhu/Zhu paper is that **§3 is large** and the **first plot of §7 mirrors the breakdown plot of §3**. That bookending is what most distinguishes their work from typical arch papers.

---

## §1. Introduction

### What it contains
- **Paragraph 1 — the workload's industry weight.** A single sentence positions the workload as already deployed at scale (recommendation models at Meta/Google, LLM serving at OpenAI/Anthropic, neural rendering in XR products, autonomous-machine perception). Quantitative grounding (datacenter footprint %, latency SLO, memory-capacity demand) appears here, not later.
- **Paragraph 2 — the architectural gap.** Why is current hardware (GPU / NPU / TPU / NoC) a bad fit for this workload? One concrete number: e.g. "70% of training time is spent on embedding lookups that achieve <5% of peak HBM bandwidth."
- **Paragraph 3 — what we propose.** Names the system; states the *type* of contribution (a chiplet, a near-memory architecture, a scheduler, a compiler pass).
- **Contribution bullets** — typically four bullets, one of which is *always* the workload characterization itself ("We are the first to characterize ..."). Treating the characterization as a contribution is a Rhu/Zhu signature.

### What makes their version distinctive
The intro's *first paragraph* never reads as a research-area survey ("Deep learning has revolutionized..."). It reads as a market-relevance brief ("Meta reports recommendation inference accounts for 79% of AI cycles in their datacenters..."). The reader's first impression is that the work is solving something *the industry is currently bleeding from*.

### Common failure mode if weak
Papers that lead with model-accuracy or algorithmic novelty before establishing industrial importance feel academic and reviewers find them easier to dismiss as "incremental tuning." The Rhu/Zhu pattern inoculates against that.

### Reference exemplars
- *TensorDIMM* — `01_papers/00_rhu/2019_MICRO_TensorDIMM.md`: opens with embedding-table memory dwarfing GPU HBM at hyperscalers (DLRM, YouTube), framing the CPU↔GPU PCIe transfer as the production-system pain point.
- *Centaur* — `01_papers/00_rhu/2020_ISCA_Centaur.md`: opens with production DLRM having two opposing hardware-demand profiles (dense MLP vs sparse embedding) on the *same* model.
- *OliVe* — `01_papers/01_zhu/2023_ISCA_OliVe.md`: opens with the 240×-per-2-years LLM size growth outpacing hardware, making quantization the only practical lever.
- *Cicero* — `01_papers/01_zhu/2024_ISCA_Cicero.md`: opens with NeRF at 0.8 FPS on mobile Volta and Instant-NGP taking >6 s/frame at 800×800 — far from VR-real-time.
- *LLM-PRISM* — `01_papers/01_zhu/2026_arXiv_LLMPRISM.md`: opens with concrete production telemetry — Meta's 54-day Llama snapshot saw 6 SDC-attributed interruptions; Google reports ~1 SDC/1–2 weeks during Gemini training.
- *SEAL* — `01_papers/01_zhu/2025_ISCA_SEAL.md`: opens with three energy/latency numbers in a single paragraph — image sensors emit hundreds of MB/s, MIPI byte-transfer ≈ 100 pJ (two orders > MAC), VIO frontend = 83% of end-to-end latency. The reader reaches §3 already convinced the bottleneck is real.

---

## §2. Background

### What it contains
- A concise primer on the workload's algorithmic structure (what an embedding lookup is; what NeRF inference looks like; what a Hungry-Hungry-Hippos block does).
- A concise primer on the relevant hardware substrate (HBM3 specs; SM/L2 hierarchy; PIM bank organization).
- Often *one* small figure showing the inner loop or compute graph.

### What makes their version distinctive
**Brevity.** They cut Background as much as possible — 0.5 page is common. The implicit contract is: a sophisticated reader can skim it; an unfamiliar reader uses references. The space is reclaimed for §3 (workload characterization).

### Variations
- For papers introducing a brand-new workload to the arch community (e.g. *Mesorasi* on point-cloud analytics, *Eudoxus* on robot localization), Background expands to 1.5 pages and includes more algorithm pseudocode.
- For follow-up papers in an established line (e.g. *PIM-MMU* following *PIM-malloc*), Background compresses to half a column and refers to the prior paper.

### Common failure mode
Padding Background with general DL/CV history. They never do this.

---

## §3. Workload Characterization / Motivation — *the key section*

This section is the methodological heart of both groups' work. **It is typically split into two subsections:**

### §3.1 Quantitative breakdown (the "what")
A latency / energy / memory-traffic stacked-bar chart broken down by execution stage. Stage definitions are paper-specific (e.g. embedding lookup vs FC vs all-reduce; ray generation vs intersection vs shading; capture vs ISP vs DNN). The breakdown is shown across multiple representative inputs / model sizes / configurations, not a single workload, so the dominant-stage finding is robust.

The section names a percentage: "Stage X is 62–74% of total."

### §3.2 Root-cause analysis (the "why")
This is where the section earns its weight. The dominant stage from §3.1 is profiled at one level of abstraction deeper using:
- **Real hardware counters** (Nsight Compute / nvprof) — DRAM throughput, L2 hit rate, warp occupancy, achieved-vs-peak FLOPS, TLB miss rate.
- **Roofline plots** — placing the stage's arithmetic intensity vs the device's BW/compute ridge to argue memory-bound vs compute-bound.
- **Simulator counters** (GPGPU-Sim, Accel-Sim) — when measuring something real silicon can't expose (e.g. NoC injection rate, MSHR occupancy, bank-conflict rate).
- **Memory-traffic traces** — to show which addresses/tiles are reused or thrashed.

Each sub-finding is one sentence + one number + one figure. By the end of §3, the reader knows *exactly* what the architectural villain is, not just where time was spent.

### Distinctive Rhu/Zhu trait
Both groups treat §3 as a *separate, named contribution*. The bullet "First quantitative characterization of ⟨X⟩ on commodity hardware" appears in 60+ of their papers. For some papers (*Pathfinding PIM*, *Real GPU NoC*, the IEEE CAL "Characterization and Analysis of ⟨X⟩" series) the characterization *is* the entire paper.

### Variations
- Pure characterization papers (IEEE CAL series, sometimes ISCA — e.g. *Real GPU NoC*) skip §4–§5 and expand §3 into the entire body.
- Some papers split §3 into two full sections: "Characterization" and "Insights" (e.g. *Centaur* separates the FC vs embedding measurement from the chiplet-design implications).

### Common failure mode
A breakdown that names the dominant stage without identifying *the counter that explains it* leaves the design unjustified. Rhu/Zhu papers reliably commit to a counter — readers know the cause.

### Reference exemplars
- *vTrain* — `01_papers/00_rhu/2024_MICRO_vTrain.md`: characterizes GPT-3-class LLM training across DP×TP×PP×μb search space and shows utilization varies 30–70% per choice, translating into million-dollar cost differences. The §3 contribution is a *parallelization-search-space cost surface*.
- *Pathfinding PIM* — `01_papers/00_rhu/2024_HPCA_PIMpath.md`: builds `uPIMulator` to *measure* a real UPMEM-PIM device, exposing that the academic PIM literature had over-assumed core speed and inter-DPU communication. The whole paper *is* §3.
- *Mesorasi* — `01_papers/01_zhu/2020_MICRO_Mesorasi.md`: per-stage timing on Jetson TX2 shows point-cloud DNNs take 71–5200 ms/frame; aggregation expands data K× before MLP, multiplying compute and memory.
- *Cicero* — `01_papers/01_zhu/2024_ISCA_Cicero.md`: decouples §3 into *algorithmic* redundancy (radiance proximity → up to 88% MLP redundant) and *architectural* (irregular DRAM + SRAM bank conflicts) bottlenecks, addressed by separate mechanisms in §5.
- *S2TA* — `01_papers/01_zhu/2022_HPCA_S2TA.md`: counter-level energy breakdown of conventional INT8 systolic accelerator: SRAM 21%, operand+result buffers 49%, MAC datapath 20%, activation function 10%. The crucial finding is that *prior unstructured-sparse accelerators add ~50% buffer overhead*, wiping out their MAC savings — i.e. they were attacking the wrong number.
- *TRiM* — `01_papers/00_rhu/2021_MICRO_TRiM.md`: walks the DDR5 memory hierarchy — internal-vs-channel BW quantified per tree depth (channel/rank/bank-group/bank). Exposes that rank-level NDP only achieves 1.6× of an ideal 4.3× at v_len=32 because partitioned vectors fall below the 64 B read granularity. The §3 finding determines exactly which depth (bank-group) the design must place compute at.
- *Trident* — `01_papers/00_rhu/2021_HPCA_Trident.md`: profiles four GPU generations (Kepler / Maxwell / Pascal / Volta) and shows the timing-vs-#unique-line correlation *changes sign* between generations because of 32 B sectored cache. A perfect example of a §3 finding that a single-generation evaluation would have missed.
- *Tigris* — `01_papers/01_zhu/2019_MICRO_Tigris.md`: *design-space-exploration first* — sweeps the registration pipeline across keypoint/descriptor/normal-estimation choices and shows KD-tree search exceeds 50% of time across *all* design points, before specializing. Methodologically cleaner than picking one algorithm and characterizing it.

---

## §4. Key Insight / Design Principle

### What it contains
A short, often boxed paragraph that names the *architectural lever* the design will pull. It is specifically written so that the reader can predict the rest of the paper from this paragraph alone.

Examples:
- "Embedding lookups are bandwidth-bound on the DRAM-CPU link, not compute-bound. Therefore the right architecture moves compute *to* the DRAM, not data to the compute."
- "Outliers determine LLM quantization quality, but only ~0.1% of values are outliers. Therefore quantize at fine granularity with a victim slot per group."
- "Neural rendering's per-pixel work is dominated by ray-tile reuse that the GPU memory hierarchy cannot capture. Therefore radiance-warp-aware reuse must be exposed to architecture."

### Distinctive trait
The insight is a *one-to-one functional response* to a counter from §3. A reader scanning §3 then §4 should be able to fill in the proposed mechanism without reading §5.

### Common failure mode
Papers without an explicit insight section often dilute the connection between problem and solution. Rhu/Zhu papers make the link unmissable.

---

## §5. Design / Architecture

### What it contains
- Algorithm-side change (when applicable): a new schedule, new data layout, new quantization scheme, new tiling.
- Hardware-side change: block diagram, microarchitectural state machines, augmented controllers, custom datapath.
- Software/runtime change (when applicable): driver / runtime / compiler-pass description.
- A "design walkthrough" subsection that traces a single workload step end-to-end through the new system.

### Distinctive trait
**Each subcomponent is anchored back to a §3 finding.** A typical Rhu/Zhu §5 has subsection titles like:
- "5.1 Reducing Cross-die Traffic (Addresses Finding 1: 71% NoC injection)"
- "5.2 Pipelined Address Translation (Addresses Finding 2: TLB miss = 38%)"

This labeling makes reviewers' job mechanical: every block in the design has a justifying counter.

### Variations
- Algorithm-only proposals (*PREMA*, *Lazy Batching*, *Tensor Casting*) keep §5 short and shift weight to §3 and §7.
- Hardware-only proposals (*Centaur*, *BTS*, *DiVa*, *ARK*) sometimes split §5 into "5. Architecture" and "6. Microarchitecture."

### Common failure mode
A design section that adds features uncorrelated with §3 findings. Rhu/Zhu papers reliably resist scope creep in §5.

---

## §6. Implementation / Methodology

### What it contains
- Simulator stack: GPGPU-Sim / Accel-Sim / cycle-accurate accelerator sim / Ramulator / DRAMsim3.
- RTL synthesis: tech node, area, frequency, power numbers (when proposing a hardware accelerator).
- Real-hardware setup: GPU model (A100 / H100 / RTX 40-series), driver versions, NCCL versions, profiler used.
- Workload set: representative models (e.g. RM1/RM2 for recommendation; LLaMA-7B/13B/30B/70B for LLMs; DLBI/RNN-T/etc.).
- Baselines: clearly named (vendor library, prior arch proposal, naïve port).

### Distinctive trait
Both groups *over-document* this section relative to the field. The expected workload coverage includes 3–5 model sizes, 2+ batch sizes, 2+ hardware platforms when relevant. This forestalls "you only tested at one point" reviews.

### Common failure mode
None notable — both groups treat this section as table-stakes.

---

## §7. Evaluation

### What it contains
- **Headline plot (always first):** a re-measurement of the §3 root-cause counter under the proposed system, showing the bottleneck is gone or amortized.
- **Performance plot:** speedup / throughput vs baseline across the workload sweep from §6.
- **Energy plot:** energy-per-inference, energy-per-frame, or pJ/op.
- **Ablation:** turn off each contribution one at a time; show degradation.
- **Sensitivity sweep:** vary one design parameter (cache size, # of PEs, batch size).
- **Comparison to prior work:** when applicable.
- **Real-system validation (when possible):** run on actual silicon to corroborate the simulator results.

### Distinctive trait
The *first plot* of §7 is the same metric as the dominant breakdown in §3, just with the proposed system overlaid. This visually closes the loop. Reviewers see at-a-glance that the diagnosed disease was cured.

### Common failure mode
Skipping the "did the counter actually move?" plot. A speedup number without a counter-level confirmation leaves the causal story untested.

### Reference exemplars
- *OliVe* §7 — `01_papers/01_zhu/2023_ISCA_OliVe.md`: 4.5× speedup, 4.0× energy reduction vs. GOBO; accuracy preserved across LLM tasks at the same bitwidth.
- *Mesorasi* §7 — `01_papers/01_zhu/2020_MICRO_Mesorasi.md`: three-tier evaluation (algorithm-only on mobile Pascal GPU = 1.6×; +NPU augmentation = 3.6×; futuristic full HW = 6.7×) — gives a realistic deployment story across deployment maturity levels.
- *Cicero* §7 — `01_papers/01_zhu/2024_ISCA_Cicero.md`: separate reporting of pure-algorithm (8.0×) vs +HW (28.2×) makes contributions individually attributable; quality loss <1.0 dB PSNR is the closing-the-loop quality plot.
- *Tigris* §7 — `01_papers/01_zhu/2019_MICRO_Tigris.md`: 77.2× speedup on KD-tree search (the §3 dominant stage), 7.4× power reduction, then 41.7% end-to-end registration speedup as the final perf number.
- *LazyDP* §7 — `01_papers/00_rhu/2024_ASPLOS_LazyDP.md`: 119× average training throughput improvement on a software-only intervention; mathematically-equivalent DP guarantee proved (closes the loop on a *correctness* axis the speedup numbers alone can't).

---

## §8. Related Work + Conclusion

### What it contains
- Compact related-work section (often half a column), grouped by axis (algorithmic vs architectural vs system) rather than chronologically.
- Single-paragraph conclusion that re-states the §1 industry framing in past tense ("We have shown that...").

### Distinctive trait
Related Work is rarely the place these papers spend creative energy. Both groups invest in being well-read but communicate it with restraint.

---

## Variations and exceptions worth noting

The structure above describes the **conference-length, end-to-end accelerator/system paper**. Other formats deviate:

| Format | Example summaries | Variation |
|--------|-------------------|-----------|
| **IEEE CAL short paper** | `2024_IEEECAL_3DGS.md`, `2024_IEEECAL_DiffusionT2I.md`, `2024_IEEECAL_H3.md` | §1 + §3 + §7 only, in 4 pages. The "Characterization and Analysis of ⟨X⟩" CAL series follows this pattern — workload characterization without proposing a fix. |
| **PIM / FHE accelerator papers** | `2022_ISCA_BTS.md`, `2022_MICRO_ARK.md`, `2022_MICRO_DiVa.md` | Larger §5 because multiple custom hardware blocks must be described. §3 uses analytical models more than profiling because there is no realistic baseline silicon for FHE/DP at the time of writing. |
| **Pure characterization papers** | `2024_HPCA_PIMpath.md`, `2024_MICRO_GPUNoC.md`, `2025_IEEECAL_HSTU.md`, `2025_ISCA_Gaudi.md`, `2026_arXiv_LLMPRISM.md` | §3 *is* the paper. §4–§5 collapse into "Implications for future architecture" subsection. Often the contribution is also a measurement *tool* (uPIMulator, LLM-PRISM injection framework, CamJ energy model). |
| **Tool-paper variant** | `2024_MICRO_vTrain.md`, `2024_HPCA_PIMpath.md`, `2023_ISCA_CamJ.md` | The *deliverable* is a simulator/model, not an architectural design point. §6 (validation) gets disproportionate weight because the tool's credibility depends on agreement with real silicon — CamJ validates against 9 real CIS chips with MAPE 7.5%; vTrain validates against measured production training runs. |
| **Algorithm-only papers** | `2024_ASPLOS_LazyDP.md`, `2021_HPCA_TensorCasting.md`, `2021_HPCA_LazyBatching.md`, `2020_HPCA_PREMA.md` | §5 is purely algorithmic / software; no hardware change. Compensated by an unusually rigorous correctness argument (LazyDP proves DP-guarantee equivalence) or a software-system implementation. |
| **Attack + countermeasure pair** | `2021_HPCA_Trident.md` | §3 establishes the attack viability (across 4 GPU generations); §5 presents the attack mechanism; §6 *also* presents a defense (TridentShield) with its own ablation. Distinct from a pure characterization paper because the defense must be evaluated for performance overhead vs prior defenses. |
| **Paradigm-port papers** | `2025_ISCA_SEAL.md` (race logic into in-sensor vision); `2022_ISCA_BTS.md` (NTT into FHE accelerator) | §1 / §2 must establish *portability validity* — the imported paradigm's primitives are complete-and-causal for the new workload. §3 then quantifies the cost the paradigm-port eliminates. Larger Background section than usual because the imported paradigm needs introduction. |

---

## How to use this template when *writing* a new paper

1. **Lock the §1 industry-importance number** before starting §3. If you can't cite an industrial deployment number, you have not yet picked a strong enough workload.
2. **Build §3 first.** Don't write §1–§2 until §3 has a stage-breakdown plot and at least one counter-level root-cause finding.
3. **Force §4 to be one paragraph.** If your insight requires more than that, you have multiple insights; pick one.
4. **Tag §5 subsections with §3 findings.** If a subcomponent doesn't trace back to a finding, it's scope creep — cut it.
5. **The first plot of §7 must be the same metric as §3.** This is the cheapest way to make the paper feel "complete" to reviewers.

---

## Cross-reference index — summaries that best illustrate each phase

For a learner who wants to trace the canonical structure to concrete papers, the following set is dense in methodology signal:

| Phase / signature | Best illustrative summaries |
|---|---|
| Industry-importance hook (§1) | `2019_MICRO_TensorDIMM.md`, `2020_ISCA_Centaur.md`, `2026_arXiv_LLMPRISM.md`, `2024_ASPLOS_LazyDP.md` |
| Stage breakdown (§3.1) | `2020_MICRO_Mesorasi.md`, `2022_HPCA_S2TA.md`, `2024_ASPLOS_LazyDP.md` |
| Counter-driven root cause (§3.2) | `2020_ASPLOS_NeuMMU.md`, `2024_HPCA_PIMpath.md`, `2024_ISCA_Cicero.md`, `2018_HPCA_CompressingDMA.md` |
| Workload-tolerance argument enabling approximation (§3→§4) | `2019_MICRO_Tigris.md`, `2020_MICRO_Mesorasi.md`, `2023_ISCA_OliVe.md` |
| Algorithm-arch one-to-one solution (§4→§5) | `2018_HPCA_CompressingDMA.md`, `2019_MICRO_TensorDIMM.md`, `2023_ISCA_OliVe.md` |
| Three-tier eval (algo / minor HW / full HW) (§7) | `2020_MICRO_Mesorasi.md`, `2024_ISCA_Cicero.md` |
| Tool-paper / characterization variant | `2024_HPCA_PIMpath.md`, `2024_MICRO_vTrain.md`, `2023_ISCA_CamJ.md`, `2026_arXiv_LLMPRISM.md` |
| Validation-against-real-silicon | `2024_HPCA_PIMpath.md`, `2025_ISCA_Gaudi.md`, `2024_MICRO_GPUNoC.md`, `2023_ISCA_CamJ.md` |
