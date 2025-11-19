"""Code execution tool adapter for financial calculations"""

import sys
import io
import time
from typing import Dict, Any
from contextlib import redirect_stdout, redirect_stderr
from src.utils.logger import get_logger


class CodeExecutionAdapter:
    """Adapter for executing Python code safely"""
    
    TIMEOUT_SECONDS = 5
    
    def __init__(self):
        self.logger = get_logger("CodeExecutionAdapter")
    
    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute code and return results
        Returns {output, error, execution_time_ms}
        """
        if language != "python":
            return {
                'output': '',
                'error': f"Unsupported language: {language}",
                'execution_time_ms': 0
            }
        
        start_time = time.time()
        
        try:
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Create a restricted namespace for execution
            namespace = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'dict': dict,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'round': round,
                    'abs': abs,
                }
            }
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            # Extract any variables that were created
            result_vars = {
                k: v for k, v in namespace.items()
                if not k.startswith('__') and k != '__builtins__'
            }
            
            # If there's a 'result' variable, include it in output
            if 'result' in result_vars:
                output += f"\nResult: {result_vars['result']}"
            
            self.logger.info(f"Code executed successfully in {execution_time_ms}ms")
            
            return {
                'output': output,
                'error': error if error else None,
                'execution_time_ms': execution_time_ms,
                'variables': result_vars
            }
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"Code execution failed: {error_msg}")
            
            return {
                'output': '',
                'error': error_msg,
                'execution_time_ms': execution_time_ms
            }
    
    def execute_calculation(self, expression: str) -> Any:
        """
        Execute a simple calculation and return the result
        Convenience method for financial calculations
        """
        code = f"result = {expression}"
        result = self.execute(code)
        
        if result['error']:
            raise ValueError(f"Calculation failed: {result['error']}")
        
        return result.get('variables', {}).get('result')
