"""Base agent class for all AstraFoundry agents"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from src.models import AgentOutput, get_schema_for_agent, validate_schema
from src.utils.logger import AgentLogger


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_name: str):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent (e.g., 'idea_agent')
        """
        self.agent_name = agent_name
        self.logger = AgentLogger(agent_name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute agent logic and return structured output
        
        Args:
            context: Dictionary containing input data and previous agent outputs
        
        Returns:
            AgentOutput with execution results
        """
        pass
    
    def run(self, context: Dict[str, Any], run_id: Optional[str] = None) -> AgentOutput:
        """
        Run the agent with validation and timing
        
        Args:
            context: Input context
            run_id: Optional run ID for logging
        
        Returns:
            AgentOutput with results
        """
        if run_id:
            self.logger.run_id = run_id
        
        start_time = time.perf_counter()  # Use perf_counter for better precision
        
        try:
            # Validate input
            if not self.validate_input(context):
                raise ValueError(f"Invalid input context for {self.agent_name}")
            
            self.logger.info(f"Starting execution")
            
            # Execute agent logic
            output = self.execute(context)
            
            # Calculate execution time with microsecond precision
            execution_time_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            output.execution_time_ms = execution_time_ms
            
            # Validate output
            is_valid, error_msg = self.validate_output(output.data)
            if not is_valid:
                self.logger.warning(f"Output validation warning: {error_msg}")
            
            self.logger.info(
                f"Execution completed",
                duration_ms=execution_time_ms,
                status=output.status
            )
            
            return output
        
        except Exception as e:
            execution_time_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            self.logger.error(f"Execution failed: {error_msg}")
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=execution_time_ms,
                status='failed',
                data={},
                error=error_msg
            )
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        Validate input context
        
        Args:
            context: Input context dictionary
        
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - ensure context is a dict
        if not isinstance(context, dict):
            return False
        
        # Subclasses can override for specific validation
        return True
    
    def validate_output(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate output data against schema
        
        Args:
            data: Output data dictionary
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = get_schema_for_agent(self.agent_name)
        if schema:
            return validate_schema(data, schema)
        return True, None
    
    def _get_from_context(
        self,
        context: Dict[str, Any],
        key: str,
        default: Any = None
    ) -> Any:
        """
        Safely get a value from context
        
        Args:
            context: Context dictionary
            key: Key to retrieve
            default: Default value if key not found
        
        Returns:
            Value from context or default
        """
        return context.get(key, default)
    
    def _get_agent_output(
        self,
        context: Dict[str, Any],
        agent_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get output from a previous agent
        
        Args:
            context: Context dictionary
            agent_name: Name of the agent whose output to retrieve
        
        Returns:
            Agent output data or None
        """
        agent_outputs = context.get('agent_outputs', {})
        return agent_outputs.get(agent_name)
