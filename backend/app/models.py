from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class DifficultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskType(enum.Enum):
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    PROJECT = "project"


class PriorityLevel(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    # Notification settings
    reminders_enabled = Column(Boolean, default=True)
    reminder_lead_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    courses = relationship("Course", back_populates="user")
    availability_slots = relationship("AvailabilitySlot", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="courses")
    assignments = relationship("Assignment", back_populates="course")


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime(timezone=True), nullable=False)
    estimated_hours = Column(Float, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    priority = Column(Enum(PriorityLevel), nullable=False, default=PriorityLevel.MEDIUM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="assignments")
    study_sessions = relationship("StudySession", back_populates="assignment")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)  # Format: "HH:MM"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="availability_slots")


class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, default=False)
    notes = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    assignment = relationship("Assignment", back_populates="study_sessions")
    reminder_log = relationship("StudySessionReminder", back_populates="study_session", uselist=False, cascade="all, delete-orphan")


class StudySessionReminder(Base):
    __tablename__ = "study_session_reminders"

    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"), unique=True, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    study_session = relationship("StudySession", back_populates="reminder_log")


# UIUC Course Catalog Models
class CourseSection(Base):
    __tablename__ = "course_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    crn = Column(String, nullable=False)
    days = Column(String)
    times = Column(String)
    instructor = Column(String)
    course_catalog_id = Column(Integer, ForeignKey("course_catalog.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course_catalog = relationship("CourseCatalog", back_populates="sections")


class CourseCatalog(Base):
    __tablename__ = "course_catalog"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False, index=True)
    number = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    credit_hours = Column(Float)
    description = Column(Text)
    semester = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sections = relationship("CourseSection", back_populates="course_catalog", cascade="all, delete-orphan")


# ML and Web Scraping Models

class ScraperSource(enum.Enum):
    RATEMYPROFESSOR = "ratemyprofessor"
    REDDIT = "reddit"
    COURSE_REVIEW = "course_review"
    COURSE_FORUM = "course_forum"


class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProfessorRating(Base):
    __tablename__ = "professor_ratings"

    id = Column(Integer, primary_key=True, index=True)
    professor_name = Column(String, nullable=False, index=True)
    course_subject = Column(String, nullable=False)
    course_number = Column(String, nullable=False)
    overall_rating = Column(Float)  # 1-5 scale
    difficulty_rating = Column(Float)  # 1-5 scale
    would_take_again_percent = Column(Float)  # 0-100
    source = Column(Enum(ScraperSource), nullable=False)
    source_url = Column(Text)
    rating_count = Column(Integer, default=0)
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CourseInsight(Base):
    __tablename__ = "course_insights"

    id = Column(Integer, primary_key=True, index=True)
    course_subject = Column(String, nullable=False, index=True)
    course_number = Column(String, nullable=False, index=True)
    avg_hours_per_week = Column(Float)
    difficulty_score = Column(Float)  # 0-10 scale
    workload_rating = Column(Float)  # 1-5 scale
    assignment_frequency = Column(String)  # "weekly", "biweekly", etc.
    exam_count = Column(Integer)
    source = Column(Enum(ScraperSource), nullable=False)
    semester = Column(String)
    year = Column(Integer)
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AssignmentPattern(Base):
    __tablename__ = "assignment_patterns"

    id = Column(Integer, primary_key=True, index=True)
    course_subject = Column(String, nullable=False)
    course_number = Column(String, nullable=False)
    assignment_type = Column(Enum(TaskType), nullable=False)
    typical_duration_hours = Column(Float)
    difficulty_avg = Column(Float)
    student_feedback_count = Column(Integer, default=0)
    source = Column(Text)
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MLModelType(enum.Enum):
    TIME_ESTIMATOR = "time_estimator"
    SCHEDULER_POLICY = "scheduler_policy"


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(Enum(MLModelType), nullable=False)
    version = Column(String, nullable=False)
    model_path = Column(String, nullable=False)  # Filesystem path
    metrics = Column(Text)  # JSON string of metrics
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    feature_importance = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudyTimePrediction(Base):
    __tablename__ = "study_time_predictions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    predicted_hours = Column(Float, nullable=False)
    confidence_score = Column(Float)  # 0-1 scale
    model_version = Column(String)
    features_used = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignment = relationship("Assignment")


class StudySessionFeedback(Base):
    __tablename__ = "study_session_feedback"

    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=False)
    actual_duration_hours = Column(Float)
    productivity_rating = Column(Float)  # 1-5 scale
    difficulty_rating = Column(Float)  # 1-5 scale
    was_sufficient = Column(Boolean)
    student_comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    study_session = relationship("StudySession")


class ScraperJob(Base):
    __tablename__ = "scraper_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False)  # "professor", "course", "assignment"
    target_identifier = Column(String, nullable=False)  # Course code, professor name
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    records_scraped = Column(Integer, default=0)
    next_scheduled_run = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
