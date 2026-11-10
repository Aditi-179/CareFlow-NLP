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

echo "=== 3. Pre-downloading NLTK Data ==="
cd backend
python -c "
import nltk, os
nltk_dir = os.path.expanduser('~/nltk_data')
os.makedirs(nltk_dir, exist_ok=True)
nltk.download('punkt', download_dir=nltk_dir, quiet=True)
nltk.download('punkt_tab', download_dir=nltk_dir, quiet=True)
nltk.download('stopwords', download_dir=nltk_dir, quiet=True)
print('NLTK data ready.')
"
cd ..

echo "=== Build Complete! Ready to serve. ==="
