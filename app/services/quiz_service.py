"""
Quiz service for assessment management operations
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from datetime import datetime

from app.models.models.quiz import Quiz, Question, QuestionOption, QuizAttempt, QuizResponse, QuestionType
from app.models.models.module import Module
from app.models.models.user import User
from app.schemas.quiz import (
    QuizCreateSchema, QuizUpdateSchema, QuizSummarySchema, QuizDetailSchema,
    QuizAttemptStartSchema, QuizSubmissionSchema, QuizResultSchema, QuizResultDetailSchema,
    QuizAttemptSchema, QuestionCreateSchema, QuestionUpdateSchema, QuestionSchema,
    QuizAttemptStartSchema, QuizDetailSchema
)
from app.schemas.base import PaginatedResponse


class QuizService:
    """Quiz and assessment management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_quizzes(self, page: int = 1, limit: int = 20, search: Optional[str] = None, module_id: Optional[str] = None) -> PaginatedResponse[QuizSummarySchema]:
        """Get paginated list of quizzes"""
        query = select(Quiz)
        
        if module_id:
            query = query.where(Quiz.module_id == module_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Quiz.title.ilike(search_term)) |
                (Quiz.description.ilike(search_term))
            )
        
        total_query = select(func.count(Quiz.id))
        if module_id:
            total_query = total_query.where(Quiz.module_id == module_id)
        if search:
            search_term = f"%{search}%"
            total_query = total_query.where(
                (Quiz.title.ilike(search_term)) |
                (Quiz.description.ilike(search_term))
            )
        
        total = await self.db.exec(total_query)
        total = total.first()
        
        offset = (page - 1) * limit
        quizz = await self.db.exec(query.offset(offset).limit(limit))
        quizzes = quizz.all()
        
        quiz_schemas = []
        for quiz in quizzes:
            total_questions = len(quiz.questions)
            total_points = sum(q.points for q in quiz.questions)
            
            quiz_schemas.append(QuizSummarySchema(
                id=quiz.id,
                module_id=quiz.module_id,
                title=quiz.title,
                description=quiz.description,
                time_limit=quiz.time_limit,
                max_attempts=quiz.max_attempts,
                passing_score=quiz.passing_score,
                total_questions=total_questions,
                total_points=total_points,
                created_at=quiz.created_at,
                updated_at=quiz.updated_at
            ))
        
        return PaginatedResponse.create(quiz_schemas, total, page, limit)
    
    async def get_quiz_by_id(self, quiz_id: str, user_id: Optional[str] = None) -> QuizDetailSchema:
        """Get quiz by ID with detailed information"""
        quizzes = await self.db.exec(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quizzes.first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Get module information
        modules = await self.db.exec(select(Module).where(Module.id == quiz.module_id))
        module = modules.first()
        
        # Get questions with options
        questions = []
        for question in quiz.questions:
            question_schema = QuestionSchema(
                id=question.id,
                quiz_id=question.quiz_id,
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                order_index=question.order_index,
                explanation=question.explanation,
                options=[
                    {
                        "id": opt.id,
                        "question_id": opt.question_id,
                        "option_text": opt.option_text,
                        "is_correct": opt.is_correct,
                        "order_index": opt.order_index,
                        "created_at": opt.created_at,
                        "updated_at": opt.updated_at
                    }
                    for opt in question.options
                ],
                created_at=question.created_at,
                updated_at=question.updated_at
            )
            questions.append(question_schema)
        
        # Get user attempt information if user_id provided
        user_attempts = 0
        best_score = None
        can_attempt = True
        
        if user_id:
            attempt = await self.db.exec(
                select(QuizAttempt).where(
                    (QuizAttempt.quiz_id == quiz_id) & (QuizAttempt.user_id == user_id)
                )
            )
            attempts = attempt.all()
            
            user_attempts = len(attempts)
            completed_attempts = [a for a in attempts if a.completed_at is not None]
            
            if completed_attempts:
                best_score = max(a.score for a in completed_attempts)
            
            can_attempt = user_attempts < quiz.max_attempts
        
        return QuizDetailSchema(
            id=quiz.id,
            module_id=quiz.module_id,
            module_title=module.title if module else "Unknown",
            title=quiz.title,
            description=quiz.description,
            time_limit=quiz.time_limit,
            max_attempts=quiz.max_attempts,
            passing_score=quiz.passing_score,
            randomize_questions=quiz.randomize_questions,
            show_results_immediately=quiz.show_results_immediately,
            allow_review=quiz.allow_review,
            questions=questions,
            user_attempts=user_attempts,
            best_score=best_score,
            can_attempt=can_attempt,
            created_at=quiz.created_at,
            updated_at=quiz.updated_at
        )
    
    async def create_quiz(self, quiz_data: QuizCreateSchema) -> QuizDetailSchema:
        """Create a new quiz"""
        # Verify module exists
        modules = await self.db.exec(select(Module).where(Module.id == quiz_data.module_id))
        module = modules.first()
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Create new quiz
        new_quiz = Quiz(
            module_id=quiz_data.module_id,
            title=quiz_data.title,
            description=quiz_data.description,
            time_limit=quiz_data.time_limit,
            max_attempts=quiz_data.max_attempts,
            passing_score=quiz_data.passing_score,
            randomize_questions=quiz_data.randomize_questions,
            show_results_immediately=quiz_data.show_results_immediately,
            allow_review=quiz_data.allow_review
        )
        
        self.db.add(new_quiz)
        await self.db.commit()
        await self.db.refresh(new_quiz)
        
        # Add questions if provided
        for i, question_data in enumerate(quiz_data.questions):
            self._create_question(new_quiz.id, question_data, i)
        
        return await self.get_quiz_by_id(new_quiz.id)
    
    async def update_quiz(self, quiz_id: str, quiz_data: QuizUpdateSchema) -> QuizDetailSchema:
        """Update quiz information"""
        quizzes = await self.db.exec(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quizzes.first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Update fields
        if quiz_data.title is not None:
            quiz.title = quiz_data.title
        if quiz_data.description is not None:
            quiz.description = quiz_data.description
        if quiz_data.time_limit is not None:
            quiz.time_limit = quiz_data.time_limit
        if quiz_data.max_attempts is not None:
            quiz.max_attempts = quiz_data.max_attempts
        if quiz_data.passing_score is not None:
            quiz.passing_score = quiz_data.passing_score
        if quiz_data.randomize_questions is not None:
            quiz.randomize_questions = quiz_data.randomize_questions
        if quiz_data.show_results_immediately is not None:
            quiz.show_results_immediately = quiz_data.show_results_immediately
        if quiz_data.allow_review is not None:
            quiz.allow_review = quiz_data.allow_review
        
        self.db.add(quiz)
        await self.db.commit()
        await self.db.refresh(quiz)
        
        return await self.get_quiz_by_id(quiz.id)
    
    async def delete_quiz(self, quiz_id: str) -> Dict[str, str]:
        """Delete a quiz"""
        quizzes = await self.db.exec(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quizzes.first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Check if quiz has attempts
        attempt = await self.db.exec(select(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id))
        attempts = attempt.all()
        if attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete quiz with existing attempts"
            )
        
        self.db.delete(quiz)
        await self.db.commit()
        
        return {"message": "Quiz deleted successfully"}
    
    async def _create_question(self, quiz_id: str, question_data: QuestionCreateSchema, order_index: int) -> Question: 
        """Helper to create a question and its options"""
        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            points=question_data.points,
            order_index=order_index,
            explanation=question_data.explanation
        )
        self.db.add(new_question)
        self.db.flush()  # Flush to get the ID for options

        for option_data in question_data.options:
            new_option = QuestionOption(
                question_id=new_question.id,
                option_text=option_data.option_text,
                is_correct=option_data.is_correct,
                order_index=option_data.order_index
            )
            self.db.add(new_option)
        
        return new_question

    async def add_question_to_quiz(self, quiz_id: str, question_data: QuestionCreateSchema) -> QuestionSchema:
        """Add a question to a quiz"""
        quizzes = await self.db.exec(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quizzes.first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Determine the next order index
        max_orders = await self.db.exec(
            select(func.max(Question.order_index)).where(Question.quiz_id == quiz_id)
        )
        max_order = max_orders.first()
        order_index = (max_order or 0) + 1
        
        new_question = await self._create_question(quiz_id, question_data, order_index)
        await self.db.commit()
        await self.db.refresh(new_question)
        
        return QuestionSchema.model_validate(new_question)

    async def update_question(self, question_id: str, question_data: QuestionUpdateSchema) -> QuestionSchema:
        """Update question information"""
        questions = await self.db.exec(select(Question).where(Question.id == question_id))
        question = questions.first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if question_data.question_text is not None:
            question.question_text = question_data.question_text
        if question_data.question_type is not None:
            question.question_type = question_data.question_type
        if question_data.points is not None:
            question.points = question_data.points
        if question_data.order_index is not None:
            question.order_index = question_data.order_index
        if question_data.explanation is not None:
            question.explanation = question_data.explanation
        
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        
        return QuestionSchema.model_validate(question)

    async def delete_question(self, question_id: str) -> Dict[str, str]:
        """Delete a question"""
        questions = await self.db.exec(select(Question).where(Question.id == question_id))
        question = questions.first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        self.db.delete(question)
        await self.db.commit()
        
        return {"message": "Question deleted successfully"}

    async def submit_quiz_attempt(self, quiz_id: str, user_id: str, attempt_data: QuizAttemptStartSchema) -> QuizDetailSchema:
        """Submit a quiz attempt"""
        quizzes = await self.db.exec(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quizzes.first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Check if user can attempt
        user_attempts_counts = await self.db.exec(
            select(func.count(QuizAttempt.id)).where(
                (QuizAttempt.quiz_id == quiz_id) & (QuizAttempt.user_id == user_id)
            )
        )
        user_attempts_count = user_attempts_counts.first()
        
        if user_attempts_count >= quiz.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum attempts reached"
            )

        new_attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            started_at=datetime.utcnow(),
            attempt_number=user_attempts_count + 1,
            total_points=sum(q.points for q in quiz.questions)
        )
        self.db.add(new_attempt)
        self.db.flush()

        earned_points = 0
        for response_data in attempt_data.responses:
            questions = await self.db.exec(select(Question).where(Question.id == response_data.question_id))
            question = questions.first()
            if not question:
                continue

            is_correct = False
            if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
                if response_data.selected_option_id:
                    selected_options = await self.db.exec(
                        select(QuestionOption).where(QuestionOption.id == response_data.selected_option_id)
                    )
                    selected_option = selected_options.first()
                    if selected_option and selected_option.is_correct:
                        is_correct = True
                        earned_points += question.points
            elif question.question_type in [QuestionType.SHORT_ANSWER, QuestionType.ESSAY]:
                # For text responses, a simple check for non-empty response
                if response_data.text_response and response_data.text_response.strip():
                    is_correct = True # Placeholder for actual grading
                    earned_points += question.points # Placeholder for actual grading

            quiz_response = QuizResponse(
                attempt_id=new_attempt.id,
                question_id=question.id,
                selected_option_id=response_data.selected_option_id,
                text_response=response_data.text_response,
                is_correct=is_correct,
                points_earned=question.points if is_correct else 0
            )
            self.db.add(quiz_response)

        new_attempt.completed_at = datetime.utcnow()
        new_attempt.earned_points = earned_points
        new_attempt.score = (earned_points / new_attempt.total_points * 100) if new_attempt.total_points > 0 else 0
        new_attempt.is_passed = new_attempt.score >= quiz.passing_score
        new_attempt.time_spent = int((new_attempt.completed_at - new_attempt.started_at).total_seconds())

        self.db.add(new_attempt)
        await self.db.commit()
        await self.db.refresh(new_attempt)

        return await self.get_quiz_attempt_by_id(new_attempt.id)

    async def get_quiz_attempts(self, quiz_id: str, page: int = 1, limit: int = 20, user_id: Optional[str] = None) -> PaginatedResponse[QuizAttemptSchema]:
        """Get paginated list of quiz attempts for a quiz"""
        query = select(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id)
        if user_id:
            query = query.where(QuizAttempt.user_id == user_id)
        
        total_query = select(func.count(QuizAttempt.id)).where(QuizAttempt.quiz_id == quiz_id)
        if user_id:
            total_query = total_query.where(QuizAttempt.user_id == user_id)
        
        total = self.db.exec(total_query).first()
        
        offset = (page - 1) * limit
        attemptss = await self.db.exec(query.offset(offset).limit(limit))
        attempts = attemptss.all()
        
        attempt_schemas = []
        for attempt in attempts:
            userss = await self.db.exec(select(User).where(User.id == attempt.user_id))
            user = userss.first()
            quizzes = await self.db.exec(select(Quiz).where(Quiz.id == attempt.quiz_id))
            quiz = quizzes.first()
            attempt_schemas.append(QuizAttemptSchema(
                id=attempt.id,
                quiz_id=attempt.quiz_id,
                user_id=attempt.user_id,
                started_at=attempt.started_at,
                completed_at=attempt.completed_at,
                score=attempt.score,
                is_passed=attempt.is_passed,
                attempt_number=attempt.attempt_number,
                time_spent=attempt.time_spent,
                user_name=user.full_name if user else "Unknown",
                quiz_title=quiz.title if quiz else "Unknown"
            ))
        
        return PaginatedResponse.create(attempt_schemas, total, page, limit)

    async def get_quiz_attempt_by_id(self, attempt_id: str) -> QuizDetailSchema:
        """Get quiz attempt by ID with detailed information"""
        attempts = await self.db.exec(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
        attempt = attempts.first()
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz attempt not found"
            )
        
        quizz = await self.db.exec(select(Quiz).where(Quiz.id == attempt.quiz_id))
        quiz = quizz.first()
        userss = await self.db.exec(select(User).where(User.id == attempt.user_id))
        user = userss.first()
        
        responses = []
        for response in attempt.responses:
            questionss = await self.db.exec(select(Question).where(Question.id == response.question_id))
            question = questionss.first()
            selected_option = None
            if response.selected_option_id:
                selected_options = await self.db.exec(select(QuestionOption).where(QuestionOption.id == response.selected_option_id))
                selected_option = selected_options.first()
            
            responses.append({
                "question_id": response.question_id,
                "question_text": question.question_text if question else "",
                "selected_option_id": response.selected_option_id,
                "selected_option_text": selected_option.option_text if selected_option else response.text_response,
                "text_response": response.text_response,
                "is_correct": response.is_correct,
                "points_earned": response.points_earned,
                "correct_answer": [opt.option_text for opt in question.options if opt.is_correct] if question and question.options else []
            })
        
        return QuizDetailSchema(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            user_id=attempt.user_id,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            score=attempt.score,
            is_passed=attempt.is_passed,
            attempt_number=attempt.attempt_number,
            time_spent=attempt.time_spent,
            user_name=user.full_name if user else "Unknown",
            quiz_title=quiz.title if quiz else "Unknown",
            responses=responses
        )


