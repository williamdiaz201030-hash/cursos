from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
import sys
sys.path.insert(0, '/app')

import models
from database_sql import get_db, create_db_and_tables
import requests
import os

app = FastAPI(title="Evaluations Service")

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
    return {"status": "ok", "service": "evaluations"}

# Quiz endpoints
@app.post("/quizzes/", response_model=models.Quiz)
def create_quiz(quiz: models.QuizCreate, db: Session = Depends(get_db)):
    db_quiz = models.Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@app.get("/quizzes/{quiz_id}", response_model=models.Quiz)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.get("/lessons/{lesson_id}/quizzes/", response_model=List[models.Quiz])
def get_lesson_quizzes(lesson_id: int, db: Session = Depends(get_db)):
    quizzes = db.query(models.Quiz)\
        .filter(models.Quiz.lesson_id == lesson_id)\
        .all()
    return quizzes

# Quiz attempt endpoints
@app.post("/quiz-attempts/", response_model=models.QuizAttempt)
async def submit_quiz(
    submission: models.AnswerSubmission,
    db: Session = Depends(get_db)
):
    # Get the quiz
    quiz = db.query(models.Quiz).filter(models.Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    total_questions = len(quiz.questions)
    correct_answers = 0
    
    for i, question in enumerate(quiz.questions):
        if str(i) in submission.answers and submission.answers[str(i)] == question["correct_option"]:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100
    passed = score >= quiz.passing_score
    
    # Create quiz attempt record
    db_attempt = models.QuizAttempt(
        quiz_id=submission.quiz_id,
        student_id=submission.student_id,
        answers=submission.answers,
        score=score,
        passed=passed,
        completed_at=datetime.utcnow()
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    # Update progress service if quiz was passed
    if passed:
        try:
            progress_service_url = os.getenv("PROGRESS_SERVICE_URL", "http://service2-service:8003")
            requests.post(
                f"{progress_service_url}/progress/lesson/",
                json={
                    "student_id": submission.student_id,
                    "lesson_id": quiz.lesson_id,
                    "course_id": quiz.course_id,
                    "status": "completed"
                }
            )
        except Exception as e:
            print(f"Error updating progress service: {e}")
    
    return db_attempt

@app.get("/quiz-attempts/{attempt_id}", response_model=models.QuizAttempt)
def get_quiz_attempt(attempt_id: int, db: Session = Depends(get_db)):
    attempt = db.query(models.QuizAttempt).filter(models.QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    return attempt

@app.get("/students/{student_id}/quiz-attempts/", response_model=List[models.QuizAttempt])
def get_student_attempts(student_id: str, db: Session = Depends(get_db)):
    attempts = db.query(models.QuizAttempt)\
        .filter(models.QuizAttempt.student_id == student_id)\
        .all()
    return attempts

@app.get("/quizzes/{quiz_id}/attempts/", response_model=List[models.QuizAttempt])
def get_quiz_attempts(quiz_id: int, db: Session = Depends(get_db)):
    attempts = db.query(models.QuizAttempt)\
        .filter(models.QuizAttempt.quiz_id == quiz_id)\
        .all()
    return attempts
