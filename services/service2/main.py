from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import sys
sys.path.insert(0, '/app')

import models
from database_sql import get_db, create_db_and_tables

app = FastAPI(title="Progress Tracking Service")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Warning: could not create DB tables at startup: {e}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "progress"}

# Student Progress endpoints
@app.post("/progress/course/", response_model=models.StudentProgress)
def create_course_progress(
    progress: models.StudentProgressCreate,
    db: Session = Depends(get_db)
):
    db_progress = models.StudentProgress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@app.get("/progress/student/{student_id}/courses/", response_model=List[models.StudentProgress])
def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    progress = db.query(models.StudentProgress)\
        .filter(models.StudentProgress.student_id == student_id)\
        .all()
    return progress

@app.get("/progress/course/{course_id}/student/{student_id}", response_model=models.StudentProgress)
def get_course_progress(course_id: int, student_id: str, db: Session = Depends(get_db)):
    progress = db.query(models.StudentProgress)\
        .filter(
            models.StudentProgress.course_id == course_id,
            models.StudentProgress.student_id == student_id
        ).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress

# Lesson Progress endpoints
@app.post("/progress/lesson/", response_model=models.LessonProgress)
def create_lesson_progress(
    progress: models.LessonProgressCreate,
    db: Session = Depends(get_db)
):
    # Create or update lesson progress
    db_progress = db.query(models.LessonProgress)\
        .filter(
            models.LessonProgress.student_id == progress.student_id,
            models.LessonProgress.lesson_id == progress.lesson_id
        ).first()
    
    if db_progress:
        # Update existing progress
        for key, value in progress.dict().items():
            setattr(db_progress, key, value)
        db_progress.updated_at = datetime.utcnow()
        
        if progress.status == "completed" and not db_progress.completed_at:
            db_progress.completed_at = datetime.utcnow()
            
            # Update course progress
            course_progress = db.query(models.StudentProgress)\
                .filter(
                    models.StudentProgress.course_id == progress.course_id,
                    models.StudentProgress.student_id == progress.student_id
                ).first()
            if course_progress:
                course_progress.completed_lessons += 1
                course_progress.progress_percentage = (
                    course_progress.completed_lessons / course_progress.total_lessons * 100
                )
                course_progress.last_accessed = datetime.utcnow()
    else:
        # Create new progress
        db_progress = models.LessonProgress(**progress.dict())
        if progress.status == "completed":
            db_progress.completed_at = datetime.utcnow()
        db.add(db_progress)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress

@app.get("/progress/lesson/{lesson_id}/student/{student_id}", response_model=models.LessonProgress)
def get_lesson_progress(lesson_id: int, student_id: str, db: Session = Depends(get_db)):
    progress = db.query(models.LessonProgress)\
        .filter(
            models.LessonProgress.lesson_id == lesson_id,
            models.LessonProgress.student_id == student_id
        ).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress

@app.get("/progress/module/{module_id}/student/{student_id}", response_model=List[models.LessonProgress])
def get_module_progress(module_id: int, student_id: str, db: Session = Depends(get_db)):
    progress = db.query(models.LessonProgress)\
        .filter(
            models.LessonProgress.module_id == module_id,
            models.LessonProgress.student_id == student_id
        ).all()
    return progress
