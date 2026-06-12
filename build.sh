#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "========================================="
echo "Building Frontend (Next.js)"
echo "========================================="
cd frontend
npm install
npm run build
cd ..

echo "========================================="
echo "Building Backend (FastAPI)"
echo "========================================="
cd backend
pip install -r requirements.txt
echo "Build complete."
