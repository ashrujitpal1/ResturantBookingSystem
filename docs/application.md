Restaurant Booking System

I want to create a Restaurant Booking System which will be driven by the Agents.

## MCP Tools (Lambda Functions)

### Restaurant Discovery Tools
1. **fetchRestaurantDetails**
   - **Purpose**: Search restaurants by filters (city, cuisine, price range, rating)
   - **Input**: `{city?, cuisine?, priceRange?, minRating?}`
   - **Output**: `{restaurants: [{restaurantId, name, menuCard, location, description, cuisine, rating}]}`
   - **Lambda**: `fetchRestaurantDetails-dev`

2. **fetchRestaurantDetailsById**
   - **Purpose**: Get specific restaurant details by ID
   - **Input**: `{restaurantId: string}`
   - **Output**: `{restaurantId, name, menuCard, location, description, cuisine, rating, capacity, openHours}`
   - **Lambda**: `fetchRestaurantDetailsById-dev`

### User Management Tools
3. **searchUserDetails**
   - **Purpose**: Retrieve user profile and preferences from memory
   - **Input**: `{username?, userMobileNo?}`
   - **Output**: `{userId, username, mobileNo, userCity, preferences: {cuisine[], dietaryRestrictions[], priceRange}}`
   - **Lambda**: `searchUserDetails-dev`

4. **registerUser**
   - **Purpose**: Create new user profile with preferences
   - **Input**: `{username: string, mobileNo: string, userPreference: object, userCity: string}`
   - **Output**: `{userId, username, message: "User registered successfully"}`
   - **Lambda**: `registerUser-dev`

### Booking & Payment Tools
5. **tokenAmountCalculation**
   - **Purpose**: Calculate booking token amount based on guests and meal type
   - **Input**: `{noOfGuests: int, mealType?: string, restaurantTier?: string}`
   - **Output**: `{tokenAmount: float, calculation: {baseAmount, discountRate, finalAmount}}`
   - **Lambda**: `tokenAmountCalculation-dev`

6. **bookATable**
   - **Purpose**: Create table reservation with availability check
   - **Input**: `{restaurantId, userName, userMobileNo, date, time, type, cityName, noOfGuests, tokenAmount}`
   - **Output**: `{bookingId, bookingReference, restaurantId, bookingDate, bookingTime, noOfGuests, message}`
   - **Lambda**: `bookATable-dev`

7. **paymentAPI**
   - **Purpose**: Process token payment and generate payment record
   - **Input**: `{userId, restaurantId, bookingId?, date, time, tokenAmount, paymentMethod?}`
   - **Output**: `{paymentId, transactionId, amount, paymentStatus, paymentDate}`
   - **Lambda**: `paymentAPI-dev`

8. **bookRestaurant** *(Legacy - simplified booking)*
   - **Purpose**: Simple booking without availability check
   - **Input**: `{restaurantId, userName, userMobileNo, date, type}`
   - **Output**: `{bookingId}`
   - **Lambda**: `bookRestaurant-dev`

## User Workflow

### Phase 1: Restaurant Discovery (Restaurant Finder Agent)
1. **User Query**: User requests restaurants by menu items, cuisine, or location
2. **Agent Search**: Restaurant Finder Agent calls `fetchRestaurantDetails()` with filters
3. **Results Display**: Agent presents matching restaurants with details (name, menu, location, rating)
4. **Refinement**: User refines search with additional criteria (price range, specific dishes)
5. **Agent Re-search**: Agent calls `fetchRestaurantDetailsById()` or re-queries with new filters

### Phase 2: Booking & Payment (Booking Agent)
6. **Booking Intent**: User selects restaurant and requests table booking
7. **Handoff**: LangGraph routes to Booking Agent with context transfer
8. **Information Gathering**: Booking Agent collects:
   - Date, time, meal type (Breakfast/Lunch/Dinner)
   - Number of guests
   - User details (name, mobile) via `searchUserDetails()` or `registerUser()`
9. **Token Calculation**: Agent calls `tokenAmountCalculation(noOfGuests)` → returns amount
10. **Booking Execution**:
    - Calls `bookATable()` with all parameters → receives `bookingId`
    - Calls `paymentAPI()` with token amount → receives `paymentId`
11. **Confirmation**: Agent generates booking reference and returns:
    - Booking ID (for user)
    - Booking reference (to show at restaurant)
    - Payment confirmation
    - Restaurant details and reservation time

