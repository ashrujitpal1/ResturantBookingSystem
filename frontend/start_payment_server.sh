#!/bin/bash
# Start payment page server

echo "🌐 Starting Payment Page Server..."
echo "   Payment page: http://localhost:8502/payment.html"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8502
