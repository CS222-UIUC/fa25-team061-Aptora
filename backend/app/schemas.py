from pydantic import BaseModel, EmailStr, validator, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
from .models import DifficultyLevel, TaskType, PriorityLevel


def _validate_future_due_date(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("Due date must include timezone information")
    if value <= datetime.now(timezone.utc):
        raise ValueError("Due date must be in the future")
    return value


def _validate_optional_future_due_date(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return value
    return _validate_future_due_date(value)


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
    priority: PriorityLevel = PriorityLevel.MEDIUM


class AssignmentCreate(AssignmentBase):
    course_id: int
    @field_validator("due_date")
    def validate_due_date(cls, value: datetime) -> datetime:
        return _validate_future_due_date(value)


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    difficulty: Optional[DifficultyLevel] = None
    task_type: Optional[TaskType] = None
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None

    @field_validator("due_date")
    def validate_due_date(cls, value: Optional[datetime]) -> Optional[datetime]:
        return _validate_optional_future_due_date(value)


class Assignment(AssignmentBase):
    id: int
    course_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


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


# Course Catalog schemas
class CourseSectionBase(BaseModel):
    crn: str
    days: Optional[str] = None
    times: Optional[str] = None
    instructor: Optional[str] = None


class CourseSectionCreate(CourseSectionBase):
    pass


class CourseSection(CourseSectionBase):
    id: int
    course_catalog_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CourseCatalogBase(BaseModel):
    subject: str
    number: str
    title: str
    credit_hours: Optional[float] = None
    description: Optional[str] = None
    semester: str
    year: int


class CourseCatalogCreate(CourseCatalogBase):
    sections: Optional[List[CourseSectionCreate]] = []


class CourseCatalogUpdate(BaseModel):
    subject: Optional[str] = None
    number: Optional[str] = None
    title: Optional[str] = None
    credit_hours: Optional[float] = None
    description: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None


class CourseCatalog(CourseCatalogBase):
    id: int
    sections: List[CourseSection] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CourseCatalogSearch(BaseModel):
    subject: Optional[str] = None
    number: Optional[str] = None
    title: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None

# ML and Scraping Schemas

class ProfessorRatingBase(BaseModel):
    professor_name: str
    course_subject: str
    course_number: str
    overall_rating: Optional[float] = None
    difficulty_rating: Optional[float] = None
    would_take_again_percent: Optional[float] = None
    source: str
    source_url: Optional[str] = None
    rating_count: Optional[int] = 0


class ProfessorRatingCreate(ProfessorRatingBase):
    pass


class ProfessorRating(ProfessorRatingBase):
    id: int
    last_scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseInsightBase(BaseModel):
    course_subject: str
    course_number: str
    avg_hours_per_week: Optional[float] = None
    difficulty_score: Optional[float] = None
    workload_rating: Optional[float] = None
    assignment_frequency: Optional[str] = None
    exam_count: Optional[int] = None
    source: str
    semester: Optional[str] = None
    year: Optional[int] = None


class CourseInsightCreate(CourseInsightBase):
    pass


class CourseInsight(CourseInsightBase):
    id: int
    last_scraped_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudyTimePredictionBase(BaseModel):
    assignment_id: int
    predicted_hours: float
    confidence_score: Optional[float] = None
    model_version: Optional[str] = None
    features_used: Optional[dict] = None


class StudyTimePredictionCreate(StudyTimePredictionBase):
    pass


class StudyTimePrediction(StudyTimePredictionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudySessionFeedbackBase(BaseModel):
    study_session_id: int
    actual_duration_hours: Optional[float] = None
    productivity_rating: Optional[float] = None
    difficulty_rating: Optional[float] = None
    was_sufficient: Optional[bool] = None
    student_comments: Optional[str] = None


class StudySessionFeedbackCreate(StudySessionFeedbackBase):
    pass


class StudySessionFeedback(StudySessionFeedbackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MLScheduleRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    use_ml: bool = True


class MLPredictionResponse(BaseModel):
    predicted_hours: float
    confidence: float
    confidence_interval: tuple[float, float]
    feature_importance: dict


class CourseInsightsResponse(BaseModel):
    course_insights: List[CourseInsight]
    professor_ratings: List[ProfessorRating]
    avg_difficulty: Optional[float] = None
    avg_hours_per_week: Optional[float] = None


class MLScheduleResponse(BaseModel):
    study_sessions: List['StudySession']
    predictions: List[MLPredictionResponse]
    total_hours_scheduled: float
    ml_insights: dict
