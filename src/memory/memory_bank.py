"""Long-term memory storage for user preferences and history"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class MemoryBank:
    """Manages long-term storage for user preferences and learned patterns"""
    
    MAX_TOKENS = 1000  # Threshold for context compaction
    STORAGE_DIR = "memory_bank"
    
    # PII patterns for filtering
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    # Simplified address pattern
    ADDRESS_PATTERN = r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b'
    
    # Credential patterns
    API_KEY_PATTERN = r'(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)[\s:=]+["\']?([a-zA-Z0-9_\-]{20,})["\']?'
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or self.STORAGE_DIR
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> str:
        """Get file path for user data"""
        return os.path.join(self.storage_dir, f"{user_id}.json")
    
    def _load_user_data(self, user_id: str) -> dict:
        """Load user data from file"""
        file_path = self._get_user_file(user_id)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {
            "user_id": user_id,
            "preferences": {},
            "history": []
        }
    
    def _save_user_data(self, user_id: str, data: dict) -> None:
        """Save user data to file"""
        file_path = self._get_user_file(user_id)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def store_preference(self, user_id: str, key: str, value: Any) -> None:
        """Store a user preference"""
        data = self._load_user_data(user_id)
        data["preferences"][key] = value
        self._save_user_data(user_id, data)
    
    def get_preferences(self, user_id: str) -> dict:
        """Get all preferences for a user"""
        data = self._load_user_data(user_id)
        return data.get("preferences", {})
    
    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get a specific preference"""
        preferences = self.get_preferences(user_id)
        return preferences.get(key, default)
    
    def store_blueprint_summary(
        self,
        user_id: str,
        run_id: str,
        idea_title: str,
        summary: str
    ) -> None:
        """Store a blueprint summary in user history"""
        # Filter PII and credentials
        summary = self._filter_pii(summary)
        summary = self._filter_credentials(summary)
        
        # Compact if too long
        summary = self.compact_text(summary, self.MAX_TOKENS)
        
        data = self._load_user_data(user_id)
        
        history_entry = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "idea_title": idea_title,
            "summary": summary
        }
        
        data["history"].append(history_entry)
        
        # Keep only last 10 entries
        if len(data["history"]) > 10:
            data["history"] = data["history"][-10:]
        
        self._save_user_data(user_id, data)
    
    def get_user_history(self, user_id: str) -> List[dict]:
        """Get user's blueprint history"""
        data = self._load_user_data(user_id)
        return data.get("history", [])
    
    def compact_text(self, text: str, max_tokens: int) -> str:
        """
        Compact text if it exceeds max_tokens
        Simple approximation: ~4 characters per token
        """
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        
        # Truncate and add ellipsis
        return text[:max_chars - 3] + "..."
    
    def _filter_pii(self, text: str) -> str:
        """Filter out PII from text"""
        # Remove emails
        text = re.sub(self.EMAIL_PATTERN, '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(self.PHONE_PATTERN, '[PHONE]', text)
        
        # Remove addresses
        text = re.sub(self.ADDRESS_PATTERN, '[ADDRESS]', text, flags=re.IGNORECASE)
        
        return text
    
    def _filter_credentials(self, text: str) -> str:
        """Filter out API keys and credentials from text"""
        text = re.sub(self.API_KEY_PATTERN, r'\1: [REDACTED]', text)
        return text
    
    def validate_no_credentials(self, text: str) -> bool:
        """
        Validate that text doesn't contain credentials
        Returns True if safe, False if credentials detected
        """
        if re.search(self.API_KEY_PATTERN, text):
            return False
        return True
    
    def clear_user_data(self, user_id: str) -> None:
        """Clear all data for a user"""
        file_path = self._get_user_file(user_id)
        if os.path.exists(file_path):
            os.remove(file_path)


# Global memory bank instance
_memory_bank: Optional[MemoryBank] = None


def get_memory_bank() -> MemoryBank:
    """Get or create global memory bank instance"""
    global _memory_bank
    if _memory_bank is None:
        _memory_bank = MemoryBank()
    return _memory_bank
