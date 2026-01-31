"""User management tools."""
from src.utils.llm_providers import get_llm_provider
from src.utils.circuit_breaker import parse_mcp_response


def search_user_tool(mobile: str) -> dict:
    """Search user by mobile number."""
    provider = get_llm_provider()
    result = provider.invoke(
        "search-user-details-target___searchUserDetails",
        {"userMobileNo": mobile}
    )
    return parse_mcp_response(result)


def register_user_tool(username: str, mobile: str, city: str, preferences: dict, correlation_id: str) -> dict:
    """Register new user with idempotency."""
    provider = get_llm_provider()
    result = provider.invoke(
        "register-user-target___registerUser",
        {
            "username": username,
            "mobileNo": mobile,
            "userCity": city,
            "userPreference": preferences,
            "requestId": f"{correlation_id}_register_1"
        }
    )
    return parse_mcp_response(result)
