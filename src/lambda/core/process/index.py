import json
import os
import boto3
from typing import Dict, Any
from decimal import Decimal
from common import (
    get_logger, 
    with_cors, 
    create_success_response, 
    create_error_response,
    log_lambda_event
)

logger = get_logger(__name__)
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('PROCESS_TABLE_NAME')
table = dynamodb.Table(table_name)


def convert_floats_to_decimal(obj: Any) -> Any:
    """
    Recursively convert float values to Decimal for DynamoDB compatibility
    """
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj


@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process handler - Saves process data to DynamoDB
    """
    log_lambda_event(logger, event, context)
    
    try:
        # Parse request body
        body = event.get('body', '{}')
        process_data = json.loads(body) if isinstance(body, str) else body
        
        # Validate required fields
        if not process_data.get('processId'):
            return create_error_response(
                error_message='processId is required',
                status_code=400,
                error_code='MISSING_PROCESS_ID'
            )
        
        # Convert floats to Decimal for DynamoDB
        process_data_converted = convert_floats_to_decimal(process_data)
        
        # Prepare item for DynamoDB
        item = {
            'id': process_data_converted['processId'],
            'createdAt': process_data_converted.get('createdAt', ''),
            **process_data_converted
        }
        
        # Save to DynamoDB
        table.put_item(Item=item)
        
        logger.info(f"Process saved successfully: {process_data_converted['processId']}")
        
        return create_success_response(
            data={'processId': process_data_converted['processId']},
            message='Process saved successfully'
        )
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return create_error_response(
            error_message='Invalid JSON format',
            status_code=400,
            error_code='INVALID_JSON'
        )
    
    except Exception as e:
        logger.error(f"Error saving process: {str(e)}")
        return create_error_response(
            error_message='Failed to save process',
            status_code=500,
            error_code='PROCESS_SAVE_ERROR'
        )