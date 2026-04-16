#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3.11 -m PyInstaller \
  --name LotteryEdgeLab \
  --onefile \
  --windowed \
  --clean \
  --noconfirm \
  --paths src \
  --collect-all customtkinter \
  src/lottery_edge_lab/desktop_app.py

echo "Build complete: dist/LotteryEdgeLab"
