"""
Lambda function for handling post-confirmation signup actions
Uses the common layer for standardized logging, responses, and utilities
"""

import json
from datetime import datetime
from typing import Dict, Any

# Import from common layer
from common import (
    get_logger, 
    log_lambda_event, 
    log_error,
    create_success_response,
    create_error_response,
    with_cors
)

# Import shared utilities
import sys
import os
import boto3
from datetime import datetime

# Add paths for shared utilities (when available)
sys.path.append('/opt/python')  # Layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# Initialize logger
logger = get_logger(__name__)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for post-confirmation signup
    
    Args:
        event: Cognito post-confirmation trigger event
        context: Lambda context
    
    Returns:
        Modified event for Cognito
    """
    # Log event and context
    log_lambda_event(logger, event, context)
    
    try:
        # Extract user information from event
        user_id = event.get('userName')
        user_attributes = event.get('request', {}).get('userAttributes', {})
        
        if not user_id:
            logger.error("User ID not found in event")
            return event  # Return original event for Cognito triggers
        
        # Prepare user data for storage
        user_data = {
            'id': user_id,
            'email': user_attributes.get('email'),
            'email_verified': user_attributes.get('email_verified', 'false') == 'true',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'profile': {
                'given_name': user_attributes.get('given_name'),
                'family_name': user_attributes.get('family_name'),
                'name': user_attributes.get('name'),
            }
        }
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        user_data['profile'] = {k: v for k, v in user_data['profile'].items() if v is not None}
        
        # Store user in DynamoDB
        try:
            table_name = os.getenv('USER_TABLE_NAME')
            if table_name:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(table_name)
                table.put_item(Item=user_data)
                success = True
            else:
                logger.warning("USER_TABLE_NAME not configured")
                success = False
        except Exception as db_error:
            logger.error(f"DynamoDB error: {str(db_error)}")
            success = False
        
        if success:
            logger.info(f"Successfully created user profile for: {user_id}")
        else:
            logger.error(f"Failed to create user profile for: {user_id}")
            # Don't fail the Cognito trigger, just log the error
        
        # For Cognito triggers, always return the original event
        return event
        
    except Exception as e:
        log_error(logger, e, "Post-confirmation signup processing")
        # For Cognito triggers, return the original event even on error
        # to avoid blocking user registration
        return event

# Example of how this would be used in an API Gateway Lambda with CORS
@with_cors()
def api_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Example API Gateway handler using the common layer with CORS
    
    Args:
        event: API Gateway event
        context: Lambda context
    
    Returns:
        API Gateway response with CORS headers
    """
    log_lambda_event(logger, event, context)
    
    try:
        # Extract user ID from Authorization header or event
        auth_header = event.get('headers', {}).get('Authorization')
        if not auth_header:
            return create_error_response(
                error_message="Authorization header required",
                status_code=401
            )
        
        # For this example, we'll extract user ID from a simple token
        # In production, you'd validate the JWT token properly
        user_id = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        if not user_id:
            return create_error_response(
                error_message="Invalid token format",
                status_code=401
            )
        
        # Get user data from DynamoDB
        try:
            table_name = os.getenv('USER_TABLE_NAME')
            if not table_name:
                return create_error_response(
                    error_message="Database configuration error",
                    status_code=500
                )
            
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(table_name)
            response = table.get_item(Key={'id': user_id})
            user_data = response.get('Item')
            
            if not user_data:
                return create_error_response(
                    error_message="User not found",
                    status_code=404
                )
            
            return create_success_response(
                data=user_data,
                message="User data retrieved successfully"
            )
            
        except Exception as db_error:
            log_error(logger, db_error, "Database query failed")
            return create_error_response(
                error_message="Database error",
                status_code=500
            )
        
    except Exception as e:
        log_error(logger, e, "API request processing")
        return create_error_response(
            error_message="Internal server error",
            status_code=500
        )