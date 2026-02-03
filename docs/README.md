# Restaurant Discovery Agent - AgentCore Runtime

Phase 1: Restaurant Search and Recommendation with LangGraph + Memory

## Architecture

- **Framework**: LangGraph for workflow orchestration
- **Runtime**: AWS Bedrock AgentCore
- **Memory**: AgentCore Memory (30-day retention)
- **Tools**: MCP Gateway (fetchRestaurantDetails, fetchRestaurantDetailsById)

## Production Patterns Implemented

✅ **Idempotency**: All tool calls include `requestId = f"{correlation_id}_search_{attempt}"`  
✅ **Circuit Breaker**: Max 3 retries with exponential backoff (2^attempt seconds)  
✅ **Timeout**: 5-second hard limit on MCP tool calls  
✅ **Cost Optimization**: Nova Lite for search operations  
✅ **Memory Storage**: Actor-based isolation with 30-day retention  
✅ **Error Handling**: Graceful fallbacks and error messages  

## File Structure

```
restaurant_agent_runtime/
├── __init__.py                 # Package initialization
├── restaurant_workflow.py      # Main LangGraph workflow (DEPLOYABLE)
├── config.py                   # Configuration loader
├── requirements.txt            # Dependencies
├── test_workflow.py            # Local testing script
└── README.md                   # This file
```

## Workflow

```
User Query
    ↓
Entry Router (Intent Detection)
    ↓
    ├─→ "search" → Restaurant Finder Agent → Save Memory → END
    └─→ "history" → Retrieve Memory → END
```

## Configuration

Set environment variables or use `agentcore-gateway-config.json`:

```bash
export AWS_REGION="us-east-1"
export GATEWAY_URL="https://restaurantappgatewaymi99khe1-tmnyzeshe6.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
export MEMORY_ID="your-memory-id"
export COGNITO_CLIENT_ID="6u5ven1dru18pvpdn00nnlrop"
export COGNITO_CLIENT_SECRET="your-secret"
export COGNITO_TOKEN_ENDPOINT="https://agentcore-d9eb5364.auth.us-east-1.amazoncognito.com/oauth2/token"
```

## Local Testing

```bash
cd restaurant_agent_runtime
python test_workflow.py
```

## Deployment to AgentCore Runtime

### Option 1: Using Starter Toolkit (Recommended)

```python
from bedrock_agentcore_starter_toolkit.notebook import Runtime

runtime = Runtime()
runtime.configure(
    entrypoint="restaurant_agent_runtime/restaurant_workflow.py",
    requirements_file="restaurant_agent_runtime/requirements.txt",
    agent_name="restaurant_discovery_agent",
    auto_create_ecr=True,
    execution_role="arn:aws:iam::ACCOUNT:role/AgentCoreRole"
)
runtime.launch()
```

### Option 2: Manual Docker Deployment

```bash
# Build Docker image
docker build -t restaurant-agent:latest .

# Tag for ECR
docker tag restaurant-agent:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/restaurant-agent:latest

# Push to ECR
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/restaurant-agent:latest

# Deploy to AgentCore Runtime
aws bedrock-agentcore create-agent \
  --agent-name restaurant-discovery-agent \
  --image-uri ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/restaurant-agent:latest \
  --execution-role-arn arn:aws:iam::ACCOUNT:role/AgentCoreRole
```

## Usage Examples

### Search Restaurants

```python
payload = {
    "prompt": "Find Italian restaurants in New York",
    "user_id": "user_123",
    "session_id": "session_001",
    "search_params": {
        "city": "New York",
        "cuisine": "Italian"
    }
}

response = runtime.invoke(payload=payload)
```

### Retrieve History

```python
payload = {
    "prompt": "Show me my previous searches",
    "user_id": "user_123",
    "session_id": "session_001"
}

response = runtime.invoke(payload=payload)
```

## Response Format

```json
{
  "correlation_id": "req_abc123",
  "intent": "search",
  "restaurant_results": [
    {
      "restaurantId": "rest_001",
      "name": "Italian Bistro",
      "cuisine": "Italian",
      "rating": 4.5
    }
  ],
  "final_response": "Found 10 restaurants:\n1. Italian Bistro - Italian - Rating: 4.5\n...",
  "memory_status": "saved",
  "status": "success"
}
```

## Next Steps (Phase 2)

- [ ] Add Booking Agent with SAGA pattern
- [ ] Implement payment processing with compensation
- [ ] Add HITL for large group bookings (>10 guests)
- [ ] Implement prompt caching for cost optimization
- [ ] Add PII scrubbing before memory storage

## Cost Estimates

- **Intent Classification**: Nova Micro ($0.00015/1K tokens)
- **Restaurant Search**: Nova Lite ($0.0006/1K tokens)
- **MCP Tool Calls**: ~$0.001 per fetchRestaurantDetails
- **Memory Storage**: Included in AgentCore

**Estimated cost per search**: ~$0.002
