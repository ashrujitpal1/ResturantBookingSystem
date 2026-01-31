# Local Testing Instructions

## The Issue
You tried to invoke the agent, but the development server wasn't running yet.

## Solution: Two-Step Process

### Terminal 1: Start Dev Server

```bash
# Make sure you're in project root
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem

# Install uv first (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Start the development server
agentcore dev
```

**Keep this terminal open!** You should see:
```
🚀 Starting development server with hot reloading
Agent: restaurant_discovery_agent
Server will be available at:
  • Localhost: http://localhost:8080/invocations
```

### Terminal 2: Test the Agent

**Open a NEW terminal window**, then:

```bash
# Test with agentcore CLI
agentcore invoke --dev "Find Italian restaurants in New York"

# Or test with curl
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find Italian restaurants in New York",
    "search_params": {"city": "New York", "cuisine": "Italian"}
  }'
```

## Quick Start Script

Or use the automated script:

```bash
# Terminal 1
./start_local_testing.sh

# Terminal 2 (after server starts)
agentcore invoke --dev "Find Italian restaurants in New York"
```

## Testing Different Scenarios

### Search Restaurants
```bash
agentcore invoke --dev "Find Italian restaurants in New York"
```

### Book a Table
```bash
agentcore invoke --dev "Book a table at an Italian restaurant for 2 people tomorrow at 7pm"
```

### View History
```bash
agentcore invoke --dev "Show me my booking history"
```

## Troubleshooting

### "Development Server Not Found"
- **Cause**: Dev server not running
- **Fix**: Start `agentcore dev` in Terminal 1 first

### "No such file or directory: 'uv'"
- **Cause**: uv not installed
- **Fix**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### "Port 8080 already in use"
- **Cause**: Another process using port 8080
- **Fix**: 
  ```bash
  lsof -i :8080
  kill -9 <PID>
  ```

## Production Testing

Once local testing works, deploy and test production:

```bash
# Deploy
bedrock-agentcore deploy

# Test deployed agent
python test_deployed_agent.py
```
