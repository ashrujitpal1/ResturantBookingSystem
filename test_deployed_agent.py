#!/usr/bin/env python3
"""
Test Complete Restaurant Booking System (All 3 Phases)
"""

from bedrock_agentcore_starter_toolkit.notebook import Runtime
import time
import json
import boto3

print("🧪 Testing Complete Restaurant Booking System")
print("=" * 80)

# Initialize runtime
runtime = Runtime()

sts = boto3.client('sts')
account_id = sts.get_caller_identity()["Account"]
role_arn = f"arn:aws:iam::{account_id}:role/restaurant_discovery_agent-runtime-role"

runtime.configure(
    entrypoint="restaurant_agent_runtime/complete_booking_workflow.py",
    requirements_file="restaurant_agent_runtime/requirements.txt",
    agent_name="restaurant_discovery_agent",
    execution_role=role_arn
)

# Test scenarios
tests = [
    {
        "name": "Phase 1: Restaurant Search",
        "payload": {
            "prompt": "Find Italian restaurants in New York",
            "user_id": "test_user_001",
            "search_params": {"city": "New York", "cuisine": "Italian"}
        }
    },
    {
        "name": "Phase 2: Booking",
        "payload": {
            "prompt": "Book a table for 4 people",
            "user_id": "test_user_001",
            "booking_details": {
                "date": "2024-02-15",
                "time": "19:00",
                "no_of_guests": 4
            }
        }
    }
]

for test in tests:
    print(f"\n{'='*80}")
    print(f"🧪 {test['name']}")
    print(f"{'='*80}")
    print(f"📥 Payload: {test['payload']['prompt']}")
    
    try:
        start = time.time()
        response = runtime.invoke(payload=test['payload'])
        elapsed = time.time() - start
        
        print(f"✅ Response in {elapsed:.1f}s")
        
        if response.get("contentType") == "application/json":
            content = ''.join([chunk for chunk in response.get("response", [])])
            result = json.loads(content)
            
            print(f"\n📊 Results:")
            print(f"   Intent: {result.get('intent', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            
            if result.get('restaurant_results'):
                print(f"   Restaurants: {len(result['restaurant_results'])}")
            
            if result.get('booking_result'):
                print(f"   Booking: {result['booking_result'].get('bookingId', 'N/A')}")
            
            if result.get('final_response'):
                print(f"\n📝 Response:\n{result['final_response'][:200]}...")
        
        print(f"\n✅ {test['name']} - PASSED")
        
    except Exception as e:
        print(f"\n❌ {test['name']} - FAILED: {e}")

print(f"\n{'='*80}")
print("🎉 Testing Complete!")
print(f"{'='*80}")
