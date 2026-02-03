"""User management tools."""
from src.utils.llm_providers import get_llm_provider
from src.utils.circuit_breaker import parse_mcp_response


def search_user_tool(mobile: str, requestId: str = None) -> dict:
    """Search user by mobile number with idempotency."""
    provider = get_llm_provider()
    args = {"userMobileNo": mobile}
    if requestId:
        args["requestId"] = requestId
    result = provider.invoke(
        "search-user-details-target___searchUserDetails",
        args
    )
    return parse_mcp_response(result)


def register_user_tool(username: str, mobile: str, city: str, preferences: dict, requestId: str = None) -> dict:
    """Register new user with idempotency."""
    provider = get_llm_provider()
    args = {
        "username": username,
        "mobileNo": mobile,
        "userCity": city,
        "userPreference": preferences
    }
    if requestId:
        args["requestId"] = requestId
    result = provider.invoke(
        "register-user-target___registerUser",
        args
    )
    return parse_mcp_response(result)
