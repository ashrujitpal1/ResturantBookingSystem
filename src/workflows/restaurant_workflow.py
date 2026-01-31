"""Restaurant booking workflow orchestration using LangGraph."""
import uuid
import random
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from src.config.models import RestaurantBookingState
from src.agents.restaurant_finder import entry_router_node, restaurant_finder_node
from src.agents.booking_agent import (
    booking_validation_node,
    user_management_node,
    token_calculation_node,
    booking_execution_node
)
from src.agents.memory_agent import retrieve_memory_node, save_memory_node


app = BedrockAgentCoreApp()


def create_restaurant_booking_workflow():
    """Create LangGraph workflow for restaurant booking."""
    workflow = StateGraph(RestaurantBookingState)
    
    # Add nodes
    workflow.add_node("entry_router", entry_router_node)
    workflow.add_node("restaurant_finder", restaurant_finder_node)
    workflow.add_node("booking_validation", booking_validation_node)
    workflow.add_node("user_management", user_management_node)
    workflow.add_node("token_calculation", token_calculation_node)
    workflow.add_node("booking_execution", booking_execution_node)
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("save_memory", save_memory_node)
    
    # Set entry point
    workflow.set_entry_point("entry_router")
    
    # Entry router edges
    workflow.add_conditional_edges(
        "entry_router",
        lambda state: state.get("next", "END"),
        {
            "restaurant_finder": "restaurant_finder",
            "booking_validation": "booking_validation",
            "retrieve_memory": "retrieve_memory",
            "END": END
        }
    )
    
    # Restaurant finder handoff
    workflow.add_conditional_edges(
        "restaurant_finder",
        lambda state: "booking_validation" if state.get("booking_intent") else "save_memory",
        {
            "booking_validation": "booking_validation",
            "save_memory": "save_memory"
        }
    )
    
    # Booking flow with validation gate
    workflow.add_conditional_edges(
        "booking_validation",
        lambda state: "END" if (state.get("validation_errors") or state.get("requires_hitl")) else "user_management",
        {
            "user_management": "user_management",
            "END": END
        }
    )
    workflow.add_edge("user_management", "token_calculation")
    workflow.add_edge("token_calculation", "booking_execution")
    workflow.add_edge("booking_execution", "save_memory")
    
    # Memory flows
    workflow.add_edge("save_memory", END)
    workflow.add_edge("retrieve_memory", END)
    
    return workflow.compile(checkpointer=MemorySaver())


langgraph_workflow = create_restaurant_booking_workflow()


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint with memory support."""
    from src.utils.logger import logger
    logger.info(f"📥 Received payload: {payload}")
    
    prompt = payload.get("prompt", "")
    user_id = payload.get("user_id", "default_user")
    session_id = payload.get("session_id", f"session_{uuid.uuid4()}")
    correlation_id = f"req_{uuid.uuid4()}"
    
    # Get conversation history from memory
    conversation_history = payload.get("conversation_history", [])
    
    if not prompt:
        return "No prompt provided"
    
    # Get previous booking details from conversation context
    previous_booking = {}
    for msg in conversation_history:
        if "booking_details" in str(msg):
            # Extract any previous booking info
            pass
    
    initial_state = {
        "correlation_id": correlation_id,
        "user_id": user_id,
        "session_id": session_id,
        "messages": conversation_history,
        "prompt": prompt,
        "intent": "",
        "search_params": payload.get("search_params", {}),
        "restaurant_results": payload.get("restaurant_results", []),
        "selected_restaurant": {},
        "booking_intent": False,
        "booking_details": payload.get("booking_details", previous_booking),
        "user_details": {},
        "token_amount": 0,
        "booking_result": {},
        "payment_result": {},
        "compensation_stack": [],
        "final_response": "",
        "memory_status": "enabled",
        "requires_hitl": False,
        "hitl_reason": "",
        "validation_errors": []
    }
    
    config = {"configurable": {"thread_id": f"thread_{random.randint(1000, 9999)}"}}
    
    try:
        final_state = langgraph_workflow.invoke(initial_state, config)
        
        # Return response with context for Streamlit
        response = {
            "response": final_state.get("final_response", "No response generated."),
            "restaurant_results": final_state.get("restaurant_results", []),
            "search_params": final_state.get("search_params", {}),
            "booking_details": final_state.get("booking_details", {})
        }
        
        # For CLI compatibility, return just the response text
        # AgentCore will serialize the full response
        return final_state.get("final_response", "No response generated.")
    
    except Exception as e:
        logger.error(f"❌ Workflow error: {str(e)}")
        return f"Error: {str(e)}"


print("✅ Restaurant Booking System initialized (Modular Architecture)")

if __name__ == "__main__":
    from src.utils.logger import logger
    logger.info("🚀 Starting Restaurant Booking Agent...")
    app.run()
