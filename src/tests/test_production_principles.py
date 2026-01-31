import json
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lambda'))

class TestIdempotency:
    """Test idempotency implementation"""
    
    @patch('book_a_table.check_idempotency')
    @patch('book_a_table.store_idempotency')
    def test_duplicate_booking_returns_cached_response(self, mock_store, mock_check):
        """Same requestId should return cached response"""
        from book_a_table import lambda_handler
        
        cached = {
            'statusCode': 200,
            'body': json.dumps({'bookingId': 'booking_123'})
        }
        mock_check.return_value = cached
        
        event = {
            'body': json.dumps({
                'requestId': 'req_duplicate',
                'restaurantId': 'rest_001',
                'userName': 'John',
                'userMobileNo': '1234567890',
                'date': '2024-12-25',
                'type': 'Dinner',
                'cityName': 'NYC',
                'noOfGuests': 4,
                'tokenAmount': 100.0
            })
        }
        
        result = lambda_handler(event, None)
        assert result == cached
        mock_check.assert_called_once_with('req_duplicate')
    
    def test_missing_request_id_returns_400(self):
        """Missing requestId should return 400 error"""
        from book_a_table import lambda_handler
        
        event = {
            'body': json.dumps({
                'restaurantId': 'rest_001',
                'userName': 'John'
            })
        }
        
        result = lambda_handler(event, None)
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'requestId' in body['error']


class TestDeterministicBehavior:
    """Test deterministic payment processing"""
    
    def test_same_request_id_produces_same_result(self):
        """Same requestId should always produce same payment result"""
        from payment_api import process_payment
        
        request_id = 'req_test_123'
        result1 = process_payment(100.0, 'credit_card', request_id)
        result2 = process_payment(100.0, 'credit_card', request_id)
        
        assert result1 == result2


class TestSchemaValidation:
    """Test strict input validation"""
    
    def test_invalid_guest_count_rejected(self):
        """Guest count outside 1-20 range should be rejected"""
        from utils import validate_guests
        
        is_valid, error = validate_guests(0)
        assert not is_valid
        assert '1 and 20' in error
        
        is_valid, error = validate_guests(25)
        assert not is_valid
    
    def test_invalid_phone_rejected(self):
        """Invalid phone format should be rejected"""
        from utils import validate_phone
        
        is_valid, error = validate_phone('123')
        assert not is_valid
        assert '10 digits' in error


class TestOutputSizeLimits:
    """Test output size enforcement"""
    
    @patch('fetch_restaurant_details.table')
    def test_restaurant_results_limited_to_50(self, mock_table):
        """Should return max 50 restaurants"""
        from fetch_restaurant_details import lambda_handler, MAX_RESULTS
        
        # Mock 100 restaurants
        mock_restaurants = [{'restaurantId': f'rest_{i}', 'rating': 4.5} for i in range(100)]
        mock_table.scan.return_value = {'Items': mock_restaurants}
        
        event = {'queryStringParameters': {}}
        result = lambda_handler(event, None)
        
        body = json.loads(result['body'])
        assert len(body['restaurants']) == MAX_RESULTS


class TestHITL:
    """Test Human-in-the-Loop for large groups"""
    
    @patch('book_a_table.check_idempotency')
    @patch('book_a_table.store_idempotency')
    def test_large_group_requires_approval(self, mock_store, mock_check):
        """Groups >10 should require manual approval"""
        from book_a_table import lambda_handler
        
        mock_check.return_value = None
        
        event = {
            'body': json.dumps({
                'requestId': 'req_large_group',
                'restaurantId': 'rest_001',
                'userName': 'John',
                'userMobileNo': '1234567890',
                'date': '2024-12-25',
                'type': 'Dinner',
                'cityName': 'NYC',
                'noOfGuests': 15,
                'tokenAmount': 500.0
            })
        }
        
        result = lambda_handler(event, None)
        assert result['statusCode'] == 202
        body = json.loads(result['body'])
        assert body['requiresApproval'] is True


class TestCircuitBreaker:
    """Test circuit breaker pattern"""
    
    @patch('payment_api.check_circuit')
    def test_circuit_open_rejects_requests(self, mock_check):
        """Open circuit should reject payment requests"""
        from payment_api import lambda_handler, CircuitBreakerOpen
        
        mock_check.side_effect = CircuitBreakerOpen("Circuit open")
        
        event = {
            'body': json.dumps({
                'requestId': 'req_payment',
                'userId': 'user_001',
                'restaurantId': 'rest_001',
                'tokenAmount': 100.0
            })
        }
        
        result = lambda_handler(event, None)
        assert result['statusCode'] == 503
        body = json.loads(result['body'])
        assert 'circuit breaker' in body['error'].lower()


class TestBoundedExecution:
    """Test timeout configurations"""
    
    def test_timeout_values_in_sam_template(self):
        """Verify SAM template has correct timeouts"""
        import yaml
        
        with open('../../template.yaml', 'r') as f:
            template = yaml.safe_load(f)
        
        resources = template['Resources']
        
        assert resources['FetchRestaurantDetailsFunction']['Properties']['Timeout'] == 5
        assert resources['TokenAmountCalculationFunction']['Properties']['Timeout'] == 2
        assert resources['BookATableFunction']['Properties']['Timeout'] == 10
        assert resources['PaymentAPIFunction']['Properties']['Timeout'] == 15


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
