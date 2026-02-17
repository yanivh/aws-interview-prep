"""
AWS Interview Prep - Lambda Function Handler
Main Lambda handler with API Gateway integration
"""
import base64
import json
import os
from typing import Dict, Any

from models import (
    GenerateQuestionRequest,
    EvaluateAnswerRequest,
    QuestionResponse,
    AnswerEvaluationResponse,
    TopicsResponse,
    FlashcardRequest,
    FlashcardResponse,
    LearningPlanResponse,
    ProgressRequest,
    ProgressResponse
)
from bedrock_service import BedrockService
from aws_context import AWSContext
from botocore.exceptions import ClientError

# Initialize services
bedrock_service = BedrockService()
aws_context = AWSContext()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for API Gateway events
    
    Routes requests to appropriate handlers based on HTTP method and path
    """
    try:
        # Handle OPTIONS for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse API Gateway event
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        # Parse request body (API Gateway may base64-encode it)
        body = {}
        raw_body = event.get('body')
        if raw_body:
            try:
                if event.get('isBase64Encoded'):
                    raw_body = base64.b64decode(raw_body).decode('utf-8')
                body = json.loads(raw_body) if isinstance(raw_body, str) else {}
            except (json.JSONDecodeError, TypeError, ValueError):
                body = {}
        
        # Route to appropriate handler
        if http_method == 'POST' and '/generate-question' in path:
            return handle_generate_question(body)
        elif http_method == 'POST' and '/evaluate-answer' in path:
            return handle_evaluate_answer(body)
        elif http_method == 'GET' and '/topics' in path:
            return handle_get_topics(query_parameters)
        elif http_method == 'GET' and '/flashcard' in path:
            return handle_get_flashcard(query_parameters)
        elif http_method == 'GET' and '/learning-plan' in path:
            return handle_get_learning_plan()
        elif http_method == 'GET' and '/progress' in path:
            return handle_get_progress(query_parameters)
        elif http_method == 'POST' and '/progress' in path:
            return handle_update_progress(body)
        else:
            return create_response(404, {'error': 'Not Found', 'path': path, 'method': http_method})
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        error_details = {
            'error': 'Internal Server Error',
            'message': str(e),
            'type': type(e).__name__
        }
        try:
            error_details['traceback'] = traceback.format_exc()
        except:
            pass
        return create_response(500, error_details)


def handle_generate_question(body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle question generation request"""
    try:
        # Validate request
        request = GenerateQuestionRequest(**body)
        
        # Generate question with refinement
        result = bedrock_service.generate_question(
            topic=request.topic,
            subtopic=request.subtopic,
            difficulty=request.difficulty
        )
        
        try:
            response = QuestionResponse(**result)
            # Handle both Pydantic v1 and v2
            response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
            return create_response(200, response_data)
        except Exception as e:
            print(f"Error creating QuestionResponse: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return the result directly if validation fails
            return create_response(200, result)
    
    except ValueError as e:
        return create_response(400, {'error': 'Invalid request', 'message': str(e)})
    except ClientError as e:
        err = e.response.get('Error', {})
        code = err.get('Code', '')
        msg = err.get('Message', str(e))
        print(f"Bedrock ClientError: {code} - {msg}")
        if 'AccessDenied' in code or 'access' in msg.lower():
            user_msg = (
                'AWS Bedrock model access denied. Enable the model in AWS Bedrock (eu-central-1): '
                'open Model catalog, select the Claude model, and submit use case details if prompted. '
                'See TROUBLESHOOTING.md for details.'
            )
        else:
            user_msg = msg
        return create_response(503, {'error': 'Service unavailable', 'message': user_msg})
    except Exception as e:
        print(f"Error generating question: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_response(500, {'error': 'Failed to generate question', 'message': str(e)})


def handle_evaluate_answer(body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle answer evaluation request"""
    try:
        # Validate request
        request = EvaluateAnswerRequest(**body)
        
        # Evaluate answer using Bedrock Agent
        result = bedrock_service.evaluate_answer(
            topic=request.topic,
            question=request.question,
            user_answer=request.user_answer,
            difficulty=request.difficulty
        )
        
        response = AnswerEvaluationResponse(**result)
        response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        return create_response(200, response_data)
    
    except ValueError as e:
        return create_response(400, {'error': 'Invalid request', 'message': str(e)})
    except Exception as e:
        print(f"Error evaluating answer: {str(e)}")
        return create_response(500, {'error': 'Failed to evaluate answer', 'message': str(e)})


def handle_get_topics(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle topics list request"""
    try:
        topics = aws_context.get_topics_structure()
        response = TopicsResponse(topics=topics)
        response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        return create_response(200, response_data)
    
    except Exception as e:
        print(f"Error getting topics: {str(e)}")
        return create_response(500, {'error': 'Failed to get topics', 'message': str(e)})


def handle_get_flashcard(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle flashcard generation request"""
    try:
        request = FlashcardRequest(**query_params)
        
        result = bedrock_service.generate_flashcard(
            topic=request.topic,
            subtopic=request.subtopic,
            difficulty=request.difficulty
        )
        
        response = FlashcardResponse(**result)
        response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        return create_response(200, response_data)
    
    except ValueError as e:
        return create_response(400, {'error': 'Invalid request', 'message': str(e)})
    except Exception as e:
        print(f"Error generating flashcard: {str(e)}")
        return create_response(500, {'error': 'Failed to generate flashcard', 'message': str(e)})


def handle_get_learning_plan() -> Dict[str, Any]:
    """Handle learning plan request"""
    try:
        learning_plan = aws_context.get_learning_plan()
        response = LearningPlanResponse(**learning_plan)
        response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        return create_response(200, response_data)
    
    except Exception as e:
        print(f"Error getting learning plan: {str(e)}")
        return create_response(500, {'error': 'Failed to get learning plan', 'message': str(e)})


def handle_get_progress(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle progress retrieval request (optional - can use localStorage)"""
    # This is optional as progress can be stored in localStorage
    # For now, return empty progress
    return create_response(200, {'progress': {}})


def handle_update_progress(body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle progress update request (optional - can use localStorage)"""
    # This is optional as progress can be stored in localStorage
    # For now, just acknowledge
    return create_response(200, {'status': 'ok'})


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response format"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Max-Age': '3600'
        },
        'body': json.dumps(body)
    }
