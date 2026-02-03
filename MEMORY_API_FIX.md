# ✅ AgentCore Memory API - Fixed Implementation

## Issue Confirmed

**I was NOT using the correct AgentCore Memory API.**

### What I Was Using (WRONG):
```python
# ❌ WRONG - create_blob_event doesn't exist in the way I used it
self.memory_client.create_blob_event(
    memory_id=self.memory_id,
    actor_id=session_id,
    session_id=session_id,
    blob_data=state
)
```

### What I Should Use (CORRECT):
```python
# ✅ CORRECT - create_event with messages
self.memory_client.create_event(
    memory_id=self.memory_id,
    actor_id=session_id,
    session_id=session_id,
    messages=[
        (f"STATE:{json.dumps(state)}", "TOOL")
    ]
)
```

## Changes Made

### 1. Save Method - Now Uses create_event
```python
def _save_to_agentcore(self, session_id: str, state: Dict[str, Any]):
    """Save state using create_event with TOOL message."""
    state_json = json.dumps(state)
    
    self.memory_client.create_event(
        memory_id=self.memory_id,
        actor_id=session_id,
        session_id=session_id,
        messages=[
            (f"STATE:{state_json}", "TOOL")  # Store as TOOL message
        ]
    )
```

### 2. Load Method - Searches for STATE: marker
```python
def _load_from_agentcore(self, session_id: str) -> Dict[str, Any]:
    """Load state by finding STATE: marker in events."""
    events = self.memory_client.list_events(
        memory_id=self.memory_id,
        actor_id=session_id,
        session_id=session_id,
        max_results=10,
        include_payload=True
    )
    
    # Find most recent STATE: message
    for event in reversed(events):
        for item in event.get('payload', []):
            if 'conversationalMessage' in item:
                msg = item['conversationalMessage']
                if msg.get('role') == 'TOOL' and 'STATE:' in msg.get('content', ''):
                    state_json = msg['content'].replace('STATE:', '').strip()
                    return json.loads(state_json)
    
    return {}
```

## Test Result: ❌ Still Not Working

**After deployment:**
- Search returns restaurants ✅
- Book doesn't remember restaurants ❌

**Possible reasons:**
1. Environment variables still not passed to runtime
2. Memory API calls failing silently
3. Session ID handling issue

## Verification Needed

Check if Memory API is actually being called:

```python
# Add to workflow.py
print(f"USE_AGENTCORE_MEMORY={os.getenv('USE_AGENTCORE_MEMORY')}", flush=True)
print(f"MEMORY_ID={os.getenv('MEMORY_ID')}", flush=True)
print(f"State persistence initialized: {state_persistence.use_agentcore}", flush=True)
```

## Alternative: Use Conversation History

Instead of custom state storage, use AgentCore's built-in conversation memory:

```python
# Save conversation with state embedded
client.create_event(
    memory_id=memory_id,
    actor_id=session_id,
    session_id=session_id,
    messages=[
        ("Find Italian restaurants in NYC", "USER"),
        (f"Found restaurants: {json.dumps(restaurants)}", "ASSISTANT")
    ]
)

# Load conversation history
events = client.list_events(
    memory_id=memory_id,
    actor_id=session_id,
    session_id=session_id,
    max_results=10
)

# Extract restaurants from conversation
for event in reversed(events):
    # Parse assistant messages for restaurant data
```

## Recommendation

**The core issue is environment variables not being passed to the runtime container.**

Without `USE_AGENTCORE_MEMORY=true` and `MEMORY_ID`, the code defaults to local file storage, which doesn't work in AgentCore runtime.

**Next steps:**
1. Verify environment variables are accessible in runtime
2. If not, use DynamoDB instead of AgentCore Memory
3. Or implement client-side state management (pass state in payload)
