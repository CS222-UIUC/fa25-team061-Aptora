# Aptora

A web application that helps students create personalized study plans by balancing assignment deadlines, task difficulty, and their own productivity habits. It reduces stress and helps students work more efficiently to stay on top of their coursework by optimizing time management.

## Features

- **User Authentication**: Secure login and registration with email/password
- **Course Management**: Add, edit, and delete courses
- **Assignment Tracking**: Manage assignments with due dates, difficulty levels, and estimated hours
- **Availability Scheduling**: Set your preferred study times and availability
- **Smart Schedule Generation**: AI-powered algorithm that creates optimized study schedules
- **Progress Tracking**: Mark study sessions as completed and track progress
- **Modern UI**: Beautiful, responsive interface built with Material-UI

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Reliable relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **FastAPI Users**: Authentication and user management
- **scikit-learn**: Machine learning for schedule optimization
- **Celery**: Task queue for notifications and reminders

### Frontend
- **React**: Modern JavaScript library for building user interfaces
- **TypeScript**: Type-safe JavaScript for reduced bugs and better development experience
- **Material-UI**: React components implementing Google's Material Design
- **React Query**: Data fetching and caching with optimistic updates
- **React Hook Form**: Form handling with validation using Yup schemas
- **React Router**: Client-side routing with protected routes
- **React Testing Library**: Comprehensive testing framework for user interactions
- **Jest**: JavaScript testing framework with coverage reporting
- **React Big Calendar**: Interactive calendar component for schedule visualization

## Project Structure

```
fa25-fa25-team061/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication setup
│   │   ├── schedule_generator.py # Schedule optimization algorithm
│   │   └── routers/             # API route handlers
│   │       ├── auth.py
│   │       ├── courses.py
│   │       ├── assignments.py
│   │       ├── availability.py
│   │       └── schedules.py
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Application runner
│   └── env.example              # Environment variables template
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/          # Reusable React components
    │   ├── pages/               # Page components
    │   ├── contexts/            # React contexts
    │   ├── App.tsx              # Main application component
    │   └── index.tsx            # Application entry point
    └── package.json             # Node.js dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis (for Celery)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your database and other settings
   ```

5. Set up the database:
   ```bash
   # Create PostgreSQL database
   createdb aptora
   
   # Run migrations
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Run tests:
   ```bash
   npm test
   ```

5. Run tests with coverage:
   ```bash
   npm test -- --coverage
   ```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Features

### Smart Schedule Generation

The application uses a sophisticated algorithm to generate study schedules:

1. **Priority Calculation**: Assignments are prioritized based on:
   - Time urgency (closer due dates get higher priority)
   - Difficulty level (harder assignments get more time)
   - Estimated hours required

2. **Availability Matching**: The system matches assignments with your available time slots

3. **Optimization**: Uses clustering algorithms to minimize context switching and maximize productivity

### User Experience

- **Intuitive Interface**: Clean, modern design that's easy to navigate
- **Real-time Updates**: Changes are reflected immediately across the application
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Progress Tracking**: Visual indicators show completion status and progress
- **Calendar Visualization**: Interactive calendar view for schedule management
- **Comprehensive Testing**: Thorough test coverage ensures reliability
- **Error Handling**: Graceful error handling with user-friendly feedback

## Contributing

### Git branching strategy

- Main branches:
  - `main`: stable, production-ready. Only fast-forward merges from `develop` on release.
  - `develop`: integration branch for completed features; always green (CI passes).
- Short-lived branches:
  - `feature/<name>`: new features and UI work. Branch off `develop`, open PR into `develop`.
  - `fix/<name>`: bug fixes. Branch off `develop` (or `main` for hotfix), PR back accordingly.
  - `chore/<name>`: tooling, docs, or non-functional changes.
  - `hotfix/<name>`: urgent production fixes. Branch off `main`, PR into `main` and `develop`.
- Workflow:
  1) Create branch from `develop`.
  2) Commit with conventional prefix (feat:, fix:, chore:, docs:, test:).
  3) Open PR to `develop` with checklist and brief description.
  4) Require 1 reviewer approval + passing CI.
  5) Squash-merge; delete branch.

Naming examples: `feature/auth-jwt`, `fix/assignments-delete`, `chore/ci-pytest`.

### Team development setup

Backend
1. `cp backend/env.example backend/.env` and set `DATABASE_URL`, `SECRET_KEY`, `FRONTEND_URL`.
2. Create venv and install: `pip install -r backend/requirements.txt`.
3. Initialize DB (SQLite or Postgres). For local dev you may set `DATABASE_URL=sqlite:///./dev.db`.
4. Run API: `python backend/run.py` → `http://localhost:8000`.
5. Run tests: `pytest backend -q`.

Frontend
1. `cd frontend && npm install`.
2. `npm start` → `http://localhost:3000`.
3. Environment: use proxy or set `REACT_APP_API_URL` if needed.
4. Tests: `npm test`.

Notes on requested tech changes
- The project already uses FastAPI + SQLAlchemy; introducing MongoDB now would duplicate models and slow velocity. If MongoDB is still desired, we can plan a separate `feature/mongo-dev` spike to add an optional dev-only store without disrupting current SQL flows.
- The frontend is already set up and integrated; migrating to Vite can be scheduled later (`feature/vite-migration`) without blocking current delivery.

### Pull requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Team

This project was developed as part of CS222 coursework by Team 061.

## Future Enhancements

- Calendar export functionality (Google Calendar, iCal)
- Email notifications and reminders
- Mobile app development
- Advanced analytics and insights
- Integration with learning management systems
- Collaborative study planning features