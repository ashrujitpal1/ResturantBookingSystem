# AgentCore Setup for Restaurant Booking System

## AgentCore Installation (Already Completed)
You have correctly installed AgentCore using:
```bash
pip install bedrock-agentcore-starter-toolkit
```

## AgentCore Components Available
With the bedrock-agentcore-starter-toolkit, you now have access to:
- **AgentCore Runtime** - Serverless agent execution environment
- **AgentCore Memory** - Short-term and long-term memory management
- **AgentCore Identity** - Authentication and access management
- **AgentCore Gateway** - API-to-MCP tool conversion
- **AgentCore Observability** - Tracing and monitoring

### Step 1: Check Available AgentCore Commands

#### 1.1 Verify Installation and Available Commands
```bash
# Verify AgentCore installation
python -c "import bedrock_agentcore; print('AgentCore installed successfully')"

# Check available agentcore commands
agentcore --help
```

#### 1.2 Configure AWS Credentials
```bash
# Configure AWS CLI (if not already done)
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

#### 1.3 Create Project Directory Manually
```bash
# Create project directory manually since 'init' command doesn't exist
mkdir restaurant-booking-system
cd restaurant-booking-system
```

### Step 2: Configure AgentCore Runtime (Updated for Modular Structure)

#### 2.1 Runtime Configuration Already Set

The `.bedrock_agentcore.yaml` file is already configured with:
- Entrypoint: `src/workflows/restaurant_workflow.py`
- Deployment type: Container
- Platform: linux/arm64
- Region: us-east-1

#### 2.2 Deploy Runtime Environment
```bash
# Deploy AgentCore runtime with modular structure
bedrock-agentcore deploy
```

### Step 3: Set up AgentCore Memory (Already Configured)

#### 3.1 Memory Configuration

Memory is configured in the workflow using:
- `bedrock_agentcore.memory.MemoryClient`
- PII scrubbing before storage (see `src/utils/cost_tracker.py`)
- Actor-based isolation for multi-user support

#### 3.2 Enable Memory (if needed)
```bash
# Enable memory for the agent
python enable_memory.py
```

#### 3.3 Memory Implementation

Memory is implemented in `src/agents/memory_agent.py` with:
- Semantic search for cuisine/restaurant queries
- Exact match for booking IDs
- PII scrubbing (phone, email, card numbers)
- Structured metadata for better retrieval

### Step 4: Configure AgentCore Identity

#### 4.1 Set up Identity Configuration
```python
# Create identity_config.py
from bedrock_agentcore.identity import IdentityConfig

identity_config = IdentityConfig(
    config_name="restaurant-booking-identity",
    identity_providers=[
        {
            "type": "COGNITO",
            "user_pool_id": "<USER_POOL_ID>"
        }
    ]
)
```

#### 4.2 Configure Agent Permissions
```python
# Create agent_permissions.py
from bedrock_agentcore.identity import AgentIdentity

# Restaurant Finder Agent permissions
restaurant_finder = AgentIdentity(
    agent_name="restaurant-finder",
    permissions=[
        "restaurant:search",
        "user:read-preferences"
    ]
)

# Booking Agent permissions
booking_agent = AgentIdentity(
    agent_name="booking-agent",
    permissions=[
        "booking:create",
        "payment:process",
        "user:read-write"
    ]
)
```

#### 4.3 Deploy Identity Configuration
```bash
# Deploy identity setup
agentcore identity deploy --config identity_config.py
```

### Step 5: Configure AgentCore Gateway (Already Configured)

#### 5.1 Gateway Configuration

The gateway is already configured with:
- Gateway URL in `.bedrock_agentcore.yaml`
- Cognito authentication
- MCP tool definitions in `mcp-tool-definitions.json`

#### 5.2 Lambda Functions as MCP Tools

Lambda functions are registered as MCP tools:
- `fetch-restaurant-details-target___fetchRestaurantDetails`
- `book-a-table-target___bookATable`
- `payment-api-target___paymentAPI`
- `search-user-details-target___searchUserDetails`
- `register-user-target___registerUser`
- `token-amount-calculation-target___tokenAmountCalculation`

#### 5.3 Tool Invocation

Tools are invoked through the modular structure:
- `src/tools/restaurant_tools.py` - Restaurant search tools
- `src/tools/user_tools.py` - User management tools
- `src/tools/booking_tools.py` - Booking and payment tools

All tool calls include `requestId` for idempotency.

### Step 6: Enable AgentCore Observability (Built-in)

#### 6.1 Observability Features

The modular structure includes built-in observability:

**Cost Tracking** (`src/utils/cost_tracker.py`):
- Correlation IDs for request tracking
- Token usage tracking
- Model selection per task (Nova Micro → Lite → Claude)

**Security** (`src/utils/circuit_breaker.py`):
- Prompt injection validation
- Governance policy enforcement
- Input validation

**Circuit Breaker** (`src/utils/llm_providers.py`):
- Primary → Secondary LLM fallback
- Failure threshold tracking
- Automatic failover

#### 6.2 Observability Configuration

Observability is enabled in `.bedrock_agentcore.yaml`:
```yaml
observability:
  enabled: true
```

#### 6.3 Monitoring

Monitor your agent through:
- AWS CloudWatch Logs
- AWS X-Ray tracing
- Cost tracking output in logs

## Quick Start - Deploy Modular Architecture

### 0. Install Prerequisites
```bash
# Install uv (required for agentcore dev)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Verify installation
uv --version
```

### 1. Verify Setup
```bash
# Run pre-deployment verification
python verify_deployment.py
```

### 2. Test Locally (Development Mode)
```bash
# Start development server with hot reloading
agentcore dev

