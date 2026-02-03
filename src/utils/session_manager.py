"""Session management with property file persistence."""
import uuid
import os
from pathlib import Path
from typing import Optional


class SessionManager:
    """Manages session IDs and API configuration via .properties file."""
    
    PROPERTIES_FILE = Path.home() / ".restaurant_booking" / "session.properties"
    
    @staticmethod
    def _ensure_properties_dir():
        """Create properties directory if it doesn't exist."""
        SessionManager.PROPERTIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID (33+ characters)."""
        return f"session_{uuid.uuid4()}"  # 45 chars total
    
    @staticmethod
    def load_or_create_session() -> tuple[str, str]:
        """Load session_id and api_url from properties file, or create new.
        
        Returns:
            tuple[str, str]: (session_id, api_url)
        """
        SessionManager._ensure_properties_dir()
        
        session_id = None
        api_url = None
        
        # Try to load existing properties
        if SessionManager.PROPERTIES_FILE.exists():
            with open(SessionManager.PROPERTIES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('session_id='):
                        session_id = line.split('=', 1)[1]
                    elif line.startswith('api_url='):
                        api_url = line.split('=', 1)[1]
        
        # Generate new session_id if not found or invalid
        if not session_id or len(session_id) < 33:
            session_id = SessionManager.generate_session_id()
        
        # Default API URL (can be overridden in properties file)
        if not api_url:
            api_url = os.getenv(
                "AGENTCORE_API_URL",
                "arn:aws:bedrock-agentcore:us-east-1:696072349808:runtime/restaurant_discovery_agent-VCrIJ15seV"
            )
        
        # Save to properties file
        SessionManager.save_properties(session_id, api_url)
        
        return session_id, api_url
    
    @staticmethod
    def save_properties(session_id: str, api_url: str):
        """Save session_id and api_url to properties file."""
        SessionManager._ensure_properties_dir()
        
        with open(SessionManager.PROPERTIES_FILE, 'w') as f:
            f.write(f"# Restaurant Booking System Session Configuration\n")
            f.write(f"# Generated: {uuid.uuid4()}\n\n")
            f.write(f"session_id={session_id}\n")
            f.write(f"api_url={api_url}\n")
    
    @staticmethod
    def get_session_id() -> str:
        """Get current session_id from properties file."""
        session_id, _ = SessionManager.load_or_create_session()
        return session_id
    
    @staticmethod
    def get_api_url() -> str:
        """Get API URL from properties file."""
        _, api_url = SessionManager.load_or_create_session()
        return api_url
    
    @staticmethod
    def reset_session() -> str:
        """Generate and save a new session_id."""
        new_session_id = SessionManager.generate_session_id()
        api_url = SessionManager.get_api_url()
        SessionManager.save_properties(new_session_id, api_url)
        return new_session_id
