"""LLM-based helpers for intent classification and entity extraction."""
import json
import re
from typing import Dict, Any, List
from functools import lru_cache
from aws_xray_sdk.core import xray_recorder
from src.utils.logger import logger
from src.utils.llm_providers import get_bedrock_provider
from src.utils.circuit_breaker import load_prompt
from src.utils.cost_tracker import track_cost
from src.config.models import PROMPT_VERSION


@xray_recorder.capture('classify_intent')
def classify_intent(user_message: str, conversation_history: List[Any], model_id: str = "amazon.nova-micro-v1:0", correlation_id: str = "") -> Dict[str, Any]:
    """Use LLM to classify user intent from conversation context."""
    provider = get_bedrock_provider()
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        recent_msgs = conversation_history[-3:]
        for msg in recent_msgs:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"
    
    # Load versioned prompt from S3
    system_prompt = load_prompt("intent_classifier", PROMPT_VERSION)
    
    prompt = f"""{system_prompt}

Conversation History:
{history_text if history_text else "No previous conversation"}

Current User Message: {user_message}

Return ONLY a JSON object with this exact format:
{{"intent": "search|booking|history|invalid", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""
    
    try:
        result = provider.invoke(
            model_id=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inference_config={"temperature": 0.1, "maxTokens": 200},
            request_id=f"{correlation_id}_intent_1" if correlation_id else None
        )
        
        # Track cost
        track_cost(correlation_id, "system", 150, model_id)
        
        logger.info(f"[{correlation_id}] 🤖 Intent Classification: {result}")
        return result
    
    except Exception as e:
        logger.error(f"[{correlation_id}] ❌ Intent classification failed: {e}")
        return {"intent": "search", "confidence": 0.5, "reasoning": "fallback due to error"}


@xray_recorder.capture('extract_booking_details')
def extract_booking_details(user_message: str, conversation_history: List[Any], model_id: str = "amazon.nova-lite-v1:0", correlation_id: str = "") -> Dict[str, Any]:
    """Use LLM to extract booking details from conversation."""
    provider = get_bedrock_provider()
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        recent_msgs = conversation_history[-5:]
        for msg in recent_msgs:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"
    
    # Load versioned prompt from S3
    system_prompt = load_prompt("booking_agent", PROMPT_VERSION)
    
    prompt = f"""{system_prompt}

Conversation History:
{history_text if history_text else "No previous conversation"}

Current User Message: {user_message}

Today's date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

Extract booking details and return ONLY valid JSON."""
    
    try:
        result = provider.invoke(
            model_id=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inference_config={"temperature": 0.1, "maxTokens": 400},
            request_id=f"{correlation_id}_extract_1" if correlation_id else None
        )
        
        logger.info(f"[{correlation_id}] 🤖 Raw extraction result: {result}")
        
        # Handle if result is not a dict
        if not isinstance(result, dict):
            logger.warning(f"[{correlation_id}] Result is not dict, attempting to parse: {type(result)}")
            # If it's a string, try to parse as JSON
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.error(f"[{correlation_id}] Failed to parse result as JSON: {result}")
                    return {}
            else:
                return {}
        
        # Remove null values and empty strings
        result = {k: v for k, v in result.items() if v is not None and v != "null" and v != ""}
        
        # Track cost
        track_cost(correlation_id, "system", 300, model_id)
        
        logger.info(f"[{correlation_id}] 🤖 Extracted Booking Details: {result}")
        return result
    
    except json.JSONDecodeError as e:
        logger.error(f"[{correlation_id}] ❌ JSON decode error: {e}")
        return {}
    except Exception as e:
        logger.error(f"[{correlation_id}] ❌ Booking extraction failed: {e}", exc_info=True)
        return {}


@xray_recorder.capture('extract_restaurant_context')
def extract_restaurant_context_from_history(conversation_history: List[Any], model_id: str = "amazon.nova-lite-v1:0", correlation_id: str = "") -> Dict[str, Any]:
    """Use LLM to extract restaurant context from conversation history."""
    provider = get_bedrock_provider()
    
    # Build conversation text
    history_text = ""
    for msg in conversation_history[-5:]:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_text += f"{role}: {content}\n\n"
    
    if not history_text:
        return {"restaurant_results": [], "search_params": {}}
    
    # Load versioned prompt from S3
    system_prompt = load_prompt("restaurant_finder", PROMPT_VERSION)
    
    prompt = f"""{system_prompt}

Conversation:
{history_text}

Extract:
1. List of restaurants mentioned (with name, rating, priceRange, address, city, restaurantId, cuisine)
2. Search parameters (city, cuisine)

Return ONLY a JSON object:
{{"restaurant_results": [...], "search_params": {{"city": "...", "cuisine": "..."}}}}

If no restaurants found, return: {{"restaurant_results": [], "search_params": {{}}}}"""
    
    try:
        result = provider.invoke(
            model_id=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inference_config={"temperature": 0.1, "maxTokens": 1000},
            request_id=f"{correlation_id}_context_1" if correlation_id else None
        )
        
        # Track cost
        track_cost(correlation_id, "system", 800, model_id)
        
        logger.info(f"[{correlation_id}] 🤖 Extracted Context: {len(result.get('restaurant_results', []))} restaurants")
        return result
    
    except Exception as e:
        logger.error(f"[{correlation_id}] ❌ Context extraction failed: {e}")
        return {"restaurant_results": [], "search_params": {}}


@xray_recorder.capture('extract_search_params')
def extract_search_params(user_message: str, model_id: str = "amazon.nova-micro-v1:0", correlation_id: str = "") -> Dict[str, str]:
    """Extract search parameters from user message."""
    provider = get_bedrock_provider()
    
    # Load versioned prompt from S3
    system_prompt = load_prompt("restaurant_finder", PROMPT_VERSION)
    
    prompt = f"""{system_prompt}

User Message: {user_message}

Extract:
- city: City name (e.g., "New York", "Boston")
- cuisine: Cuisine type (e.g., "Italian", "Chinese", "Indian")

Return ONLY a JSON object:
{{"city": "...", "cuisine": "..."}}

If not found, use empty string."""
    
    try:
        result = provider.invoke(
            model_id=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inference_config={"temperature": 0.1, "maxTokens": 100},
            request_id=f"{correlation_id}_search_params_1" if correlation_id else None
        )
        
        # Handle if result is not a dict
        if not isinstance(result, dict):
            logger.warning(f"[{correlation_id}] Result is not dict, attempting to parse: {type(result)}")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.error(f"[{correlation_id}] Failed to parse search params as JSON: {result}")
                    return {"city": "", "cuisine": ""}
            else:
                return {"city": "", "cuisine": ""}
        
        # Ensure keys exist
        if "city" not in result:
            result["city"] = ""
        if "cuisine" not in result:
            result["cuisine"] = ""
        
        # Track cost
        track_cost(correlation_id, "system", 80, model_id)
        
        logger.info(f"[{correlation_id}] 🤖 Extracted Search Params: {result}")
        return result
    
    except Exception as e:
        logger.error(f"[{correlation_id}] ❌ Search extraction failed: {e}")
        return {"city": "", "cuisine": ""}
