#!/bin/bash
# Setup memory store before deployment

set -e

REGION="us-east-1"
MEMORY_NAME="restaurant-booking-memory"

echo "🧠 Setting up memory store..."

# Check if memory exists
EXISTING_MEMORY=$(aws bedrock-agentcore list-memories --region $REGION 2>/dev/null | \
    jq -r ".memories[] | select(.memoryName==\"$MEMORY_NAME\") | .memoryId" || echo "")

if [ -n "$EXISTING_MEMORY" ]; then
    echo "✅ Memory already exists: $EXISTING_MEMORY"
    MEMORY_ID=$EXISTING_MEMORY
    MEMORY_ARN="arn:aws:bedrock-agentcore:$REGION:$(aws sts get-caller-identity --query Account --output text):memory/$MEMORY_ID"
else
    echo "Creating memory store..."
    MEMORY_OUTPUT=$(aws bedrock-agentcore create-memory \
        --memory-name $MEMORY_NAME \
        --retention-days 30 \
        --region $REGION \
        --output json 2>/dev/null || echo "{}")
    
    MEMORY_ID=$(echo $MEMORY_OUTPUT | jq -r '.memoryId // empty')
    MEMORY_ARN=$(echo $MEMORY_OUTPUT | jq -r '.memoryArn // empty')
    
    if [ -n "$MEMORY_ID" ]; then
        echo "✅ Memory created: $MEMORY_ID"
    else
        echo "❌ Failed to create memory"
        exit 1
    fi
fi

# Update config
echo "Updating .bedrock_agentcore.yaml..."
python3 << EOF
import yaml

with open('.bedrock_agentcore.yaml', 'r') as f:
    config = yaml.safe_load(f)

default_agent = config.get('default_agent')
if default_agent and default_agent in config.get('agents', {}):
    config['agents'][default_agent]['memory']['memory_id'] = '$MEMORY_ID'
    config['agents'][default_agent]['memory']['memory_arn'] = '$MEMORY_ARN'

with open('.bedrock_agentcore.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("✅ Config updated")
EOF

echo ""
echo "✅ Memory setup complete!"
echo "   Memory ID: $MEMORY_ID"
echo ""
echo "Add to environment:"
echo "export MEMORY_ID=\"$MEMORY_ID\""
