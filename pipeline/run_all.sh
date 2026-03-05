#!/usr/bin/env bash
#
# Run the full pipeline: inference → detection → report
#
# Usage:
#   bash pipeline/run_all.sh                  # Full run (all models, BF16)
#   bash pipeline/run_all.sh --quantize 4bit  # 4-bit quantized (lower VRAM)
#   bash pipeline/run_all.sh --model qwen2.5-coder-7b  # Single model
#

set -euo pipefail
cd "$(dirname "$0")/.."

EXTRA_ARGS="${@}"

echo "============================================"
echo "  Code Smell Detection Pipeline"
echo "============================================"
echo ""
echo "Step 1: Check GPU availability"
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
echo ""

echo "Step 2: Run inference on all models"
python3 -m pipeline.run_inference --resume ${EXTRA_ARGS}
echo ""

echo "Step 3: Run code smell detection"
python3 -m pipeline.run_detection ${EXTRA_ARGS}
echo ""

echo "============================================"
echo "  Pipeline complete!"
echo "  Results in: outputs/"
echo "============================================"
