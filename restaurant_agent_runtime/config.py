"""
Configuration loader for Restaurant Agent Runtime
Loads settings from agentcore-gateway-config.json
"""

import json
import os

def load_config(config_path: str = "../agentcore-gateway-config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Config file not found: {config_path}")
        return {}

def get_env_config() -> dict:
    """Get configuration from environment variables or config file"""
    config = load_config()
    
    return {
        "REGION": os.getenv("AWS_REGION", config.get("region", "us-east-1")),
        "GATEWAY_URL": os.getenv("GATEWAY_URL", config.get("gateway_url", "")),
        "MEMORY_ID": os.getenv("MEMORY_ID", config.get("memory_id", "")),
        "COGNITO_INFO": {
            "client_id": os.getenv("COGNITO_CLIENT_ID", config.get("client_info", {}).get("client_id", "")),
            "client_secret": os.getenv("COGNITO_CLIENT_SECRET", config.get("client_info", {}).get("client_secret", "")),
            "token_endpoint": os.getenv("COGNITO_TOKEN_ENDPOINT", config.get("client_info", {}).get("token_endpoint", ""))
        }
    }
