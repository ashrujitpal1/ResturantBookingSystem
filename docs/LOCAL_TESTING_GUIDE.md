# Local Testing Guide: State Persistence

## Overview

Test the state persistence solution **locally** without deploying to AgentCore. The system uses file-based storage for local testing and can switch to AgentCore Memory for production.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              StatePersistence Layer                      │
│                                                           │
│  Local Mode (default):                                   │
│    - Stores state in ~/.restaurant_booking/state/        │
│    - One JSON file per session_id                        │
│    - Perfect for local testing                           │
│                                                           │
│  AgentCore Mode (production):                            │
│    - Uses AgentCore Memory API                           │
│    - Persistent across deployments                       │
│    - Enable with USE_AGENTCORE_MEMORY=true               │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Run Local Test
```bash
python test_state_persistence_local.py
```

**Expected Output:**
```
📍 TEST 1: Search for Restaurants
Restaurants found: 5
Search params: {'city': 'Boston', 'cuisine': 'Italian'}

📅 TEST 2: Book Restaurant (Multi-turn)
Restaurants in context: 5

✅ SUCCESS: State persisted across requests!
```

### 2. Check State Files
```bash
ls -la ~/.restaurant_booking/state/
cat ~/.restaurant_booking/state/session_*.json
```

**Example State File:**
```json
{
  "restaurant_results": [
    {
      "name": "Bella Italia",
      "restaurantId": "R001",
      "rating": 4.8,
      "cuisine": "Italian"
    }
  ],
  "search_params": {
    "city": "Boston",
    "cuisine": "Italian"
  },
  "booking_details": {},
  "selected_restaurant": {},
  "last_intent": "search",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Test Scenarios

### Scenario 1: Multi-turn Restaurant Booking
```python
# Request 1: Search
payload1 = {
    "prompt": "Find Italian restaurants in Boston",
    "session_id": "session_abc123...",
    "restaurant_results": []  # Empty
}
# → Returns 5 restaurants
# → Saves to ~/.restaurant_booking/state/session_abc123.json

# Request 2: Book (references "first one")
payload2 = {
    "prompt": "Book the first one for 2 people",
    "session_id": "session_abc123...",  # Same session
    "restaurant_results": []  # Empty - loads from state!
}
# → Loads 5 restaurants from state file
# → Resolves "first one" to restaurant[0]
# → Proceeds with booking
```

### Scenario 2: Session Isolation
```python
# Session A
invoke({"session_id": "session_A", "prompt": "Find Indian restaurants"})

# Session B
invoke({"session_id": "session_B", "prompt": "Find Italian restaurants"})

# Session A continues
invoke({"session_id": "session_A", "prompt": "Book the first one"})
# → Loads Indian restaurants (not Italian)
```

### Scenario 3: State Persistence Across Restarts
```bash
# Run 1
python test_state_persistence_local.py
# → Creates state file

# Stop application

# Run 2 (later)
python test_state_persistence_local.py
# → Loads previous state from file
```

## Configuration

### Local Mode (Default)
```bash
# No environment variables needed
python test_state_persistence_local.py
```

**Storage Location:** `~/.restaurant_booking/state/`

### AgentCore Memory Mode
```bash
export USE_AGENTCORE_MEMORY=true
export MEMORY_ID=restaurant_booking_memory-aOsBjaAma6

python test_state_persistence_local.py
```

**Storage Location:** AgentCore Memory service

## Debugging

### View State Files
```bash
# List all sessions
ls ~/.restaurant_booking/state/

# View specific session
cat ~/.restaurant_booking/state/session_<YOUR_SESSION_ID>.json | jq .

# Watch state changes in real-time
watch -n 1 'cat ~/.restaurant_booking/state/session_*.json | jq .'
```

### Clear State
```bash
# Clear all state files
rm -rf ~/.restaurant_booking/state/*

# Clear specific session
rm ~/.restaurant_booking/state/session_<SESSION_ID>.json
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Verification Checklist

- [ ] Test 1: Search returns restaurants
- [ ] Test 2: State file created in `~/.restaurant_booking/state/`
- [ ] Test 3: Multi-turn booking loads previous restaurants
- [ ] Test 4: Different sessions have isolated state
- [ ] Test 5: State persists after application restart

## Common Issues

### Issue 1: State Not Persisting
**Symptom:** Request 2 doesn't have restaurant context

**Check:**
```bash
ls ~/.restaurant_booking/state/
# Should show session_*.json files
```

**Solution:** Verify `state_persistence.save_state()` is called after workflow

### Issue 2: Wrong Restaurants Loaded
**Symptom:** Session A loads Session B's restaurants

**Check:** Verify session_id is consistent across requests

**Solution:** Use SessionManager to ensure consistent session_id

### Issue 3: Permission Denied
**Symptom:** Cannot write to `~/.restaurant_booking/state/`

**Solution:**
```bash
mkdir -p ~/.restaurant_booking/state
chmod 755 ~/.restaurant_booking/state
```

## Performance Metrics

### Local File Storage
- **Load time:** ~1-5ms
- **Save time:** ~2-10ms
- **Storage:** ~1-10KB per session
- **Limit:** Disk space

### AgentCore Memory
- **Load time:** ~50-100ms
- **Save time:** ~50-100ms
- **Storage:** ~100KB per event
- **Limit:** Service quota

## Migration to Production

### Step 1: Test Locally
```bash
# Use local file storage
python test_state_persistence_local.py
```

### Step 2: Test with AgentCore Memory (Local)
```bash
# Create AgentCore Memory resource first
export USE_AGENTCORE_MEMORY=true
export MEMORY_ID=your-memory-id

python test_state_persistence_local.py
```

### Step 3: Deploy to AgentCore Runtime
```bash
# Deploy with environment variables
agentcore deploy \
  --env USE_AGENTCORE_MEMORY=true \
  --env MEMORY_ID=your-memory-id
```

## Next Steps

1. ✅ Run `python test_state_persistence_local.py`
2. ✅ Verify state files created
3. ✅ Test multi-turn conversations
4. ✅ Create AgentCore Memory resource
5. ✅ Test with `USE_AGENTCORE_MEMORY=true`
6. ✅ Deploy to AgentCore Runtime

## Files Created

- `src/utils/state_persistence.py` - State persistence layer
- `test_state_persistence_local.py` - Local test script
- `~/.restaurant_booking/state/*.json` - State files (auto-created)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_AGENTCORE_MEMORY` | `false` | Use AgentCore Memory instead of files |
| `MEMORY_ID` | `None` | AgentCore Memory resource ID |

## Support

For issues or questions:
1. Check state files exist: `ls ~/.restaurant_booking/state/`
2. Review logs for errors
3. Verify session_id consistency
4. Test with fresh session_id
