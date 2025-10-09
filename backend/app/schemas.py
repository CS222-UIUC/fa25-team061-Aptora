from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import DifficultyLevel, TaskType


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Course schemas
class CourseBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class Course(CourseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Assignment schemas
class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    estimated_hours: float
    difficulty: DifficultyLevel
    task_type: TaskType


class AssignmentCreate(AssignmentBase):
    course_id: int


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    difficulty: Optional[DifficultyLevel] = None
    task_type: Optional[TaskType] = None
    is_completed: Optional[bool] = None


class Assignment(AssignmentBase):
    id: int
    course_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Availability slot schemas
class AvailabilitySlotBase(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str  # Format: "HH:MM"
    end_time: str  # Format: "HH:MM"


class AvailabilitySlotCreate(AvailabilitySlotBase):
    pass


class AvailabilitySlotUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class AvailabilitySlot(AvailabilitySlotBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Study session schemas
class StudySessionBase(BaseModel):
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None


class StudySessionCreate(StudySessionBase):
    assignment_id: int


class StudySessionUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None


class StudySession(StudySessionBase):
    id: int
    user_id: int
    assignment_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schedule generation schemas
class ScheduleRequest(BaseModel):
    start_date: datetime
    end_date: datetime


class ScheduleResponse(BaseModel):
    study_sessions: List[StudySession]
    total_hours_scheduled: float
    assignments_covered: List[int]


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
