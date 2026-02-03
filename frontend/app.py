import streamlit as st
import requests
import json
import sys
import uuid
from pathlib import Path

st.set_page_config(page_title="Restaurant Booking System", page_icon="🍽️", layout="wide")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

MEMORY_ID = "restaurant_booking_memory-mQq0w43dkO"

# Initialize session state with new session ID on app start
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4()}"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'restaurant_results' not in st.session_state:
    st.session_state.restaurant_results = []
if 'search_params' not in st.session_state:
    st.session_state.search_params = {}
if 'booking_details' not in st.session_state:
    st.session_state.booking_details = {}


def _safe_rerun():
    """Rerun the Streamlit script in a way that's compatible across versions.

    Prefer `st.experimental_rerun()` when available; fall back to raising the
    internal RerunException or calling `st.stop()`.
    """
    try:
        # Preferred API
        return st.experimental_rerun()
    except Exception:
        # Try raising the internal rerun exception (works in many Streamlit versions)
        try:
            from streamlit.runtime.scriptrunner.script_runner import RerunException
            raise RerunException()
        except Exception:
            # Last resort: stop execution (user will need to interact to continue)
            return st.stop()

# Header
st.title("🍽️ Restaurant Booking System")
st.caption("Powered by AWS Bedrock AgentCore Runtime")

# Sidebar
with st.sidebar:
    st.header("Session Info")
    st.text(f"Session: {st.session_state.session_id[:12]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    
    st.divider()
    st.subheader("Example Queries")
    st.code("Find Indian restaurants in New York")
    st.code("Book for 2 on 2026-02-15 at 19:00")
    st.code("My name is John, phone 1234567890")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.restaurant_results = []
        st.session_state.search_params = {}
        st.session_state.booking_details = {}
        _safe_rerun()

    if st.button("🔄 New Session"):
        st.session_state.session_id = f"session_{uuid.uuid4()}"
        st.session_state.messages = []
        st.session_state.restaurant_results = []
        st.session_state.search_params = {}
        st.session_state.booking_details = {}
        _safe_rerun()

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with AgentCore
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build conversation history
                conversation_history = []
                for msg in st.session_state.messages[:-1]:
                    conversation_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # Call local workflow directly
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from src.workflows.restaurant_workflow import invoke as invoke_workflow
                
                result = invoke_workflow({
                    "prompt": prompt,
                    "session_id": st.session_state.session_id,
                    "user_id": st.session_state.session_id,
                    "conversation_history": conversation_history
                })
                
                # Parse JSON response and extract only the conversational text
                if isinstance(result, str):
                    try:
                        result_json = json.loads(result)
                        response_text = result_json.get("response", result)
                        # Update session state for context
                        st.session_state.restaurant_results = result_json.get("restaurant_results", [])
                        st.session_state.search_params = result_json.get("search_params", {})
                        st.session_state.booking_details = result_json.get("booking_details", {})
                    except json.JSONDecodeError:
                        response_text = result
                else:
                    response_text = str(result)
                
                # Display response
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                # Debug info
                with st.expander("🔍 Debug Info"):
                    st.json({
                        "session_id": st.session_state.session_id,
                        "restaurants_found": len(st.session_state.restaurant_results),
                        "search_params": st.session_state.search_params,
                        "response_length": len(response_text)
                    })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Show full traceback
                import traceback
                with st.expander("🐛 Full Error"):
                    st.code(traceback.format_exc())
