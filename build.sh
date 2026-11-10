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

echo "=== 3. Pre-warming Embedding Model ==="
cd backend
python -c "from app.embeddings.vectorizer import get_embedding_engine; e = get_embedding_engine(); print(f'Model ready. Dimension: {e.dimension}')"
cd ..

echo "=== Build Complete! Ready to serve. ==="