# In another terminal, test the agent
agentcore invoke --dev "Find Italian restaurants in New York"
```

### 3. Deploy Lambda Functions
```bash
# Deploy Lambda functions (if not already deployed)
sam build
sam deploy --guided
```

### 4. Deploy AgentCore Runtime
```bash
# Deploy with modular structure
bedrock-agentcore deploy

# Or use deployment script
python deploy_restaurant_agent.py
```

### 5. Test Deployment
```bash
# Test the deployed agent
python test_deployed_agent.py
```

## Architecture Benefits

The modular structure provides:

✅ **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution  
✅ **Design Patterns**: Handoff, SAGA, Circuit Breaker, Idempotency  
✅ **Security**: Prompt injection defense, PII scrubbing, governance policies  
✅ **Cost Optimization**: Model selection per task (Nova Micro → Lite → Claude)  
✅ **Observability**: Correlation IDs, cost tracking, HITL for large bookings  
✅ **Testability**: Unit tests for each module, integration tests for workflows

## Documentation

- `src/README.md` - Architecture documentation
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `QUICK_START.md` - Quick start guide
- `REFACTORING_SUMMARY.md` - Refactoring details

## Current Project Structure (Modular Architecture)

The project now uses a modular architecture following SOLID principles:

```
ResturantBookingSystem/
├── src/                              # Modular architecture
│   ├── agents/                       # Agent nodes (Single Responsibility)
│   │   ├── restaurant_finder.py      # Search & intent routing
│   │   ├── booking_agent.py          # Booking validation & execution
│   │   └── memory_agent.py           # History with PII scrubbing
│   ├── tools/                        # MCP tool wrappers (Idempotency)
│   │   ├── restaurant_tools.py       # Search restaurants
│   │   ├── user_tools.py             # User management
│   │   └── booking_tools.py          # Booking & payment
│   ├── workflows/                    # LangGraph orchestration
│   │   └── restaurant_workflow.py    # Main workflow entrypoint
│   ├── utils/                        # Shared utilities
│   │   ├── llm_providers.py          # LLM abstraction (Circuit Breaker)
│   │   ├── circuit_breaker.py        # Security & governance
│   │   └── cost_tracker.py           # Cost tracking & PII scrubbing
│   ├── config/                       # Configuration
│   │   └── models.py                 # State schema & model selection
│   └── lambda/                       # Lambda functions (MCP tools)
│       ├── fetch_restaurant_details.py
│       ├── book_a_table.py
│       ├── payment_api.py
│       └── ...
├── .bedrock_agentcore.yaml           # AgentCore config (updated)
├── Dockerfile                        # Container config (updated)
├── template.yaml                     # SAM template for Lambda
├── requirements.txt                  # Root dependencies
└── deploy_restaurant_agent.py        # Deployment script
```

## Deployment Configuration

### AgentCore Configuration (.bedrock_agentcore.yaml)

The entrypoint has been updated to use the modular workflow:

```yaml
default_agent: restaurant_discovery_agent
agents:
  restaurant_discovery_agent:
    name: restaurant_discovery_agent
    language: python
    entrypoint: /path/to/src/workflows/restaurant_workflow.py  # ✅ Updated
    deployment_type: container
    platform: linux/arm64
```

### Container Configuration (Dockerfile)

The Dockerfile has been updated to use the modular structure:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

# Install dependencies from root requirements.txt
COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

# Copy entire project
COPY . .

# Run modular workflow
CMD ["python", "-m", "src.workflows.restaurant_workflow"]  # ✅ Updated
```

## Deployment Steps

### 1. Deploy Lambda Functions (SAM)

```bash
# Lambda functions remain unchanged
sam build
sam deploy --guided
```

### 2. Deploy AgentCore Runtime

```bash
# Deploy with updated modular structure
bedrock-agentcore deploy

# Or use deployment script
python deploy_restaurant_agent.py
```

### 3. Verify Deployment

```bash
# Pre-deployment verification
python verify_deployment.py

# Post-deployment testing
python test_deployed_agent.py
```


## Troubleshooting

### Error: "No such file or directory: 'uv'"

**Problem**: The `uv` package installer is not installed.

**Solution**:
```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Verify installation
uv --version
```

### Error: "No agent project found in current directory"

**Problem**: Running `agentcore dev` from wrong directory.

**Solution**:
```bash
# Make sure you're in the project root
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem

# Verify .bedrock_agentcore.yaml exists
ls -la .bedrock_agentcore.yaml

# Then run
agentcore dev
```

### Error: "Module not found: src.workflows.restaurant_workflow"

**Problem**: Python can't find the modular structure.

**Solution**:
```bash
# Ensure all __init__.py files exist
find src -name "__init__.py"

# Run from project root
python -m src.workflows.restaurant_workflow
```

### Development Server Not Starting

**Problem**: Port 8080 already in use or dependencies missing.

**Solution**:
```bash
# Check if port is in use
lsof -i :8080

# Kill process if needed
kill -9 <PID>

# Reinstall dependencies
pip install -r requirements.txt

# Try again
agentcore dev
```

### Testing the Development Server

Once `agentcore dev` is running successfully:

```bash
# In a new terminal window
agentcore invoke --dev "Find Italian restaurants in New York"

# Or test with curl
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find Italian restaurants in New York"}'
```
