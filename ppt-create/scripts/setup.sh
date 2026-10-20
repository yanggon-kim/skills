#!/usr/bin/env bash
# Installs the deck tool chain into a work folder (never into the skill folder):
#   <work>/node_modules/pptxgenjs   (npm, pinned 3.12.0)
#   <work>/venv                     (python-pptx, lxml, Pillow, beautifulsoup4, defusedxml)
# Usage: bash setup.sh [WORK]        (default: ./.deck_work)
# Re-running is cheap: what is already installed is kept. Prints the two paths the other scripts need.
set -euo pipefail
WORK="$(realpath -m "${1:-.deck_work}")"
mkdir -p "$WORK"

if ! command -v node >/dev/null || ! command -v npm >/dev/null; then
  echo "node and npm are needed (Node 18 or newer)" >&2; exit 1
fi
if [ ! -f "$WORK/node_modules/pptxgenjs/package.json" ]; then
  [ -f "$WORK/package.json" ] || printf '{"name":"deck-work","private":true}\n' > "$WORK/package.json"
  (cd "$WORK" && npm install --no-audit --no-fund --silent pptxgenjs@3.12.0)
fi

if [ ! -x "$WORK/venv/bin/python" ]; then
  python3 -m venv "$WORK/venv"
fi
"$WORK/venv/bin/python" - 2>/dev/null <<'EOF' || "$WORK/venv/bin/pip" install --quiet python-pptx lxml Pillow beautifulsoup4 defusedxml
import pptx, lxml, PIL, bs4, defusedxml  # noqa: F401
EOF

node -e "require('$WORK/node_modules/pptxgenjs'); console.log('pptxgenjs', require('$WORK/node_modules/pptxgenjs/package.json').version)"
"$WORK/venv/bin/python" -c "import pptx, lxml, PIL, bs4; print('python-pptx', pptx.__version__)"
for t in soffice pdftoppm; do command -v "$t" >/dev/null || echo "note: $t not found (needed only for render.py)"; done
[ -f /usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf ] || [ -n "$(fc-list 2>/dev/null | grep -i 'Liberation Sans')" ] \
  || echo "note: Liberation Sans not found (deck_qa.py's fit check and the renders need it)"
echo "WORK=$WORK"
echo "PY=$WORK/venv/bin/python"
