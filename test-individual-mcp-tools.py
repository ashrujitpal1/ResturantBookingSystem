#!/usr/bin/env python3
"""
Test Individual MCP Tools
Tests each registered Lambda function using MCP protocol calls
"""

import json
import requests
import time
from pprint import pprint

def load_gateway_config():
    """Load gateway configuration"""
    with open('agentcore-gateway-config.json', 'r') as f:
        return json.load(f)

def call_mcp_tool(gateway_url, access_token, tool_name, arguments=None):
    """Call MCP tool using JSON-RPC protocol"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    try:
        response = requests.post(gateway_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

def test_fetch_restaurants(gateway_url, access_token):
    """Test fetchRestaurantDetails tool"""
    
    print("🧪 Testing fetchRestaurantDetails...")
    
    result = call_mcp_tool(
        gateway_url, 
        access_token,
        "fetch-restaurant-details-target___fetchRestaurantDetails"
    )
    
    if "error" not in result:
        print("✅ fetchRestaurantDetails - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            print(f"   Debug - Content type: {type(content)}")
            print(f"   Debug - Content: {content}")
            if isinstance(content, list) and len(content) > 0:
                restaurants_text = content[0]["text"]
                print(f"   Debug - Text: {restaurants_text[:200]}...")
                restaurants = json.loads(restaurants_text)
                print(f"   Debug - Parsed type: {type(restaurants)}")
                print(f"   Found {len(restaurants) if isinstance(restaurants, list) else 'N/A'} restaurants")
                if isinstance(restaurants, list) and len(restaurants) > 0:
                    print(f"   Sample: {restaurants[0].get('name', 'Unknown')}")
                else:
                    print("   No restaurants in response or not a list")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ fetchRestaurantDetails - Failed: {result['error']}")
        return False

def test_fetch_restaurant_by_id(gateway_url, access_token):
    """Test fetchRestaurantDetailsById tool"""
    
    print("\n🧪 Testing fetchRestaurantDetailsById...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token, 
        "fetch-restaurant-by-id-target___fetchRestaurantDetailsById",
        {"restaurantId": "rest_001"}
    )
    
    if "error" not in result:
        print("✅ fetchRestaurantDetailsById - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                restaurant_text = content[0]["text"]
                restaurant = json.loads(restaurant_text)
                print(f"   Restaurant: {restaurant.get('name', 'Unknown')}")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ fetchRestaurantDetailsById - Failed: {result['error']}")
        return False

def test_token_calculation(gateway_url, access_token):
    """Test tokenAmountCalculation tool"""
    
    print("\n🧪 Testing tokenAmountCalculation...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "token-amount-calculation-target___tokenAmountCalculation",
        {
            "noOfGuests": 4,
            "mealType": "Dinner",
            "restaurantTier": "standard"
        }
    )
    
    if "error" not in result:
        print("✅ tokenAmountCalculation - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                calculation = json.loads(content[0]["text"])
                print(f"   Total Amount: ${calculation.get('totalAmount', 'N/A')}")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ tokenAmountCalculation - Failed: {result['error']}")
        return False

import json
import time

def generate_request_id(operation):
    """Generate unique requestId for idempotency"""
    return f"test_{int(time.time())}_{operation}"

def test_register_user(gateway_url, access_token):
    """Test registerUser tool"""
    
    print("\n🧪 Testing registerUser...")
    
    timestamp = int(time.time())
    username = f"TestUser{timestamp}"
    # Generate proper 10-digit phone number
    mobile_no = f"+1555{timestamp % 10000000:07d}"
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "register-user-target___registerUser",
        {
            "username": username,
            "mobileNo": mobile_no,
            "userCity": "New York",
            "userPreference": {"cuisine": ["Italian"]},
            "requestId": generate_request_id("register")
        }
    )
    
    if "error" not in result:
        print("✅ registerUser - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            print(f"   Debug - Content: {content}")
            if isinstance(content, list) and len(content) > 0:
                text_content = content[0].get("text", "")
                print(f"   Debug - Text: {text_content}")
                if text_content:
                    user_result = json.loads(text_content)
                    user_id = user_result.get('userId')
                    error_msg = user_result.get('error')
                    if error_msg:
                        print(f"   Error from Lambda: {error_msg}")
                        return None, None
                    print(f"   User ID: {user_id}")
                    return user_id, mobile_no
            else:
                print(f"   Response: {content}")
        return None, None
    else:
        print(f"❌ registerUser - Failed: {result['error']}")
        return None, None

def test_search_user(gateway_url, access_token, mobile_no):
    """Test searchUserDetails tool"""
    
    print("\n🧪 Testing searchUserDetails...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "search-user-details-target___searchUserDetails",
        {"userMobileNo": mobile_no}
    )
    
    if "error" not in result:
        print("✅ searchUserDetails - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                user = json.loads(content[0]["text"])
                print(f"   Found user: {user.get('username', 'Unknown')}")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ searchUserDetails - Failed: {result['error']}")
        return False

def test_book_table(gateway_url, access_token, user_id):
    """Test bookATable tool"""
    
    print("\n🧪 Testing bookATable...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "book-a-table-target___bookATable",
        {
            "restaurantId": "rest_001",
            "userName": "Test User",
            "userMobileNo": "+1234567890",
            "date": "2024-12-25",
            "time": "19:00",
            "type": "Dinner",
            "cityName": "New York",
            "noOfGuests": 4,
            "tokenAmount": 100.0,
            "requestId": generate_request_id("booking")  # REQUIRED for idempotency
        }
    )
    
    if "error" not in result:
        print("✅ bookATable - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            print(f"   Debug - Content: {content}")
            if isinstance(content, list) and len(content) > 0:
                text_content = content[0].get("text", "")
                print(f"   Debug - Text: {text_content}")
                if text_content:
                    booking = json.loads(text_content)
                    booking_id = booking.get('bookingId')
                    error_msg = booking.get('error')
                    if error_msg:
                        print(f"   Error from Lambda: {error_msg}")
                        return None
                    print(f"   Booking ID: {booking_id}")
                    return booking_id
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ bookATable - Failed: {result['error']}")
        return None

def test_payment(gateway_url, access_token, booking_id, user_id):
    """Test paymentAPI tool"""
    
    print("\n🧪 Testing paymentAPI...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "payment-api-target___paymentAPI",
        {
            "userId": user_id,
            "restaurantId": "rest_001",
            "bookingId": booking_id,
            "tokenAmount": 100.0,
            "paymentMethod": "credit_card",
            "requestId": generate_request_id("payment")  # REQUIRED for idempotency
        }
    )
    
    if "error" not in result:
        print("✅ paymentAPI - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                payment = json.loads(content[0]["text"])
                print(f"   Payment Status: {payment.get('status', 'Unknown')}")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ paymentAPI - Failed: {result['error']}")
        return False

def test_book_restaurant(gateway_url, access_token):
    """Test bookRestaurant tool"""
    
    print("\n🧪 Testing bookRestaurant...")
    
    result = call_mcp_tool(
        gateway_url,
        access_token,
        "book-restaurant-target___bookRestaurant",
        {
            "restaurantId": "rest_001",
            "userDetails": {
                "name": "John Doe",
                "mobile": "+1234567890",
                "email": "john.doe@email.com"
            },
            "bookingDate": "2024-01-15",
            "bookingTime": "19:30",
            "numberOfGuests": 4
        }
    )
    
    if "error" not in result:
        print("✅ bookRestaurant - Success")
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                booking = json.loads(content[0]["text"])
                print(f"   Booking Reference: {booking.get('bookingReference', 'Unknown')}")
            else:
                print(f"   Response: {content}")
        return True
    else:
        print(f"❌ bookRestaurant - Failed: {result['error']}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of all MCP tools"""
    
    print("🧪 Comprehensive MCP Tools Testing")
    print("=" * 50)
    
    # Load configuration
    config = load_gateway_config()
    gateway_url = config['gateway_url']
    access_token = config['access_token']
    
    print(f"Gateway URL: {gateway_url}")
    print(f"Testing {8} MCP tools...\n")
    
    results = {}
    
    # Test restaurant discovery
    results['fetchRestaurants'] = test_fetch_restaurants(gateway_url, access_token)
    time.sleep(1)
    
    results['fetchRestaurantById'] = test_fetch_restaurant_by_id(gateway_url, access_token)
    time.sleep(1)
    
    results['tokenCalculation'] = test_token_calculation(gateway_url, access_token)
    time.sleep(1)
    
    # Test user management
    user_id, mobile_no = test_register_user(gateway_url, access_token)
    results['registerUser'] = user_id is not None
    time.sleep(1)
    
    if user_id:
        # Test search user
        results['searchUser'] = test_search_user(gateway_url, access_token, mobile_no)
        time.sleep(1)
        
        # Test booking with registered user
        booking_id = test_book_table(gateway_url, access_token, user_id)
        results['bookTable'] = booking_id is not None
        time.sleep(1)
        
        if booking_id:
            # Test payment
            results['payment'] = test_payment(gateway_url, access_token, booking_id, user_id)
            time.sleep(1)
    
    # Test simple booking - REMOVED (not registered as MCP tool)
    # results['bookRestaurant'] = test_book_restaurant(gateway_url, access_token)
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    success_count = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All MCP tools are working correctly!")
    else:
        print("⚠️  Some tools need attention")

if __name__ == "__main__":
    run_comprehensive_test()