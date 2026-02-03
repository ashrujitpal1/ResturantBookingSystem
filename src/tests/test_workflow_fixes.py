"""Workflow validation tests to verify fixes."""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

class TestConditionalEdgeRouting:
    """Test that conditional edges route correctly based on intent."""
    
    def test_entry_router_search_intent(self):
        """Test that search intent routes to restaurant_finder."""
        from src.workflows.restaurant_workflow import create_restaurant_booking_workflow
        from src.config.models import RestaurantBookingState
        
        workflow = create_restaurant_booking_workflow()
        
        initial_state = {
            "correlation_id": "test_001",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "prompt": "Find Italian restaurants",
            "intent": "search",  # ✅ Should route to restaurant_finder
            "search_params": {},
            "restaurant_results": [],
            "selected_restaurant": {},
            "booking_intent": False,
            "booking_details": {},
            "user_details": {},
            "token_amount": 0,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        config = {"configurable": {"thread_id": f"session_{initial_state['session_id']}"}}
        
        with patch('src.agents.restaurant_finder.fetch_restaurants_tool') as mock_fetch:
            mock_fetch.return_value = {
                "restaurants": [
                    {"name": "Mario's", "cuisine": "Italian", "rating": 4.5}
                ]
            }
            
            result = workflow.invoke(initial_state, config)
            
            # Should have called restaurant finder and got results
            assert "restaurant_results" in result
            assert len(result['restaurant_results']) > 0
    
    def test_entry_router_booking_intent(self):
        """Test that booking intent routes to booking_validation."""
        from src.agents.restaurant_finder import entry_router_node
        from src.config.models import RestaurantBookingState
        
        state = {
            "correlation_id": "test_002",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "prompt": "I want to book a table",
            "intent": "",
            "search_params": {},
            "restaurant_results": [{"name": "Mario's", "restaurantId": "R001"}],
            "selected_restaurant": {},
            "booking_intent": False,
            "booking_details": {},
            "user_details": {},
            "token_amount": 0,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        with patch('src.utils.llm_helpers.classify_intent') as mock_classify:
            mock_classify.return_value = {
                "intent": "booking",
                "confidence": 0.95
            }
            
            result = entry_router_node(state)
            
            # Should preserve restaurant context
            assert result.get("intent") == "booking"
            assert result.get("booking_intent") == True
            assert "restaurant_results" in result
            assert len(result['restaurant_results']) > 0


class TestStateContextPreservation:
    """Test that state context is preserved through transitions."""
    
    def test_restaurant_results_preserved_to_booking(self):
        """Test that restaurant_results survive entry_router → booking_validation."""
        from src.agents.restaurant_finder import entry_router_node
        
        restaurants = [
            {"name": "Mario's", "restaurantId": "R001", "cuisine": "Italian"},
            {"name": "Sakura", "restaurantId": "R002", "cuisine": "Japanese"}
        ]
        
        state = {
            "prompt": "Book a table",
            "intent": "",
            "restaurant_results": restaurants,
            "search_params": {"city": "NYC", "cuisine": "Italian"},
            "correlation_id": "test_003",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "selected_restaurant": {},
            "booking_intent": False,
            "booking_details": {},
            "user_details": {},
            "token_amount": 0,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        with patch('src.utils.llm_helpers.classify_intent') as mock_classify:
            mock_classify.return_value = {"intent": "booking"}
            
            result = entry_router_node(state)
            
            # Verify context preservation
            assert result['restaurant_results'] == restaurants
            assert result['search_params'] == {"city": "NYC", "cuisine": "Italian"}
            assert len(result['restaurant_results']) == 2


class TestBookingExecutionErrors:
    """Test error handling in booking execution."""
    
    def test_missing_restaurant_fallback(self):
        """Test that booking execution falls back to first restaurant if name not found."""
        from src.agents.booking_agent import booking_execution_node
        
        state = {
            "correlation_id": "test_004",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "prompt": "",
            "intent": "booking",
            "search_params": {},
            "restaurant_results": [
                {"name": "Mario's", "restaurantId": "R001"},
                {"name": "Sakura", "restaurantId": "R002"}
            ],
            "selected_restaurant": {},
            "booking_intent": True,
            "booking_details": {
                "restaurant_name": "NonExistent",  # ❌ Doesn't match
                "date": "2024-12-25",
                "time": "7:00 PM",
                "no_of_guests": 4,
                "user_name": "John",
                "user_mobile": "5551234567"
            },
            "user_details": {"userId": "U001"},
            "token_amount": 100,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        with patch('src.agents.booking_agent.book_table_tool') as mock_book:
            with patch('src.agents.booking_agent.process_payment_tool') as mock_pay:
                mock_book.return_value = ({"bookingId": "B001"}, "")
                mock_pay.return_value = ({"paymentId": "P001"}, "")
                
                result = booking_execution_node(state)
                
                # Should still succeed with fallback restaurant
                assert "✅ Booking confirmed" in result['final_response']
                mock_book.assert_called_once()
                # Verify it used first restaurant as fallback
                call_args = mock_book.call_args[0][0]
                assert call_args['restaurantId'] == 'R001'


class TestLLMResponseParsing:
    """Test LLM response parsing error handling."""
    
    def test_string_response_parsing(self):
        """Test that string JSON responses are properly parsed."""
        from src.utils.llm_helpers import extract_booking_details
        
        with patch('src.utils.llm_helpers.get_bedrock_provider') as mock_provider:
            mock_llm = MagicMock()
            # Return string instead of dict
            mock_llm.invoke.return_value = '{"restaurant_name": "Mario\'s", "date": "2024-12-25"}'
            mock_provider.return_value = mock_llm
            
            result = extract_booking_details(
                "Book Mario's for 4 on Dec 25",
                [],
                correlation_id="test_005"
            )
            
            # Should parse string to dict
            assert isinstance(result, dict)
            assert result.get('restaurant_name') == "Mario's"
            assert result.get('date') == "2024-12-25"
    
    def test_invalid_json_fallback(self):
        """Test that invalid JSON returns empty dict without crashing."""
        from src.utils.llm_helpers import extract_booking_details
        
        with patch('src.utils.llm_helpers.get_bedrock_provider') as mock_provider:
            mock_llm = MagicMock()
            # Return invalid JSON
            mock_llm.invoke.return_value = 'not valid json at all'
            mock_provider.return_value = mock_llm
            
            result = extract_booking_details(
                "Book a table",
                [],
                correlation_id="test_006"
            )
            
            # Should return empty dict, not crash
            assert result == {}


class TestValidationErrors:
    """Test booking validation error handling."""
    
    def test_validation_prevents_progression(self):
        """Test that validation errors prevent progression to user_management."""
        from src.agents.booking_agent import booking_validation_node
        
        state = {
            "correlation_id": "test_007",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "prompt": "Book for 0 guests",
            "intent": "booking",
            "search_params": {},
            "restaurant_results": [{"name": "Mario's"}],
            "selected_restaurant": {},
            "booking_intent": True,
            "booking_details": {
                "restaurant_name": "Mario's",
                "date": "2024-12-25",
                "time": "7:00 PM",
                "no_of_guests": 0,  # ❌ Invalid
                "user_name": "John",
                "user_mobile": "5551234567"
            },
            "user_details": {},
            "token_amount": 0,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        result = booking_validation_node(state)
        
        # Should have validation errors
        assert len(result['validation_errors']) > 0
        assert "❌" in result['final_response']


class TestHistoryRouting:
    """Test memory/history intent routing."""
    
    def test_history_intent_routes_to_memory(self):
        """Test that history intent routes to retrieve_memory."""
        from src.agents.restaurant_finder import entry_router_node
        
        state = {
            "prompt": "Show my booking history",
            "intent": "",
            "correlation_id": "test_008",
            "user_id": "user_123",
            "session_id": "a" * 33,
            "messages": [],
            "search_params": {},
            "restaurant_results": [],
            "selected_restaurant": {},
            "booking_intent": False,
            "booking_details": {},
            "user_details": {},
            "token_amount": 0,
            "booking_result": {},
            "payment_result": {},
            "compensation_stack": [],
            "final_response": "",
            "memory_status": "",
            "requires_hitl": False,
            "hitl_reason": "",
            "validation_errors": []
        }
        
        with patch('src.utils.llm_helpers.classify_intent') as mock_classify:
            mock_classify.return_value = {"intent": "history"}
            
            result = entry_router_node(state)
            
            assert result['intent'] == "history"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
