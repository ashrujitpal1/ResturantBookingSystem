"""Model selection and cost optimization configuration."""
import os
from typing import TypedDict, List, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class RestaurantBookingState(TypedDict):
    """State schema for restaurant booking workflow."""
    correlation_id: str
    user_id: str
    session_id: str
    messages: Annotated[List[AnyMessage], add_messages]
    prompt: str
    intent: str
    search_params: dict
    restaurant_results: list
    selected_restaurant: dict
    booking_intent: bool
    booking_details: dict
    user_details: dict
    token_amount: float
    booking_result: dict
    payment_result: dict
    compensation_stack: list
    final_response: str
    memory_status: str
    requires_hitl: bool
    hitl_reason: str
    validation_errors: list


class CostOptimizedModelRouter:
    """Cost-optimized model selection per task type."""
    MODEL_COSTS = {
        "amazon.nova-micro-v1:0": 0.00015,
        "amazon.nova-lite-v1:0": 0.0006,
        "anthropic.claude-3-haiku": 0.00025,
        "anthropic.claude-3-sonnet": 0.003
    }
    
    @staticmethod
    def select_model(task_type: str) -> str:
        routing = {
            "intent_classification": "amazon.nova-micro-v1:0",
            "restaurant_search": "amazon.nova-lite-v1:0",
            "booking_validation": "anthropic.claude-3-sonnet",
            "payment_processing": "anthropic.claude-3-sonnet"
        }
        return routing.get(task_type, "amazon.nova-lite-v1:0")
    
    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        cost_per_token = CostOptimizedModelRouter.MODEL_COSTS.get(model, 0.0006)
        return ((input_tokens + output_tokens) / 1000) * cost_per_token


# Configuration
REGION = os.getenv("AWS_REGION", "us-east-1")
GATEWAY_URL = os.getenv("GATEWAY_URL", "https://restaurantappgatewaymi99khe1-tmnyzeshe6.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp")
MEMORY_ID = os.getenv("MEMORY_ID", "restaurant_booking_memory-aOsBjaAma6")
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "1.0.0")
PROMPT_BUCKET = os.getenv("PROMPT_BUCKET", "restaurant-booking-prompts")

COGNITO_INFO = {
    "client_id": os.getenv("COGNITO_CLIENT_ID", "6u5ven1dru18pvpdn00nnlrop"),
    "client_secret": os.getenv("COGNITO_CLIENT_SECRET", "1kqf3jqpj42bn1ese41qc4bo3h9t1hr7b7grb17nonkvss2c6slc"),
    "token_endpoint": os.getenv("COGNITO_TOKEN_ENDPOINT", "https://agentcore-d9eb5364.auth.us-east-1.amazoncognito.com/oauth2/token"),
    "scope": os.getenv("COGNITO_SCOPE", "RestaurantBookingAuth/invoke")
}
