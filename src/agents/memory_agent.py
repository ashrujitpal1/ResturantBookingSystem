"""Memory agent - handles conversation history with PII scrubbing."""
from datetime import datetime
from bedrock_agentcore.memory import MemoryClient
from src.config.models import RestaurantBookingState, MEMORY_ID, REGION
from src.utils.cost_tracker import scrub_pii
from src.utils.llm_helpers import extract_search_params
import re


memory_client = MemoryClient(region_name=REGION) if MEMORY_ID else None


def retrieve_memory_node(state: RestaurantBookingState) -> dict:
    """Retrieve conversation history with semantic and exact match search."""
    if not memory_client or not MEMORY_ID:
        return {"final_response": "Memory not configured", "memory_status": "disabled"}
    
    try:
        user_id = state.get("user_id", "default_user")
        session_id = state.get("session_id", "default_session")
        prompt = state.get("prompt", "")
        
        # Use LLM to extract search parameters for semantic filtering
        search_params = extract_search_params(prompt)
        cuisine = search_params.get("cuisine", "")
        
        # Semantic search for cuisine/restaurant queries
        if cuisine:
            events = memory_client.list_events(
                memory_id=MEMORY_ID,
                actor_id=user_id,
                max_results=20
            )
            
            filtered = [e for e in events if cuisine.lower() in str(e).lower()]
            
            if filtered:
                history = f"# {cuisine} Bookings\n\n"
                history += "\n".join([f"{i}. {e}" for i, e in enumerate(filtered, 1)])
                return {"final_response": history, "memory_status": "retrieved_semantic"}
        
        # Exact match for booking IDs
        elif "booking" in prompt.lower() and any(char.isdigit() for char in prompt):
            booking_id_match = re.search(r'booking_[a-f0-9]{8}', prompt)
            if booking_id_match:
                booking_id = booking_id_match.group(0)
                events = memory_client.list_events(
                    memory_id=MEMORY_ID,
                    actor_id=user_id,
                    max_results=50
                )
                
                matched = [e for e in events if booking_id in str(e)]
                if matched:
                    return {"final_response": f"# Booking {booking_id}\n\n{matched[0]}", "memory_status": "retrieved_exact"}
        
        # Default: Recent history
        events = memory_client.list_events(
            memory_id=MEMORY_ID,
            actor_id=user_id,
            session_id=session_id,
            max_results=10
        )
        
        history = "# Recent History\n\n" + "\n".join([f"{i}. {e}" for i, e in enumerate(events, 1)]) if events else "No history found."
        return {"final_response": history, "memory_status": "retrieved"}
    
    except Exception as e:
        return {"final_response": f"Error: {str(e)}", "memory_status": "error"}


def save_memory_node(state: RestaurantBookingState) -> dict:
    """Save conversation with PII scrubbing and structured metadata."""
    if not memory_client or not MEMORY_ID:
        return {"memory_status": "disabled"}
    
    try:
        user_id = state.get("user_id", "default_user")
        session_id = state.get("session_id", "default_session")
        prompt = state.get("prompt", "")
        response = state.get("final_response", "")
        
        # Scrub PII before storage
        scrubbed_prompt = scrub_pii(prompt)
        scrubbed_response = scrub_pii(response)
        
        # Add structured metadata for semantic search
        booking_result = state.get("booking_result", {})
        selected_restaurant = state.get("selected_restaurant", {})
        
        metadata = {
            "intent": state.get("intent", ""),
            "restaurant_name": selected_restaurant.get("name", ""),
            "cuisine": selected_restaurant.get("cuisine", ""),
            "booking_date": state.get("booking_details", {}).get("date", ""),
            "booking_id": booking_result.get("bookingId", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Enrich messages with metadata for better retrieval
        user_message = f"{scrubbed_prompt} [cuisine:{metadata['cuisine']}]"
        assistant_message = f"{scrubbed_response} [restaurant:{metadata['restaurant_name']}]"
        
        memory_client.save_conversation(
            memory_id=MEMORY_ID,
            actor_id=user_id,
            session_id=session_id,
            messages=[
                (user_message, "USER"),
                (assistant_message, "ASSISTANT")
            ]
        )
        
        return {"memory_status": "saved"}
    
    except Exception as e:
        print(f"Memory save error: {str(e)}")
        return {"memory_status": "save_failed"}
