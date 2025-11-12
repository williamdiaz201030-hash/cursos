from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# Define la base declarativa
Base = declarative_base()

class StudentProgress(Base):
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)  # MongoDB ID from auth service
    course_id = Column(Integer, index=True)  # From courses service
    completed_lessons = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    lesson_id = Column(Integer, index=True)
    module_id = Column(Integer, index=True)
    course_id = Column(Integer, index=True)
    status = Column(String)  # "not_started", "in_progress", "completed"
    time_spent = Column(Integer, default=0)  # Time spent in seconds
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models for API
class ProgressBase(BaseModel):
    student_id: str
    course_id: int

class StudentProgressCreate(ProgressBase):
    total_lessons: int

class LessonProgressCreate(ProgressBase):
    lesson_id: int
    module_id: int
    status: str
    time_spent: Optional[int] = 0

class LessonProgress(LessonProgressCreate):
    id: int
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class StudentProgress(ProgressBase):
    id: int
    completed_lessons: int
    total_lessons: int
    progress_percentage: float
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
