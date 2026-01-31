"""Restaurant finder agent - handles search only."""
from src.config.models import RestaurantBookingState, CostOptimizedModelRouter
from src.tools.restaurant_tools import fetch_restaurants_tool
from src.utils.circuit_breaker import validate_user_input, wrap_user_input


def entry_router_node(state: RestaurantBookingState) -> dict:
    """Route based on intent - uses Nova Micro for cost efficiency."""
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
    prompt = wrapped_prompt.lower()
    
    # Check conversation history for context
    has_restaurant_context = any("restaurant" in str(msg).lower() and "found" in str(msg).lower() 
                                  for msg in conversation_history[-3:] if msg)
    
    # If user says "yes" and previous message mentioned restaurants, go to booking
    if has_restaurant_context and any(kw in prompt for kw in ["yes", "sure", "ok", "book", "reserve"]):
        return {"intent": "booking", "booking_intent": True, "next": "booking_validation", "model_used": model, "prompt": wrapped_prompt}
    
    if any(kw in prompt for kw in ["history", "previous", "show me", "past"]):
        return {"intent": "history", "next": "retrieve_memory", "model_used": model, "prompt": wrapped_prompt}
    
    if any(kw in prompt for kw in ["book", "reserve", "table", "reservation"]):
        return {"intent": "booking", "booking_intent": True, "next": "restaurant_finder", "model_used": model, "prompt": wrapped_prompt}
    
    return {"intent": "search", "booking_intent": False, "next": "restaurant_finder", "model_used": model, "prompt": wrapped_prompt}


def restaurant_finder_node(state: RestaurantBookingState) -> dict:
    """Restaurant search - uses Nova Lite for cost optimization."""
    correlation_id = state.get("correlation_id", "")
    prompt = state.get("prompt", "")
    search_params = state.get("search_params", {})
    model = CostOptimizedModelRouter.select_model("restaurant_search")
    
    # Extract city and cuisine from prompt if not in search_params
    city = search_params.get("city", "")
    cuisine = search_params.get("cuisine", "")
    
    if not city or not cuisine:
        prompt_lower = prompt.lower()
        
        # Extract city
        cities = ["new york", "boston", "chicago", "seattle", "san francisco", 
                  "los angeles", "miami", "austin", "denver", "atlanta"]
        for c in cities:
            if c in prompt_lower:
                city = c.title()
                break
        
        # Extract cuisine
        cuisines = ["italian", "chinese", "japanese", "mexican", "indian", 
                    "french", "thai", "american", "greek", "spanish"]
        for cu in cuisines:
            if cu in prompt_lower:
                cuisine = cu.title()
                break
    
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
