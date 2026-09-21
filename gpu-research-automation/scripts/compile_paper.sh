#!/usr/bin/env bash
# compile_paper.sh — build a single paper PDF using latexmk + ACM template.
#
# Usage:
#   compile_paper.sh <paper_dir>
#
# The paper_dir must contain paper.tex (or sample-sigconf.tex) and all
# necessary template files (acmart.cls, ACM-Reference-Format.bst, etc.).
# Output: paper_dir/paper.pdf.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <paper_dir>" >&2
  exit 1
fi

paper_dir="$(realpath "$1")"

if [[ ! -d "$paper_dir" ]]; then
  echo "error: $paper_dir is not a directory." >&2
  exit 2
fi

# Find the main .tex file. Prefer paper.tex; fall back to sample-sigconf.tex.
main_tex=""
for candidate in paper.tex sample-sigconf.tex; do
  if [[ -f "$paper_dir/$candidate" ]]; then
    main_tex="$candidate"
    break
  fi
done

if [[ -z "$main_tex" ]]; then
  echo "error: no paper.tex or sample-sigconf.tex found in $paper_dir." >&2
  exit 3
fi

if ! command -v latexmk >/dev/null 2>&1; then
  echo "error: latexmk not found. Install with 'apt install latexmk' or equivalent." >&2
  exit 4
fi

echo "Building $paper_dir/$main_tex …"

cd "$paper_dir"
latexmk -pdf -interaction=nonstopmode -halt-on-error "$main_tex" || {
  echo "error: latexmk failed. Check the .log file:" >&2
  echo "       $paper_dir/${main_tex%.tex}.log" >&2
  exit 5
}

# Rename output to paper.pdf if it isn't already.
out_pdf="${main_tex%.tex}.pdf"
if [[ "$out_pdf" != "paper.pdf" ]]; then
  mv "$out_pdf" paper.pdf
fi

# Page count check.
if command -v pdfinfo >/dev/null 2>&1; then
  pages="$(pdfinfo paper.pdf | awk '/^Pages/ { print $2 }')"
  echo "Built $paper_dir/paper.pdf (${pages} pages)."
else
  echo "Built $paper_dir/paper.pdf."
fi
