# Restaurant Booking System - Development TODO List

## Phase 1: Infrastructure Setup & Data Foundation

### 1. AWS AgentCore Platform Setup
- [ ] Enable AgentCore in your AWS account
- [ ] Configure AgentCore Runtime for serverless agent execution
- [ ] Set up AgentCore Memory for short-term and long-term storage
- [ ] Configure AgentCore Identity with appropriate IAM roles
- [ ] Initialize AgentCore Gateway for MCP tool integration
- [ ] Enable AgentCore Observability with CloudWatch integration

### 2. DynamoDB Data Structure Design
- [x] Design DynamoDB table schema for restaurants data (PK: restaurantId, attributes: name, menu, location, description)
- [x] Design DynamoDB table schema for user profiles (PK: userId, attributes: username, mobile, preferences, city)
- [x] Design DynamoDB table schema for bookings (PK: bookingId, GSI: userId, attributes: restaurantId, userDetails, date, time, guests)
- [x] Design DynamoDB table schema for payments (PK: paymentId, GSI: bookingId, attributes: amount, status, timestamp)
- [x] Create DynamoDB tables with appropriate indexes and capacity settings
- [x] Populate sample data in DynamoDB tables for testing

### 3. Lambda Functions Development
- [x] Create `fetchRestaurantDetails` Lambda function (DynamoDB scan/query)
- [x] Create `fetchRestaurantDetailsById` Lambda function (DynamoDB get_item)
- [x] Create `bookRestaurant` Lambda function (DynamoDB put_item)
- [x] Create `bookATable` Lambda function (DynamoDB put_item with booking logic)
- [x] Create `searchUserDetails` Lambda function (DynamoDB get_item from user table)
- [x] Create `registerUser` Lambda function (DynamoDB put_item)
- [x] Create `tokenAmountCalculation` Lambda function (business logic only)
- [x] Create `paymentAPI` Lambda function (DynamoDB put_item for payment records)

## Phase 2: MCP Setup & Direct Lambda Integration

### 4. ~~API Gateway Configuration~~ (Not Required - Direct Lambda Integration)
- [x] ~~Set up API Gateway for all Lambda functions~~ (Bypassed by direct Lambda MCP integration)
- [x] ~~Configure proper HTTP methods and endpoints~~ (Not needed for MCP tools)
- [x] ~~Add request/response validation schemas~~ (Handled by MCP tool schemas)
- [x] ~~Set up CORS policies~~ (Not applicable for direct Lambda invocation)

### 5. ~~OpenAPI Specifications~~ (Generated but Not Used for MCP)
- [x] ~~Generate OpenAPI 3.0 specifications for all 8 APIs~~ (Created for documentation only)
- [x] ~~Include detailed parameter descriptions and examples~~ (MCP tool schemas used instead)
- [x] ~~Add response schemas and error handling~~ (Handled by Lambda functions directly)
- [x] ~~Validate API specifications~~ (Not used in final implementation)

### 6. Bedrock AgentCore Gateway Setup
- [x] Initialize GatewayClient from bedrock-agentcore-starter-toolkit
- [x] Create Cognito OAuth authorizer for gateway authentication
- [x] Create MCP Gateway with authorizer configuration
- [x] Capture Gateway ID and Gateway URL for API registration
- [x] Generate access token for gateway authentication
- [x] Configure IAM role with Lambda invoke permissions (AgentCoreGatewayExecutionRole)
- [x] Register Lambda functions as MCP tools (direct invocation)
- [x] Configure all 8 Lambda functions as MCP tools
- [x] Test MCP tool discovery and invocation
- [x] Validate tool responses and error handling
- [x] Generate comprehensive configuration file for agent integration

## Phase 3: Agent Development with LangGraph + Strands

### 7. Restaurant Finder Agent
- [ ] Define RestaurantBookingState schema with TypedDict (user query, restaurant data, booking info, memory status)
- [ ] Create LangGraph StateGraph workflow structure
- [ ] Implement entry_router node for intent detection (search | booking | history)
- [ ] Build restaurant_finder_node using Strands Agent:
  - Configure Claude/Nova model via Strands
  - Register fetchRestaurantDetails and fetchRestaurantDetailsById as MCP tools
  - Define system prompt for restaurant search expertise
  - Implement user preference filtering logic
- [ ] Create AgentCore Runtime execution role with Bedrock and Lambda permissions

### 8. Booking Agent  
- [ ] Build booking_agent_node using Strands Agent:
  - Configure Claude/Nova model via Strands
  - Register MCP tools: searchUserDetails, registerUser, tokenAmountCalculation, bookATable, paymentAPI
  - Define system prompt for booking specialist role
  - Implement booking validation and confirmation logic
- [ ] Add user registration flow with preference capture
- [ ] Implement token calculation and payment processing sequence
- [ ] Generate booking reference and confirmation message

