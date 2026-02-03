"""LLM Provider abstraction with circuit breaker pattern."""
import time
import random
import requests
import boto3
import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.config.models import GATEWAY_URL, COGNITO_INFO, REGION

try:
    from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
except ImportError:
    class GatewayClient:
        def __init__(self, region_name):
            self.region_name = region_name
        
        def get_access_token_for_cognito(self, cognito_info):
            response = requests.post(
                cognito_info["token_endpoint"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": cognito_info["client_id"],
                    "client_secret": cognito_info["client_secret"],
                    "scope": cognito_info.get("scope", "")
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            return response.json()["access_token"]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    @abstractmethod
    def invoke(self, tool_name: str, arguments: dict) -> dict:
        pass


class BedrockConverseProvider(LLMProvider):
    """Bedrock Converse API provider for auxiliary LLM calls."""
    def __init__(self, region: str):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
    
    def invoke(self, model_id: str, messages: list, inference_config: dict, request_id: str = None) -> Dict[str, Any]:
        """Invoke Bedrock Converse API with idempotency."""
        try:
            params = {
                "modelId": model_id,
                "messages": messages,
                "inferenceConfig": inference_config
            }
            if request_id:
                params["requestMetadata"] = {"requestId": request_id}
            
            response = self.bedrock.converse(**params)
            result_text = response['output']['message']['content'][0]['text'].strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('\n', 1)[1].rsplit('\n```', 1)[0]
            
            return json.loads(result_text)
        except Exception as e:
            raise Exception(f"Bedrock Converse failed: {e}")


class MCPToolProvider(LLMProvider):
    """MCP Tool provider implementation."""
    def __init__(self, gateway_url: str, cognito_info: dict, region: str):
        self.gateway_url = gateway_url
        self.cognito_info = cognito_info
        self.gateway_client = GatewayClient(region_name=region)
    
    def invoke(self, tool_name: str, arguments: dict) -> dict:
        bearer_token = self.gateway_client.get_access_token_for_cognito(self.cognito_info)
        return self._call_tool(tool_name, arguments, bearer_token)
    
    def _call_tool(self, tool_name: str, arguments: dict, bearer_token: str, max_retries: int = 3) -> dict:
        for attempt in range(max_retries):
            try:
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {bearer_token}"}
                payload = {
                    "jsonrpc": "2.0",
                    "id": random.randint(1, 10000),
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments}
                }
                response = requests.post(self.gateway_url, headers=headers, json=payload, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)


class FallbackProvider(LLMProvider):
    """Fallback provider with circuit breaker pattern."""
    def __init__(self, primary: LLMProvider, secondary: LLMProvider):
        self.primary = primary
        self.secondary = secondary
        self.failure_count = 0
        self.failure_threshold = 3
    
    def invoke(self, *args, **kwargs) -> dict:
        try:
            result = self.primary.invoke(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            print(f"⚠️ Primary provider failed ({self.failure_count}/{self.failure_threshold}): {e}")
            if self.failure_count >= self.failure_threshold:
                print("🔄 Switching to secondary provider")
                return self.secondary.invoke(*args, **kwargs)
            raise


_llm_provider = None
_bedrock_provider = None

def get_llm_provider() -> LLMProvider:
    """Factory function to create LLM provider with fallback."""
    global _llm_provider
    if _llm_provider is None:
        primary = MCPToolProvider(gateway_url=GATEWAY_URL, cognito_info=COGNITO_INFO, region=REGION)
        secondary = MCPToolProvider(gateway_url=GATEWAY_URL, cognito_info=COGNITO_INFO, region=REGION)
        _llm_provider = FallbackProvider(primary, secondary)
    return _llm_provider

def get_bedrock_provider() -> BedrockConverseProvider:
    """Factory function to create Bedrock Converse provider with circuit breaker."""
    global _bedrock_provider
    if _bedrock_provider is None:
        primary = BedrockConverseProvider(region=REGION)
        secondary = BedrockConverseProvider(region=REGION)
        _bedrock_provider = FallbackProvider(primary, secondary)
    return _bedrock_provider
