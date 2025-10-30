from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routers import auth, courses, assignments, availability, schedules, course_catalog, admin, progress
from .scheduler import scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aptora API",
    description="A web app that helps students create personalized study plans",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(availability.router)
app.include_router(schedules.router)
app.include_router(course_catalog.router)
app.include_router(admin.router)
app.include_router(progress.router)


@app.on_event("startup")
async def startup_event():
    """Start the background scheduler on application startup"""
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the background scheduler on application shutdown"""
    scheduler.stop()


@app.get("/")
async def root():
    return {"message": "Aptora API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
