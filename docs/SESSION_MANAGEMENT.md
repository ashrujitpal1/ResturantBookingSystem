# Session Management Implementation

## Overview
This implementation addresses the 4 scenarios for session management and API configuration:

1. ✅ **Unique Session ID Generation**: 33+ character session ID generated on startup
2. ✅ **No User Login**: Removed user_id-based login from Streamlit app
3. ✅ **API URL from Properties**: All API calls read URL from `.properties` file
4. ✅ **Consistent Session ID**: All agents and test scripts use session_id from requests

## Architecture

### Session Manager (`src/utils/session_manager.py`)
Centralized utility for session and configuration management:

```python
from src.utils.session_manager import SessionManager

# Load or create session
session_id, api_url = SessionManager.load_or_create_session()

# Get individual values
session_id = SessionManager.get_session_id()
api_url = SessionManager.get_api_url()

# Reset session
new_session_id = SessionManager.reset_session()
```

### Properties File Location
`~/.restaurant_booking/session.properties`

**Format:**
```properties
# Restaurant Booking System Session Configuration
session_id=session_a1b2c3d4-e5f6-7890-abcd-ef1234567890
api_url=arn:aws:bedrock-agentcore:us-east-1:696072349808:runtime/restaurant_discovery_agent-VCrIJ15seV
```

### Session ID Format
- **Pattern**: `session_{uuid4}`
- **Length**: 45 characters (exceeds 33 minimum)
- **Example**: `session_a1b2c3d4-e5f6-7890-abcd-ef1234567890`

## Changes Made

### 1. Streamlit App (`frontend/app.py`)
**Removed:**
- User login form
- `user_id` state variable
- `logged_in` state variable
- Login/logout buttons

**Added:**
- SessionManager integration
- Session ID loaded from properties file on startup
- API URL loaded from properties file
- "New Session" button to reset session

**Key Changes:**
```python
# Before
user_id = st.session_state.user_id
session_id = _make_session_id_from_user(user_id)

# After
session_id = SessionManager.get_session_id()
api_url = SessionManager.get_api_url()
```

### 2. Workflow (`src/workflows/restaurant_workflow.py`)
**Changed:**
- Removed `user_id` from payload requirements
- Derives `user_id` from `session_id` for consistency
- All operations use `session_id` as primary identifier

**Key Changes:**
```python
# Before
user_id = payload.get("user_id", "default_user")
session_id = payload.get("session_id", str(uuid.uuid4()))

# After
session_id = payload.get("session_id", str(uuid.uuid4()))
user_id = session_id  # Derived from session_id
```

### 3. Test Scripts
**Updated:**
- `test_agentcore_endpoint.py`: Uses SessionManager for session_id
- `test_booking_flow.py`: Uses SessionManager for session_id

**Key Changes:**
```python
# Before
session_id = "test-session-12345678901234567890123"

# After
from src.utils.session_manager import SessionManager
session_id = SessionManager.get_session_id()
```

### 4. Agent Nodes
All agent nodes (`booking_agent.py`, `restaurant_finder.py`, `memory_agent.py`) now:
- Receive `session_id` from state
- Use `session_id` for correlation and tracking
- No hardcoded user IDs or session IDs

## Usage

### Streamlit App
```bash
cd frontend
streamlit run app.py
```

On first launch:
1. Session ID automatically generated (45 chars)
2. Saved to `~/.restaurant_booking/session.properties`
3. API URL loaded from properties or environment variable
4. No login required - direct access to chat

### Test Scripts
```bash
# Test AgentCore endpoint
python test_agentcore_endpoint.py

# Test booking flow
python test_booking_flow.py
```

Both scripts automatically:
1. Load session_id from properties file
2. Use consistent session across all test calls
3. Display session_id in output

### Manual Session Reset
```python
from src.utils.session_manager import SessionManager

# Generate new session
new_session = SessionManager.reset_session()
print(f"New session: {new_session}")
```

Or use the "🔄 New Session" button in Streamlit sidebar.

## Configuration

### Environment Variables
```bash
# Override API URL (optional)
export AGENTCORE_API_URL="arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/AGENT_NAME"
```

### Properties File Override
Edit `~/.restaurant_booking/session.properties`:
```properties
session_id=session_custom-session-id-here-min-33-chars
api_url=your-custom-api-url-here
```

## Benefits

1. **Stateless Authentication**: No user credentials needed
2. **Session Persistence**: Session survives app restarts
3. **Centralized Config**: Single source of truth for API URL
4. **Test Consistency**: Same session management for all environments
5. **Idempotency**: Session ID enables request deduplication
6. **Traceability**: All operations tracked by session_id

## Migration Notes

### For Existing Code
If you have existing code using `user_id`:

```python
# Old pattern
payload = {
    "user_id": "user_123",
    "session_id": "session_abc..."
}

# New pattern
payload = {
    "session_id": SessionManager.get_session_id()
}
# user_id is derived from session_id internally
```

### For AgentCore Invocations
```python
# Old
response = client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_ARN,
    runtimeSessionId=session_id,
    runtimeUserId=user_id,  # Removed
    payload=payload
)

# New
response = client.invoke_agent_runtime(
    agentRuntimeArn=SessionManager.get_api_url(),
    runtimeSessionId=SessionManager.get_session_id(),
    payload=json.dumps(payload).encode('utf-8')
)
```

## Troubleshooting

### Session ID Too Short
If you see: `Invalid session_id length (X), generating new UUID`

**Solution**: SessionManager automatically generates valid session_id (45 chars)

### Properties File Not Found
First run creates: `~/.restaurant_booking/session.properties`

**Manual creation:**
```bash
mkdir -p ~/.restaurant_booking
cat > ~/.restaurant_booking/session.properties << EOF
session_id=session_$(uuidgen)
api_url=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/AGENT
EOF
```

### API URL Not Loading
Check priority order:
1. Properties file: `~/.restaurant_booking/session.properties`
2. Environment variable: `AGENTCORE_API_URL`
3. Default hardcoded value

## Testing

Verify implementation:
```bash
# Check properties file
cat ~/.restaurant_booking/session.properties

# Test session manager
python -c "from src.utils.session_manager import SessionManager; print(SessionManager.get_session_id())"

# Run full test suite
python test_booking_flow.py
```

## Security Considerations

1. **Session ID Format**: UUID-based, cryptographically random
2. **No Credentials**: No passwords or tokens in properties file
3. **Local Storage**: Properties file in user home directory
4. **Permissions**: File created with default user permissions

## Future Enhancements

- [ ] Session expiration/TTL
- [ ] Multi-environment support (dev/staging/prod)
- [ ] Session encryption at rest
- [ ] Distributed session storage (Redis/DynamoDB)
- [ ] Session analytics and monitoring
