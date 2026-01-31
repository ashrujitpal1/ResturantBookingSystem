#!/bin/bash
# Quick redeploy after code changes

echo "🔄 Redeploying Restaurant Booking System..."
echo ""

echo "📝 Changes made:"
echo "  - Fixed restaurant_finder.py to extract city/cuisine from prompt"
echo ""

echo "🚀 Deploying..."
agentcore deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🧪 Test with:"
echo "  agentcore invoke 'Can you find an Indian restaurant in New York'"
