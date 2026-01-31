#!/bin/bash
# Local Testing Guide - Step by Step

echo "🚀 Restaurant Booking System - Local Testing"
echo "=============================================="
echo ""

# Step 1: Install uv if needed
echo "Step 1: Checking uv installation..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed"
else
    echo "✅ uv already installed: $(uv --version)"
fi

echo ""
echo "Step 2: Starting development server..."
echo "⚠️  IMPORTANT: Keep this terminal window open!"
echo ""
echo "Run this command in THIS terminal:"
echo "  agentcore dev"
echo ""
echo "Then open a NEW terminal and run:"
echo "  agentcore invoke --dev \"Find Italian restaurants in New York\""
echo ""
echo "Press Enter to start the dev server..."
read

agentcore dev
