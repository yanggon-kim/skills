# Project Directory Structure Template

Copy this structure when starting a new workload analysis project.

```
project_root/
├── venv/                           # Python virtual environment
│   └── ...
│
├── models/                         # Model source code and weights
│   ├── <model_repo>/               # Git clone of the model repository
│   └── weights/
│       └── <model_name>/           # Downloaded model weights
│
├── scripts/                        # Profiling and analysis scripts
│   ├── profile_workload.py         # Main profiling script (adapt from skill template)
│   ├── ncu_profile_workload.py     # NCU-targeted script (adapt from skill template)
│   ├── parse_ncu_results.py        # NCU CSV parser (copy from skill)
│   ├── parse_ncu_detailed.py       # Detailed NCU analysis (copy from skill)
│   ├── plot_roofline.py            # Roofline plot generator (copy from skill)
│   ├── plot_timeline.py            # Timeline visualization (copy from skill)
│   ├── run_nsys_profile.sh         # nsys wrapper (adapt from skill)
│   └── run_ncu_profile.sh          # ncu wrapper (adapt from skill)
│
├── profiles/                       # Binary profile files (DO NOT commit to git)
│   ├── *.nsys-rep                  # NSight Systems profiles
│   └── *.ncu-rep                   # NSight Compute profiles (can be 100MB-1GB)
│
├── traces/                         # Chrome trace JSON files
│   └── trace_bs*.json              # PyTorch Profiler Chrome traces
│
└── analysis/                       # All analysis outputs
    ├── profiling_results_*.json    # Raw timing data from profiling script
    ├── ncu_analysis_*.json         # Parsed NCU kernel summaries
    ├── ncu_detailed_*.json         # Detailed NCU metrics (occupancy, stalls)
    ├── kernel_summary_*.txt        # PyTorch Profiler kernel tables
    ├── *_roofline.png/pdf          # Roofline plots
    ├── *_timeline.png/pdf          # Execution timeline visualizations
    ├── *_kernel_breakdown.png/pdf  # Kernel category pie charts
    ├── *_profiling_results.md      # Main analysis report
    └── *_bottleneck_analysis.md    # Bottleneck deep-dive report
```

## Key Principles

1. **Separate concerns**: scripts, raw profiles, and analysis outputs go in different directories
2. **Don't commit profiles**: .nsys-rep and .ncu-rep files can be huge — add to .gitignore
3. **Version your scripts**: profiling scripts should be committed
4. **Name outputs consistently**: prefix with the workload name (e.g., `groot_roofline.png`)
5. **JSON for data, Markdown for reports**: machine-readable data in JSON, human-readable in Markdown
