"""Circuit breaker, governance policies, and security validation."""
import re
import json
import boto3
from functools import lru_cache
from src.config.models import REGION, PROMPT_VERSION, PROMPT_BUCKET


# Prompt Injection Defense
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"you\s+are\s+now\s+a",
    r"disregard\s+(everything|all)",
    r"new\s+instructions?:",
    r"system\s+prompt:",
    r"forget\s+(everything|all)",
    r"<\s*system\s*>",
    r"role\s*:\s*system"
]

def validate_user_input(user_message: str) -> tuple[bool, str]:
    """Validate user input for prompt injection attacks."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_message, re.IGNORECASE):
            print(f"⚠️ Prompt injection detected: {pattern}")
            return False, "Invalid input detected. Please rephrase your request."
    
    if len(user_message) > 2000:
        return False, "Message too long. Please keep requests under 2000 characters."
    
    return True, ""

def wrap_user_input(user_message: str) -> str:
    """Wrap user input in structured tags."""
    return f"<user_input>\n{user_message}\n</user_input>"


# Governance Policies
class GovernancePolicy:
    """Policy enforcement for booking operations."""
    POLICIES = {
        "book-a-table-target___bookATable": {
            "max_guests": 20,
            "max_token_amount": 500.0,
            "require_approval_if": lambda args: args.get("noOfGuests", 0) > 10,
            "allowed_meal_types": ["Breakfast", "Lunch", "Dinner"]
        }
    }
    
    @staticmethod
    def evaluate(tool_name: str, arguments: dict) -> tuple[bool, str]:
        """Evaluate if tool invocation meets policy requirements."""
        policy = GovernancePolicy.POLICIES.get(tool_name)
        if not policy:
            return True, ""
        
        if "max_guests" in policy and arguments.get("noOfGuests", 0) > policy["max_guests"]:
            return False, f"Maximum {policy['max_guests']} guests allowed"
        
        if "max_token_amount" in policy and arguments.get("tokenAmount", 0) > policy["max_token_amount"]:
            return False, f"Maximum booking amount ${policy['max_token_amount']} exceeded"
        
        if "require_approval_if" in policy and policy["require_approval_if"](arguments):
            return False, "REQUIRES_HUMAN_APPROVAL"
        
        return True, ""


# Prompt Versioning
@lru_cache(maxsize=10)
def load_prompt(agent_name: str, version: str) -> str:
    """Load versioned prompt from S3 with caching."""
    try:
        s3 = boto3.client('s3', region_name=REGION)
        key = f"prompts/{agent_name}/v{version}/system_prompt.md"
        response = s3.get_object(Bucket=PROMPT_BUCKET, Key=key)
        return response["Body"].read().decode('utf-8')
    except Exception as e:
        print(f"⚠️ Failed to load prompt from S3: {e}")
        return get_default_prompt(agent_name)

def get_default_prompt(agent_name: str) -> str:
    """Fallback prompts when S3 is unavailable."""
    defaults = {
        "intent_classifier": "You are an intent classifier. Classify user intent as: search, booking, or history.",
        "restaurant_finder": "You are a restaurant search assistant. Help users find restaurants based on their preferences.",
        "booking_agent": "You are a booking assistant. Collect booking details: date, time, guests, and validate them.",
        "payment_processor": "You are a payment processor. Handle payment transactions securely."
    }
    return defaults.get(agent_name, "You are a helpful restaurant booking assistant.")


# MCP Response Parser
def parse_mcp_response(result: dict) -> dict:
    """Parse MCP response with robust error handling."""
    try:
        # Case 1: Direct Lambda response (already a dict with expected fields)
        if isinstance(result, dict) and any(key in result for key in [
            "paymentId", "bookingId", "userId", "restaurantId", "restaurants", 
            "totalAmount", "tokenAmount", "bookingReference", "message", "error"
        ]):
            return result
        
        # Case 2: Nested MCP response
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "body" in parsed:
                    return json.loads(parsed["body"])
                return parsed
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw": content}
        
        # Case 3: Return as-is if already valid
        return result
    except Exception as e:
        return {"error": f"Parse error: {str(e)}", "raw": str(result)}
