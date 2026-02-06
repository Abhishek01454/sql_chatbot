#!/bin/bash

# Core AI Chatbot - Clean Build & Deploy Script
# This script ensures all caches are cleared before deployment

echo "🚀 Core AI Chatbot - Clean Build & Deploy"
echo "=========================================="

# Navigate to frontend directory
cd frontend

echo ""
echo "📦 Step 1: Cleaning build caches..."
rm -rf build
rm -rf dist
rm -rf .vercel
rm -rf node_modules/.cache
rm -rf node_modules/.vite
echo "✅ Caches cleared"

echo ""
echo "📥 Step 2: Installing dependencies..."
npm install
echo "✅ Dependencies installed"

echo ""
echo "🔨 Step 3: Building production bundle..."
npm run build
echo "✅ Build complete"

echo ""
echo "🚀 Step 4: Deploying to Vercel..."
vercel --prod --force

echo ""
echo "=========================================="
echo "✅ Deployment complete!"
echo ""
echo "🔍 Please verify:"
echo "   - Scrollbar is gray (not blue)"
echo "   - Sidebar buttons are gray (not blue)"
echo "   - Settings modal is gray (not blue)"
echo "   - Input field focus is gray (not blue)"
echo "   - NO blue colors anywhere"
echo ""
echo "💡 Tip: Clear browser cache (Ctrl+Shift+Delete) if colors look wrong"
echo ""