### Phase 3: History & Memory
12. **Memory Storage**: Agent saves booking details and preferences to AgentCore Memory
13. **Future Queries**: User can ask "Show my bookings" → Agent retrieves from memory

Technical Details:
1.	Create one Agent which will help the user to find the Restaurant of their preference.
2.	Create another Agent will do the booking, take payments etc.
3.	All the APIs will store their data in DynamoDB tables. Create separate DynamoDB tables for restaurants, users, bookings, and payments.
4.	Use Python as the application development codebase
5.	Use AgentCore as the Application Hosting Ground.
6.	Expose all the operations as APIs using Lambda. These APIs will be used as tools for the Agents
7.	Use OpenAI to create the API specifications for the APIs. 
8.	Consume the APIs using MCP protocol from the Agent applications.
9.	Use **LangGraph + Strands** hybrid approach:
   - **LangGraph**: Workflow orchestration, state management, and multi-agent coordination
   - **Strands**: AWS Bedrock agent execution, tool calling, and runtime optimizations

## Agent Architecture Pattern

### Multi-Agent Orchestration with LangGraph

**Pattern**: Handoff Pattern with Entry Router

```
┌─────────────────────────────────────────────┐
│         Entry Router (LangGraph)            │
│  Analyzes intent: search | booking | history│
└─────────────────────────────────────────────┘
           ↓                    ↓
┌──────────────────┐   ┌──────────────────────┐
│ Restaurant Finder│   │   Booking Agent      │
│  (Strands Agent) │   │  (Strands Agent)     │
│                  │   │                      │
│ Tools:           │   │ Tools:               │
│ - fetchRestaurant│   │ - searchUserDetails  │
│ - fetchById      │   │ - registerUser       │
│                  │   │ - tokenCalculation   │
│                  │   │ - bookATable         │
│                  │   │ - paymentAPI         │
└──────────────────┘   └──────────────────────┘
           ↓                    ↓
┌─────────────────────────────────────────────┐
│      AgentCore Memory (State & History)     │
│  - User preferences                         │
│  - Booking history                          │
│  - Conversation context                     │
└─────────────────────────────────────────────┘
```

### Framework Responsibilities

**LangGraph Handles:**
- State schema definition (RestaurantBookingState)
- Entry router logic (intent detection)
- Conditional edges (when to handoff between agents)
- Context transfer between agents
- Memory save/retrieve nodes
- Error handling and fallback paths
- Workflow visualization and debugging

**Strands Handles:**
- Agent execution within each node
- Bedrock model integration (Claude, Nova)
- MCP tool invocation
- Tool response parsing
- AWS service integration
- Production optimizations

### Implementation Structure

```python
from langgraph.graph import StateGraph, END
from strands_agents import StrandsAgent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient

app = BedrockAgentCoreApp()

# LangGraph workflow definition
workflow = StateGraph(RestaurantBookingState)

# Strands agents as workflow nodes
def restaurant_finder_node(state):
    agent = StrandsAgent(
        model="anthropic.claude-3-sonnet",
        tools=[fetch_restaurants_tool, fetch_by_id_tool],
        system_prompt="You are a restaurant search expert..."
    )
    return agent.invoke(state)

def booking_agent_node(state):
    agent = StrandsAgent(
        model="anthropic.claude-3-sonnet",
        tools=[search_user_tool, register_user_tool, 
               token_calc_tool, book_table_tool, payment_tool],
        system_prompt="You are a booking specialist..."
    )
    return agent.invoke(state)

# LangGraph orchestration
workflow.add_node("entry_router", entry_router)
workflow.add_node("restaurant_finder", restaurant_finder_node)
workflow.add_node("booking_agent", booking_agent_node)
workflow.add_node("save_memory", save_memory_node)

workflow.add_conditional_edges(
    "entry_router",
    route_by_intent,
    {
        "search": "restaurant_finder",
        "booking": "booking_agent",
        "history": "retrieve_memory"
    }
)

@app.entrypoint
def invoke(payload):
    return workflow.invoke(payload)
```

### Why This Hybrid Approach?

1. **LangGraph Strengths**:
   - Clear workflow visualization
   - Deterministic state management
   - Easy to debug multi-agent flows
   - Framework-agnostic (portable)

2. **Strands Strengths**:
   - Deep AWS Bedrock integration
   - Optimized for AgentCore Runtime
   - Production-ready tool calling
   - Native MCP protocol support

3. **Combined Benefits**:
   - Best of both worlds
   - Production-grade on AWS
   - Maintainable and testable
   - Follows AWS best practices