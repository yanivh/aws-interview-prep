# Async Migration Plan for AWS Interview Prep Lambda

## Overview
Migrate from synchronous boto3 to async/await pattern using aioboto3 for better performance and resource utilization in Lambda functions.

## Current State Analysis

### Files to Migrate
1. **lambda/bedrock_service.py** - Main service using boto3 clients
2. **lambda/lambda_function.py** - Handler that calls bedrock_service
3. **lambda/aws_context.py** - Context provider (likely no changes needed)

### Current Dependencies
- `boto3>=1.34.0`
- `botocore>=1.34.0`
- `pydantic>=2.0.0`

### Current Architecture
- Synchronous boto3 clients initialized in `__init__`
- Blocking calls to `bedrock_runtime.invoke_model()`
- Sequential question generation (candidates → refinement)

## Migration Strategy

### Phase 1: Update Dependencies
- [ ] Add `aioboto3>=12.0.0` to requirements.txt
- [ ] Keep boto3 for compatibility during transition
- [ ] Update Lambda runtime to Python 3.11+ (if not already)

### Phase 2: Refactor BedrockService
- [ ] Convert `BedrockService` to async class
- [ ] Replace boto3 clients with aioboto3 clients
- [ ] Convert all methods to async:
  - [ ] `generate_question()` → `async def generate_question()`
  - [ ] `_generate_question_candidates()` → `async def _generate_question_candidates()`
  - [ ] `_refine_question_candidates()` → `async def _refine_question_candidates()`
  - [ ] `evaluate_answer()` → `async def evaluate_answer()`
  - [ ] `_evaluate_with_model()` → `async def _evaluate_with_model()`
  - [ ] `generate_flashcard()` → `async def generate_flashcard()`
  - [ ] `_invoke_bedrock_model()` → `async def _invoke_bedrock_model()`
  - [ ] `_parse_agent_response()` → `async def _parse_agent_response()` (if needed)

### Phase 3: Update Lambda Handler
- [ ] Convert `lambda_handler` to async
- [ ] Update all handler functions to async:
  - [ ] `handle_generate_question()` → `async def handle_generate_question()`
  - [ ] `handle_evaluate_answer()` → `async def handle_evaluate_answer()`
  - [ ] `handle_get_topics()` → `async def handle_get_topics()`
  - [ ] `handle_get_flashcard()` → `async def handle_get_flashcard()`
  - [ ] `handle_get_learning_plan()` → `async def handle_get_learning_plan()`
  - [ ] `handle_get_progress()` → `async def handle_get_progress()`
  - [ ] `handle_update_progress()` → `async def handle_update_progress()`
- [ ] Use `asyncio.run()` or Lambda's async handler support

### Phase 4: Optimize Concurrent Operations
- [ ] Parallelize candidate generation (if generating multiple candidates)
- [ ] Consider parallel refinement if multiple questions needed
- [ ] Optimize agent response parsing if streaming

### Phase 5: Testing & Validation
- [ ] Test all endpoints locally
- [ ] Verify async context managers are properly closed
- [ ] Check for resource leaks
- [ ] Performance benchmarking (before/after)
- [ ] Deploy to staging environment

## Detailed Implementation Steps

### Step 1: Update requirements.txt
```python
boto3>=1.34.0
aioboto3>=12.0.0
pydantic>=2.0.0
botocore>=1.34.0
```

### Step 2: Refactor BedrockService.__init__
```python
def __init__(self):
    # Remove synchronous client initialization
    # Clients will be created in async context
    self.region = os.environ.get('AWS_REGION', 'eu-central-1')
    self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    self.agent_id = os.environ.get('BEDROCK_AGENT_ID', '')
    self.agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
    self.aws_context = AWSContext()
    
    # Optional: Create session for reuse
    self.session = None
```

### Step 3: Create async context manager for clients
```python
async def _get_bedrock_client(self):
    """Get async bedrock-runtime client"""
    import aioboto3
    if self.session is None:
        self.session = aioboto3.Session()
    async with self.session.client('bedrock-runtime', region_name=self.region) as client:
        return client
```

### Step 4: Convert _invoke_bedrock_model
```python
async def _invoke_bedrock_model(self, prompt: str) -> str:
    """Invoke Bedrock model with prompt (async)"""
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    async with self.session.client('bedrock-runtime', region_name=self.region) as bedrock:
        response = await bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(await response['body'].read())
        
        if 'content' in response_body:
            text = ""
            for block in response_body['content']:
                if block['type'] == 'text':
                    text += block['text']
            return text
        
        return str(response_body)
```

### Step 5: Update Lambda Handler
```python
import asyncio
from typing import Dict, Any

async def async_lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Async Lambda handler"""
    try:
        # Handle OPTIONS for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse API Gateway event
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        # Parse request body
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                body = {}
        
        # Route to appropriate handler
        if http_method == 'POST' and '/generate-question' in path:
            return await handle_generate_question(body)
        elif http_method == 'POST' and '/evaluate-answer' in path:
            return await handle_evaluate_answer(body)
        # ... other routes
        
    except Exception as e:
        # error handling
        pass

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Synchronous wrapper for async handler"""
    return asyncio.run(async_lambda_handler(event, context))
```

## Benefits of Migration

1. **Performance**: Non-blocking I/O allows better resource utilization
2. **Scalability**: Can handle more concurrent requests
3. **Cost**: Potentially lower Lambda execution time
4. **Modern Pattern**: Aligns with Python async best practices
5. **Future-proof**: Better support for streaming responses

## Risks & Considerations

1. **Lambda Runtime**: Ensure Python 3.11+ for best async support
2. **Context Management**: Must properly close async clients
3. **Error Handling**: Async exceptions need proper handling
4. **Testing**: More complex to test async code
5. **Backward Compatibility**: May need to support both sync/async during transition

## Rollback Plan

1. Keep original sync version in git branch
2. Feature flag to switch between sync/async
3. Monitor CloudWatch metrics for errors
4. Quick revert if issues detected

## Testing Checklist

- [ ] Unit tests for async methods
- [ ] Integration tests with mock Bedrock
- [ ] Load testing for concurrent requests
- [ ] Error scenario testing
- [ ] Memory leak detection
- [ ] Cold start performance
- [ ] Warm start performance

## Migration Timeline

1. **Week 1**: Update dependencies, refactor BedrockService
2. **Week 2**: Update Lambda handler, add tests
3. **Week 3**: Testing and optimization
4. **Week 4**: Deploy to production, monitor

## Notes

- Consider using `asyncio.gather()` for parallel operations
- Use `async with` for proper resource cleanup
- Monitor Lambda memory usage during migration
- Consider using `aioboto3.Session()` for connection pooling
