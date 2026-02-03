#!/bin/bash
# Deploy Restaurant Booking System to AgentCore

set -e

echo "🚀 Deploying Restaurant Booking System to AgentCore"
echo "=================================================="

# Step 1: Create AgentCore Memory (if not exists)
echo ""
echo "📝 Step 1: Create AgentCore Memory"
echo "----------------------------------"
read -p "Do you need to create a new Memory resource? (y/n): " create_memory

if [ "$create_memory" = "y" ]; then
    echo "Creating Memory resource..."
    MEMORY_ID=$(agentcore memory create \
        --name restaurant_booking_memory \
        --description "State persistence for restaurant booking system" \
        --output json | jq -r '.memoryId')
    
    echo "✅ Memory created: $MEMORY_ID"
    
    # Add semantic strategy
    echo "Adding semantic strategy..."
    agentcore memory add-strategy \
        --memory-id $MEMORY_ID \
        --strategy-type semantic \
        --name restaurant_context
    
    echo "✅ Strategy added"
else
    read -p "Enter existing Memory ID: " MEMORY_ID
fi

# Step 2: Update .env.agentcore
echo ""
echo "📝 Step 2: Update Configuration"
echo "--------------------------------"
sed -i.bak "s/MEMORY_ID=.*/MEMORY_ID=$MEMORY_ID/" .env.agentcore
echo "✅ Updated .env.agentcore with MEMORY_ID=$MEMORY_ID"

# Step 3: Deploy to AgentCore
echo ""
echo "📝 Step 3: Deploy Application"
echo "------------------------------"
echo "Deploying with AgentCore Memory enabled..."

agentcore deploy \
    --name restaurant_booking_agent \
    --runtime-file src/workflows/restaurant_workflow.py \
    --env-file .env.agentcore \
    --timeout 300

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Configuration:"
echo "  - Memory ID: $MEMORY_ID"
echo "  - State Persistence: AgentCore Memory"
echo "  - Multi-turn conversations: Enabled"
echo ""
echo "Test your deployment:"
echo "  agentcore invoke --prompt 'Find Italian restaurants in Boston'"
