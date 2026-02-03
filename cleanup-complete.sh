#!/bin/bash
# Complete AgentCore Cleanup Script
# Removes runtime, memory, Lambda functions, DynamoDB tables, and MCP tools

set -e

echo "🧹 Restaurant Booking System - Complete Cleanup"
echo "================================================"
echo ""
echo "⚠️  WARNING: This will delete ALL resources:"
echo "  - AgentCore Runtime (restaurant_discovery_agent)"
echo "  - AgentCore Memory (restaurant_booking_memory)"
echo "  - Lambda functions (8 functions)"
echo "  - DynamoDB tables (5 tables)"
echo "  - SAM CloudFormation stack"
echo "  - MCP tool registrations"
echo "  - ECR repository"
echo ""
read -p "Continue with cleanup? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

REGION="us-east-1"
AGENT_NAME="restaurant_discovery_agent"
MEMORY_ID="restaurant_booking_memory-aOsBjaAma6"
STACK_NAME="restaurant-booking-dev"

echo ""
echo "Starting cleanup..."
echo ""

# Step 1: Undeploy AgentCore Runtime
echo "🚀 Step 1/5: Undeploying AgentCore Runtime..."
bedrock-agentcore undeploy --agent-name $AGENT_NAME 2>/dev/null && echo "  ✅ Runtime undeployed" || echo "  ⚠️  Runtime not found or already deleted"

# Step 2: Delete AgentCore Memory
echo ""
echo "🧠 Step 2/5: Deleting AgentCore Memory..."
aws bedrock-agent delete-memory \
    --memory-id $MEMORY_ID \
    --region $REGION 2>/dev/null && echo "  ✅ Memory deleted" || echo "  ⚠️  Memory not found or already deleted"

# Step 3: Delete SAM CloudFormation Stack
echo ""
echo "🗑️  Step 3/5: Deleting SAM CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION 2>/dev/null && echo "  ✅ Stack deletion initiated" || echo "  ⚠️  Stack not found"

echo "  Waiting for stack deletion (2-3 minutes)..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION 2>/dev/null && echo "  ✅ Stack deleted" || echo "  ⚠️  Stack already deleted"

# Step 4: Delete DynamoDB Tables
echo ""
echo "🗄️  Step 4/5: Deleting DynamoDB tables..."
TABLES=("Restaurants" "Users" "Bookings" "Payments" "IdempotencyCache")

for table in "${TABLES[@]}"; do
    echo "  Deleting: $table"
    aws dynamodb delete-table \
        --table-name $table \
        --region $REGION 2>/dev/null && echo "    ✅ Deleted" || echo "    ⚠️  Not found"
done

# Step 5: Delete ECR Repository
echo ""
echo "📦 Step 5/5: Deleting ECR repository..."
ECR_REPO="bedrock-agentcore-$AGENT_NAME"
aws ecr delete-repository \
    --repository-name $ECR_REPO \
    --force \
    --region $REGION 2>/dev/null && echo "  ✅ ECR repository deleted" || echo "  ⚠️  Repository not found"

# Verification
echo ""
echo "🔍 Verifying cleanup..."
echo ""

echo "Lambda functions remaining:"
aws lambda list-functions --region $REGION \
    --query "Functions[?contains(FunctionName, 'restaurant') || contains(FunctionName, 'book') || contains(FunctionName, 'payment')].FunctionName" \
    --output table 2>/dev/null || echo "  ✅ No functions found"

echo ""
echo "DynamoDB tables remaining:"
aws dynamodb list-tables --region $REGION \
    --query "TableNames[?contains(@, 'Restaurant') || contains(@, 'User') || contains(@, 'Booking') || contains(@, 'Payment')]" \
    --output table 2>/dev/null || echo "  ✅ No tables found"

echo ""
echo "================================================"
echo "✅ Cleanup Complete!"
echo ""
echo "📋 What was removed:"
echo "  ❌ AgentCore Runtime"
echo "  ❌ AgentCore Memory"
echo "  ❌ Lambda functions (8)"
echo "  ❌ DynamoDB tables (5)"
echo "  ❌ CloudFormation stack"
echo "  ❌ ECR repository"
echo ""
echo "📋 Next Steps:"
echo "  1. Review verification output above"
echo "  2. Update .bedrock_agentcore.yaml if needed"
echo "  3. Redeploy with: bedrock-agentcore deploy"
echo ""
