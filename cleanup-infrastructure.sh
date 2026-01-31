#!/bin/bash
# Complete Infrastructure Cleanup Script
# This removes all existing resources to start fresh

set -e

echo "🧹 Restaurant Booking System - Complete Cleanup"
echo "================================================"
echo ""
echo "⚠️  WARNING: This will delete ALL resources including:"
echo "  - Lambda functions (8 functions)"
echo "  - DynamoDB tables (5 tables including IdempotencyCache)"
echo "  - SAM CloudFormation stack"
echo "  - MCP tool registrations in AgentCore Gateway"
echo ""
# Auto-approve mode
confirm="yes"
echo "Auto-approve mode: proceeding with cleanup..."

REGION="us-east-1"
STACK_NAME="restaurant-booking-dev"
GATEWAY_ID="restaurantappgatewayuop91kvy-xg33kutnwg"

echo ""
echo "Starting cleanup..."
echo ""

# Step 1: Unregister MCP tools from AgentCore Gateway
echo "📤 Step 1/3: Unregistering MCP tools from AgentCore Gateway..."
echo ""

TOOLS=(
    "fetch-restaurant-details-target"
    "fetch-restaurant-by-id-target"
    "search-user-details-target"
    "register-user-target"
    "token-amount-calculation-target"
    "book-a-table-target"
    "payment-api-target"
    "book-restaurant-target"
)

for tool in "${TOOLS[@]}"; do
    echo "  Unregistering: $tool"
    aws bedrock-agent delete-agent-action-group \
        --agent-id $GATEWAY_ID \
        --action-group-id $tool \
        --region $REGION 2>/dev/null && echo "    ✅ Unregistered" || echo "    ⚠️  Not found or already deleted"
done

# Step 2: Delete SAM CloudFormation Stack (includes Lambda functions)
echo ""
echo "🗑️  Step 2/3: Deleting SAM CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION 2>/dev/null && echo "  ✅ Stack deletion initiated" || echo "  ⚠️  Stack not found"

echo "  Waiting for stack deletion to complete (this may take 2-3 minutes)..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION 2>/dev/null && echo "  ✅ Stack deleted successfully" || echo "  ⚠️  Stack already deleted or not found"

# Step 3: Delete DynamoDB Tables
echo ""
echo "🗄️  Step 3/3: Deleting DynamoDB tables..."
echo ""

TABLES=(
    "Restaurants"
    "Users"
    "Bookings"
    "Payments"
    "IdempotencyCache"
)

for table in "${TABLES[@]}"; do
    echo "  Deleting table: $table"
    aws dynamodb delete-table \
        --table-name $table \
        --region $REGION 2>/dev/null && echo "    ✅ Deleted" || echo "    ⚠️  Not found or already deleted"
done

echo ""
echo "⏳ Waiting for tables to be fully deleted (30 seconds)..."
sleep 30

# Verification
echo ""
echo "🔍 Verifying cleanup..."
echo ""

echo "Lambda functions remaining:"
aws lambda list-functions --region $REGION \
    --query "Functions[?contains(FunctionName, 'restaurant') || contains(FunctionName, 'book') || contains(FunctionName, 'payment') || contains(FunctionName, 'user') || contains(FunctionName, 'token')].FunctionName" \
    --output table || echo "  ✅ No Lambda functions found"

echo ""
echo "DynamoDB tables remaining:"
aws dynamodb list-tables --region $REGION \
    --query "TableNames[?contains(@, 'Restaurant') || contains(@, 'User') || contains(@, 'Booking') || contains(@, 'Payment') || contains(@, 'Idempotency')]" \
    --output table || echo "  ✅ No tables found"

echo ""
echo "================================================"
echo "✅ Cleanup Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Review the verification output above"
echo "  2. Run: ./setup-fresh-infrastructure.sh"
echo "  3. Follow the step-by-step deployment guide"
echo ""
