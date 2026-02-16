"""
Example implementation showing async migration pattern
This is a reference file showing how to convert the current sync code to async
"""

import json
import os
import asyncio
import aioboto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError


class AsyncBedrockService:
    """Async version of BedrockService using aioboto3"""
    
    def __init__(self):
        self.region = os.environ.get('AWS_REGION', 'eu-central-1')
        self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        self.agent_id = os.environ.get('BEDROCK_AGENT_ID', '')
        self.agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
        
        # Create session for reuse (more efficient)
        self.session = aioboto3.Session()
        
        print(f"AsyncBedrockService initialized with model_id: {self.model_id}, region: {self.region}")
    
    async def generate_question(self, topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """
        Two-step refinement process to generate high-quality interview questions (async)
        
        Step 1: Generate 3 candidate questions with answers
        Step 2: Refine and select the best question-answer pair
        """
        # Step 1: Generate candidates
        candidates = await self._generate_question_candidates(topic, subtopic, difficulty)
        
        # Step 2: Refine and select
        refined = await self._refine_question_candidates(candidates, topic, subtopic, difficulty)
        
        return refined
    
    async def _generate_question_candidates(self, topic: str, subtopic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Step 1: Generate 3 candidate questions with comprehensive answers (async)"""
        
        # Build prompt (same as before)
        system_prompt = "Your system prompt here"
        aws_context = "Your AWS context here"
        difficulty_instructions = self._get_difficulty_instructions(difficulty)
        
        prompt = f"""{system_prompt}

{aws_context}

Difficulty: {difficulty.capitalize()}
{difficulty_instructions}

Generate 3 AWS Systems Engineer interview questions about {topic} - {subtopic} ({difficulty} level).

**CRITICAL: Return ONLY JSON array. NO text before/after. Start with [ and end with ].**
...
"""
        
        # Call Bedrock (async)
        response = await self._invoke_bedrock_model(prompt)
        
        # Parse response (same as before)
        extracted = self._extract_json_from_response(response)
        # ... rest of parsing logic same as sync version
        
        return candidates
    
    async def _refine_question_candidates(self, candidates: List[Dict[str, Any]], topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """Step 2: Evaluate and refine candidates to select best question (async)"""
        
        prompt = f"""Evaluate 3 AWS Systems Engineer interview questions and select/improve the best one.
...
"""
        
        # Call Bedrock (async)
        response = await self._invoke_bedrock_model(prompt)
        
        # Parse response (same as before)
        refined = self._extract_json_from_response(response)
        # ... rest of logic same as sync version
        
        return result
    
    async def _invoke_bedrock_model(self, prompt: str) -> str:
        """Invoke Bedrock model with prompt (async version)"""
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            # Use async context manager for client
            async with self.session.client('bedrock-runtime', region_name=self.region) as bedrock:
                response = await bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                
                # Read response body (async)
                response_body = json.loads(await response['body'].read())
                
                # Extract text from Claude response
                if 'content' in response_body:
                    text = ""
                    for block in response_body['content']:
                        if block['type'] == 'text':
                            text += block['text']
                    return text
                
                return str(response_body)
                
        except ClientError as e:
            print(f"Bedrock invocation error: {str(e)}")
            raise
    
    async def evaluate_answer(self, topic: str, question: str, user_answer: str, difficulty: str) -> Dict[str, Any]:
        """Evaluate user answer using Bedrock Agent (async)"""
        
        if not self.agent_id:
            # Fallback to direct model if agent not configured
            return await self._evaluate_with_model(topic, question, user_answer, difficulty)
        
        # Use Bedrock Agent for enhanced evaluation (async)
        try:
            async with self.session.client('bedrock-agent-runtime', region_name=self.region) as agent:
                response = await agent.invoke_agent(
                    agentId=self.agent_id,
                    agentAliasId=self.agent_alias_id,
                    sessionId=f"eval-{topic}-{difficulty}",
                    inputText=f"""Evaluate this answer...
"""
                )
                
                # Parse agent response (async)
                result = await self._parse_agent_response(response)
                return result
                
        except Exception as e:
            print(f"Error invoking agent: {str(e)}")
            return await self._evaluate_with_model(topic, question, user_answer, difficulty)
    
    async def _evaluate_with_model(self, topic: str, question: str, user_answer: str, difficulty: str) -> Dict[str, Any]:
        """Fallback evaluation using direct model (async)"""
        
        prompt = f"""Evaluate this answer...
"""
        
        response = await self._invoke_bedrock_model(prompt)
        result = self._extract_json_from_response(response)
        
        return {
            "score": result.get("score", 0),
            "feedback": result.get("feedback", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "expected_key_points": result.get("expected_key_points", []),
            "missing_key_points": result.get("missing_key_points", [])
        }
    
    async def generate_flashcard(self, topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """Generate flashcard content (async)"""
        
        prompt = f"""Create a flashcard...
"""
        
        response = await self._invoke_bedrock_model(prompt)
        result = self._extract_json_from_response(response)
        
        return {
            "front": result.get("front", ""),
            "back": result.get("back", ""),
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "key_points": result.get("key_points", [])
        }
    
    async def _parse_agent_response(self, response: Any) -> Dict[str, Any]:
        """Parse Bedrock Agent response (async)"""
        # Agent responses come as streaming events
        result_text = ""
        async for event in response.get('completion', []):
            if 'chunk' in event:
                result_text += event['chunk']['bytes'].decode('utf-8')
        
        # Extract JSON from agent response
        return self._extract_json_from_response(result_text)
    
    # Helper methods (no async needed, same as sync version)
    def _extract_json_from_response(self, response: str) -> Any:
        """Extract JSON from LLM response (same as sync version)"""
        # ... same implementation as current sync version
        pass
    
    def _get_difficulty_instructions(self, difficulty: str) -> str:
        """Get difficulty-specific instructions (same as sync version)"""
        # ... same implementation as current sync version
        pass


# Example async Lambda handler
async def async_lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Async Lambda handler"""
    try:
        # Handle OPTIONS for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse API Gateway event
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        query_parameters = event.get('queryStringParameters') or {}
        
        # Parse request body
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                body = {}
        
        # Initialize service (can be reused across invocations in warm Lambda)
        bedrock_service = AsyncBedrockService()
        
        # Route to appropriate handler
        if http_method == 'POST' and '/generate-question' in path:
            return await handle_generate_question(body, bedrock_service)
        elif http_method == 'POST' and '/evaluate-answer' in path:
            return await handle_evaluate_answer(body, bedrock_service)
        # ... other routes
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})


