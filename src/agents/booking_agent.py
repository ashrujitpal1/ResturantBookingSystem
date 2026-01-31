"""Booking agent - handles booking validation and execution with SAGA pattern."""
from datetime import datetime, timedelta
from src.config.models import RestaurantBookingState, CostOptimizedModelRouter
from src.tools.user_tools import search_user_tool, register_user_tool
from src.tools.booking_tools import calculate_token_amount_tool, book_table_tool, process_payment_tool


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number (10+ digits)."""
    import re
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10:
        return False, f"Phone must have 10+ digits (got {len(digits)})"
    return True, ""


def validate_date(date_str: str) -> tuple[bool, str]:
    """Validate booking date (future dates only)."""
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d")
        if booking_date.date() < datetime.now().date():
            return False, "Date must be in the future"
        if booking_date.date() > (datetime.now() + timedelta(days=90)).date():
            return False, "Date must be within 90 days"
        return True, ""
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)"


def validate_guests(num_guests: int) -> tuple[bool, str, bool]:
    """Validate guest count with governance policy, return (valid, error, requires_hitl)."""
    if num_guests < 1:
        return False, "Must have at least 1 guest", False
    
    if num_guests > 20:
        return False, "Maximum 20 guests allowed per booking", False
    
    if num_guests > 10:
        return True, "", True  # Valid but requires HITL
    
    return True, "", False


def booking_validation_node(state: RestaurantBookingState) -> dict:
    """Gather booking information and validate - uses Claude Sonnet for accuracy."""
    booking_details = state.get("booking_details", {})
    validation_errors = []
    missing_info = []
    requires_hitl = False
    hitl_reason = ""
    model = CostOptimizedModelRouter.select_model("booking_validation")
    prompt = state.get("prompt", "").lower()
    conversation_history = state.get("messages", [])
    
    # Extract restaurant context from conversation history using LLM
    restaurants = state.get("restaurant_results", [])
    
    # If no restaurants in state, use LLM to extract from conversation
    if not restaurants and conversation_history:
        import json
        import boto3
        
        # Build conversation context
        conv_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in conversation_history[-3:] if isinstance(msg, dict)])
        
        extraction_prompt = f"""Extract restaurant information from this conversation and return ONLY a JSON array.

Conversation:
{conv_text}

Return format (JSON array only, no other text):
[{{"name": "Restaurant Name", "rating": "4.5", "priceRange": "$$", "address": "123 Main St", "city": "City Name", "restaurantId": "rest_001"}}]

