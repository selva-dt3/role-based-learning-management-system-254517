from typing import List, Optional
from pydantic import BaseModel, Field


class LessonBase(BaseModel):
    title: str = Field(..., description="Lesson title")
    description: Optional[str] = Field(None, description="Lesson description")
    file_url: Optional[str] = Field(None, description="Public URL to lesson file in storage")


class LessonCreate(LessonBase):
    """Payload for creating a lesson."""
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    file_url: Optional[str] = Field(None, description="Updated file URL")


class Lesson(LessonBase):
    id: str = Field(..., description="Lesson ID")


class QuizBase(BaseModel):
    lesson_id: str = Field(..., description="Related lesson ID")
    title: str = Field(..., description="Quiz title")
    questions: List[dict] = Field(..., description="List of question objects")


class QuizCreate(QuizBase):
    """Payload for creating a quiz."""
    pass


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    questions: Optional[List[dict]] = Field(None, description="Updated questions")


class Quiz(QuizBase):
    id: str = Field(..., description="Quiz ID")


class AssignmentCreate(BaseModel):
    lesson_id: str = Field(..., description="Lesson ID to assign")
    employee_id: str = Field(..., description="Employee identifier")


class Assignment(BaseModel):
    id: str = Field(..., description="Assignment ID")
    lesson_id: str = Field(..., description="Lesson ID")
    employee_id: str = Field(..., description="Employee ID")


class CompletionCreate(BaseModel):
    lesson_id: str = Field(..., description="Completed lesson ID")
    employee_id: str = Field(..., description="Employee identifier")


class Completion(BaseModel):
    id: str = Field(..., description="Completion ID")
    lesson_id: str = Field(..., description="Lesson ID")
    employee_id: str = Field(..., description="Employee ID")
