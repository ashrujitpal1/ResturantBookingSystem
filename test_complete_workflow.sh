#!/bin/bash
# Complete end-to-end test for Restaurant Booking System

echo "🧪 Testing Complete Restaurant Booking Workflow"
echo "================================================"
echo ""

echo "📍 Step 1: Search for Indian restaurant in New York"
echo "---------------------------------------------------"
agentcore invoke 'Find me an Indian restaurant in New York'
echo ""
echo ""

echo "📅 Step 2: Book a table at the restaurant"
echo "-------------------------------------------"
agentcore invoke 'Book a table for 4 people at Spice Symphony on 2026-02-15 at 19:00. My name is John Doe, email john@example.com, phone 555-1234'
echo ""
echo ""

echo "📜 Step 3: Check booking history"
echo "---------------------------------"
agentcore invoke 'Show me my booking history'
echo ""
echo ""

echo "✅ Complete workflow test finished!"
