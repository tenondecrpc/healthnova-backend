import json
import boto3
import os
from typing import Dict, Any
from common import get_logger, with_cors, create_success_response, create_error_response

logger = get_logger(__name__)
s3_client = boto3.client('s3')
bucket_name = os.environ.get('PHOTOS_BUCKET_NAME')

@with_cors()
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Received event: {json.dumps(event, default=str)}")
    
    try:        
        body = event.get('body', '{}')
        logger.info(f"Request body: {body}")

        body_params = json.loads(body) if body else {}
        file_name = body_params.get('fileName', '')
        file_type = body_params.get('fileType', '')

        if not file_name or not file_type:
            logger.warning(f"Missing parameters - fileName: {file_name}, fileType: {file_type}")
            return create_error_response(
                error_message='fileName and fileType are required',
                status_code=400,
                error_code='MISSING_PARAMETERS'
            )
            
        presigned_post = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=file_name,
            Fields={"Content-Type": file_type},
            Conditions=[
                {"Content-Type": file_type},
                ["content-length-range", 0, 10485760]  # Max 10MB
            ],
            ExpiresIn=300  # 5 minutes
        )

        return create_success_response(
            data=presigned_post,
            message='Upload URL generated successfully'
        )
    
    except Exception as e:
        logger.error(f"Error generating upload URL: {str(e)}")
        return create_error_response(
            error_message='Failed to generate upload URL',
            status_code=500,
            error_code='PRESIGNED_URL_ERROR'
        )