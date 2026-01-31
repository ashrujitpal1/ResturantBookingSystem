"""Restaurant search and details tools."""
from src.utils.llm_providers import get_llm_provider
from src.utils.circuit_breaker import parse_mcp_response


def fetch_restaurants_tool(city: str, cuisine: str, correlation_id: str) -> dict:
    """Fetch restaurants with idempotency."""
    provider = get_llm_provider()
    result = provider.invoke(
        "fetch-restaurant-details-target___fetchRestaurantDetails",
        {
            "city": city,
            "cuisine": cuisine,
            "requestId": f"{correlation_id}_search_1"
        }
    )
    return parse_mcp_response(result)


def fetch_restaurant_by_id_tool(restaurant_id: str, correlation_id: str) -> dict:
    """Fetch restaurant by ID with idempotency."""
    provider = get_llm_provider()
    result = provider.invoke(
        "fetch-restaurant-details-by-id-target___fetchRestaurantDetailsById",
        {
            "restaurantId": restaurant_id,
            "requestId": f"{correlation_id}_fetch_id_1"
        }
    )
    return parse_mcp_response(result)
