"""
Request/Response models for Lambda function
"""
from typing import List, Dict, Any, Optional
try:
    from pydantic import BaseModel, Field
    PYDANTIC_V2 = hasattr(BaseModel, 'model_dump')
except ImportError:
    from pydantic import BaseModel, Field
    PYDANTIC_V2 = False


class GenerateQuestionRequest(BaseModel):
    """Request model for question generation"""
    topic: str = Field(..., description="Topic name (e.g., 'linux', 'networking')")
    subtopic: str = Field(..., description="Subtopic name (e.g., 'processes', 'tls')")
    difficulty: str = Field(..., description="Difficulty level: 'newbie', 'intermediate', or 'pro'")


class EvaluateAnswerRequest(BaseModel):
    """Request model for answer evaluation"""
    topic: str
    question: str
    user_answer: str
    difficulty: str


class StepDetail(BaseModel):
    """Step detail in answer"""
    step: int
    title: str
    description: str
    commands: List[str] = []
    aws_services: List[str] = []


class AWSServiceDetail(BaseModel):
    """AWS service detail"""
    name: str
    usage: str


class CodeExample(BaseModel):
    """Code example"""
    language: str
    code: str
    description: str


class ComparisonOption(BaseModel):
    """Comparison table option"""
    option: str
    pros: List[str]
    cons: List[str]
    when_to_use: str


class AnswerStructure(BaseModel):
    """Structured answer with visual formatting"""
    summary: str
    steps: List[StepDetail]
    aws_services: List[AWSServiceDetail]
    key_points: List[str]
    best_practices: List[str]
    common_pitfalls: List[str]
    code_examples: List[CodeExample] = []
    comparison_table: List[ComparisonOption] = []


class QuestionResponse(BaseModel):
    """Response model for question generation"""
    question: str
    answer: AnswerStructure
    topic: str
    subtopic: str
    difficulty: str


class AnswerEvaluationResponse(BaseModel):
    """Response model for answer evaluation"""
    score: float = Field(..., ge=0, le=100, description="Score out of 100")
    feedback: str
    strengths: List[str]
    improvements: List[str]
    expected_key_points: List[str]
    missing_key_points: List[str]


class SubtopicDetail(BaseModel):
    """Subtopic detail"""
    name: str
    description: str
    recommended_difficulty_progression: List[str] = ["newbie", "intermediate", "pro"]


class TopicDetail(BaseModel):
    """Topic detail"""
    name: str
    description: str
    subtopics: List[SubtopicDetail]


class TopicsResponse(BaseModel):
    """Response model for topics list"""
    topics: List[TopicDetail]


class FlashcardRequest(BaseModel):
    """Request model for flashcard generation"""
    topic: str
    subtopic: str
    difficulty: str


class FlashcardResponse(BaseModel):
    """Response model for flashcard"""
    front: str
    back: str
    topic: str
    subtopic: str
    difficulty: str
    key_points: List[str]


class PhaseDetail(BaseModel):
    """Learning phase detail"""
    phase: int
    name: str
    description: str
    weeks: str
    topics: List[Dict[str, Any]]


class LearningPlanResponse(BaseModel):
    """Response model for learning plan"""
    phases: List[PhaseDetail]
    total_weeks: int
    description: str


class ProgressRequest(BaseModel):
    """Request model for progress update"""
    topic: str
    subtopic: str
    difficulty: str
    completed: bool


class ProgressResponse(BaseModel):
    """Response model for progress"""
    progress: Dict[str, Any]
