"""
Quiz and assessment-related database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg 




class QuestionType(str, enum.Enum):
    """Question type enumeration"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"


class Quiz(SQLModel, table=True):
    """Quiz model""" 
    __tablename__ = "quiz" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
        
    # Foreign key
    module_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="module.id",default=None)
    
    # Quiz details
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, sa_type=Text)
    
    # Quiz settings
    time_limit: Optional[int] = Field(default=None)  # in minutes
    max_attempts: int = Field(default=3)
    passing_score: float = Field(default=70.0)  # percentage
    randomize_questions: bool = Field(default=False)
    show_results_immediately: bool = Field(default=True)
    allow_review: bool = Field(default=True) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    module: "Module" = Relationship(back_populates="quizzes")
    questions: List["Question"] = Relationship(back_populates="quiz")
    quiz_attempts: List["QuizAttempt"] = Relationship(back_populates="quiz")
    
    @property
    def total_questions(self) -> int:
        """Get total number of questions"""
        return len(self.questions)
    
    @property
    def total_points(self) -> float:
        """Get total points for the quiz"""
        return sum(question.points for question in self.questions)


class Question(SQLModel, table=True):
    """Question model""" 
    __tablename__ = "question" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
        
    # Foreign key
    quiz_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="quiz.id",default=None)
    # Question details
    question_text: str = Field(nullable=False, sa_type=Text)
    question_type: QuestionType = Field(nullable=False)
    points: float = Field(default=1.0)
    order_index: int = Field(default=0)
    explanation: Optional[str] = Field(default=None, sa_type=Text) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    quiz: Quiz = Relationship(back_populates="questions", sa_relationship_kwargs={"foreign_keys": "[Question.quiz_id]"})
    options: List["QuestionOption"] = Relationship(back_populates="question", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    quiz_responses: List["QuizResponse"] = Relationship(back_populates="question", sa_relationship_kwargs={"foreign_keys": "[QuizResponse.question_id]"})
    
    @property
    def correct_options(self) -> List["QuestionOption"]:
        """Get correct options for the question"""
        return [option for option in self.options if option.is_correct]


class QuestionOption(SQLModel, table=True):
    """Question option model for multiple choice questions""" 
    __tablename__ = "question_option" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )   
    # Foreign key
    question_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="question.id",default=None)
    
    # Option details
    option_text: str = Field(nullable=False, max_length=500)
    is_correct: bool = Field(default=False)
    order_index: int = Field(default=0) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    question: Question = Relationship(back_populates="options")
    quiz_responses: List["QuizResponse"] = Relationship(back_populates="question_option")


class QuizAttempt(SQLModel, table=True):
    """Quiz attempt model""" 
    __tablename__ = "quiz_attempt"

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )       
    # Foreign keys
    quiz_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="quiz.id",default=None)
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Attempt details
    score: Optional[float] = Field(default=None)  # percentage
    total_points: float = Field(default=0.0)
    earned_points: float = Field(default=0.0)
    
    # Timing
    started_at: datetime = Field(nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
    time_spent: int = Field(default=0)  # in seconds
    
    # Attempt metadata
    attempt_number: int = Field(default=1)
    is_passed: bool = Field(default=False) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    quiz: Quiz = Relationship(back_populates="quiz_attempts")
    users: "User" = Relationship(back_populates="quiz_attempts", sa_relationship_kwargs={"foreign_keys": "[QuizAttempt.user_id]"})
    quiz_responses: List["QuizResponse"] = Relationship(back_populates="attempt")
    
    @property
    def is_completed(self) -> bool:
        """Check if attempt is completed"""
        return self.completed_at is not None
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration"""
        hours = self.time_spent // 3600
        minutes = (self.time_spent % 3600) // 60
        seconds = self.time_spent % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class QuizResponse(SQLModel, table=True):
    """Quiz response model""" 
    __tablename__ = "quiz_response" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )     
    # Foreign keys
    attempt_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="quiz_attempt.id",default=None)
    question_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="question.id",default=None)
    question_option_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="question_option.id",default=None)
    # Response details
    text_response: Optional[str] = Field(default=None, sa_type=Text)
    is_correct: Optional[bool] = Field(default=None)
    points_earned: float = Field(default=0.0) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    attempt: QuizAttempt = Relationship(back_populates="quiz_responses")
    question: Question = Relationship(back_populates="quiz_responses")
    question_option: Optional[QuestionOption] = Relationship(back_populates="quiz_responses")


# Import other models to avoid circular imports
from app.models.models.module import Module
from app.models.models.user import User

