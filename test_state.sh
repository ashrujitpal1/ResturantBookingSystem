#!/bin/bash
SESSION="test-state-$(date +%s)"

echo "Testing State Persistence"
echo "Session: $SESSION"
echo ""

echo "1. Search for restaurants:"
agentcore invoke "{\"prompt\": \"Find Italian restaurants in NYC\", \"session_id\": \"$SESSION\"}" 2>&1 | grep -A 3 "Response:"

sleep 3

echo ""
echo "2. Book (should remember restaurants):"
agentcore invoke "{\"prompt\": \"Book Italian Bistro for 2 people\", \"session_id\": \"$SESSION\"}" 2>&1 | grep -A 10 "Response:"
