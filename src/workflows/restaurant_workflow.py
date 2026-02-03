"""Restaurant booking workflow orchestration using LangGraph."""
import uuid
import os
from datetime import datetime
from langgraph.graph import StateGraph, END
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
from src.utils.state_persistence import StatePersistence, extract_state_snapshot, merge_states


app = BedrockAgentCoreApp()

# AgentCore CLI sets BEDROCK_AGENTCORE_MEMORY_ID automatically
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
state_persistence = StatePersistence(use_agentcore=bool(MEMORY_ID), memory_id=MEMORY_ID)


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
    
    # Entry router edges - route based on LLM-classified intent
    def route_after_entry(state):
        intent = state.get("intent", "search")
        if intent == "search":
            return "restaurant_finder"
        elif intent == "booking":
            return "booking_validation"
        elif intent == "history":
            return "retrieve_memory"
        else:
            return "END"
    
    workflow.add_conditional_edges(
        "entry_router",
        route_after_entry,
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
    def route_after_validation(state):
        # Check if more info needed (iterative collection)
        needs_more_info = state.get("needs_more_info", False)
        if needs_more_info:
            return "save_memory"  # Save partial state and ask for more
        
        # Only proceed if validation passed AND no HITL required
        validation_errors = state.get("validation_errors", [])
        requires_hitl = state.get("requires_hitl", False)
        
        if validation_errors or requires_hitl:
            return "END"
        return "user_management"
    
    workflow.add_conditional_edges(
        "booking_validation",
        route_after_validation,
        {
            "user_management": "user_management",
            "save_memory": "save_memory",
            "END": END
        }
    )
    workflow.add_edge("user_management", "token_calculation")
    workflow.add_edge("token_calculation", "booking_execution")
    workflow.add_edge("booking_execution", "save_memory")
    
    # Memory flows
    workflow.add_edge("save_memory", END)
    workflow.add_edge("retrieve_memory", END)
    
    return workflow.compile()  # No checkpointer - using StatePersistence instead


langgraph_workflow = create_restaurant_booking_workflow()


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint with state persistence."""
    from src.utils.logger import logger
    import json
    
    print("="*60, flush=True)
    print(f"🚀 AGENT INVOKED - {datetime.utcnow().isoformat()}", flush=True)
    print(f"📥 Payload: {json.dumps(payload, indent=2)}", flush=True)
    print(f"🔑 MEMORY_ID: {MEMORY_ID}", flush=True)
    print(f"💾 State persistence: {'AgentCore Memory' if MEMORY_ID else 'Local'}", flush=True)
    print("="*60, flush=True)
    
    logger.info(f"📥 Received payload: {payload}")
    logger.info(f"🔑 Using Memory ID: {MEMORY_ID}")
    
    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id", str(uuid.uuid4()))
    
    if len(session_id) < 33:
        logger.warning(f"Invalid session_id length ({len(session_id)}), generating new UUID")
        session_id = f"session_{uuid.uuid4()}"
    
    print(f"🎯 Session ID: {session_id}", flush=True)
    
    user_id = session_id
    correlation_id = f"req_{uuid.uuid4()}"
    conversation_history = payload.get("conversation_history", [])
    
    if not prompt:
        return "No prompt provided"
    
    # 1. Load previous state
    logger.info(f"🔍 Loading previous state for session: {session_id}")
    print(f"🔍 Loading state...", flush=True)
    previous_state = state_persistence.load_state(session_id)
    
    # 2. Merge with payload
    merged_state = merge_states(previous_state, payload)
    
    # 3. Build initial state
    initial_state = {
        "correlation_id": correlation_id,
        "user_id": user_id,
        "session_id": session_id,
        "messages": conversation_history,
        "prompt": prompt,
        "intent": "",
        "search_params": merged_state["search_params"],
        "restaurant_results": merged_state["restaurant_results"],
        "selected_restaurant": merged_state["selected_restaurant"],
        "booking_intent": False,
        "booking_details": merged_state["booking_details"],
        "user_details": {},
        "token_amount": 0,
        "booking_result": {},
        "payment_result": {},
        "compensation_stack": [],
        "final_response": "",
        "memory_status": "enabled",
        "requires_hitl": False,
        "hitl_reason": "",
        "validation_errors": [],
        "needs_more_info": False
    }
    
    # No config needed - StatePersistence handles state management
    
    try:
        # 4. Execute workflow (stateless execution)
        final_state = langgraph_workflow.invoke(initial_state)
        
        # 5. Save updated state
        state_snapshot = extract_state_snapshot(final_state)
        state_persistence.save_state(session_id, state_snapshot)
        
        # 6. Return structured response
        response = {
            "response": final_state.get("final_response", "No response generated."),
            "restaurant_results": final_state.get("restaurant_results", []),
            "search_params": final_state.get("search_params", {}),
            "booking_details": final_state.get("booking_details", {})
        }
        
        return json.dumps(response)
    
    except Exception as e:
        logger.error(f"❌ Workflow error: {str(e)}")
        return json.dumps({"response": f"Error: {str(e)}", "restaurant_results": [], "search_params": {}, "booking_details": {}})


print("✅ Restaurant Booking System initialized (Modular Architecture)")

if __name__ == "__main__":
    from src.utils.logger import logger
    logger.info("🚀 Starting Restaurant Booking Agent...")
    app.run()
