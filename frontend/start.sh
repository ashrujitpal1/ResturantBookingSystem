#!/bin/bash
# Quick start script for Restaurant Booking System Frontend

echo "🍽️  Restaurant Booking System - Frontend Setup"
echo "=============================================="
echo ""

# Check if in frontend directory
if [ ! -f "app.py" ]; then
    echo "📁 Navigating to frontend directory..."
    cd frontend
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured!"
    echo "Run: aws configure"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Streamlit app..."
echo "   App will open at: http://localhost:8501"
echo ""

streamlit run app.py
