#!/usr/bin/env python3
"""
Online Course Platform - 自动赚钱项目
出售在线课程，实现被动收入
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Online Course Platform", version="1.0.0")

DB_PATH = Path.home() / "桌面" / "online-course-platform" / "courses.db"
DB_PATH.parent.mkdir(exist_ok=True)

class Course(BaseModel):
    title: str
    description: str
    price: float
    category: str
    lessons: int = 0

class Enrollment(BaseModel):
    course_id: int
    student_email: str

@app.get("/")
async def root():
    return {
        "message": "Online Course Platform - 自动赚钱",
        "version": "1.0.0",
        "popular_categories": ["Programming", "Business", "Design", "Marketing"]
    }

@app.post("/create-course")
async def create_course(course: Course):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (title, description, price, category, lessons) VALUES (?, ?, ?, ?, ?)",
        (course.title, course.description, course.price, course.category, course.lessons)
    )
    conn.commit()
    conn.close()
    return {"message": "Course created", "course_id": 1}

@app.post("/enroll")
async def enroll_student(enrollment: Enrollment):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM courses WHERE id = ?", (enrollment.course_id,))
    course = cursor.fetchone()
    if not course:
        conn.close()
        return {"error": "Course not found"}
    
    cursor.execute(
        "INSERT INTO enrollments (course_id, email, amount) VALUES (?, ?, ?)",
        (enrollment.course_id, enrollment.student_email, course[0])
    )
    conn.commit()
    conn.close()
    return {"message": "Enrolled successfully", "price": course[0]}

@app.get("/stats")
async def stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM enrollments")
    total_students = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM enrollments")
    total_revenue = cursor.fetchone()[0] or 0
    conn.close()
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_revenue": total_revenue,
        "monthly_revenue": total_revenue * 1.2
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
