# 🚀 Quick Start: Local Testing

## You Need TWO Terminal Windows

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│   TERMINAL 1 (Dev Server)       │     │   TERMINAL 2 (Testing)          │
│                                 │     │                                 │
│  $ agentcore dev                │     │  $ agentcore invoke --dev       │
│                                 │     │    "Find Italian restaurants"   │
│  🚀 Starting dev server...      │     │                                 │
│  Server at localhost:8080       │     │  ✅ Response received...        │
│                                 │     │                                 │
│  ⚠️  KEEP THIS OPEN!            │     │  💡 Run tests here              │
└─────────────────────────────────┘     └─────────────────────────────────┘
```

## Step-by-Step

### 1️⃣ Install uv (One Time Only)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Terminal 1: Start Server
```bash
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem
agentcore dev
```
**✋ STOP! Keep this terminal open and running**

### 3️⃣ Terminal 2: Test Agent
Open a **NEW** terminal:
```bash
agentcore invoke --dev "Find Italian restaurants in New York"
```

## ✅ Success Looks Like

**Terminal 1:**
```
🚀 Starting development server with hot reloading
Agent: restaurant_discovery_agent
Language: Python
Module: src.workflows.restaurant_workflow:app
Server will be available at:
  • Localhost: http://localhost:8080/invocations
```

**Terminal 2:**
```
✅ Restaurant Booking System initialized (Modular Architecture)
Found 10 restaurants:
1. Carbone - Italian - Rating: 4.8
2. L'Artusi - Italian - Rating: 4.7
...
```

## 🎯 What You Did Wrong

You ran:
```bash
agentcore invoke --dev "..."  # ❌ Server not running!
```

You should have:
```bash
# Terminal 1
agentcore dev                 # ✅ Start server first

# Terminal 2 (NEW window)
agentcore invoke --dev "..."  # ✅ Then test
```

## 📚 More Info

- Full guide: `LOCAL_TESTING.md`
- Troubleshooting: `docs/AgentCore-Setup-Steps.md`
- Fix script: `./fix_agentcore_dev.sh`
