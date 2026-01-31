#!/usr/bin/env python3
"""
MCP Tools Testing Script
Tests the registered Restaurant Booking APIs as MCP tools through AgentCore Gateway
"""

import json
import requests
import logging

def load_gateway_config():
    """Load gateway configuration from file"""
    try:
        with open('agentcore-gateway-config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Gateway configuration file not found. Run setup-agentcore-gateway.py first.")
        return None

def test_mcp_tool_discovery(gateway_config):
    """Test MCP tool discovery through the gateway"""
    
    print("🔍 Testing MCP tool discovery...")
    
    gateway_url = gateway_config['gateway_url']
    access_token = gateway_config['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test tool discovery endpoint
    discovery_url = f"{gateway_url}/tools"
    
    try:
        response = requests.get(discovery_url, headers=headers)
        
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ Discovered {len(tools)} MCP tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return tools
        else:
            print(f"❌ Tool discovery failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during tool discovery: {str(e)}")
        return None

def test_restaurant_tools(gateway_config):
    """Test restaurant-related MCP tools"""
    
    print("\n🍽️  Testing Restaurant MCP Tools...")
    
    gateway_url = gateway_config['gateway_url']
    access_token = gateway_config['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test cases for restaurant tools
    test_cases = [
        {
            "tool": "fetchRestaurantDetails",
            "description": "Fetch all restaurants",
            "method": "GET",
            "data": None
        },
        {
            "tool": "fetchRestaurantDetailsById", 
            "description": "Fetch specific restaurant",
            "method": "POST",
            "data": {"restaurantId": "rest_001"}
        },
        {
            "tool": "tokenAmountCalculation",
            "description": "Calculate booking amount",
            "method": "POST", 
            "data": {
                "restaurantId": "rest_001",
                "numberOfGuests": 4,
                "bookingDate": "2024-01-15",
                "bookingTime": "19:30"
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['tool']}: {test_case['description']}")
        
        tool_url = f"{gateway_url}/tools/{test_case['tool']}"
        
        try:
            if test_case['method'] == 'GET':
                response = requests.get(tool_url, headers=headers)
            else:
                response = requests.post(tool_url, headers=headers, json=test_case['data'])
            
            if response.status_code in [200, 201]:
                print(f"✅ {test_case['tool']} - Success")
                result_data = response.json()
                print(f"   Response: {json.dumps(result_data, indent=2)[:200]}...")
                results.append({"tool": test_case['tool'], "status": "success", "data": result_data})
            else:
                print(f"❌ {test_case['tool']} - Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                results.append({"tool": test_case['tool'], "status": "failed", "error": response.text})
                
        except Exception as e:
            print(f"❌ {test_case['tool']} - Exception: {str(e)}")
            results.append({"tool": test_case['tool'], "status": "error", "error": str(e)})
    
    return results

def test_booking_tools(gateway_config):
    """Test booking-related MCP tools"""
    
    print("\n📅 Testing Booking MCP Tools...")
    
    gateway_url = gateway_config['gateway_url']
    access_token = gateway_config['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test user registration first
    print("\n🧪 Testing registerUser")
    register_url = f"{gateway_url}/tools/registerUser"
    user_data = {
        "username": "test_user_mcp",
        "mobile": "+1234567890",
        "city": "New York",
        "preferences": ["Italian", "Mexican"]
    }
    
    try:
        response = requests.post(register_url, headers=headers, json=user_data)
        if response.status_code in [200, 201]:
            print("✅ registerUser - Success")
            user_result = response.json()
            user_id = user_result.get('body', {}).get('userId')
            
            if user_id:
                # Test booking with the created user
                print("\n🧪 Testing bookATable")
                booking_url = f"{gateway_url}/tools/bookATable"
                booking_data = {
                    "restaurantId": "rest_001",
                    "userId": user_id,
                    "bookingDate": "2024-01-15",
                    "bookingTime": "19:30",
                    "numberOfGuests": 4,
                    "specialRequests": "Window seat preferred"
                }
                
                booking_response = requests.post(booking_url, headers=headers, json=booking_data)
                if booking_response.status_code in [200, 201]:
                    print("✅ bookATable - Success")
                    return booking_response.json()
                else:
                    print(f"❌ bookATable - Failed: {booking_response.status_code}")
                    return None
        else:
            print(f"❌ registerUser - Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Booking tools test - Exception: {str(e)}")
        return None

def generate_test_report(discovery_results, restaurant_results, booking_results):
    """Generate comprehensive test report"""
    
    print("\n📊 MCP Tools Test Report")
    print("=" * 50)
    
    # Discovery results
    if discovery_results:
        print(f"✅ Tool Discovery: {len(discovery_results)} tools found")
    else:
        print("❌ Tool Discovery: Failed")
    
    # Restaurant tools results
    if restaurant_results:
        success_count = len([r for r in restaurant_results if r['status'] == 'success'])
        print(f"🍽️  Restaurant Tools: {success_count}/{len(restaurant_results)} successful")
    else:
        print("❌ Restaurant Tools: Not tested")
    
    # Booking tools results
    if booking_results:
        print("📅 Booking Tools: Successful")
    else:
        print("❌ Booking Tools: Failed")
    
    # Save detailed report
    report = {
        "discovery": discovery_results,
        "restaurant_tools": restaurant_results,
        "booking_tools": booking_results,
        "summary": {
            "total_tools_discovered": len(discovery_results) if discovery_results else 0,
            "restaurant_tools_tested": len(restaurant_results) if restaurant_results else 0,
            "booking_tools_success": booking_results is not None
        }
    }
    
    with open('mcp-tools-test-report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n📄 Detailed report saved to: mcp-tools-test-report.json")

if __name__ == "__main__":
    print("🧪 Testing MCP Tools Integration")
    print("=" * 50)
    
    # Load gateway configuration
    gateway_config = load_gateway_config()
    if not gateway_config:
        exit(1)
    
    print(f"Gateway URL: {gateway_config['gateway_url']}")
    print(f"Gateway ID: {gateway_config['gateway_id']}")
    
    # Test tool discovery
    discovery_results = test_mcp_tool_discovery(gateway_config)
    
    # Test restaurant tools
    restaurant_results = test_restaurant_tools(gateway_config)
    
    # Test booking tools
    booking_results = test_booking_tools(gateway_config)
    
    # Generate report
    generate_test_report(discovery_results, restaurant_results, booking_results)
    
    print("\n✅ MCP Tools testing completed!")