If no restaurants found, return: []"""
        
        try:
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            response = bedrock.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                body=json.dumps({
                    "messages": [{"role": "user", "content": extraction_prompt}],
                    "inferenceConfig": {"temperature": 0.1, "maxTokens": 500}
                })
            )
            result = json.loads(response['body'].read())
            extracted_text = result.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '[]')
            
            print(f"🔍 LLM Extraction Result: {extracted_text}")
            
            # Parse JSON from response
            restaurants = json.loads(extracted_text.strip())
            if not isinstance(restaurants, list):
                restaurants = []
            
            print(f"✅ Extracted {len(restaurants)} restaurants from conversation")
        except Exception as e:
            print(f"❌ LLM extraction failed: {e}")
            restaurants = []
    
    # Extract booking details from prompt
    if not booking_details:
        import re
        from datetime import datetime, timedelta
        
        # Extract restaurant name from conversation or prompt
        restaurant_name = ""
        
        # Try to find restaurant in extracted data
        if restaurants:
            restaurant_name = restaurants[0].get("name", "")
        
        # Extract guest count
        guests_match = re.search(r'(\d+)\s+(?:people|guests|persons)', prompt)
        if not guests_match:
            # Check for "alone", "myself", "solo"
            if any(word in prompt for word in ['alone', 'myself', 'solo', 'just me']):
                num_guests = 1
            else:
                num_guests = None
        else:
            num_guests = int(guests_match.group(1))
        
        # Extract date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', prompt)
        if date_match:
            booking_date = date_match.group(1)
        elif 'tomorrow' in prompt:
            booking_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif 'today' in prompt:
            booking_date = datetime.now().strftime("%Y-%m-%d")
        else:
            booking_date = None
        
        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2})', prompt)
        if time_match:
            booking_time = time_match.group(1)
        elif any(word in prompt for word in ['lunch', 'afternoon']):
            booking_time = "13:00"
        elif any(word in prompt for word in ['dinner', 'evening']):
            booking_time = "19:00"
        else:
            booking_time = None
        
        # Extract name
        name_match = re.search(r'(?:name is|i am|i\'m)\s+([a-z]+\s+[a-z]+)', prompt)
        user_name = name_match.group(1).title() if name_match else None
        
        # Extract email
        email_match = re.search(r'([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})', prompt)
        user_email = email_match.group(1) if email_match else ""
        
        # Extract phone
        phone_match = re.search(r'(?:phone|mobile|number)\s+([\d-]+)', prompt)
        user_mobile = phone_match.group(1) if phone_match else None
        
        booking_details = {
            "date": booking_date,
            "time": booking_time,
            "meal_type": "Dinner",
            "no_of_guests": num_guests,
            "user_mobile": user_mobile,
            "user_name": user_name,
            "user_email": user_email,
            "restaurant_name": restaurant_name
        }
    
    # Check for missing required information
    if not booking_details.get("restaurant_name"):
        missing_info.append("restaurant name")
    if not booking_details.get("date"):
        missing_info.append("date")
    if not booking_details.get("time"):
        missing_info.append("time")
    if not booking_details.get("no_of_guests"):
        missing_info.append("number of guests")
    if not booking_details.get("user_name"):
        missing_info.append("your name")
    if not booking_details.get("user_mobile"):
        missing_info.append("phone number")
    
    # If missing info, ask for it
    if missing_info:
        return {
            "booking_details": booking_details,
            "restaurant_results": restaurants,
            "validation_errors": [],
            "requires_hitl": False,
            "final_response": (
                f"Great! I'd love to help you book a table at {booking_details.get('restaurant_name', 'the restaurant')}.\n\n"
                f"I still need a few more details:\n\n" +
                "\n".join(f"• {info.title()}" for info in missing_info) +
                "\n\nPlease provide these details so I can complete your booking! 😊"
            )
        }
    
    # Validate phone
    phone_valid, phone_error = validate_phone(booking_details.get("user_mobile", ""))
    if not phone_valid:
        validation_errors.append(phone_error)
    
    # Validate date
    date_valid, date_error = validate_date(booking_details.get("date", ""))
    if not date_valid:
        validation_errors.append(date_error)
    
    # Validate guests (check HITL)
    guests_valid, guests_error, needs_hitl = validate_guests(booking_details.get("no_of_guests", 0))
    if not guests_valid:
        validation_errors.append(guests_error)
    if needs_hitl:
        requires_hitl = True
        hitl_reason = f"Large group booking ({booking_details.get('no_of_guests')} guests) requires manager approval"
    
    if validation_errors:
        return {
            "booking_details": booking_details,
            "restaurant_results": restaurants,
            "validation_errors": validation_errors,
            "requires_hitl": False,
            "final_response": f"❌ Oops! I need a bit more information:\n\n" + "\n".join(f"• {e}" for e in validation_errors) + "\n\nPlease provide the correct details and I'll help you complete the booking!"
        }
    
    if requires_hitl:
        return {
            "booking_details": booking_details,
            "restaurant_results": restaurants,
            "validation_errors": [],
            "requires_hitl": True,
            "hitl_reason": hitl_reason,
            "final_response": f"⏸️ {hitl_reason}\n\nA manager will review your request shortly. We'll get back to you within 24 hours to confirm your reservation. Thank you for your patience! 🙏"
        }
    
    return {
        "booking_details": booking_details,
        "restaurant_results": restaurants,
        "validation_errors": [],
        "requires_hitl": False,
        "model_used": model
    }


def user_management_node(state: RestaurantBookingState) -> dict:
    """Search or register user."""
    correlation_id = state.get("correlation_id")
    booking_details = state.get("booking_details", {})
    mobile = booking_details.get("user_mobile")
    
    try:
        parsed = search_user_tool(mobile)
        
        if not parsed or "error" in str(parsed).lower():
            parsed = register_user_tool(
                username=booking_details.get("user_name"),
                mobile=mobile,
                city="New York",
                preferences={"cuisine": ["Italian"]},
                correlation_id=correlation_id
            )
        
        return {"user_details": parsed}
    
    except Exception as e:
        return {"user_details": {}, "final_response": f"User management error: {str(e)}"}


def token_calculation_node(state: RestaurantBookingState) -> dict:
    """Calculate booking token amount."""
    correlation_id = state.get("correlation_id")
    booking_details = state.get("booking_details", {})
    
    try:
        parsed = calculate_token_amount_tool(
            num_guests=booking_details.get("no_of_guests", 2),
            meal_type=booking_details.get("meal_type", "Dinner"),
            tier="standard",
            correlation_id=correlation_id
        )
        
        token_amount = 0
        if "error" not in parsed:
            token_amount = parsed.get("totalAmount") or parsed.get("tokenAmount") or parsed.get("amount") or 0
            if isinstance(token_amount, str):
                try:
                    token_amount = float(token_amount)
                except ValueError:
                    token_amount = 0
        
        return {"token_amount": token_amount}
    
    except Exception as e:
        return {"token_amount": 0, "final_response": f"Token calculation error: {str(e)}"}


def booking_execution_node(state: RestaurantBookingState) -> dict:
    """Execute booking with SAGA pattern - uses Claude Sonnet for payment."""
    correlation_id = state.get("correlation_id")
    booking_details = state.get("booking_details", {})
    token_amount = state.get("token_amount", 0)
    model = CostOptimizedModelRouter.select_model("payment_processing")
    
    # Find restaurant by name from booking details
    restaurant_name = booking_details.get("restaurant_name", "")
    restaurants = state.get("restaurant_results", [])
    selected_restaurant = None
    
    if restaurant_name:
        for r in restaurants:
            if r.get("name", "").lower() == restaurant_name.lower():
                selected_restaurant = r
                break
    
    if not selected_restaurant and restaurants:
        selected_restaurant = restaurants[0]
    
    if not selected_restaurant:
        print(f"❌ DEBUG: No restaurant found. restaurant_name={restaurant_name}, restaurants={len(restaurants)}, booking_details={booking_details}")
        return {"final_response": f"❌ No restaurant selected for booking. Please start over by searching for restaurants first."}
    
    try:
        # Step 1: Book table
        booking_args = {
            "restaurantId": selected_restaurant.get("restaurantId", "rest_001"),
            "userName": booking_details.get("user_name"),
            "userMobileNo": booking_details.get("user_mobile"),
            "date": booking_details.get("date"),
            "time": booking_details.get("time"),
            "type": booking_details.get("meal_type"),
            "cityName": selected_restaurant.get("location", {}).get("city", "New York"),
            "noOfGuests": booking_details.get("no_of_guests"),
            "tokenAmount": token_amount
        }
        
        booking_parsed, error = book_table_tool(booking_args, correlation_id)
        
        if error:
            if error == "REQUIRES_HUMAN_APPROVAL":
                return {
                    "requires_hitl": True,
                    "hitl_reason": f"Large group booking requires approval",
                    "final_response": f"⏸️ Booking requires approval"
                }
            return {"final_response": f"❌ Policy violation: {error}"}
        
        booking_id = booking_parsed.get("bookingId") or booking_parsed.get("booking_id") or booking_parsed.get("id")
        if not booking_id:
            raise ValueError(f"No booking ID in response")
        
        # Step 2: Process payment
        try:
            user_details = state.get("user_details", {})
            payment_args = {
                "userId": user_details.get("userId", "user_001"),
                "restaurantId": selected_restaurant.get("restaurantId", "rest_001"),
                "bookingId": booking_id,
                "date": booking_details.get("date"),
                "time": booking_details.get("time"),
                "tokenAmount": token_amount,
                "paymentMethod": "credit_card"
            }
            
            payment_parsed, error = process_payment_tool(payment_args, correlation_id)
            
            if error:
                print(f"⚠️ Payment blocked: {error}. Cancelling booking.")
                return {"final_response": f"❌ Payment blocked: {error}. Booking cancelled."}
            
            payment_status = payment_parsed.get("paymentStatus") or payment_parsed.get("status") or "unknown"
            
            # Generate payment link
            payment_link = f"http://localhost:8502/payment.html?booking_id={booking_id}&amount={token_amount}"
            
            return {
                "booking_result": booking_parsed,
                "payment_result": payment_parsed,
                "final_response": (
                    f"✅ **Booking Confirmed!**\n\n"
                    f"🏪 Restaurant: {selected_restaurant.get('name')}\n"
                    f"📅 Date: {booking_details.get('date')}\n"
                    f"🕒 Time: {booking_details.get('time')}\n"
                    f"👥 Guests: {booking_details.get('no_of_guests')}\n"
                    f"🎫 Booking ID: {booking_id}\n\n"
                    f"💰 **Token Amount: ${token_amount}**\n"
                    f"This token amount will be adjusted from your final bill.\n\n"
                    f"🔗 **Complete Payment:** {payment_link}\n\n"
                    f"Once payment is completed, you'll receive a confirmation with all details! 🍽️"
                ),
                "model_used": model
            }
        
        except Exception as payment_error:
            print(f"Payment failed, compensating: {payment_error}")
            return {"final_response": f"❌ Payment failed. Booking cancelled."}
    
    except Exception as e:
        return {"final_response": f"Booking error: {str(e)}"}
