from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routers import auth, courses, assignments, availability, schedules

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Study Scheduler API",
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


@app.get("/")
async def root():
    return {"message": "Smart Study Scheduler API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
