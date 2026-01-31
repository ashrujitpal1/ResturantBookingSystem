# Restaurant Booking System - Modular Architecture

## 📁 Project Structure

```
src/
├── agents/                    # Agent node functions (Single Responsibility)
│   ├── restaurant_finder.py  # Search & intent routing
│   ├── booking_agent.py       # Booking validation & execution (SAGA)
│   └── memory_agent.py        # History retrieval & storage (PII scrubbing)
├── tools/                     # MCP tool wrappers (Idempotency)
│   ├── restaurant_tools.py    # Search & fetch restaurants
│   ├── user_tools.py          # User search & registration
│   └── booking_tools.py       # Booking, payment, cancellation
├── workflows/                 # LangGraph orchestration
│   └── restaurant_workflow.py # Main workflow with state management
├── utils/                     # Shared utilities
│   ├── llm_providers.py       # LLM abstraction (Circuit Breaker)
│   ├── circuit_breaker.py     # Governance, security, prompt versioning
│   └── cost_tracker.py        # Cost tracking & PII scrubbing
└── config/                    # Configuration
    └── models.py              # State schema & model selection
```

## 🎯 Architecture Principles

### SOLID Compliance
- ✅ **Single Responsibility**: Each agent handles ONE task
- ✅ **Open/Closed**: LLMProvider abstraction for extensibility
- ✅ **Liskov Substitution**: Polymorphic provider switching
- ✅ **Interface Segregation**: Tool-specific interfaces
- ✅ **Dependency Inversion**: Constructor injection

### Design Patterns
- ✅ **Handoff Pattern**: Restaurant Finder → Booking Agent
- ✅ **SAGA Pattern**: Compensatable booking/payment operations
- ✅ **Circuit Breaker**: Primary → Secondary LLM fallback
- ✅ **Idempotency**: All tool calls include requestId

## 🚀 Usage

### Run the Workflow
```bash
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem
python -m src.workflows.restaurant_workflow
```

### Import Modules
```python
from src.workflows.restaurant_workflow import langgraph_workflow
from src.agents.restaurant_finder import restaurant_finder_node
from src.tools.booking_tools import book_table_tool
from src.utils.llm_providers import get_llm_provider
```

## 🔒 Security Features
- Prompt injection validation
- PII scrubbing before memory storage
- Governance policy enforcement
- Input validation (phone, date, guests)

## 💰 Cost Optimization
- Nova Micro for intent classification
- Nova Lite for restaurant search
- Claude Sonnet for booking/payment (high-stakes)

## 📊 Observability
- Correlation IDs for request tracking
- Cost tracking per model
- HITL (Human-in-the-Loop) for large bookings

## 🧪 Testing
```bash
# Unit tests for individual agents
pytest src/agents/test_restaurant_finder.py

# Integration tests
pytest restaurant_agent_runtime/test_integration_e2e.py
```

## 📝 Migration Notes

### Old Structure (Monolithic)
- ❌ All code in `restaurant_agent_runtime/complete_booking_workflow.py`
- ❌ 900+ lines in single file
- ❌ Hard to test and maintain

### New Structure (Modular)
- ✅ Separated into 13 focused modules
- ✅ Each module < 200 lines
- ✅ Easy to test, extend, and maintain
- ✅ Follows project rules exactly

## 🔄 Backward Compatibility

The old workflow files remain in `restaurant_agent_runtime/` for reference. To use the new modular structure, update your imports:

```python
# Old
from restaurant_agent_runtime.complete_booking_workflow import invoke

# New
from src.workflows.restaurant_workflow import invoke
```
