#!/usr/bin/env python3
"""Add test Indian restaurant in New York for complete workflow testing."""
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Restaurants')

restaurant = {
    'restaurantId': 'rest_indian_ny_001',
    'name': 'Spice Symphony',
    'cuisine': 'Indian',
    'city': 'New York',
    'location': {
        'address': '789 Broadway',
        'city': 'New York',
        'coordinates': {'lat': Decimal('40.7589'), 'lng': Decimal('-73.9851')}
    },
    'rating': Decimal('4.8'),
    'priceRange': '$$',
    'capacity': 60,
    'openHours': {
        'monday': '11:00-23:00',
        'tuesday': '11:00-23:00',
        'wednesday': '11:00-23:00',
        'thursday': '11:00-23:00',
        'friday': '11:00-00:00',
        'saturday': '12:00-00:00',
        'sunday': '12:00-22:00'
    },
    'description': 'Authentic North Indian cuisine with tandoori specialties',
    'menuCard': [
        {'category': 'Main Course', 'items': ['Butter Chicken', 'Lamb Rogan Josh', 'Paneer Tikka Masala']},
        {'category': 'Appetizers', 'items': ['Samosas', 'Pakoras']},
        {'category': 'Desserts', 'items': ['Gulab Jamun', 'Kheer']}
    ],
    'createdAt': datetime.utcnow().isoformat() + 'Z'
}

table.put_item(Item=restaurant)
print(f"✅ Added {restaurant['name']} - {restaurant['cuisine']} in {restaurant['city']}")