### 9. Agent Orchestration (LangGraph Workflow)
- [ ] Implement unified multi-agent workflow:
  ```python
  workflow = StateGraph(RestaurantBookingState)
  workflow.add_node("entry_router", entry_router)
  workflow.add_node("restaurant_finder", restaurant_finder_node)  # Strands
  workflow.add_node("booking_agent", booking_agent_node)          # Strands
  workflow.add_node("retrieve_memory", retrieve_memory_node)
  workflow.add_node("save_memory", save_memory_node)
  ```
- [ ] Configure conditional edges for intent routing:
  - entry_router → restaurant_finder (search intent)
  - entry_router → booking_agent (booking intent)
  - entry_router → retrieve_memory (history intent)
- [ ] Implement handoff logic: restaurant_finder → booking_agent
- [ ] Set up context transfer mechanisms between agents (state updates)
- [ ] Add error handling nodes and fallback paths
- [ ] Deploy to AgentCore Runtime:
  - Create Dockerfile with LangGraph + Strands dependencies
  - Configure bedrock_agentcore.runtime entrypoint
  - Use Runtime toolkit for deployment

## Phase 4: Memory & State Management

### 10. AgentCore Memory Setup
- [ ] Create AgentCore Memory execution role:
  - IAM role with bedrock:InvokeModel permissions
  - DynamoDB access for memory storage
  - CloudWatch Logs permissions
- [ ] Initialize memory store using MemoryClient:
  ```python
  memory_client.create_memory_and_wait(
      name="RestaurantBookingMemory",
      description="User preferences and booking history",
      event_expiry_days=30,
      memory_execution_role_arn=MEMORY_ROLE_ARN
  )
  ```
- [ ] Configure actor-based memory isolation (actor_id = user_id)
- [ ] Set up conversation-style memory format for booking history
- [ ] Implement memory nodes in LangGraph workflow:
  - retrieve_memory_node: Fetch user preferences and past bookings
  - save_memory_node: Store conversation and booking details

### 11. Session Management
- [ ] Configure session isolation using session_id per conversation
- [ ] Implement user preference extraction:
  - Capture cuisine preferences from conversations
  - Store location preferences
  - Track meal time preferences (breakfast/lunch/dinner)
- [ ] Add booking history retrieval:
  - Query past bookings by user_id
  - Display booking references and restaurant names
- [ ] Set up context window management:
  - Summarize long conversations
  - Maintain last N turns in short-term memory
- [ ] Configure memory cleanup policies:
  - Auto-expire bookings after 30 days
  - Archive completed bookings

## Phase 5: Security & Governance

### 12. Security Implementation
- [ ] Implement prompt injection protection
- [ ] Add input validation and sanitization
- [ ] Configure PII detection and redaction
- [ ] Set up content safety filters
- [ ] Add rate limiting and quota management

### 13. Policy & Governance
- [ ] Define policy-as-code for tool access control
- [ ] Implement approval workflows for high-value transactions
- [ ] Add audit logging for all agent actions
- [ ] Configure compliance monitoring

## Phase 6: Testing & Validation

### 14. Unit Testing
- [x] Test individual Lambda functions with sample data
- [x] Validate API responses and error handling
- [x] Test MCP tool integration
- [x] Debug and fix parameter mapping issues for MCP tools

### 15. Integration Testing
- [ ] Test end-to-end restaurant search workflow
- [ ] Test complete booking and payment flow
- [ ] Validate agent handoff mechanisms
- [ ] Test memory persistence and retrieval

### 16. User Acceptance Testing
- [ ] Create test scenarios for different user personas
- [ ] Test edge cases and error conditions
- [ ] Validate booking confirmation and reference generation
- [ ] Test payment processing and failure scenarios

## Phase 7: Deployment & Monitoring

### 17. Production Deployment
- [ ] Deploy agents to AgentCore Runtime
- [ ] Configure production environment variables
- [ ] Set up DNS and custom domains
- [ ] Enable SSL/TLS certificates

### 18. Monitoring & Observability
- [ ] Configure CloudWatch dashboards for agent metrics
- [ ] Set up distributed tracing for request flows
- [ ] Add cost tracking and budget alerts
- [ ] Configure performance monitoring and alerting

### 19. Documentation & Handover
- [ ] Create API documentation
- [ ] Document agent capabilities and limitations
- [ ] Create operational runbooks
- [ ] Prepare user guides and troubleshooting guides

## Phase 8: Optimization & Maintenance

### 20. Performance Optimization
- [ ] Implement prompt caching strategies
- [ ] Optimize model selection for cost efficiency
- [ ] Add batch processing for bulk operations
- [ ] Configure auto-scaling policies

### 21. Continuous Improvement
- [ ] Set up A/B testing for agent prompts
- [ ] Implement feedback collection mechanisms
- [ ] Add quality evaluation metrics
- [ ] Plan for iterative improvements

---

**Note**: This sequential approach ensures proper foundation setup before building the agents, follows production-grade practices, and maintains security and governance throughout the development process.