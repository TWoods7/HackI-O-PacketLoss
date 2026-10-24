#!/usr/bin/env bash
# Download the AEP challenge data and extract it into data/extracted/.
# Usage (from repo root): bash scripts/get_data.sh
set -euo pipefail

BASE="https://github.com/hackohio/aep_challenge_hack26/raw/HEAD"
cd "$(dirname "$0")/.."
mkdir -p data/raw data/extracted/Data1 data/extracted/Data2 data/extracted/matched_upstream

for f in Data1.zip Data2.zip matched_upstream.zip; do
  [ -f "data/raw/$f" ] || curl -fsSL -o "data/raw/$f" "$BASE/data/raw/$f"
done
[ -f data/raw/Install_Labor_HackOHIO.xlsx ] || curl -fsSL -o data/raw/Install_Labor_HackOHIO.xlsx "$BASE/data/Install_Labor_HackOHIO.xlsx"
[ -f data/raw/structure_drawings.pdf ] || curl -fsSL -o data/raw/structure_drawings.pdf "$BASE/docs/structure_drawings.pdf"

unzip -qn data/raw/Data1.zip -d data/extracted/Data1
unzip -qn data/raw/Data2.zip -d data/extracted/Data2
unzip -qn data/raw/matched_upstream.zip -d data/extracted/matched_upstream

echo "Done. Shapefiles in data/extracted/Data1 and Data2, topology in data/extracted/matched_upstream."
