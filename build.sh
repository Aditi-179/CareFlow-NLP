#!/usr/bin/env bash
set -o errexit

echo "=== 1. Building React Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== 2. Installing Backend Python Dependencies ==="
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "=== Build Complete! Ready to serve. ==="

