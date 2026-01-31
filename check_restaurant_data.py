#!/usr/bin/env python3
"""Quick test to see what restaurant data exists"""

import json
import requests
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Load config
with open('agentcore-gateway-config.json', 'r') as f:
    config = json.load(f)

GATEWAY_URL = config['gateway_url']
COGNITO_INFO = config['client_info']
REGION = config['region']

# Get fresh token
gateway_client = GatewayClient(region_name=REGION)
access_token = gateway_client.get_access_token_for_cognito(COGNITO_INFO)

print(f"✅ Got fresh token: {access_token[:20]}...")

# Test 1: Get all restaurants (no filters)
print("\n🧪 Test 1: Fetch all restaurants (no filters)")
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "fetch-restaurant-details-target___fetchRestaurantDetails",
        "arguments": {}
    }
}

response = requests.post(GATEWAY_URL, headers=headers, json=payload)
if response.status_code == 200:
    result = response.json()
    if "result" in result and "content" in result["result"]:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        restaurants = data.get("restaurants", [])
        print(f"✅ Found {len(restaurants)} restaurants")
        
        # Show first 5 with details
        print("\n📋 Sample restaurants:")
        for i, r in enumerate(restaurants[:5], 1):
            print(f"\n{i}. {r.get('name', 'Unknown')}")
            print(f"   City: {r.get('location', {}).get('city', 'N/A')}")
            print(f"   Cuisine: {r.get('cuisine', 'N/A')}")
            print(f"   Rating: {r.get('rating', 'N/A')}")
            print(f"   ID: {r.get('restaurantId', 'N/A')}")
        
        # Get unique cities and cuisines
        cities = set(r.get('location', {}).get('city', '') for r in restaurants if r.get('location', {}).get('city'))
        cuisines = set(r.get('cuisine', '') for r in restaurants if r.get('cuisine'))
        
        print(f"\n📍 Available cities: {', '.join(sorted(cities))}")
        print(f"🍽️ Available cuisines: {', '.join(sorted(cuisines))}")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

# Test 2: Search by specific city
print("\n\n🧪 Test 2: Search by city (using first city found)")
if cities:
    test_city = list(cities)[0]
    payload["params"]["arguments"] = {"city": test_city}
    
    response = requests.post(GATEWAY_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        restaurants = data.get("restaurants", [])
        print(f"✅ Found {len(restaurants)} restaurants in {test_city}")
    else:
        print(f"❌ Failed: {response.status_code}")
