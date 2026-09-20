#!/usr/bin/env bash
# Rebuild the OpenVVVF sponsorship materials (PDF + raster previews).
# Usage: Docs/White-Papers/build.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHROMIUM="${CHROMIUM:-chromium}"

render () { # $1 = doc dir, $2 = html name, $3 = pdf name
  "$CHROMIUM" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
    --virtual-time-budget=10000 \
    --print-to-pdf="$1/$3" "file://$1/$2"
}

# --- One-Pager ---
ONE="$HERE/One-Pager"
render "$ONE" onepager.html OpenVVVF-OnePager.pdf
pdftoppm -png -r 110 -f 1 -l 1 "$ONE/OpenVVVF-OnePager.pdf" "$ONE/preview"
mv -f "$ONE/preview-1.png" "$ONE/preview.png"

# --- Three-Pager ---
THREE="$HERE/Three-Pager"
render "$THREE" threepager.html OpenVVVF-ThreePager.pdf
pdftoppm -png -r 110 "$THREE/OpenVVVF-ThreePager.pdf" "$THREE/preview"

echo "Built:"
ls -la "$ONE/OpenVVVF-OnePager.pdf" "$ONE/preview.png" \
       "$THREE/OpenVVVF-ThreePager.pdf" "$THREE"/preview-*.png
pdfinfo "$ONE/OpenVVVF-OnePager.pdf" | grep -E "Pages|Page size"
pdfinfo "$THREE/OpenVVVF-ThreePager.pdf" | grep -E "Pages|Page size"
