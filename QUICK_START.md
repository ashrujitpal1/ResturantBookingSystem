# Quick Start - Modular Restaurant Booking System

## ✅ Refactoring Complete

Your Restaurant Booking System has been successfully refactored into a modular architecture.

## 📁 New Structure

```
src/
├── agents/                    # Agent nodes (Single Responsibility)
│   ├── restaurant_finder.py  # Search & intent routing
│   ├── booking_agent.py       # Booking validation & execution
│   └── memory_agent.py        # History with PII scrubbing
│
├── tools/                     # MCP tool wrappers (Idempotency)
│   ├── restaurant_tools.py    # Search restaurants
│   ├── user_tools.py          # User management
│   └── booking_tools.py       # Booking & payment
│
├── workflows/                 # LangGraph orchestration
│   └── restaurant_workflow.py # Main workflow
│
├── utils/                     # Shared utilities
│   ├── llm_providers.py       # LLM abstraction (Circuit Breaker)
│   ├── circuit_breaker.py     # Security & governance
│   └── cost_tracker.py        # Cost tracking & PII scrubbing
│
└── config/                    # Configuration
    └── models.py              # State schema & model selection
```

## 🚀 Run the Workflow

```bash
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem
python -m src.workflows.restaurant_workflow
```

## 🧪 Run Tests

```bash
python src/tests/test_modular_architecture.py
```

## 📝 Import Examples

```python
# Workflow
from src.workflows.restaurant_workflow import langgraph_workflow, invoke

# Agents
from src.agents.restaurant_finder import restaurant_finder_node
from src.agents.booking_agent import booking_validation_node
from src.agents.memory_agent import save_memory_node

# Tools
from src.tools.restaurant_tools import fetch_restaurants_tool
from src.tools.booking_tools import book_table_tool

# Utils
from src.utils.llm_providers import get_llm_provider
from src.utils.circuit_breaker import validate_user_input, GovernancePolicy

# Config
from src.config.models import RestaurantBookingState, CostOptimizedModelRouter
```

## ✨ Key Features

- ✅ **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution
- ✅ **Design Patterns**: Handoff, SAGA, Circuit Breaker, Idempotency
- ✅ **Security**: Prompt injection defense, PII scrubbing, governance policies
- ✅ **Cost Optimization**: Model selection per task (Nova Micro → Lite → Claude)
- ✅ **Observability**: Correlation IDs, cost tracking, HITL for large bookings

## 📊 Test Results

All tests passing:
- ✅ Module imports
- ✅ SOLID principles
- ✅ Security features
- ✅ Cost optimization

## 📚 Documentation

- `src/README.md` - Detailed architecture guide
- `REFACTORING_SUMMARY.md` - Complete refactoring details
- `.amazonq/rules/project-rules.md` - Project rules (already followed)

## 🔄 Migration

Old monolithic file remains at:
- `restaurant_agent_runtime/complete_booking_workflow.py`

You can safely delete it once you've verified the new structure works for your use case.
