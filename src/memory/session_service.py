"""Session management service for AstraFoundry"""

import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from src.models import Session


class SessionService:
    """Manages short-term session state for pipeline executions"""
    
    TTL_HOURS = 24  # Time to live for failed sessions
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
    
    def create_session(self, user_id: str) -> Session:
        """Create a new session with UUID-based session ID"""
        session_id = str(uuid.uuid4())
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            agent_outputs={},
            status='active'
        )
        
        with self._lock:
            self._sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        with self._lock:
            return self._sessions.get(session_id)
    
    def store_agent_output(
        self,
        session_id: str,
        agent_name: str,
        output: Dict[str, Any]
    ) -> None:
        """Store agent output in session with thread-safe access"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.agent_outputs[agent_name] = output
    
    def get_agent_output(
        self,
        session_id: str,
        agent_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific agent output from session"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.agent_outputs.get(agent_name)
        return None
    
    def get_full_context(self, session_id: str) -> Dict[str, Any]:
        """Get all agent outputs for a session"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.agent_outputs.copy()
        return {}
    
    def update_session_status(self, session_id: str, status: str) -> None:
        """Update session status"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = status
    
    def cleanup_session(self, session_id: str) -> None:
        """Remove session immediately (for successful completions)"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up failed sessions older than TTL
        Returns number of sessions cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=self.TTL_HOURS)
        cleaned_count = 0
        
        with self._lock:
            expired_sessions = [
                session_id
                for session_id, session in self._sessions.items()
                if session.status == 'failed' and session.created_at < cutoff_time
            ]
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
                cleaned_count += 1
        
        return cleaned_count
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        with self._lock:
            return len(self._sessions)
    
    def get_sessions_by_user(self, user_id: str) -> list[Session]:
        """Get all sessions for a specific user"""
        with self._lock:
            return [
                session
                for session in self._sessions.values()
                if session.user_id == user_id
            ]


# Global session service instance
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get or create global session service instance"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
