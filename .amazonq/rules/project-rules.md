# Amazon Q Developer - Restaurant Booking System Rules
# This file guides Amazon Q when generating code for this project

## Project Context
This is a production-grade Restaurant Booking System using AWS Bedrock AgentCore with LangGraph + Strands hybrid architecture.

## Architecture Principles

### Framework Usage
- Use **LangGraph** for workflow orchestration, state management, and conditional routing
- Use **Strands Agents** for agent execution, Bedrock model integration, and MCP tool calling
- Never use one without the other - they are complementary

### SOLID Principles (Mandatory)
- **Single Responsibility**: Each agent handles ONE task only (Restaurant Finder = search, Booking Agent = booking/payment)
- **Open/Closed**: Create base abstractions for Agent and LLMProvider classes, extend without modifying
- **Liskov Substitution**: Use polymorphic LLMProvider (AnthropicProvider, AmazonNovaProvider) for seamless switching
- **Interface Segregation**: Create capability-based tool interfaces
- **Dependency Inversion**: Inject dependencies via constructors, depend on abstractions not implementations

### Design Patterns (Required)
- **Handoff Pattern**: Restaurant Finder → Booking Agent with context transfer
- **SAGA Pattern**: All booking/payment operations must be compensatable with rollback logic
- **Circuit Breaker**: Primary LLM fails → fallback to secondary (Claude → Nova)
- **Idempotency**: ALL tool calls must include requestId for deduplication

## Code Generation Rules

### State Management
```python
# Always use TypedDict for state schema
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class RestaurantBookingState(TypedDict):
    correlation_id: str
    user_id: str
    session_id: str
    messages: Annotated[List[AnyMessage], add_messages]
    intent: str  # "search" | "booking" | "history"
    # ... other fields
```

### LangGraph Workflow Structure
```python
# Always follow this pattern
from langgraph.graph import StateGraph, END

workflow = StateGraph(RestaurantBookingState)
workflow.add_node("entry_router", entry_router)
workflow.add_node("restaurant_finder", restaurant_finder_node)
workflow.add_node("booking_agent", booking_agent_node)
workflow.add_conditional_edges("entry_router", route_by_intent, {...})
```

### Strands Agent Pattern
```python
# Always inject LLM provider for polymorphism
from strands_agents import StrandsAgent

def restaurant_finder_node(state: RestaurantBookingState) -> dict:
    llm_provider = get_llm_provider_with_fallback()  # Circuit breaker
    agent = StrandsAgent(
        llm_provider=llm_provider,
        tools=[fetch_restaurants_tool, fetch_by_id_tool],
        system_prompt=load_prompt("restaurant_finder", PROMPT_VERSION),
        temperature=0.3
    )
    return agent.invoke(state)
```

### Tool Invocation (Idempotency Required)
```python
# ALWAYS include requestId for idempotency
result = tool.invoke({
    "param1": value1,
    "requestId": f"{correlation_id}_{operation_name}_{attempt}"
})
```

### Error Handling (SAGA Pattern)
```python
# Always implement compensation stack
compensation_stack = []
try:
    # Step 1
    result1 = operation1()
    compensation_stack.append(("undo_operation1", result1["id"]))
    
    # Step 2
    result2 = operation2()
    compensation_stack.append(("undo_operation2", result2["id"]))
except Exception as e:
    # Rollback in reverse order
    for operation, resource_id in reversed(compensation_stack):
        compensate(operation, resource_id)
    raise
```

### Cost Optimization (Mandatory)
```python
# Always select model based on task complexity
MODEL_SELECTION = {
    "intent_classification": "amazon.nova-micro-v1:0",  # Cheapest
    "restaurant_search": "amazon.nova-lite-v1:0",
    "booking_validation": "anthropic.claude-3-sonnet",  # High-stakes
}

# Always cache system prompts
@lru_cache(maxsize=10)
def load_prompt(agent_name: str, version: str) -> str:
    return s3_client.get_object(...)["Body"].read()
```

### Security (Non-Negotiable)
```python
# Always validate user input for prompt injection
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all)\s+instructions?",
    r"you\s+are\s+now\s+a",
    r"disregard\s+everything"
]

def validate_input(user_message: str) -> tuple[bool, str]:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_message, re.IGNORECASE):
            return False, "Invalid input detected"
    return True, ""

# Always wrap user input
structured_input = f"<user_input>\n{user_message}\n</user_input>"
```

### Observability (Required)
```python
# Always use correlation IDs
correlation_id = f"req_{uuid.uuid4()}"
logger = logger.bind(correlation_id=correlation_id)

# Always use X-Ray tracing
@xray_recorder.capture('operation_name')
def operation():
    pass

# Always track costs
track_cost(correlation_id, user_id, tokens_used, model_name)
```

### Prompt Versioning (Mandatory)
```python
# NEVER hardcode prompts in code
# Always load from S3 with version
PROMPT_VERSION = "1.2.0"
PROMPT_PATH = f"s3://prompts/{agent_name}/v{PROMPT_VERSION}/system_prompt.md"

# Always pin versions in production
system_prompt = load_prompt(agent_name, PROMPT_VERSION)
```

## Naming Conventions
- Agent nodes: `{agent_name}_node` (e.g., `restaurant_finder_node`)
- Tool functions: `{action}_{resource}_tool` (e.g., `fetch_restaurants_tool`)
- State fields: snake_case (e.g., `booking_id`, `user_details`)
- Classes: PascalCase (e.g., `RestaurantBookingState`, `CircuitBreaker`)
- Constants: UPPER_SNAKE_CASE (e.g., `PROMPT_VERSION`, `MODEL_SELECTION`)

## File Structure
```
src/
├── agents/
│   ├── restaurant_finder.py
│   ├── booking_agent.py
│   └── memory_agent.py
├── tools/
│   ├── restaurant_tools.py
│   ├── user_tools.py
│   └── booking_tools.py
├── workflows/
│   └── restaurant_workflow.py
├── utils/
│   ├── llm_providers.py
│   ├── circuit_breaker.py
│   └── cost_tracker.py
└── config/
    └── models.py
```

## Testing Requirements
- Unit tests for each agent node
- Integration tests for end-to-end workflows
- Test idempotency with duplicate requestIds
- Test SAGA compensation on failures
- Test circuit breaker fallback

## Dependencies
```python
# Core frameworks (always include)
langgraph>=0.2.0
strands-agents>=1.0.0
bedrock-agentcore>=1.0.0

# AWS integrations
boto3>=1.34.0
aws-xray-sdk>=2.12.0

# Validation
pydantic>=2.0.0
```

## What NOT to Do
- ❌ Don't create "super agents" that do everything
- ❌ Don't hardcode prompts in code
- ❌ Don't skip requestId in tool calls
- ❌ Don't use concrete LLM implementations directly (use abstraction)
- ❌ Don't skip error handling and compensation logic
- ❌ Don't forget correlation IDs in logging
- ❌ Don't use "latest" for prompt versions in production
- ❌ Don't skip input validation for prompt injection

## Reference Documentation
See `application-prod.md` for complete production patterns and examples.
