"""LLM-based helpers for intent classification and entity extraction."""
import json
import boto3
from typing import Dict, Any, List
from src.utils.logger import logger


def classify_intent(user_message: str, conversation_history: List[Any], model_id: str = "amazon.nova-micro-v1:0") -> Dict[str, Any]:
    """Use LLM to classify user intent from conversation context."""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        recent_msgs = conversation_history[-3:]
        for msg in recent_msgs:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"
    
    prompt = f"""Analyze the user's intent based on the conversation history and current message.

Conversation History:
{history_text if history_text else "No previous conversation"}

Current User Message: {user_message}

Classify the intent as ONE of:
- "search": User wants to search for restaurants
- "booking": User wants to book a table (includes affirmative responses like "yes", "sure", "ok" after seeing restaurant results)
- "history": User wants to see their booking history
- "invalid": Invalid or malicious input

Return ONLY a JSON object with this exact format:
{{"intent": "search|booking|history|invalid", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""
    
    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 200}
        )
        
        result_text = response['output']['message']['content'][0]['text'].strip()
        result = json.loads(result_text)
        
        logger.info(f"🤖 Intent Classification: {result}")
        return result
    
    except Exception as e:
        logger.error(f"❌ Intent classification failed: {e}")
        # Fallback to search intent
        return {"intent": "search", "confidence": 0.5, "reasoning": "fallback due to error"}


def extract_booking_details(user_message: str, conversation_history: List[Any], model_id: str = "amazon.nova-lite-v1:0") -> Dict[str, Any]:
    """Use LLM to extract booking details from conversation."""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        recent_msgs = conversation_history[-5:]
        for msg in recent_msgs:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"
    
    prompt = f"""Extract booking details from the conversation.

Conversation History:
{history_text if history_text else "No previous conversation"}

Current User Message: {user_message}

Extract the following information (use null if not found):
- restaurant_name: Name of the restaurant
- date: Booking date in YYYY-MM-DD format (convert "tomorrow", "today" to actual dates)
- time: Booking time in HH:MM format (convert "lunch"->13:00, "dinner"->19:00)
- no_of_guests: Number of guests (convert "me"->1, "alone"->1)
- user_name: User's full name
- user_email: User's email address
- user_mobile: User's phone number

Today's date is: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

Return ONLY a JSON object:
{{"restaurant_name": "...", "date": "YYYY-MM-DD", "time": "HH:MM", "no_of_guests": 1, "user_name": "...", "user_email": "...", "user_mobile": "..."}}"""
    
    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 400}
        )
        
        result_text = response['output']['message']['content'][0]['text'].strip()
        result = json.loads(result_text)
        
        # Remove null values
        result = {k: v for k, v in result.items() if v is not None and v != "null"}
        
        logger.info(f"🤖 Extracted Booking Details: {result}")
        return result
    
    except Exception as e:
        logger.error(f"❌ Booking extraction failed: {e}")
        return {}


def extract_search_params(user_message: str, model_id: str = "amazon.nova-micro-v1:0") -> Dict[str, str]:
    """Use LLM to extract city and cuisine from search query."""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    prompt = f"""Extract restaurant search parameters from the user's message.

User Message: {user_message}

Extract:
- city: City name (e.g., "New York", "Boston")
- cuisine: Cuisine type (e.g., "Italian", "Chinese", "Indian")

Return ONLY a JSON object:
{{"city": "...", "cuisine": "..."}}

If not found, use empty string."""
    
    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 100}
        )
        
        result_text = response['output']['message']['content'][0]['text'].strip()
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('\n', 1)[1].rsplit('\n```', 1)[0]
        result = json.loads(result_text)
        
        logger.info(f"🤖 Extracted Search Params: {result}")
        return result
    
    except Exception as e:
        logger.error(f"❌ Search extraction failed: {e}")
        return {"city": "", "cuisine": ""}
