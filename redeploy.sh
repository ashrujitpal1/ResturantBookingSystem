#!/bin/bash
# Quick redeploy after code changes

echo "🔄 Redeploying Restaurant Booking System (LLM-Based Refactoring)..."
echo ""

echo "📝 Changes made:"
echo "  ✅ Replaced regex patterns with LLM-based extraction"
echo "  ✅ Added llm_helpers.py for intent classification & entity extraction"
echo "  ✅ Refactored entry_router_node to use LLM for intent detection"
echo "  ✅ Refactored restaurant_finder_node to use LLM for search params"
echo "  ✅ Refactored booking_validation_node to use LLM for booking details"
echo "  ✅ Fixed context preservation for 'yes for me on tomorrow' flow"
echo ""

echo "🚀 Deploying..."
agentcore deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🧪 Test with:"
echo "  agentcore invoke 'Find Indian restaurants in New York'"
echo "  agentcore invoke 'yes for me on tomorrow'  # After seeing results"
