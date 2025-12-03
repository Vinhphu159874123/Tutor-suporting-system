#!/bin/bash

# Script để deploy frontend lên Vercel

echo "🚀 Deploying frontend to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Deploy to Vercel
echo "📦 Deploying..."
vercel --prod

echo "✅ Deployment complete!"
echo "📝 Don't forget to set environment variable on Railway:"
echo "   ALLOWED_ORIGINS=https://tutor-suporting-system.vercel.app,https://*.vercel.app,http://localhost:3000"
