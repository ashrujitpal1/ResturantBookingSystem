"""Booking and payment tools with SAGA pattern."""
from src.utils.llm_providers import get_llm_provider
from src.utils.circuit_breaker import parse_mcp_response, GovernancePolicy


def calculate_token_amount_tool(num_guests: int, meal_type: str, tier: str, correlation_id: str) -> dict:
    """Calculate booking token amount with idempotency."""
    provider = get_llm_provider()
    result = provider.invoke(
        "token-amount-calculation-target___tokenAmountCalculation",
        {
            "noOfGuests": num_guests,
            "mealType": meal_type,
            "restaurantTier": tier,
            "requestId": f"{correlation_id}_calc_1"
        }
    )
    return parse_mcp_response(result)


def book_table_tool(booking_args: dict, correlation_id: str) -> tuple[dict, str]:
    """Book table with governance policy check and idempotency."""
    # Evaluate governance policy
    allowed, reason = GovernancePolicy.evaluate("book-a-table-target___bookATable", booking_args)
    if not allowed:
        return {"error": reason}, reason
    
    booking_args["requestId"] = f"{correlation_id}_book_1"
    provider = get_llm_provider()
    result = provider.invoke("book-a-table-target___bookATable", booking_args)
    return parse_mcp_response(result), ""


def process_payment_tool(payment_args: dict, correlation_id: str) -> tuple[dict, str]:
    """Process payment with governance policy check and idempotency."""
    # Evaluate governance policy
    allowed, reason = GovernancePolicy.evaluate("payment-api-target___paymentAPI", payment_args)
    if not allowed:
        return {"error": reason}, reason
    
    payment_args["requestId"] = f"{correlation_id}_pay_1"
    provider = get_llm_provider()
    result = provider.invoke("payment-api-target___paymentAPI", payment_args)
    return parse_mcp_response(result), ""


def cancel_booking_tool(booking_id: str, correlation_id: str) -> dict:
    """Cancel booking (compensation operation)."""
    # Placeholder for actual cancellation API
    print(f"🔄 Compensating: Cancelling booking {booking_id}")
    return {"status": "cancelled", "booking_id": booking_id}
