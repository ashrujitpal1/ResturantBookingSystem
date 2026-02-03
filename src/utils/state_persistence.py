"""State persistence layer - works locally and with AgentCore Memory."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from src.utils.logger import logger


class StatePersistence:
    """Unified state persistence - local file or AgentCore Memory."""
    
    def __init__(self, use_agentcore: bool = False, memory_id: Optional[str] = None):
        self.use_agentcore = use_agentcore
        self.memory_id = memory_id
        self.local_storage_path = Path.home() / ".restaurant_booking" / "state"
        
        if not use_agentcore:
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Using local state storage: {self.local_storage_path}")
        else:
            from bedrock_agentcore.memory import MemoryClient
            self.memory_client = MemoryClient()
            logger.info(f"☁️ Using AgentCore Memory: {memory_id}")
    
    def load_state(self, session_id: str) -> Dict[str, Any]:
        """Load previous state for session."""
        if self.use_agentcore:
            return self._load_from_agentcore(session_id)
        else:
            return self._load_from_file(session_id)
    
    def save_state(self, session_id: str, state: Dict[str, Any]):
        """Save state for session."""
        if self.use_agentcore:
            self._save_to_agentcore(session_id, state)
        else:
            self._save_to_file(session_id, state)
    
    def _load_from_file(self, session_id: str) -> Dict[str, Any]:
        """Load state from local file."""
        state_file = self.local_storage_path / f"{session_id}.json"
        
        if not state_file.exists():
            logger.info(f"📭 No previous state for session: {session_id}")
            return {}
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            logger.info(f"✅ Loaded state from file: {session_id}")
            return state
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")
            return {}
    
    def _save_to_file(self, session_id: str, state: Dict[str, Any]):
        """Save state to local file."""
        state_file = self.local_storage_path / f"{session_id}.json"
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"✅ Saved state to file: {session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def _load_from_agentcore(self, session_id: str) -> Dict[str, Any]:
        """Load state from AgentCore Memory using list_events."""
        try:
            print(f"🔍 Loading from AgentCore Memory: session={session_id}", flush=True)
            
            events = self.memory_client.list_events(
                memory_id=self.memory_id,
                actor_id=session_id,
                session_id=session_id,
                max_results=10,
                include_payload=True
            )
            
            print(f"📦 Found {len(events)} events", flush=True)
            
            if not events:
                logger.info(f"📭 No previous state in AgentCore Memory: {session_id}")
                return {}
            
            # Find the most recent state event
            for event in reversed(events):
                payload = event.get('payload', [])
                for item in payload:
                    # Handle both 'conversational' and 'conversationalMessage' keys
                    msg = item.get('conversational') or item.get('conversationalMessage')
                    if msg:
                        role = msg.get('role')
                        content = msg.get('content', {})
                        
                        # Handle both string content and dict with 'text' key
                        if isinstance(content, dict):
                            content_text = content.get('text', '')
                        else:
                            content_text = content
                        
                        if role == 'TOOL' and 'STATE:' in content_text:
                            state_json = content_text.replace('STATE:', '').strip()
                            state = json.loads(state_json)
                            logger.info(f"✅ Loaded state from AgentCore Memory: {session_id}")
                            print(f"✅ State loaded: {len(state.get('restaurant_results', []))} restaurants", flush=True)
                            return state
            
            logger.info(f"📭 No state found in events: {session_id}")
            return {}
        
        except Exception as e:
            logger.error(f"❌ Failed to load from AgentCore Memory: {e}")
            print(f"❌ Load error: {e}", flush=True)
            return {}
    
    def _save_to_agentcore(self, session_id: str, state: Dict[str, Any]):
        """Save state to AgentCore Memory using create_event."""
        try:
            print(f"💾 Saving to AgentCore Memory: session={session_id}", flush=True)
            
            # Store state as a TOOL message (our custom state marker)
            state_json = json.dumps(state)
            
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=session_id,
                session_id=session_id,
                messages=[
                    (f"STATE:{state_json}", "TOOL")
                ]
            )
            
            logger.info(f"✅ Saved state to AgentCore Memory: {session_id}")
            print(f"✅ State saved: {len(state.get('restaurant_results', []))} restaurants", flush=True)
        except Exception as e:
            logger.error(f"❌ Failed to save to AgentCore Memory: {e}")
            print(f"❌ Save error: {e}", flush=True)


def extract_state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only the fields needed for persistence."""
    return {
        "restaurant_results": state.get("restaurant_results", []),
        "search_params": state.get("search_params", {}),
        "booking_details": state.get("booking_details", {}),
        "selected_restaurant": state.get("selected_restaurant", {}),
        "last_intent": state.get("intent", ""),
        "timestamp": datetime.utcnow().isoformat()
    }


def merge_states(previous: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Merge previous state with payload state.
    
    Priority: payload > previous > empty
    """
    merged = {
        "restaurant_results": (
            payload.get("restaurant_results") or 
            previous.get("restaurant_results") or 
            []
        ),
        "search_params": {
            **previous.get("search_params", {}),
            **payload.get("search_params", {})
        },
        "booking_details": {
            **previous.get("booking_details", {}),
            **payload.get("booking_details", {})
        },
        "selected_restaurant": (
            payload.get("selected_restaurant") or 
            previous.get("selected_restaurant") or 
            {}
        )
    }
    
    logger.info(f"🔀 Merged state: {len(merged['restaurant_results'])} restaurants")
    return merged
