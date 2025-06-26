"""
Quiz and assessment schemas
"""
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse
from app.models.models.quiz import QuestionType


class QuestionOptionCreateSchema(BaseSchema):
    """Question option creation schema"""
    option_text: str = Field(..., min_length=1, max_length=500, description="Option text")
    is_correct: bool = Field(default=False, description="Is this option correct")
    order_index: int = Field(default=0, ge=0, description="Option order")


class QuestionOptionSchema(BaseSchema, TimestampMixin):
    """Question option response schema"""
    id: str
    question_id: str
    option_text: str
    is_correct: bool
    order_index: int


class QuestionCreateSchema(BaseSchema):
    """Question creation schema"""
    question_text: str = Field(..., min_length=1, description="Question text")
    question_type: QuestionType = Field(..., description="Question type")
    points: float = Field(default=1.0, gt=0, description="Points for correct answer")
    order_index: int = Field(default=0, ge=0, description="Question order")
    explanation: Optional[str] = Field(None, description="Explanation shown after answering")
    options: List[QuestionOptionCreateSchema] = Field(default_factory=list, description="Question options")
    
    @validator('options')
    def validate_options(cls, v, values):
        """Validate question options based on question type"""
        question_type = values.get('question_type')
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            if len(v) < 2:
                raise ValueError('Multiple choice questions must have at least 2 options')
            if not any(opt.is_correct for opt in v):
                raise ValueError('Multiple choice questions must have at least one correct option')
        elif question_type == QuestionType.TRUE_FALSE:
            if len(v) != 2:
                raise ValueError('True/False questions must have exactly 2 options')
            if sum(opt.is_correct for opt in v) != 1:
                raise ValueError('True/False questions must have exactly one correct option')
        elif question_type in [QuestionType.SHORT_ANSWER, QuestionType.ESSAY]:
            if v:
                raise ValueError('Short answer and essay questions should not have options')
        
        return v


class QuestionUpdateSchema(BaseSchema):
    """Question update schema"""
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = Field(None)
    points: Optional[float] = Field(None, gt=0)
    order_index: Optional[int] = Field(None, ge=0)
    explanation: Optional[str] = Field(None)


class QuestionSchema(BaseSchema, TimestampMixin):
    """Question response schema"""
    id: str
    quiz_id: str
    question_text: str
    question_type: QuestionType
    points: float
    order_index: int
    explanation: Optional[str]
    options: List[QuestionOptionSchema] = []


class QuizCreateSchema(BaseSchema):
    """Quiz creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    time_limit: Optional[int] = Field(None, gt=0, description="Time limit in minutes")
    max_attempts: int = Field(default=3, gt=0, description="Maximum attempts allowed")
    passing_score: float = Field(default=70.0, ge=0, le=100, description="Passing score percentage")
    randomize_questions: bool = Field(default=False, description="Randomize question order")
    show_results_immediately: bool = Field(default=True, description="Show results immediately after submission")
    allow_review: bool = Field(default=True, description="Allow review of answers")
    questions: List[QuestionCreateSchema] = Field(default_factory=list, description="Quiz questions")


class QuizUpdateSchema(BaseSchema):
    """Quiz update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    time_limit: Optional[int] = Field(None, gt=0)
    max_attempts: Optional[int] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    randomize_questions: Optional[bool] = Field(None)
    show_results_immediately: Optional[bool] = Field(None)
    allow_review: Optional[bool] = Field(None)


class QuizSummarySchema(BaseSchema, TimestampMixin):
    """Quiz summary schema for lists"""
    id: str
    module_id: str
    title: str
    description: Optional[str]
    time_limit: Optional[int]
    max_attempts: int
    passing_score: float
    total_questions: int
    total_points: float


class QuizDetailSchema(BaseSchema, TimestampMixin):
    """Detailed quiz schema"""
    id: str
    module_id: str
    module_title: str
    title: str
    description: Optional[str]
    time_limit: Optional[int]
    max_attempts: int
    passing_score: float
    randomize_questions: bool
    show_results_immediately: bool
    allow_review: bool
    questions: List[QuestionSchema] = []
    
    # User-specific data (if available)
    user_attempts: int = 0
    best_score: Optional[float] = None
    can_attempt: bool = True


class QuizAttemptStartSchema(BaseSchema):
    """Quiz attempt start response schema"""
    attempt_id: str
    quiz_id: str
    started_at: datetime
    time_limit: Optional[int]
    questions: List[QuestionSchema]


class QuizResponseSchema(BaseSchema):
    """Quiz response submission schema"""
    question_id: str = Field(..., description="Question ID")
    selected_option_id: Optional[str] = Field(None, description="Selected option ID (for multiple choice)")
    text_response: Optional[str] = Field(None, description="Text response (for short answer/essay)")


class QuizSubmissionSchema(BaseSchema):
    """Quiz submission schema"""
    attempt_id: str = Field(..., description="Quiz attempt ID")
    responses: List[QuizResponseSchema] = Field(..., description="Quiz responses")


class QuizResultSchema(BaseSchema):
    """Quiz result schema"""
    attempt_id: str
    quiz_id: str
    score: float
    total_points: float
    earned_points: float
    is_passed: bool
    completed_at: datetime
    time_spent: int
    attempt_number: int
    
    @property
    def time_spent_formatted(self) -> str:
        """Get formatted time spent"""
        hours = self.time_spent // 3600
        minutes = (self.time_spent % 3600) // 60
        seconds = self.time_spent % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class QuizResultDetailSchema(QuizResultSchema):
    """Detailed quiz result with answers"""
    responses: List["QuizResponseDetailSchema"] = []


class QuizResponseDetailSchema(BaseSchema, TimestampMixin):
    """Detailed quiz response schema"""
    id: str
    question_id: str
    question_text: str
    question_type: QuestionType
    selected_option_id: Optional[str]
    selected_option_text: Optional[str]
    text_response: Optional[str]
    is_correct: Optional[bool]
    points_earned: float
    correct_answer: Optional[str]
    explanation: Optional[str]


class QuizAttemptSchema(BaseSchema, TimestampMixin):
    """Quiz attempt schema"""
    id: str
    quiz_id: str
    quiz_title: str
    user_id: str
    score: Optional[float]
    total_points: float
    earned_points: float
    started_at: datetime
    completed_at: Optional[datetime]
    time_spent: int
    attempt_number: int
    is_passed: bool
    
    @property
    def is_completed(self) -> bool:
        """Check if attempt is completed"""
        return self.completed_at is not None


# Paginated response types
PaginatedQuizzesResponse = PaginatedResponse[QuizSummarySchema]
PaginatedQuizAttemptsResponse = PaginatedResponse[QuizAttemptSchema]

