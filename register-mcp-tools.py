#!/usr/bin/env python3
"""Register Lambda functions as MCP tools using bedrock-agentcore-control"""

import json
import boto3
import time

def load_configs():
    with open('agentcore-gateway-config.json', 'r') as f:
        gateway_config = json.load(f)
    with open('lambda-arns.json', 'r') as f:
        lambda_arns = json.load(f)
    return gateway_config, lambda_arns

def create_target(client, gateway_id, name, lambda_arn, tool_name, tool_desc, properties, required=None):
    """Create MCP gateway target"""
    try:
        schema = {
            "name": tool_name,
            "description": tool_desc,
            "inputSchema": {
                "type": "object",
                "properties": properties
            }
        }
        
        if required:
            schema["inputSchema"]["required"] = required
        
        config = {
            "mcp": {
                "lambda": {
                    "lambdaArn": lambda_arn,
                    "toolSchema": {
                        "inlinePayload": [schema]
                    }
                }
            }
        }
        
        response = client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=name,
            targetConfiguration=config,
            credentialProviderConfigurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}]
        )
        
        print(f"   ✅ Registered successfully")
        return response['targetId']
    
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

def register_tools():
    gateway_config, lambda_arns = load_configs()
    gateway_id = gateway_config['gateway_id']
    region = gateway_config['region']
    
    client = boto3.client('bedrock-agentcore-control',
                         region_name=region,
                         endpoint_url=f"https://bedrock-agentcore-control.{region}.amazonaws.com")
    
    print(f"🔧 Registering Lambda functions as MCP tools")
    print("=" * 70)
    print(f"Gateway ID: {gateway_id}")
    print(f"Region: {region}\n")
    
    tools = [
        ("fetch-restaurant-details-target", lambda_arns["fetchRestaurantDetails"], 
         "fetchRestaurantDetails", "Search restaurants by city, cuisine, price range, or rating",
         {"city": {"type": "string"}, "cuisine": {"type": "string"}, 
          "priceRange": {"type": "string"}, "minRating": {"type": "number"}}, None),
        
        ("fetch-restaurant-by-id-target", lambda_arns["fetchRestaurantDetailsById"],
         "fetchRestaurantDetailsById", "Get restaurant details by ID",
         {"restaurantId": {"type": "string"}}, ["restaurantId"]),
        
        ("search-user-details-target", lambda_arns["searchUserDetails"],
         "searchUserDetails", "Find user by username or mobile number",
         {"username": {"type": "string"}, "userMobileNo": {"type": "string"}}, None),
        
        ("register-user-target", lambda_arns["registerUser"],
         "registerUser", "Register new user with preferences",
         {"username": {"type": "string"}, "mobileNo": {"type": "string"}, 
          "userCity": {"type": "string"}, "userPreference": {"type": "object"}, 
          "requestId": {"type": "string"}}, ["username", "mobileNo", "userCity"]),
        
        ("token-amount-calculation-target", lambda_arns["tokenAmountCalculation"],
         "tokenAmountCalculation", "Calculate token amount for booking",
         {"noOfGuests": {"type": "integer"}, "mealType": {"type": "string"}, 
          "restaurantTier": {"type": "string"}}, ["noOfGuests"]),
        
        ("book-a-table-target", lambda_arns["bookATable"],
         "bookATable", "Book table at restaurant. REQUIRES requestId for idempotency",
         {"restaurantId": {"type": "string"}, "userName": {"type": "string"}, 
          "userMobileNo": {"type": "string"}, "date": {"type": "string"}, 
          "time": {"type": "string"}, "type": {"type": "string"}, 
          "cityName": {"type": "string"}, "noOfGuests": {"type": "integer"}, 
          "tokenAmount": {"type": "number"}, "requestId": {"type": "string"}},
         ["restaurantId", "userName", "userMobileNo", "date", "type", "cityName", "noOfGuests", "tokenAmount", "requestId"]),
        
        ("payment-api-target", lambda_arns["paymentAPI"],
         "paymentAPI", "Process payment for booking. REQUIRES requestId for idempotency",
         {"userId": {"type": "string"}, "restaurantId": {"type": "string"}, 
          "bookingId": {"type": "string"}, "tokenAmount": {"type": "number"}, 
          "paymentMethod": {"type": "string"}, "requestId": {"type": "string"}},
         ["userId", "restaurantId", "tokenAmount", "requestId"])
    ]
    
    for i, (name, arn, tool_name, desc, props, req) in enumerate(tools, 1):
        print(f"{i}️⃣  Registering: {tool_name}")
        print(f"   ARN: {arn}")
        create_target(client, gateway_id, name, arn, tool_name, desc, props, req)
        time.sleep(2)
        print()
    
    print("=" * 70)
    print("✅ Registration complete")

if __name__ == "__main__":
    print("🚀 Restaurant Booking System - MCP Tool Registration")
    print("=" * 70 + "\n")
    register_tools()
