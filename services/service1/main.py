from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
sys.path.insert(0, '/app')

import models
from database_sql import get_db, create_db_and_tables
from database_mongo import ContentStore

app = FastAPI(title="Courses Service")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        create_db_and_tables()
    except Exception as e:
        # Log and continue so the service doesn't crash immediately if the DB isn't ready.
        print(f"Warning: could not create DB tables at startup: {e}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "courses"}

# Course endpoints
@app.post("/courses/", response_model=models.Course)
def create_course(course: models.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=List[models.Course])
def list_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses

@app.get("/courses/{course_id}", response_model=models.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# Module endpoints
@app.post("/modules/", response_model=models.Module)
def create_module(module: models.ModuleCreate, db: Session = Depends(get_db)):
    db_module = models.Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@app.get("/courses/{course_id}/modules/", response_model=List[models.Module])
def list_course_modules(course_id: int, db: Session = Depends(get_db)):
    modules = db.query(models.Module).filter(models.Module.course_id == course_id).all()
    return modules

# Lesson endpoints
@app.post("/lessons/", response_model=models.Lesson)
async def create_lesson(lesson: models.LessonCreate, db: Session = Depends(get_db)):
    # If there's content_id, verify it exists in MongoDB
    if lesson.content_id:
        content = ContentStore.get_content(lesson.content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
    
    db_lesson = models.Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@app.get("/modules/{module_id}/lessons/", response_model=List[models.Lesson])
def list_module_lessons(module_id: int, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).filter(models.Lesson.module_id == module_id).all()
    return lessons

# Content endpoints
@app.post("/content/")
async def create_content(content_data: dict):
    content_id = ContentStore.create_content(content_data)
    return {"content_id": content_id}

@app.get("/content/{content_id}")
async def get_content(content_id: str):
    content = ContentStore.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content
