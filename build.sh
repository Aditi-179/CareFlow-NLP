#!/usr/bin/env bash
set -o errexit

echo "=== 1. Building React Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== 2. Installing Backend Python Dependencies (CPU-Optimized) ==="
cd backend
pip install --upgrade pip
# Install lightweight PyTorch CPU wheel to prevent heavy CUDA downloads on Render
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
cd ..

echo "=== Build Complete! Ready to serve. ==="
