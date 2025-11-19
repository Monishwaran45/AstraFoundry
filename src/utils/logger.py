"""Structured logging module for AstraFoundry"""

import logging
import json
from datetime import datetime
from typing import Optional, Any


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage()
        }
        
        # Add optional fields if present
        if hasattr(record, 'agent'):
            log_data['agent'] = record.agent
        if hasattr(record, 'run_id'):
            log_data['run_id'] = record.run_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with structured formatting"""
    logger = logging.getLogger(name)
    
    # Only add handler if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler with structured formatting
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


class AgentLogger:
    """Logger wrapper for agent-specific logging"""
    
    def __init__(self, agent_name: str, run_id: Optional[str] = None):
        self.agent_name = agent_name
        self.run_id = run_id
        self.logger = get_logger(agent_name)
    
    def info(self, message: str, duration_ms: Optional[int] = None, **kwargs):
        """Log info message with agent context"""
        extra = {'agent': self.agent_name}
        if self.run_id:
            extra['run_id'] = self.run_id
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with agent context"""
        extra = {'agent': self.agent_name}
        if self.run_id:
            extra['run_id'] = self.run_id
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with agent context"""
        extra = {'agent': self.agent_name}
        if self.run_id:
            extra['run_id'] = self.run_id
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with agent context"""
        extra = {'agent': self.agent_name}
        if self.run_id:
            extra['run_id'] = self.run_id
        if kwargs:
            extra['extra_data'] = kwargs
        
        self.logger.debug(message, extra=extra)