async def handle_generate_question(body: Dict[str, Any], bedrock_service: AsyncBedrockService) -> Dict[str, Any]:
    """Handle question generation request (async)"""
    try:
        from models import GenerateQuestionRequest, QuestionResponse
        
        # Validate request
        request = GenerateQuestionRequest(**body)
        
        # Generate question with refinement (async)
        result = await bedrock_service.generate_question(
            topic=request.topic,
            subtopic=request.subtopic,
            difficulty=request.difficulty
        )
        
        response = QuestionResponse(**result)
        response_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        return create_response(200, response_data)
    
    except ValueError as e:
        return create_response(400, {'error': 'Invalid request', 'message': str(e)})
    except Exception as e:
        print(f"Error generating question: {str(e)}")
        return create_response(500, {'error': 'Failed to generate question', 'message': str(e)})


async def handle_evaluate_answer(body: Dict[str, Any], bedrock_service: AsyncBedrockService) -> Dict[str, Any]:
    """Handle answer evaluation request (async)"""
    try:
        from models import EvaluateAnswerRequest, AnswerEvaluationResponse
        
        # Validate request
        request = EvaluateAnswerRequest(**body)
        
        # Evaluate answer using Bedrock Agent (async)
        result = await bedrock_service.evaluate_answer(
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


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response format (same as sync version)"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body)
    }


# Synchronous wrapper for Lambda (if needed for compatibility)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Synchronous wrapper for async handler"""
    return asyncio.run(async_lambda_handler(event, context))


# Alternative: Use Lambda's native async support (Python 3.9+)
# Just export async_lambda_handler directly if Lambda runtime supports it
