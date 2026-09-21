#!/usr/bin/env bash
# init_workspace.sh — bootstrap a new GPU-research project workspace.
#
# Usage:
#   init_workspace.sh <workload-slug>
#
# Creates $PWD/02_projects/<slug>_<YYMMDD>/ with the full directory tree,
# templates the two top-level trackers (PROGRESS.md, final_solution_candidates.md),
# and emits gpu_spec.json from nvidia-smi.
#
# Idempotent: refuses to clobber an existing workspace.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <workload-slug>" >&2
  exit 1
fi

slug="$1"
date_tag="$(date +%y%m%d)"
project_dir="$PWD/02_projects/${slug}_${date_tag}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
skill_root="$(cd -- "$script_dir/.." &> /dev/null && pwd)"

if [[ -d "$project_dir" ]]; then
  echo "error: $project_dir already exists. Refusing to clobber." >&2
  echo "       Pick a different slug, or operate inside the existing workspace." >&2
  exit 1
fi

# Create the directory tree.
mkdir -p "$project_dir"/{00_target_workload,01_workload_analysis,02_related_work,03_solutions,04_simulation_setup,05_implementations,06_evaluation,07_paper}

# Seed the two top-level trackers from templates.
cp "$skill_root/assets/templates/progress_md_template.md" "$project_dir/PROGRESS.md"
cp "$skill_root/assets/templates/final_solution_candidates_template.md" "$project_dir/final_solution_candidates.md"

# Auto-detect GPU spec.
if command -v python3 >/dev/null 2>&1 && command -v nvidia-smi >/dev/null 2>&1; then
  python3 "$script_dir/detect_gpu.py" > "$project_dir/gpu_spec.json"
  echo "GPU spec → $project_dir/gpu_spec.json"
else
  echo "warning: nvidia-smi or python3 not found; gpu_spec.json not generated." >&2
  echo "         Step 2 and Step 5 will need manual GPU spec input." >&2
fi

# Stamp the project name + date into PROGRESS.md.
sed -i "s|<workload-slug>|$slug|g; s|<YYMMDD>|$date_tag|g" "$project_dir/PROGRESS.md"

echo "Initialized workspace at: $project_dir"
echo
echo "Next steps:"
echo "  1. Read $project_dir/PROGRESS.md to see the 8 pending steps."
echo "  2. Begin Step 1: Target Workload Search."
echo "     See: $skill_root/references/step-01-target-workload.md"
