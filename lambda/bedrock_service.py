"""
AWS Bedrock Service Integration
Handles direct Bedrock model calls and Agent interactions
"""
import json
import os
import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError

from aws_context import AWSContext


class BedrockService:
    """Service for interacting with AWS Bedrock"""
    
    def __init__(self):
        # Lambda automatically sets AWS_REGION, but we can also get it from context
        import boto3
        session = boto3.Session()
        self.region = session.region_name or os.environ.get('AWS_REGION', 'eu-central-1')
        # Default to Claude 3.5 Haiku (fastest model, optimized for speed)
        # Alternative fast models: anthropic.claude-3-haiku-20240307-v1:0 (older Haiku)
        # For even faster: Consider Amazon Titan models for simple tasks
        self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-haiku-20241022-v2:0')
        self.agent_id = os.environ.get('BEDROCK_AGENT_ID', '')
        self.agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
        
        # Debug: Log the model ID being used
        print(f"BedrockService initialized with model_id: {self.model_id}, region: {self.region}")
        
        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=self.region)
        if self.agent_id:
            self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
        
        self.aws_context = AWSContext()
    
    def generate_question(self, topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """
        Generate interview question (simplified single-step for API Gateway timeout)
        """
        # Use single-step generation to avoid API Gateway 29s timeout
        return self._generate_question_single_step(topic, subtopic, difficulty)
    
    def _generate_question_single_step(self, topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """Single-step question generation (faster, avoids timeout)"""
        
        system_prompt = self.aws_context.get_role_system_prompt()
        aws_context = self.aws_context.get_aws_context_prompt(topic, subtopic)
        difficulty_instructions = self._get_difficulty_instructions(difficulty)
        
        prompt = f"""{system_prompt}

{aws_context}

Difficulty: {difficulty.capitalize()}
{difficulty_instructions}

Generate ONE AWS Systems Engineer interview question about {topic} - {subtopic} ({difficulty} level).

**CRITICAL: Return ONLY JSON object. NO text before/after. Start with {{ and end with }}.**

Return JSON:
{{
  "question": "Question text here",
  "answer": {{
    "summary": "Brief 1-2 sentence summary",
    "steps": [
      {{
        "step": 1,
        "title": "Step title",
        "description": "Detailed explanation",
        "commands": ["command1"],
        "aws_services": ["EC2"]
      }}
    ],
    "aws_services": [{{"name": "EC2", "usage": "What it's used for"}}],
    "key_points": ["Point 1", "Point 2"],
    "best_practices": ["Practice 1"],
    "common_pitfalls": ["Pitfall 1"],
    "code_examples": [{{"language": "bash", "code": "code", "description": "desc"}}],
    "comparison_table": [{{"option": "Option", "pros": [], "cons": [], "when_to_use": "when"}}]
  }},
  "topic": "{topic}",
  "subtopic": "{subtopic}",
  "difficulty": "{difficulty}"
}}

**CRITICAL: Return ONLY the JSON object. NO text before {{. NO text after }}.**
"""
        
        response = self._invoke_bedrock_model(prompt)
        extracted = self._extract_json_from_response(response)
        
        # Normalize answer structure
        if isinstance(extracted, dict):
            if "answer" in extracted and isinstance(extracted["answer"], dict):
                extracted["answer"] = self._normalize_answer_structure(extracted["answer"])
            return extracted
        else:
            # Fallback
            return {
                "question": f"Sample question about {subtopic} in {topic}",
                "answer": self._normalize_answer_structure({}),
                "topic": topic,
                "subtopic": subtopic,
                "difficulty": difficulty
            }
    
    def _generate_question_candidates(self, topic: str, subtopic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Step 1: Generate 3 candidate questions with comprehensive answers"""
        
        # Build prompt
        system_prompt = self.aws_context.get_role_system_prompt()
        aws_context = self.aws_context.get_aws_context_prompt(topic, subtopic)
        
        difficulty_instructions = self._get_difficulty_instructions(difficulty)
        
        prompt = f"""{system_prompt}

{aws_context}

Difficulty: {difficulty.capitalize()}
{difficulty_instructions}

Generate 3 AWS Systems Engineer interview questions about {topic} - {subtopic} ({difficulty} level).

**CRITICAL: Return ONLY JSON array. NO text before/after. Start with [ and end with ].**

**Format:**
Return a JSON array with 3 questions, each including question and comprehensive answer with visual structure:
[
  {{
    "question": "Question text here",
    "answer": {{
      "summary": "Brief 1-2 sentence summary of the solution",
      "steps": [
        {{
          "step": 1,
          "title": "Step title",
          "description": "Detailed explanation",
          "commands": ["command1", "command2"],
          "aws_services": ["EC2", "CloudWatch"]
        }}
      ],
      "aws_services": [
        {{
          "name": "EC2",
          "usage": "What it's used for in this context"
        }}
      ],
      "key_points": ["Key point 1", "Key point 2", "Key point 3"],
      "best_practices": ["Practice 1", "Practice 2"],
      "common_pitfalls": ["Pitfall 1", "Pitfall 2"],
      "code_examples": [
        {{
          "language": "bash",
          "code": "command or code snippet",
          "description": "What this does"
        }}
      ],
      "comparison_table": [
        {{
          "option": "Option 1",
          "pros": ["Pro 1", "Pro 2"],
          "cons": ["Con 1"],
          "when_to_use": "When to use this option"
        }}
      ]
    }},
    "context": "Brief context about why this is relevant to AWS Systems Engineers"
  }}
]

**CRITICAL REMINDER:**
- Return ONLY the JSON array
- NO text before [
- NO text after ]
- NO explanations
- NO markdown formatting
- Start with [ and end with ]
- Your entire response must be valid JSON that can be parsed with json.loads()
"""
        
        # Call Bedrock
        response = self._invoke_bedrock_model(prompt)
        
        # Parse response
        extracted = None
        try:
            # Extract JSON from response
            extracted = self._extract_json_from_response(response)
            print(f"Extracted candidates type: {type(extracted)}, value: {str(extracted)[:500]}")
            
            candidates = None
            if isinstance(extracted, list):
                candidates = extracted
                print(f"✓ Got candidates as list: {len(candidates)} items")
            elif isinstance(extracted, dict):
                # Check if this dict is actually the first item of an array that was partially parsed
                # If response starts with [, we should have gotten a list, not a dict
                # Try to extract array from dict
                candidates = extracted.get("candidates", extracted.get("questions", extracted.get("items", [])))
                if isinstance(candidates, list) and len(candidates) > 0:
                    print(f"✓ Extracted candidates from dict: {len(candidates)} items")
                elif "text" in extracted:
                    # Re-extract from text field
                    text = extracted["text"]
                    print(f"Found text field, re-extracting JSON array, length: {len(text)}")
                    # Use the improved extraction method
                    re_extracted = self._extract_json_from_response(text)
                    if isinstance(re_extracted, list):
                        candidates = re_extracted
                        print(f"✓ Re-extracted {len(candidates)} candidates from text")
                    elif isinstance(re_extracted, dict):
                        # If still a dict, it might be a single question - wrap it in array
                        candidates = [re_extracted]
                        print(f"✓ Wrapped single dict in array")
                else:
                    # If we got a dict but expected an array, it might be a single question
                    # Check if it has question/answer structure
                    if "question" in extracted or "answer" in extracted:
                        candidates = [extracted]
                        print(f"✓ Wrapped single question dict in array")
            
            if not isinstance(candidates, list) or len(candidates) == 0:
                print("No candidates found, using fallback")
                raise ValueError("No candidates generated")
            
            # Normalize to exactly 3 candidates
            if len(candidates) < 3:
                print(f"Only {len(candidates)} candidates, duplicating to reach 3")
                # Duplicate last candidate to reach 3
                while len(candidates) < 3:
                    candidates.append(candidates[-1].copy() if isinstance(candidates[-1], dict) else candidates[-1])
            elif len(candidates) > 3:
                print(f"Got {len(candidates)} candidates, taking first 3")
                # Take first 3
                candidates = candidates[:3]
            
            # Normalize each candidate's answer structure
            for candidate in candidates:
                if "answer" in candidate and isinstance(candidate["answer"], dict):
                    candidate["answer"] = self._normalize_answer_structure(candidate["answer"])
            
            print(f"Returning {len(candidates)} normalized candidates")
            return candidates
        except Exception as e:
            print(f"Error parsing candidates: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return fallback structure
            return self._create_fallback_candidates(topic, subtopic, difficulty)
    
    def _refine_question_candidates(self, candidates: List[Dict[str, Any]], topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """Step 2: Evaluate and refine candidates to select best question"""
        
        prompt = f"""Evaluate 3 AWS Systems Engineer interview questions and select/improve the best one.

Topic: {topic} - {subtopic}
Difficulty: {difficulty}

Candidates:
{self._format_candidates_for_refinement(candidates)}

Select the best question-answer pair. Return ONLY JSON object. Start with {{ and end with }}.

Return JSON:
{{
  "selected_question": "Question text",
  "selected_answer": {{
    "summary": "Summary",
    "steps": [{{"step": 1, "title": "Title", "description": "Description", "commands": [], "aws_services": []}}],
    "aws_services": [{{"name": "Service", "usage": "Usage"}}],
    "key_points": ["Point 1"],
    "best_practices": ["Practice 1"],
    "common_pitfalls": ["Pitfall 1"],
    "code_examples": [{{"language": "bash", "code": "code", "description": "desc"}}],
    "comparison_table": [{{"option": "Option", "pros": [], "cons": [], "when_to_use": "when"}}]
  }}
}}

**CRITICAL: Return ONLY JSON. NO text before/after. Start with {{ and end with }}.**
"""
        
        # Call Bedrock
        response = self._invoke_bedrock_model(prompt)
        
        # Parse response
        try:
            refined = self._extract_json_from_response(response)
            
            # Normalize answer structure to match Pydantic models
            selected_answer = refined.get("selected_answer", candidates[0].get("answer", {}))
            normalized_answer = self._normalize_answer_structure(selected_answer)
            
            # Ensure required fields
            result = {
                "question": refined.get("selected_question", candidates[0].get("question", "")),
                "answer": normalized_answer,
                "topic": topic,
                "subtopic": subtopic,
                "difficulty": difficulty
            }
            
            return result
        except Exception as e:
            print(f"Error parsing refined question: {str(e)}")
            # Return first candidate as fallback
            return {
                "question": candidates[0].get("question", ""),
                "answer": candidates[0].get("answer", {}),
                "topic": topic,
                "subtopic": subtopic,
                "difficulty": difficulty
            }
    
    def evaluate_answer(self, topic: str, question: str, user_answer: str, difficulty: str) -> Dict[str, Any]:
        """Evaluate user answer using Bedrock Agent"""
        
        if not self.agent_id:
            # Fallback to direct model if agent not configured
            return self._evaluate_with_model(topic, question, user_answer, difficulty)
        
        # Use Bedrock Agent for enhanced evaluation
        try:
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=f"eval-{topic}-{difficulty}",
                inputText=f"""Evaluate this answer for an AWS Systems Engineer interview question.

Topic: {topic}
Difficulty: {difficulty}
Question: {question}

User Answer: {user_answer}

Provide:
1. Score (0-100)
2. Detailed feedback
3. Strengths
4. Areas for improvement
5. Expected key points
6. Missing key points"""
            )
            
            # Parse agent response
            result = self._parse_agent_response(response)
            return result
            
        except Exception as e:
            print(f"Error invoking agent: {str(e)}")
            return self._evaluate_with_model(topic, question, user_answer, difficulty)
    
    def _evaluate_with_model(self, topic: str, question: str, user_answer: str, difficulty: str) -> Dict[str, Any]:
        """Fallback evaluation using direct model"""
        
        prompt = f"""Evaluate this answer for an AWS Systems Engineer interview question.

Topic: {topic}
Difficulty: {difficulty}
Question: {question}

User Answer: {user_answer}

Provide evaluation in JSON format:
{{
  "score": 75,
  "feedback": "Detailed feedback text",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Improvement 1", "Improvement 2"],
  "expected_key_points": ["Point 1", "Point 2"],
  "missing_key_points": ["Missing point 1"]
}}"""
        
        response = self._invoke_bedrock_model(prompt)
        result = self._extract_json_from_response(response)
        
        return {
            "score": result.get("score", 0),
            "feedback": result.get("feedback", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "expected_key_points": result.get("expected_key_points", []),
            "missing_key_points": result.get("missing_key_points", [])
        }
    
    def generate_flashcard(self, topic: str, subtopic: str, difficulty: str) -> Dict[str, Any]:
        """Generate flashcard content"""
        
        aws_context = self.aws_context.get_aws_context_prompt(topic, subtopic)
        
        prompt = f"""Create a flashcard for AWS Systems Engineer interview preparation.

Topic: {topic}
Subtopic: {subtopic}
Difficulty: {difficulty}

{aws_context}

Create a flashcard with:
- Front: A concise question or concept
- Back: Detailed explanation with key points
- Focus on AWS context and services

**CRITICAL: Return ONLY valid JSON, no text before or after. Start with {{ and end with }}.**

Return JSON:
{{
  "front": "Question or concept",
  "back": "Detailed explanation",
  "key_points": ["Point 1", "Point 2"]
}}

**IMPORTANT: Your entire response must be valid JSON. NO explanatory text. NO markdown. Start with {{ and end with }}.**"""
        
        response = self._invoke_bedrock_model(prompt)
        result = self._extract_json_from_response(response)
        
        return {
            "front": result.get("front", ""),
            "back": result.get("back", ""),
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "key_points": result.get("key_points", [])
        }
    
    def _invoke_bedrock_model(self, prompt: str) -> str:
        """Invoke Bedrock model with prompt"""
        
        # Prepare request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,  # Reduced for faster responses (API Gateway 29s limit)
            "temperature": 0.2,  # Lower temperature for faster, more deterministic responses
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
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
    
    def _normalize_answer_structure(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize answer structure to match Pydantic models"""
        normalized = {
            "summary": answer.get("summary", ""),
            "steps": [],
            "aws_services": [],
            "key_points": answer.get("key_points", []),
            "best_practices": answer.get("best_practices", []),
            "common_pitfalls": answer.get("common_pitfalls", []),
            "code_examples": [],
            "comparison_table": []
        }
        
        # Normalize steps
        steps = answer.get("steps", [])
        for i, step in enumerate(steps, 1):
            if isinstance(step, dict):
                normalized["steps"].append({
                    "step": step.get("step", step.get("step_number", i)),
                    "title": step.get("title", f"Step {i}"),
                    "description": step.get("description", str(step)),
                    "commands": step.get("commands", step.get("details", [])),
                    "aws_services": step.get("aws_services", [])
                })
            elif isinstance(step, str):
                normalized["steps"].append({
                    "step": i,
                    "title": f"Step {i}",
                    "description": step,
                    "commands": [],
                    "aws_services": []
                })
        
        # Normalize AWS services
        aws_services = answer.get("aws_services", [])
        for service in aws_services:
            if isinstance(service, dict):
                normalized["aws_services"].append({
                    "name": service.get("name", str(service)),
                    "usage": service.get("usage", "")
                })
            elif isinstance(service, str):
                normalized["aws_services"].append({
                    "name": service,
                    "usage": ""
                })
        
        # Normalize code examples
        code_examples = answer.get("code_examples", [])
        for example in code_examples:
            if isinstance(example, dict):
                normalized["code_examples"].append({
                    "language": example.get("language", "bash"),
                    "code": example.get("code", ""),
                    "description": example.get("description", "")
                })
        
        # Normalize comparison table
        comparison_table = answer.get("comparison_table", [])
        for option in comparison_table:
            if isinstance(option, dict):
                normalized["comparison_table"].append({
                    "option": option.get("option", ""),
                    "pros": option.get("pros", []),
                    "cons": option.get("cons", []),
                    "when_to_use": option.get("when_to_use", "")
                })
        
        return normalized
    
    def _extract_json_from_response(self, response: str) -> Any:
        """Extract JSON from LLM response using optimized regex and bracket matching"""
        import re
        
        print(f"Raw response length: {len(response)}, first 200 chars: {response[:200]}")
        
        # Strip leading/trailing whitespace
        response = response.strip()
        
        # Remove any leading text before first [ or {
        json_start = -1
        for i, char in enumerate(response):
            if char in ['[', '{']:
                json_start = i
                break
        
        if json_start > 0:
            print(f"Removing {json_start} chars before JSON")
            response = response[json_start:]
        
        # Try parsing entire response first (fastest path)
        try:
            result = json.loads(response)
            print(f"✓ Parsed entire response as JSON")
            return result
        except:
            pass
        
        # Check for array first (priority) - bracket matching for arrays
        bracket_start = response.find('[')
        if bracket_start >= 0:
            bracket_count = 0
            end_pos = -1
            in_string = False
            escape_next = False
            for i in range(bracket_start, len(response)):
                char = response[i]
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break
            if end_pos > 0:
                try:
                    json_str = response[bracket_start:end_pos]
                    result = json.loads(json_str)
                    print(f"✓ Extracted JSON array via bracket matching")
                    return result
                except Exception as e:
                    print(f"Bracket matching failed: {e}")
        
        # Fallback: Use regex to find JSON object - match from { to matching }
        json_object_pattern = r'\{(?:[^{}]|\{[^}]*\})*\}'
        match = re.search(json_object_pattern, response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(0))
                print(f"✓ Extracted JSON object via regex")
                return result
            except Exception as e:
                print(f"Regex object parse failed: {e}")
        
        # Fallback: brace matching for objects
        brace_start = response.find('{')
        if brace_start >= 0:
            brace_count = 0
            end_pos = -1
            in_string = False
            escape_next = False
            for i in range(brace_start, len(response)):
                char = response[i]
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
            if end_pos > 0:
                try:
                    json_str = response[brace_start:end_pos]
                    result = json.loads(json_str)
                    print(f"✓ Extracted JSON object via brace matching")
                    return result
                except Exception as e:
                    print(f"Brace matching failed: {e}")
        
        print(f"✗ Could not extract JSON, returning as text")
        return {"text": response}
    
    def _parse_agent_response(self, response: Any) -> Dict[str, Any]:
        """Parse Bedrock Agent response"""
        # Agent responses come as streaming events
        result_text = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                result_text += event['chunk']['bytes'].decode('utf-8')
        
        # Extract JSON from agent response
        return self._extract_json_from_response(result_text)
    
    def _format_candidates_for_refinement(self, candidates: List[Dict[str, Any]]) -> str:
        """Format candidates for refinement prompt"""
        formatted = []
        for i, candidate in enumerate(candidates, 1):
            formatted.append(f"""
{i}. Question: "{candidate.get('question', '')}"
   Answer: {json.dumps(candidate.get('answer', {}), indent=2)}
   Context: {candidate.get('context', '')}
""")
        return "\n".join(formatted)
    
    def _get_difficulty_instructions(self, difficulty: str) -> str:
        """Get difficulty-specific instructions"""
        instructions = {
            "newbie": "Basic AWS concepts, fundamental AWS services understanding",
            "intermediate": "Practical AWS scenarios, real-world AWS infrastructure problems",
            "pro": "Complex AWS architecture, optimization, advanced AWS service integration"
        }
        return instructions.get(difficulty.lower(), instructions["intermediate"])
    
    def _create_fallback_candidates(self, topic: str, subtopic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Create fallback candidate structure if generation fails"""
        return [
            {
                "question": f"Sample question about {subtopic} in {topic}",
                "answer": {
                    "summary": "Sample solution summary",
                    "steps": [],
                    "aws_services": [],
                    "key_points": [],
                    "best_practices": [],
                    "common_pitfalls": [],
                    "code_examples": [],
                    "comparison_table": []
                },
                "context": "Fallback candidate"
            }
        ] * 3
