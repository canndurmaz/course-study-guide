#!/usr/bin/env bash
# Build the course study guide into <COURSE>_StudyGuide.pdf
set -euo pipefail
COURSE="${COURSE:-Course}"   # set your course code here, e.g. ME521
cd "$(dirname "$0")"
mkdir -p build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
cp build/main.pdf ${COURSE}_StudyGuide.pdf
echo "Built $(pwd)/${COURSE}_StudyGuide.pdf"
