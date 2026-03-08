import logging
import json
import os
from typing import Optional, Dict, Any

def setup_logger(name: Optional[str] = None, level: Optional[str] = None) -> logging.Logger:
    """
    Setup standardized logger for Lambda functions
    
    Args:
        name: Logger name (defaults to calling module name)
        level: Log level (defaults to LOG_LEVEL env var or INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with standard configuration
    
    Args:
        name: Logger name (defaults to calling module name)
    
    Returns:
        Logger instance
    """
    return setup_logger(name)

def log_lambda_event(logger: logging.Logger, event: Dict[str, Any], context: Any = None) -> None:
    """
    Log Lambda event and context information
    
    Args:
        logger: Logger instance
        event: Lambda event
        context: Lambda context (optional)
    """
    logger.info(f"Lambda event: {json.dumps(event, default=str)}")
    
    if context:
        logger.info(f"Lambda context - Request ID: {context.aws_request_id}")
        logger.info(f"Lambda context - Function name: {context.function_name}")
        logger.info(f"Lambda context - Remaining time: {context.get_remaining_time_in_millis()}ms")

def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None) -> None:
    """
    Log error with context information
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    
    logger.error(error_msg, exc_info=True)
