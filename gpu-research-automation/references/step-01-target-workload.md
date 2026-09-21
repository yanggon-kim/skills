# Step 1 — Target Workload Search

## Purpose

Establish *what* we're researching: the algorithms, benchmarks, datasets, and industrial deployments that anchor the workload. This file's findings later govern Step 2's profiling targets, Step 3's literature scope, and (most importantly) Step 1 of the eventual paper — its industry-importance hook lives or dies here.

## Inputs

- **User-supplied workload name** (e.g. "homomorphic encryption", "LLM inference serving", "neural radiance fields", "ray tracing for VR").
- **`gpu_spec.json`** at the workspace root (auto-detected at `init_workspace.sh` time).
- Open web access for searching.

## Procedure

1. **Web search** for the workload, focusing on:
   - **Canonical algorithms** — what specific algorithms does the workload comprise? (e.g. for homomorphic encryption: BFV, BGV, CKKS, TFHE; for LLM inference: prefill / decode, paged-attention, speculative decoding.)
   - **Public benchmarks** — what evaluation suites do practitioners use? (e.g. for FHE: HEBench, FHE.org standard benchmarks; for LLM: vLLM benchmarks, LLMPerf, MLPerf Inference.)
   - **Datasets** — input data the benchmarks rely on. (e.g. plaintext / lattice parameter sets for FHE; ShareGPT prompts for LLM.)
   - **Open-source reference implementations** — what code is available? (e.g. Microsoft SEAL / OpenFHE for FHE; vLLM / TensorRT-LLM for LLM serving.)
   - **Industrial deployments** — who runs this at scale? (Concrete companies and use cases — this becomes the §1 hook of the paper.)

2. **Capture findings** in `00_target_workload/00_target_workload.md` using the template below.

3. **Flexible counts.** ≥3 algorithms / benchmarks / datasets is the preferred density, but if the field genuinely doesn't have 3 of something (e.g. a niche workload may have only one canonical benchmark), document what *is* available and note the gap. Don't pad the list with marginal options.

4. **Update `PROGRESS.md`** via `scripts/update_progress.py 1 done 00_target_workload/00_target_workload.md` and apply the checkpoint policy in `SKILL.md`. Report the artifact; wait only at a requested checkpoint or for a material unresolved choice.

## Output template — `00_target_workload/00_target_workload.md`

```markdown
# Target Workload: <workload name>

## Industrial relevance
- <company / system> uses this in <product> at <scale>, per <citation/URL>.
- <2-3 more bullets establishing why this workload matters in 2026>.

## Canonical algorithms
1. **<algorithm name>** — <one-sentence description>. Reference: <paper / spec URL>.
2. **<algorithm name>** — …
3. **<algorithm name>** — …

## Public benchmarks
| Benchmark | Maintainer | Workload coverage | URL |
|---|---|---|---|
| ... | ... | ... | ... |

## Datasets / inputs
| Dataset | Size | Format | Used by which benchmark | URL |
|---|---|---|---|---|

## Open-source reference implementations
| Project | Language | Highlights | URL |
|---|---|---|---|

## Selected target for Step 2
Identify the (algorithm, benchmark, dataset) tuple most representative of production usage. This is what Step 2 will profile. Justify the choice in 2–3 sentences.

## Gaps / caveats
- <Workloads where finding ≥3 of something failed; document the gap rather than padding.>
```

## Worked example — homomorphic encryption (sketch)

- **Industrial relevance:** Microsoft SEAL deployed in Edge / Azure Confidential Compute; Apple Private Cloud Compute uses HE for private inference; Google's HE-based PIR deployments; Meta's Private Lift Measurement.
- **Canonical algorithms:** BFV (integers), BGV (alternate integer scheme), CKKS (approximate fixed-point), TFHE (gate-by-gate Boolean).
- **Benchmarks:** HEBench (open standard), FHE.org test vectors, OpenFHE benchmarks.
- **Datasets:** parameter sets {n=2¹³, q=440-bit, …}; standard-ML dataset PSI / inference benches.
- **Reference impls:** Microsoft SEAL, OpenFHE, Lattigo, HElib.
- **Selected target for Step 2:** CKKS bootstrapping in OpenFHE — the dominant cost in deployed HE pipelines.

## Common pitfalls

- **Over-broad workload definition.** "Cryptography" is too broad; "FHE" is right; "CKKS bootstrapping in OpenFHE" is the right granularity for Step 2 profiling.
- **Selecting a benchmark with no real-world deployment.** A benchmark that doesn't appear in any production system is a poor anchor for the §1 hook. Prefer benchmarks vendors and hyperscalers use.
- **Skipping the industrial-relevance section.** Without it, Step 2's findings have no story; Steps 1, 7, and 8 will all suffer.
