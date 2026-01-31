# Restaurant Booking System - Frontend UI

A Streamlit-based chat interface for the Restaurant Booking System powered by AWS Bedrock AgentCore.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify AgentCore is Deployed
```bash
agentcore status
```

### 3. Start Both Servers

**Terminal 1 - Streamlit App:**
```bash
streamlit run app.py
```

**Terminal 2 - Payment Server:**
```bash
./start_payment_server.sh
```

The Streamlit app will open at `http://localhost:8501`  
Payment page will be available at `http://localhost:8502/payment.html`

## Features

- 🔍 **Search Restaurants** - Find restaurants by cuisine and city
- 📅 **Make Bookings** - Book tables with automatic payment processing  
- 📜 **View History** - Check your booking history
- 💬 **Natural Language Chat** - Conversational interface

## Example Queries

### Search Restaurants
```
Find Indian restaurants in New York
Show me Italian restaurants in Chicago
Find Thai food in San Francisco
```

### Make a Booking
```
Book a table for 4 at Spice Symphony on 2026-02-15 at 19:00. My name is John Doe, phone 5551234567
```

### View History
```
Show my booking history
```

## Architecture

The frontend connects to the deployed AgentCore agent via AWS Bedrock Agent Runtime API:
- **Agent ID**: `restaurant_discovery_agent-r6pGwNGe49`
- **Region**: `us-east-1`
- **Session Management**: Maintains conversation context across queries

## Troubleshooting

**Error: "Could not connect to agent"**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check agent is deployed: `agentcore status`

**Error: "Access Denied"**
- Ensure IAM user has `bedrock:InvokeAgent` permission
