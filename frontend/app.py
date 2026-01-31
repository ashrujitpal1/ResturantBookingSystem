import streamlit as st
import boto3
import json
from datetime import datetime
import subprocess

# Agent configuration
AGENT_NAME = "restaurant_discovery_agent"

st.set_page_config(page_title="Restaurant Booking System", page_icon="🍽️", layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
if 'context' not in st.session_state:
    st.session_state.context = {"restaurant_results": [], "booking_details": {}, "search_params": {}}

# Header
st.title("🍽️ Restaurant Booking System")
st.caption("Powered by AWS Bedrock AgentCore")

# Sidebar with quick actions
with st.sidebar:
    st.header("Quick Actions")
    
    if st.button("🔍 Search Restaurants"):
        st.session_state.quick_action = "search"
    if st.button("📅 Make Booking"):
        st.session_state.quick_action = "booking"
    if st.button("📜 View History"):
        st.session_state.quick_action = "history"
    
    st.divider()
    st.subheader("Example Queries")
    st.code("Find Indian restaurants in New York")
    st.code("Book a table for 4 at Spice Symphony on 2026-02-15 at 19:00")
    st.code("Show my booking history")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.context = {"restaurant_results": [], "booking_details": {}, "search_params": {}}
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about restaurants..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call AgentCore via CLI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build conversation history from messages (exclude current prompt)
                conversation_history = []
                for msg in st.session_state.messages[:-1]:  # Exclude the current user message
                    role = "user" if msg["role"] == "user" else "assistant"
                    conversation_history.append({"role": role, "content": msg["content"]})
                
                # Debug: Show what we're sending
                st.write(f"DEBUG: Sending {len(conversation_history)} history messages")
                if conversation_history:
                    st.write(f"DEBUG: Last history message: {conversation_history[-1]['content'][:100]}...")
                
                # Build payload with full conversation context
                payload = {
                    "prompt": prompt,
                    "user_id": "streamlit_user",
                    "session_id": st.session_state.session_id,
                    "conversation_history": conversation_history
                }
                
                # Pass payload as JSON string
                payload_json = json.dumps(payload)
                
                result = subprocess.run(
                    ['agentcore', 'invoke', payload_json],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd='/Users/USER/Work/AI/AgentCore/ResturantBookingSystem'
                )
                
                if result.returncode != 0:
                    error_msg = f"AgentCore CLI error:\n{result.stderr}\n{result.stdout}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.stop()
                
                # Extract response from output
                output = result.stdout
                if "Response:" in output:
                    response_text = output.split("Response:")[1].strip()
                else:
                    response_text = output.strip()
                
                # Convert payment links to clickable links
                if "http://localhost:8501/payment" in response_text:
                    # Extract payment link and make it clickable
                    import re
                    link_match = re.search(r'(http://localhost:8501/payment[^\s]+)', response_text)
                    if link_match:
                        payment_link = link_match.group(1)
                        # Replace with markdown link
                        response_text = response_text.replace(
                            payment_link,
                            f"[Click here to complete payment]({payment_link.replace('8501', '8502')})"
                        )
                        # Also add a button
                        response_text += f"\n\n[Open Payment Page]({payment_link.replace('8501', '8502')}){{:target='_blank'}}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Handle quick actions
if hasattr(st.session_state, 'quick_action'):
    action = st.session_state.quick_action
    if action == "search":
        st.chat_input("Find Italian restaurants in New York")
    elif action == "booking":
        st.chat_input("Book a table for 2 at [Restaurant Name] on [Date] at [Time]")
    elif action == "history":
        st.chat_input("Show my booking history")
    delattr(st.session_state, 'quick_action')
