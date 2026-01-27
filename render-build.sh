#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting Build Process..."

# 1. Install Python Dependencies
echo "📦 Installing Backend Dependencies..."
pip install -r backend/requirements.txt

# 2. Install Node.js Dependencies (Frontend)
echo "📦 Installing Frontend Dependencies..."
# Ensure pnpm is available
npm install -g pnpm

cd frontend
pnpm install

# 3. Build Frontend
echo "🏗️ Building Frontend..."
pnpm build

# 4. Return to root
cd ..

echo "✅ Build Complete!"
