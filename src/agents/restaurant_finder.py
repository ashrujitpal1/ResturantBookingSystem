"""Restaurant finder agent - handles search only."""
from src.config.models import RestaurantBookingState, CostOptimizedModelRouter
from src.tools.restaurant_tools import fetch_restaurants_tool
from src.utils.circuit_breaker import validate_user_input, wrap_user_input
from src.utils.llm_helpers import classify_intent, extract_search_params


def entry_router_node(state: RestaurantBookingState) -> dict:
    """Route based on intent - uses LLM for intelligent classification."""
    user_message = state.get("prompt", "")
    conversation_history = state.get("messages", [])
    model = CostOptimizedModelRouter.select_model("intent_classification")
    
    # Validate input for prompt injection
    is_valid, error_message = validate_user_input(user_message)
    if not is_valid:
        return {
            "intent": "invalid_input",
            "final_response": error_message,
            "next": "END",
            "model_used": model
        }
    
    wrapped_prompt = wrap_user_input(user_message)
    
    # Use LLM for intent classification
    correlation_id = state.get("correlation_id", "")
    intent_result = classify_intent(user_message, conversation_history, model, correlation_id)
    intent = intent_result.get("intent", "search")
    
    # If LLM returns invalid, default to booking (since regex already validated)
    if intent == "invalid":
        intent = "booking"  # Assume booking if providing details after validation passed
    
    if intent == "booking":
        # Preserve restaurant_results and search_params for booking context
        return {
            "intent": "booking",
            "booking_intent": True,
            "model_used": model,
            "prompt": wrapped_prompt,
            "restaurant_results": state.get("restaurant_results", []),
            "search_params": state.get("search_params", {}),
            "selected_restaurant": state.get("selected_restaurant", {})
        }
    
    if intent == "history":
        return {
            "intent": "history",
            "model_used": model,
            "prompt": wrapped_prompt
        }
    
    # Default to search
    return {
        "intent": "search",
        "booking_intent": False,
        "model_used": model,
        "prompt": wrapped_prompt
    }


def restaurant_finder_node(state: RestaurantBookingState) -> dict:
    """Restaurant search - uses LLM for parameter extraction."""
    correlation_id = state.get("correlation_id", "")
    prompt = state.get("prompt", "")
    model = CostOptimizedModelRouter.select_model("restaurant_search")
    
    # Always extract fresh parameters from the current prompt
    extracted = extract_search_params(prompt, model, correlation_id)
    city = extracted.get("city", "")
    cuisine = extracted.get("cuisine", "")
    
    # If extraction failed, return error
    if not city or not cuisine:
        return {
            "restaurant_results": [],
            "final_response": "I need both a city and cuisine type to search. For example: 'Find Italian restaurants in New York'"
        }
    
    try:
        parsed = fetch_restaurants_tool(
            city=city,
            cuisine=cuisine,
            correlation_id=correlation_id
        )
        
        restaurants = parsed.get("restaurants", [])[:10]
        
        if restaurants:
            # Conversational response with booking prompt
            response = f"Great! I found {len(restaurants)} {cuisine} restaurant{'s' if len(restaurants) > 1 else ''} in {city}:\n\n"
            for i, r in enumerate(restaurants, 1):
                response += f"{i}. **{r.get('name')}** - Rating: ⭐ {r.get('rating')} - {r.get('priceRange')}\n"
                response += f"   📍 {r.get('location', {}).get('address', 'N/A')}\n\n"
            
            response += "\n💡 Would you like to book a table at any of these restaurants? Just let me know which one, the date, time, and number of guests!"
            
            selected = restaurants[0] if state.get("booking_intent") else {}
            return {
                "restaurant_results": restaurants,
                "selected_restaurant": selected,
                "final_response": response,
                "model_used": model,
                "search_params": {"city": city, "cuisine": cuisine}
            }
        else:
            return {
                "restaurant_results": [], 
                "final_response": f"I couldn't find any {cuisine} restaurants in {city}. Would you like to try a different cuisine or city?"
            }
    
    except Exception as e:
        return {"restaurant_results": [], "final_response": f"Error: {str(e)}"}
