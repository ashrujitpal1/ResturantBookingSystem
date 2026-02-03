"""Booking agent - handles booking validation and execution with SAGA pattern."""
from datetime import datetime, timedelta
from aws_xray_sdk.core import xray_recorder
from src.config.models import RestaurantBookingState, CostOptimizedModelRouter
from src.tools.user_tools import search_user_tool, register_user_tool
from src.tools.booking_tools import calculate_token_amount_tool, book_table_tool
from src.utils.logger import logger
from src.utils.llm_helpers import extract_booking_details
import re


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number (10+ digits)."""
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


def validate_guests(num_guests) -> tuple[bool, str, bool]:
    """Validate guest count with governance policy, return (valid, error, requires_hitl)."""
    if num_guests is None:
        return False, "Number of guests is required", False
    
    try:
        num_guests = int(num_guests)
    except (ValueError, TypeError):
        return False, "Number of guests must be a valid number", False
    
    if num_guests < 1:
        return False, "Must have at least 1 guest", False
    if num_guests > 20:
        return False, "Maximum 20 guests allowed per booking", False
    if num_guests > 10:
        return True, "", True
    
    return True, "", False


@xray_recorder.capture('booking_validation_node')
def booking_validation_node(state: RestaurantBookingState) -> dict:
    """Gather booking information and validate - uses LLM for extraction."""
    from src.tools.restaurant_tools import fetch_restaurants_tool, fetch_restaurant_by_id_tool
    
    booking_details = state.get("booking_details", {})
    validation_errors = []
    missing_info = []
    requires_hitl = False
    hitl_reason = ""
    model = CostOptimizedModelRouter.select_model("booking_validation")
    prompt = state.get("prompt", "")
    conversation_history = state.get("messages", [])
    correlation_id = state.get("correlation_id", "")
    
    logger.info(f"🔍 booking_validation_node: prompt={prompt[:50]}, history_len={len(conversation_history)}")
    print(f"\n🔍 BOOKING VALIDATION: prompt={prompt}", flush=True)
    print(f"🔍 booking_details={booking_details}", flush=True)
    
    # Get restaurants from state
    restaurants = state.get("restaurant_results", [])
    logger.info(f"🔍 restaurants from state: {len(restaurants)}")
    print(f"🔍 restaurants from state: {len(restaurants)}", flush=True)
    
    # Extract booking details using LLM - ALWAYS extract to get latest info
    extracted = extract_booking_details(prompt, conversation_history, model, correlation_id)
    print(f"🔍 LLM extracted: {extracted}", flush=True)
    
    # Merge with existing booking_details (new values override old)
    booking_details = {**booking_details, **extracted}
    
    # If restaurant name not extracted but we have restaurants in state, use first one
    if not booking_details.get("restaurant_name") and restaurants:
        booking_details["restaurant_name"] = restaurants[0].get("name", "")
    
    # If no restaurants in state but restaurant name provided, search for it
    if not restaurants and booking_details.get("restaurant_name"):
        restaurant_name = booking_details["restaurant_name"]
        logger.info(f"🔍 No restaurants in state, searching for: {restaurant_name}")
        
        # Try to extract cuisine/city from prompt or use defaults
        search_params = state.get("search_params", {})
        extracted_params = extract_booking_details(prompt, conversation_history, model, correlation_id)
        
        city = search_params.get("city") or extracted_params.get("city") or "New York"
        cuisine = search_params.get("cuisine") or extracted_params.get("cuisine") or "Italian"
        
        try:
            result = fetch_restaurants_tool(city=city, cuisine=cuisine, correlation_id=correlation_id)
            restaurants = result.get("restaurants", [])
            
            # Filter by restaurant name if we got results
            if restaurants:
                matched = [r for r in restaurants if restaurant_name.lower() in r.get("name", "").lower()]
                if matched:
                    restaurants = matched
                    logger.info(f"✅ Found {len(restaurants)} matching restaurants")
        except Exception as e:
            logger.error(f"Failed to search restaurants: {e}")
    
    # Check for missing required information
    if not booking_details.get("restaurant_name") or booking_details.get("restaurant_name").strip() == "":
        missing_info.append("restaurant name")
    if not booking_details.get("date") or booking_details.get("date").strip() == "":
        missing_info.append("date (YYYY-MM-DD format)")
    if not booking_details.get("time") or booking_details.get("time").strip() == "":
        missing_info.append("time (HH:MM format, e.g., 19:00)")
    if not booking_details.get("no_of_guests"):
        missing_info.append("number of guests")
    if not booking_details.get("user_name") or booking_details.get("user_name").strip() == "":
        missing_info.append("your name")
    if not booking_details.get("user_mobile") or booking_details.get("user_mobile").strip() == "":
        missing_info.append("phone number")
    
    # If missing info, persist partial state and ask for it
    if missing_info:
        print(f"❌ Missing info: {missing_info}", flush=True)
        return {
            "booking_details": booking_details,
            "restaurant_results": restaurants,
            "validation_errors": [],
            "requires_hitl": False,
            "needs_more_info": True,
            "final_response": (
                f"Great! I'd love to help you book a table at {booking_details.get('restaurant_name', 'the restaurant')}.\n\n"
                f"I still need a few more details:\n\n" +
                "\n".join(f"• {info.title()}" for info in missing_info) +
                "\n\nPlease provide these details so I can complete your booking! 😊"
            )
        }
    
    # Validate phone (only check digit count, not pattern)
    phone_valid, phone_error = validate_phone(booking_details.get("user_mobile", ""))
    if not phone_valid:
        validation_errors.append(phone_error)
    
    # Validate date
    date_valid, date_error = validate_date(booking_details.get("date", ""))
    if not date_valid:
        validation_errors.append(date_error)
    
    # Validate guests (check HITL)
    num_guests = booking_details.get("no_of_guests")
    guests_valid, guests_error, needs_hitl = validate_guests(num_guests)
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


@xray_recorder.capture('user_management_node')
def user_management_node(state: RestaurantBookingState) -> dict:
    """Search or register user with idempotency."""
    correlation_id = state.get("correlation_id")
    booking_details = state.get("booking_details", {})
    mobile = booking_details.get("user_mobile")
    
    try:
        parsed = search_user_tool(
            mobile=mobile,
            requestId=f"{correlation_id}_search_user_1"
        )
        
        if not parsed or "error" in str(parsed).lower():
            parsed = register_user_tool(
                username=booking_details.get("user_name"),
                mobile=mobile,
                city="New York",
                preferences={"cuisine": ["Italian"]},
                requestId=f"{correlation_id}_register_user_1"
            )
        
        return {"user_details": parsed}
    
    except Exception as e:
        logger.error(f"[{correlation_id}] User management error: {e}")
        return {"user_details": {}, "final_response": f"User management error: {str(e)}"}


@xray_recorder.capture('token_calculation_node')
def token_calculation_node(state: RestaurantBookingState) -> dict:
    """Calculate booking token amount with idempotency."""
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
        logger.error(f"[{correlation_id}] Token calculation error: {e}")
        return {"token_amount": 0, "final_response": f"Token calculation error: {str(e)}"}


@xray_recorder.capture('booking_execution_node')
def booking_execution_node(state: RestaurantBookingState) -> dict:
    """Execute booking with SAGA pattern."""
    correlation_id = state.get("correlation_id")
    booking_details = state.get("booking_details", {})
    user_details = state.get("user_details", {})
    token_amount = state.get("token_amount", 0)
    restaurants = state.get("restaurant_results", [])
    
    restaurant_name = booking_details.get("restaurant_name", "")
    selected_restaurant = None
    
    if restaurant_name and restaurants:
        for r in restaurants:
            if r.get("name", "").lower() == restaurant_name.lower():
                selected_restaurant = r
                break
        if not selected_restaurant:
            for r in restaurants:
                if restaurant_name.lower() in r.get("name", "").lower():
                    selected_restaurant = r
                    break
    
    if not selected_restaurant and restaurants:
        selected_restaurant = restaurants[0]
        logger.warning(f"[{correlation_id}] Restaurant '{restaurant_name}' not found, using default: {selected_restaurant.get('name')}")
    
    if not selected_restaurant:
        return {
            "final_response": "❌ No restaurants available. Please search again.",
            "booking_result": {}
        }
    
    num_guests = booking_details.get("no_of_guests")
    if num_guests is None:
        return {
            "final_response": "❌ Missing number of guests. Please provide booking details.",
            "booking_result": {}
        }
    
    try:
        booking_args = {
            "restaurantId": selected_restaurant.get("restaurantId", "R001"),
            "userName": booking_details.get("user_name", "Guest"),
            "userMobileNo": booking_details.get("user_mobile", "0000000000"),
            "date": booking_details.get("date"),
            "time": booking_details.get("time"),
            "type": booking_details.get("meal_type", "Dinner"),
            "cityName": selected_restaurant.get("city", "New York"),
            "noOfGuests": int(num_guests),
            "tokenAmount": token_amount
        }
        print(f"📤 Booking args: {booking_args}", flush=True)
        
        booking_result, error = book_table_tool(booking_args, correlation_id)
        
        if error or "error" in booking_result:
            return {
                "final_response": f"❌ Booking failed: {error or booking_result.get('error')}.",
                "booking_result": {}
            }
        
        booking_id = booking_result.get("bookingId") or booking_result.get("booking_id")
        
        return {
            "booking_result": booking_result,
            "selected_restaurant": selected_restaurant,
            "final_response": (
                f"✅ Booking confirmed!\n\n"
                f"📍 Restaurant: {selected_restaurant.get('name')}\n"
                f"📅 Date: {booking_details.get('date')}\n"
                f"🕐 Time: {booking_details.get('time')}\n"
                f"👥 Guests: {booking_details.get('no_of_guests')}\n"
                f"💰 Amount: ${token_amount}\n\n"
                f"Booking ID: {booking_id}\n\n"
                f"See you soon! 🎉"
            )
        }
    
    except Exception as e:
        logger.error(f"[{correlation_id}] Booking execution failed: {e}")
        return {
            "final_response": f"❌ Booking failed: {str(e)}",
            "booking_result": {}
        }
