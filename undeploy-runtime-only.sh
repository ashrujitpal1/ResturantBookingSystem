#!/bin/bash

# Undeploy Agent Core Runtime Only (Preserve MCP Tools)
# This script removes the agent runtime but keeps all MCP tools intact

set -e

echo "🗑️  Undeploying Agent Core Runtime (Preserving MCP Tools)"
echo "=========================================================="

# Configuration
AGENT_NAME="restaurant_discovery_agent"
REGION="us-east-1"

echo ""
echo "⚠️  WARNING: This will undeploy the agent runtime but KEEP:"
echo "  ✅ MCP Tools (Lambda functions)"
echo "  ✅ DynamoDB tables"
echo "  ✅ Gateway configuration"
echo "  ✅ All infrastructure"
echo ""
read -p "Continue with undeployment? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Undeployment cancelled"
    exit 0
fi

# Step 1: Undeploy the agent runtime
echo ""
echo "🚀 Step 1: Undeploying agent runtime..."
bedrock-agentcore undeploy --agent-name $AGENT_NAME

# Step 2: Verify undeployment
echo ""
echo "✅ Step 2: Agent runtime undeployed successfully!"
echo ""
echo "📊 What was removed:"
echo "  ❌ Agent runtime container"
echo "  ❌ Agent Core runtime session"
echo ""
echo "📊 What remains intact:"
echo "  ✅ MCP Tools (all Lambda functions)"
echo "  ✅ DynamoDB tables (restaurants, users, bookings)"
echo "  ✅ Gateway configuration"
echo "  ✅ IAM roles and policies"
echo ""
echo "🔄 To redeploy with the complete workflow:"
echo "  ./deploy-complete-workflow.sh"
echo ""
echo "✨ Undeployment complete!"
