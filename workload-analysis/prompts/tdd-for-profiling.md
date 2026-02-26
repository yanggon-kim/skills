# Validation-First Development for Profiling

Adapted from TDD (Red-Green-Refactor) for GPU profiling scripts.

## Core Principle

Write the validation check first. Watch it fail. Write minimal code to pass.

**If you didn't watch the check fail, you don't know if it checks the right thing.**

## The Cycle

```
RED    → Write a check that should pass when done, but fails now
VERIFY → Run it, confirm it fails for the right reason
GREEN  → Write minimal code to make it pass
VERIFY → Run it, confirm it passes
CLEAN  → Refactor if needed, keep checks passing
```

## What "Validation Checks" Mean for Profiling

Profiling scripts aren't typical software — they produce files, plots, and metrics. Validation checks verify these outputs.

### Environment Setup

```python
# RED: These should fail before setup
assert shutil.which("nsys"), "nsys not found"
assert shutil.which("ncu"), "ncu not found"
import torch; assert torch.cuda.is_available(), "CUDA not available"
assert torch.version.cuda.startswith("13"), f"Expected CUDA 13.x, got {torch.version.cuda}"
```

### Profiling Scripts

```python
# RED: Script should produce output files
import os
output = "analysis/profiling_results_bs1.json"
assert os.path.exists(output), f"Missing {output}"

with open(output) as f:
    data = json.load(f)
assert "phases" in data, "Missing 'phases' key"
assert all(t > 0 for t in data["timings"].values()), "All timings must be positive"
```

### Profile Files

```python
# RED: Binary profiles should exist and have content
profile = "profiles/workload_bs1.nsys-rep"
assert os.path.exists(profile), f"Missing {profile}"
assert os.path.getsize(profile) > 0, "Profile file is empty"
```

### Analysis Outputs

```python
# RED: Analysis should produce expected metrics
with open("analysis/ncu_analysis_bs1.json") as f:
    ncu = json.load(f)
assert "kernels" in ncu, "Missing kernel data"
assert all(0 <= k["sm_pct"] <= 100 for k in ncu["kernels"]), "SM% out of range"
assert all(0 <= k["mem_pct"] <= 100 for k in ncu["kernels"]), "Mem% out of range"
```

### Visualization

```python
# RED: Plots should be generated
assert os.path.exists("analysis/roofline.png"), "Missing roofline plot"
from PIL import Image
img = Image.open("analysis/roofline.png")
assert img.size[0] >= 800 and img.size[1] >= 600, "Plot too small"
```

## Rules

- Write the check BEFORE the implementation
- Run the check, watch it fail
- Implement minimal code to pass
- Run the check, watch it pass
- Never skip the verify steps

## When TDD Doesn't Apply

Some profiling tasks are exploratory (reading traces, manual inspection). TDD applies to:
- Scripts that produce files or data
- Parsing and analysis code
- Visualization code
- Environment setup verification

TDD does NOT apply to:
- Manually inspecting Chrome traces in a browser
- Reading nsys timeline visually
- Exploratory analysis where you don't know what to expect yet

## Red Flags

- Writing the script first, then "adding checks after" → delete, start over
- Check passes immediately → you're checking something that already exists
- Can't write a check → maybe you don't understand what the script should produce yet
