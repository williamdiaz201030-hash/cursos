from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

Base = declarative_base()

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    lesson_id = Column(Integer, index=True)
    course_id = Column(Integer, index=True)
    time_limit = Column(Integer, nullable=True)  # Time limit in minutes, null for no limit
    passing_score = Column(Float, default=60.0)  # Percentage needed to pass
    questions = Column(JSON)  # List of questions with answers and correct answer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    student_id = Column(String, index=True)
    answers = Column(JSON)  # Student's answers
    score = Column(Float)
    passed = Column(Boolean)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    quiz = relationship("Quiz")

# Pydantic models for API
class QuestionBase(BaseModel):
    text: str
    options: List[str]
    correct_option: int

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    lesson_id: int
    course_id: int
    time_limit: Optional[int] = None
    passing_score: float = 60.0
    questions: List[QuestionBase]

class QuizCreate(QuizBase):
    pass

class Quiz(QuizBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmission(BaseModel):
    quiz_id: int
    student_id: str
    answers: Dict[str, int]  # Question number -> Selected option number

class QuizAttemptBase(BaseModel):
    quiz_id: int
    student_id: str
    answers: Dict[str, int]
    score: float
    passed: bool

class QuizAttempt(QuizAttemptBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
