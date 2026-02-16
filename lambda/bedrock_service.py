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


# Model IDs that support extended thinking (reasoning) per AWS docs:
# https://docs.aws.amazon.com/bedrock/latest/userguide/inference-reasoning.html
REASONING_MODEL_IDS = {
    "anthropic.claude-3-7-sonnet-20250219-v1:0",   # Claude 3.7 Sonnet
    "anthropic.claude-sonnet-4-20250514-v1:0",     # Claude Sonnet 4
    "anthropic.claude-sonnet-4-5-20250929-v1:0",   # Claude Sonnet 4.5
    "anthropic.claude-opus-4-20250514-v1:0",       # Claude Opus 4
    "anthropic.claude-opus-4-5-20251101-v1:0",    # Claude Opus 4.5
    "anthropic.claude-haiku-4-5-20251001-v1:0",   # Claude Haiku 4.5
}


class BedrockService:
    """Service for interacting with AWS Bedrock"""
    
    def __init__(self):
        # Lambda automatically sets AWS_REGION, but we can also get it from context
        import boto3
        session = boto3.Session()
        self.region = session.region_name or os.environ.get('AWS_REGION', 'eu-central-1')
        # Default: Claude 3.7 Sonnet with extended thinking for better questions and explanations
        # Set BEDROCK_MODEL_ID to override. Reasoning models: 3.7 Sonnet, Sonnet 4, Opus 4, etc.
        self.model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-7-sonnet-20250219-v1:0')
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
        question_style = self._get_question_style_instructions(difficulty)
        
        prompt = f"""{system_prompt}

{aws_context}

Difficulty: {difficulty.capitalize()}
{difficulty_instructions}

{question_style}

Generate ONE AWS Systems Engineer interview question about **{topic}** / **{subtopic}** at **{difficulty}** level.

**QUESTION REQUIREMENTS (mandatory):**
- The "question" field MUST be a single, concrete, technical interview question that an interviewer would ask aloud.
- Write a full question (e.g. "How would you troubleshoot high CPU caused by runaway processes on an EC2 instance?" or "Explain the difference between zombie and orphan processes and how they affect AWS workloads.").
- Do NOT use placeholders or generic text like "Sample question about X in Y" or "Question text here"—those are invalid.
- The question should be specific to {topic} and {subtopic}, and appropriate for {difficulty} level.

**CRITICAL: Return ONLY a JSON object. NO markdown, NO text before or after. Start with {{ and end with }}.**

Return JSON in this exact shape:
{{
  "question": "Your full, specific interview question as one sentence or short paragraph?",
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

**CRITICAL: Output ONLY the JSON object. No ```json, no explanation, no text before {{ or after }}.**
"""
        
        response = self._invoke_bedrock_model(prompt)
        extracted = self._extract_json_from_response(response)
        
        # Normalize answer structure
        if isinstance(extracted, dict):
            if "answer" in extracted and isinstance(extracted["answer"], dict):
                extracted["answer"] = self._normalize_answer_structure(extracted["answer"])
            # Reject placeholder-style questions so we don't surface "Sample question about..."
            q = (extracted.get("question") or "").strip()
            if not q or "sample question about" in q.lower() or q.lower().startswith("question text here"):
                extracted["question"] = self._extract_question_from_raw_response(response) or q or f"Interview question: {subtopic} in {topic} ({difficulty})"
            return extracted
        else:
            # Fallback when JSON parsing failed: try to get a real question from raw response
            fallback_question = self._extract_question_from_raw_response(response)
            if not fallback_question:
                fallback_question = f"Interview question: {subtopic} in {topic} ({difficulty} level)"
            return {
                "question": fallback_question,
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
        """Invoke Bedrock model with prompt. Uses extended thinking when model supports it."""
        use_reasoning = self.model_id in REASONING_MODEL_IDS
        # Prepare request body for Claude Messages API
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048 if use_reasoning else 800,  # More tokens for reasoning + full answer
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        if use_reasoning:
            # Extended thinking: better reasoning, more accurate explanations (per AWS inference-reasoning docs)
            # Cannot use temperature/top_p/top_k when thinking is enabled
            body["thinking"] = {"type": "enabled", "budget_tokens": 2048}
        else:
            body["temperature"] = 0.2
        
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
    
    def _extract_question_from_raw_response(self, response: str) -> Optional[str]:
        """When JSON parsing fails, try to extract a question from raw LLM text (e.g. first line ending with ?)."""
        if not response or not response.strip():
            return None
        import re
        text = response.strip()
        # Prefer line that looks like a question (ends with ?) and is not a placeholder
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 15:
                continue
            if line.endswith("?") and "sample question about" not in line.lower():
                # Strip common prefixes and markdown
                line = re.sub(r"^[\s*\-#\"']+", "", line)
                if len(line) > 20:
                    return line
        # Otherwise first substantial sentence ending with ?
        match = re.search(r"([^.!?\n]{20,}?\?)", text)
        if match:
            candidate = match.group(1).strip()
            if "sample question" not in candidate.lower():
                return candidate
        return None
    
    def _extract_json_from_response(self, response: str) -> Any:
        """Extract JSON from LLM response using optimized regex and bracket matching"""
        import re
        
        print(f"Raw response length: {len(response)}, first 200 chars: {response[:200]}")
        
        # Strip leading/trailing whitespace
        response = response.strip()
        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        if response.startswith("```"):
            response = re.sub(r"^```(?:json)?\s*", "", response)
            response = re.sub(r"\s*```\s*$", "", response)
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

    def _get_question_style_instructions(self, difficulty: str) -> str:
        """Get difficulty-specific question style so generated questions are concrete."""
        styles = {
            "newbie": "Question style: definitions, basic concepts, and simple how-to (e.g. 'What is X?', 'How do you list running processes?').",
            "intermediate": "Question style: scenario-based or troubleshooting (e.g. 'How would you debug X on an EC2 instance?', 'When would you use A vs B?').",
            "pro": "Question style: advanced scenario, trade-offs, or design (e.g. 'How would you design X for high availability?', 'Explain trade-offs between X and Y in AWS.', 'How would you troubleshoot X under load?')."
        }
        return styles.get(difficulty.lower(), styles["intermediate"])
    
    def _create_fallback_candidates(self, topic: str, subtopic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Create fallback candidate structure if generation fails"""
        return [
            {
                "question": f"Interview question: {subtopic} in {topic} ({difficulty} level). Generate again for a specific question.",
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
