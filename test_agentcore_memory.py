#!/usr/bin/env python3
"""Test AgentCore Memory read/write operations."""
import json
import uuid
from bedrock_agentcore.memory import MemoryClient

# Configuration - Get from .bedrock_agentcore.yaml
MEMORY_ID = "restaurant_booking_memory-r5Q0FaBqCt"  # Full memory name
REGION = "us-east-1"

def test_memory_operations():
    """Test write and read operations with AgentCore Memory."""
    
    print("=" * 60)
    print("AgentCore Memory Test")
    print("=" * 60)
    print(f"Memory ID: {MEMORY_ID}")
    print(f"Region: {REGION}")
    print()
    
    # Initialize client
    client = MemoryClient(region_name=REGION)
    
    # Generate test session
    session_id = f"test-session-{uuid.uuid4()}"
    actor_id = session_id
    
    print(f"Session ID: {session_id}")
    print()
    
    # Test data
    test_state = {
        "restaurant_results": [
            {
                "name": "Test Restaurant",
                "restaurantId": "R999",
                "cuisine": "Italian",
                "rating": 4.5
            }
        ],
        "search_params": {"city": "NYC", "cuisine": "Italian"},
        "booking_details": {"no_of_guests": 2}
    }
    
    # TEST 1: Write to Memory
    print("TEST 1: Writing to AgentCore Memory")
    print("-" * 60)
    try:
        state_json = json.dumps(test_state)
        
        client.create_event(
            memory_id=MEMORY_ID,
            actor_id=actor_id,
            session_id=session_id,
            messages=[
                (f"STATE:{state_json}", "TOOL")
            ]
        )
        
        print("✅ Successfully wrote to memory")
        print(f"   Data: {len(state_json)} bytes")
        print()
    except Exception as e:
        print(f"❌ Write failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # TEST 2: Read from Memory
    print("TEST 2: Reading from AgentCore Memory")
    print("-" * 60)
    try:
        events = client.list_events(
            memory_id=MEMORY_ID,
            actor_id=actor_id,
            session_id=session_id,
            max_results=10,
            include_payload=True
        )
        
        print(f"✅ Found {len(events)} events")
        
        if not events:
            print("❌ No events found - write may not have completed")
            return False
        
        # Find our state
        state_found = False
        for event in reversed(events):
            payload = event.get('payload', [])
            for item in payload:
                # Check both 'conversational' and 'conversationalMessage' keys
                msg = item.get('conversational') or item.get('conversationalMessage')
                if msg:
                    role = msg.get('role')
                    content = msg.get('content', {})
                    # Handle both string content and dict with 'text' key
                    if isinstance(content, dict):
                        content_text = content.get('text', '')
                    else:
                        content_text = content
                    
                    if role == 'TOOL' and 'STATE:' in content_text:
                        state_json = content_text.replace('STATE:', '').strip()
                        loaded_state = json.loads(state_json)
                        
                        print("✅ Successfully read state from memory")
                        print(f"   Restaurants: {len(loaded_state.get('restaurant_results', []))}")
                        print(f"   Search params: {loaded_state.get('search_params')}")
                        print(f"   Booking details: {loaded_state.get('booking_details')}")
                        
                        # Verify data matches
                        if loaded_state == test_state:
                            print("\n✅ Data integrity verified - read matches write")
                            state_found = True
                        else:
                            print("\n⚠️  Data mismatch detected")
                        break
            if state_found:
                break
        
        if not state_found:
            print("❌ State not found in events")
            print("\nEvent details:")
            for i, event in enumerate(events):
                print(f"\nEvent {i+1}:")
                print(f"  Event ID: {event.get('eventId')}")
                print(f"  Payload items: {len(event.get('payload', []))}")
                print(f"  Full payload: {json.dumps(event.get('payload', []), indent=2)}")
                for item in event.get('payload', []):
                    print(f"  Item keys: {list(item.keys())}")
                    if 'conversationalMessage' in item:
                        msg = item['conversationalMessage']
                        print(f"  Role: {msg.get('role')}")
                        print(f"  Content: {msg.get('content', '')[:200]}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Read failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 Testing AgentCore Memory Operations\n")
    
    success = test_memory_operations()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nAgentCore Memory is working correctly!")
        print("You can now use it for state persistence.")
    else:
        print("❌ TESTS FAILED")
        print("\nPossible issues:")
        print("1. Memory ID incorrect or not accessible")
        print("2. IAM permissions missing")
        print("3. Region mismatch")
    print("=" * 60)
