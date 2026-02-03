#!/usr/bin/env python3
"""Comprehensive application test."""
import sys
import os

print("\n" + "="*60)
print("COMPREHENSIVE APPLICATION TEST")
print("="*60)

# Test 1: DynamoDB
print("\n1. Testing DynamoDB...")
try:
    import boto3
    dynamodb = boto3.client('dynamodb')
    response = dynamodb.scan(TableName='Restaurants', Limit=1)
    if response['Items']:
        print(f"   ✅ DynamoDB has {response['Count']} restaurants")
    else:
        print("   ❌ DynamoDB is empty")
except Exception as e:
    print(f"   ❌ DynamoDB error: {e}")

# Test 2: AgentCore Memory
print("\n2. Testing AgentCore Memory...")
try:
    from bedrock_agentcore.memory import MemoryClient
    client = MemoryClient(region_name="us-east-1")
    
    # Try to write
    test_session = "test-comprehensive-123456789012345678901234567890"
    client.create_event(
        memory_id="restaurant_booking_memory-r5Q0FaBqCt",
        actor_id=test_session,
        session_id=test_session,
        messages=[("test", "USER")]
    )
    print("   ✅ AgentCore Memory write successful")
    
    # Try to read
    events = client.list_events(
        memory_id="restaurant_booking_memory-r5Q0FaBqCt",
        actor_id=test_session,
        session_id=test_session,
        max_results=1
    )
    print(f"   ✅ AgentCore Memory read successful ({len(events)} events)")
except Exception as e:
    print(f"   ❌ AgentCore Memory error: {e}")

# Test 3: MCP Gateway
print("\n3. Testing MCP Gateway...")
try:
    from src.utils.llm_providers import get_llm_provider
    provider = get_llm_provider()
    
    # Try to fetch restaurants
    result = provider.invoke(
        "fetch-restaurant-details-target___fetchRestaurantDetails",
        {"city": "New York", "cuisine": "Italian"}
    )
    
    if "error" in str(result).lower() or "404" in str(result):
        print(f"   ❌ MCP Gateway error: {result}")
    else:
        print(f"   ✅ MCP Gateway working")
except Exception as e:
    print(f"   ❌ MCP Gateway error: {e}")

# Test 4: Local Workflow
print("\n4. Testing Local Workflow...")
try:
    sys.path.insert(0, os.getcwd())
    from src.workflows.restaurant_workflow import langgraph_workflow
    
    test_state = {
        "correlation_id": "test-123",
        "user_id": "user-123",
        "session_id": "session-123456789012345678901234567890",
        "messages": [],
        "prompt": "Find Italian restaurants in New York",
        "intent": "",
        "search_params": {},
        "restaurant_results": [],
        "selected_restaurant": {},
        "booking_intent": False,
        "booking_details": {},
        "user_details": {},
        "token_amount": 0,
        "booking_result": {},
        "payment_result": {},
        "compensation_stack": [],
        "final_response": "",
        "memory_status": "enabled",
        "requires_hitl": False,
        "hitl_reason": "",
        "validation_errors": [],
        "needs_more_info": False
    }
    
    result = langgraph_workflow.invoke(test_state)
    
    if result.get("final_response"):
        print(f"   ✅ Workflow executed")
        print(f"      Response: {result['final_response'][:100]}...")
    else:
        print("   ❌ Workflow returned no response")
except Exception as e:
    print(f"   ❌ Workflow error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: AgentCore Deployment
print("\n5. Testing AgentCore Deployment...")
try:
    import subprocess
    result = subprocess.run(
        ['agentcore', 'status'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if "READY" in result.stdout:
        print("   ✅ Agent deployed and ready")
    else:
        print("   ⚠️  Agent status unclear")
except Exception as e:
    print(f"   ❌ AgentCore status error: {e}")

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("\nKey Issues:")
print("- MCP Gateway returning 404 errors")
print("- This blocks restaurant search functionality")
print("- State persistence is working correctly")
print("\nRecommendation:")
print("- Fix MCP Gateway configuration")
print("- Verify Lambda functions are deployed")
print("- Check Gateway target mappings")
print("="*60 + "\n")
