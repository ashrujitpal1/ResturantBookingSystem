# AgentCore Deployment Guide

## Prerequisites

- AWS CLI configured
- AgentCore CLI installed
- DynamoDB tables created (restaurants, users, bookings)
- Lambda functions deployed (MCP tools)

## Deployment Steps

### 1. Create AgentCore Memory Resource

```bash
# Create memory
aws bedrock-agentcore create-memory \
    --name restaurant_booking_memory \
    --description "State persistence for restaurant booking" \
    --region us-east-1

# Note the memoryId from output
# Example: restaurant_booking_memory-aOsBjaAma6
```

**Or use CLI:**
```bash
agentcore memory create \
    --name restaurant_booking_memory \
    --description "State persistence for restaurant booking"
```

### 2. Add Memory Strategy

```bash
# Add semantic strategy for restaurant context
aws bedrock-agentcore add-memory-strategy \
    --memory-id <MEMORY_ID> \
    --strategy-type SEMANTIC \
    --strategy-name restaurant_context
```

### 3. Update Configuration

Edit `.env.agentcore`:
```bash
USE_AGENTCORE_MEMORY=true
MEMORY_ID=restaurant_booking_memory-aOsBjaAma6  # Your actual ID
AWS_REGION=us-east-1
```

### 4. Deploy Application

**Option A: Using deployment script**
```bash
chmod +x deploy_with_memory.sh
./deploy_with_memory.sh
```

**Option B: Manual deployment**
```bash
agentcore deploy \
    --name restaurant_booking_agent \
    --runtime-file src/workflows/restaurant_workflow.py \
    --env USE_AGENTCORE_MEMORY=true \
    --env MEMORY_ID=<your-memory-id> \
    --env AWS_REGION=us-east-1 \
    --timeout 300
```

### 5. Verify Deployment

```bash
# Test search
agentcore invoke \
    --agent restaurant_booking_agent \
    --payload '{"prompt": "Find Italian restaurants in Boston", "session_id": "test-session-12345678901234567890123"}'

# Test multi-turn booking
agentcore invoke \
    --agent restaurant_booking_agent \
    --payload '{"prompt": "Book the first one for 2 people", "session_id": "test-session-12345678901234567890123"}'
```

### 6. Check Memory Storage

```bash
# List memory events
aws bedrock-agentcore list-memory-events \
    --memory-id <MEMORY_ID> \
    --actor-id test-session-12345678901234567890123 \
    --session-id test-session-12345678901234567890123
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_AGENTCORE_MEMORY` | Yes | `false` | Enable AgentCore Memory |
| `MEMORY_ID` | Yes | - | Memory resource ID |
| `AWS_REGION` | Yes | `us-east-1` | AWS region |
| `GATEWAY_URL` | Yes | - | MCP Gateway URL |
| `PROMPT_VERSION` | No | `1.0.0` | Prompt version |

### Memory Configuration

**Memory Type:** Semantic + Episodic
**Storage:** Blob events (JSON)
**TTL:** 30 days (configurable)
**Size Limit:** ~100KB per event

## Testing Multi-turn Conversations

### Test Scenario 1: Search + Book

```bash
SESSION_ID="session-$(uuidgen)"

# Request 1: Search
agentcore invoke \
    --payload "{\"prompt\": \"Find Italian restaurants in Boston\", \"session_id\": \"$SESSION_ID\"}"

# Request 2: Book (references previous search)
agentcore invoke \
    --payload "{\"prompt\": \"Book the first one for 2 people on 2026-03-15 at 19:00\", \"session_id\": \"$SESSION_ID\"}"

# Request 3: Provide details
agentcore invoke \
    --payload "{\"prompt\": \"My name is John Doe, phone 1234567890\", \"session_id\": \"$SESSION_ID\"}"
```

### Test Scenario 2: Session Isolation

```bash
# Session A
agentcore invoke \
    --payload '{"prompt": "Find Indian restaurants", "session_id": "session-A-12345678901234567890123"}'

# Session B
agentcore invoke \
    --payload '{"prompt": "Find Italian restaurants", "session_id": "session-B-12345678901234567890123"}'

# Session A continues (should have Indian context)
agentcore invoke \
    --payload '{"prompt": "Book the first one", "session_id": "session-A-12345678901234567890123"}'
```

## Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/bedrock-agentcore/restaurant_booking_agent --follow
```

### Memory Metrics

```bash
# Check memory usage
aws bedrock-agentcore get-memory-metadata \
    --memory-id <MEMORY_ID>
```

### State Verification

```bash
# List all sessions
aws bedrock-agentcore list-memory-events \
    --memory-id <MEMORY_ID> \
    --max-results 100
```

## Troubleshooting

### Issue 1: Memory Not Found

**Error:** `ResourceNotFoundException: Memory not found`

**Solution:**
```bash
# Verify memory exists
aws bedrock-agentcore get-memory --memory-id <MEMORY_ID>

# Check MEMORY_ID in .env.agentcore
cat .env.agentcore | grep MEMORY_ID
```

### Issue 2: State Not Persisting

**Check:**
```bash
# Verify USE_AGENTCORE_MEMORY is true
agentcore env list | grep USE_AGENTCORE_MEMORY

# Check memory events
aws bedrock-agentcore list-memory-events \
    --memory-id <MEMORY_ID> \
    --actor-id <session_id>
```

### Issue 3: Permission Denied

**Solution:**
```bash
# Add IAM permissions
aws iam attach-role-policy \
    --role-name AgentCoreExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## Rollback

### Disable Memory (Use Local Files)

```bash
# Update environment
agentcore env set USE_AGENTCORE_MEMORY=false

# Redeploy
agentcore deploy --name restaurant_booking_agent
```

### Delete Memory Resource

```bash
aws bedrock-agentcore delete-memory --memory-id <MEMORY_ID>
```

## Cost Estimation

### Memory Operations

- **Write:** $0.0001 per event
- **Read:** $0.00005 per event
- **Storage:** $0.10 per GB-month

### Example: 1000 bookings/day

- Writes: 3000 events/day (search + booking + confirmation)
- Reads: 3000 events/day
- Cost: ~$0.45/day = $13.50/month

## Next Steps

1. ✅ Create Memory resource
2. ✅ Deploy with `USE_AGENTCORE_MEMORY=true`
3. ✅ Test multi-turn conversations
4. ✅ Monitor CloudWatch logs
5. ✅ Set up alerts for errors
6. ✅ Configure TTL for state cleanup

## Support

For issues:
1. Check CloudWatch logs
2. Verify Memory resource exists
3. Test with local mode first (`USE_AGENTCORE_MEMORY=false`)
4. Review state in Memory events
