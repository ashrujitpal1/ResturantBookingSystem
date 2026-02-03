#!/usr/bin/env python3
"""Test AgentCore endpoint with various scenarios."""
import json
import subprocess
import sys

def invoke_agent(payload):
    """Invoke AgentCore agent."""
    result = subprocess.run(
        ['agentcore', 'invoke', json.dumps(payload)],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    
    # Extract response
    output = result.stdout
    if "Response:" in output:
        return output.split("Response:")[1].strip()
    return output

print("🧪 AgentCore Endpoint Testing\n")
print("=" * 60)

# Test 1: Restaurant Search
print("\n📍 TEST 1: Restaurant Search")
print("-" * 60)
response1 = invoke_agent({"prompt": "Find Indian restaurants in New York"})
print(response1)

# Test 2: Booking with explicit details
print("\n\n📅 TEST 2: Complete Booking Request")
print("-" * 60)
response2 = invoke_agent({
    "prompt": "I want to book a table for 2 people at Spice Symphony on 2026-02-15 at 19:00. My name is John Doe and my phone number is 1234567890",
    "restaurant_results": [{
        "name": "Spice Symphony",
        "restaurantId": "R001",
        "rating": 4.8,
        "priceRange": "$$",
        "address": "789 Broadway",
        "city": "New York",
        "cuisine": "Indian"
    }]
})
print(response2)

# Test 3: Multi-turn conversation
print("\n\n💬 TEST 3: Multi-turn Booking")
print("-" * 60)
session_id = "test-session-12345678901234567890123"

# Turn 1: Search
print("\nTurn 1: Search")
r1 = invoke_agent({
    "prompt": "Find Indian restaurants in New York",
    "session_id": session_id
})
print(r1[:200] + "...")

# Turn 2: Express booking intent
print("\nTurn 2: Booking intent")
r2 = invoke_agent({
    "prompt": "Book a table for 2",
    "session_id": session_id,
    "conversation_history": [
        {"role": "user", "content": "Find Indian restaurants in New York"},
        {"role": "assistant", "content": r1}
    ],
    "restaurant_results": [{
        "name": "Spice Symphony",
        "restaurantId": "R001",
        "rating": 4.8,
        "priceRange": "$$",
        "address": "789 Broadway",
        "city": "New York",
        "cuisine": "Indian"
    }]
})
print(r2[:300] + "...")

# Turn 3: Provide details
print("\nTurn 3: Provide missing details")
r3 = invoke_agent({
    "prompt": "Date: 2026-02-15, Time: 19:00, Name: John Doe, Phone: 1234567890",
    "session_id": session_id,
    "conversation_history": [
        {"role": "user", "content": "Find Indian restaurants in New York"},
        {"role": "assistant", "content": r1},
        {"role": "user", "content": "Book a table for 2"},
        {"role": "assistant", "content": r2}
    ],
    "restaurant_results": [{
        "name": "Spice Symphony",
        "restaurantId": "R001",
        "rating": 4.8,
        "priceRange": "$$",
        "address": "789 Broadway",
        "city": "New York",
        "cuisine": "Indian"
    }],
    "booking_details": {
        "restaurant_name": "Spice Symphony",
        "no_of_guests": 2
    }
})
print(r3)

print("\n\n" + "=" * 60)
print("✅ Testing Complete!")
