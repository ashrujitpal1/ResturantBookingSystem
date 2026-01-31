# Fix: agentcore dev Error

## Problem
```
❌ Failed to start development server: [Errno 2] No such file or directory: 'uv'
```

## Solution

### Option 1: Run Fix Script (Recommended)
```bash
./fix_agentcore_dev.sh
```

### Option 2: Manual Installation

#### Install uv (Official Method)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Or Install via pip
```bash
pip install uv
```

#### Verify Installation
```bash
uv --version
```

## After Installation

### 1. Start Development Server
```bash
# From project root
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem

# Start dev server
agentcore dev
```

You should see:
```
🚀 Starting development server with hot reloading
Agent: restaurant_discovery_agent
Language: Python
Module: src.workflows.restaurant_workflow:app

Server will be available at:
  • Localhost: http://localhost:8080/invocations
```

### 2. Test the Agent (New Terminal)
```bash
# Test with agentcore CLI
agentcore invoke --dev "Find Italian restaurants in New York"

# Or test with curl
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find Italian restaurants in New York"}'
```

## What is uv?

`uv` is an extremely fast Python package installer and resolver, written in Rust. AgentCore uses it for:
- Fast dependency installation
- Development server hot reloading
- Container builds

## Additional Resources

- uv Documentation: https://github.com/astral-sh/uv
- AgentCore Setup: `docs/AgentCore-Setup-Steps.md`
- Troubleshooting: See "Troubleshooting" section in setup docs
