# AI Usage Report

## Project

**Ethara Seat Allocation & Project Mapping System**

This project was developed using AI-assisted development (OpenAI Codex/ChatGPT) together with manual implementation, debugging, testing, and validation.

AI was used to accelerate development, generate boilerplate code, suggest architecture, and assist in debugging. Every generated component was reviewed, modified where necessary, and verified before being included in the final application.

---

# 1. Project Planning

### Prompt

> Analyze the Ethara Seat Allocation & Project Mapping assessment document and propose a scalable full-stack architecture including database design, REST APIs, frontend pages, dashboard metrics, AI assistant behavior, deployment strategy, and documentation.

### AI Output

AI suggested:

- FastAPI backend
- React + Vite frontend
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- Layered architecture
- REST API design
- Dashboard layout
- Seed data strategy

### Manual Validation

- Compared architecture against assessment requirements.
- Removed unnecessary complexity.
- Adjusted project structure.
- Verified all required features were covered.

---

# 2. Database Design

### Prompt

> Design a normalized PostgreSQL schema for employees, projects, seats, and seat allocations. Enforce unique employee codes, unique emails, unique seat locations, allocation history, seat availability, reserved seats, and project mapping.

### AI Output

Generated:

- Employees table
- Projects table
- Seats table
- Seat Allocations table
- Relationships
- Constraints
- Index recommendations

### Manual Changes

- Added Occupied seat status.
- Updated migration files.
- Verified foreign keys.
- Verified allocation rules.

---

# 3. Backend Development

### Prompt

> Create a production-ready FastAPI backend using SQLAlchemy Async ORM, Pydantic models, service layer, CRUD APIs, dashboard endpoints, CSV upload, and an AI assistant endpoint.

### AI Output

Generated:

- CRUD APIs
- Schemas
- Services
- Routers
- Validation
- Dashboard endpoints
- Assistant endpoint

### Manual Improvements

- Fixed API routing order.
- Corrected seat allocation logic.
- Added missing endpoints.
- Improved error handling.
- Fixed deployment configuration.

---

# 4. Frontend Development

### Prompt

> Build a React + Vite dashboard matching the assessment requirements with employee management, projects, seats, allocations, analytics, and AI assistant.

### AI Output

Generated:

- Dashboard
- Employee page
- Project page
- Seat page
- Allocation page
- AI Assistant page

### Manual Improvements

- Redesigned layouts.
- Fixed responsive behavior.
- Connected frontend to backend APIs.
- Added loading states.
- Improved forms.
- Fixed API integration.

---

# 5. AI Assistant

### Prompt

> Implement an offline rule-based assistant capable of answering seat allocation and project mapping questions without requiring an external LLM API.

### AI Output

Created a deterministic assistant capable of answering questions such as:

- Where is Employee00001 seated?
- Which seats are available?
- Show seats on Floor 3.
- Which project is an employee assigned to?
- Floor occupancy.
- Project utilization.

### Manual Validation

Verified responses using actual database queries.

---

# 6. Seed Data

### Prompt

> Generate realistic assessment seed data including:
>
> - 11 Projects
> - 5 Floors
> - 5,500 Seats
> - 5,000 Employees
> - 4,900 Active Allocations
> - 500 Available Seats
> - 100 Reserved Seats
> - 50 Onboarding Employees

### AI Output

Generated deterministic seed generator.

### Manual Improvements

- Fixed batch insertion.
- Solved PostgreSQL SSL issues.
- Reduced transaction failures.
- Verified dashboard metrics.

---

# 7. Debugging

AI assisted with debugging:

- PostgreSQL authentication
- Neon database connection
- Alembic migrations
- SQLAlchemy configuration
- Async session handling
- CORS
- Render deployment
- Vercel deployment
- Environment variables
- Frontend API configuration

### Manual Fixes

- Updated Render environment variables.
- Fixed frontend production API URL.
- Fixed deployment configuration.
- Corrected routing issues.
- Validated production deployment.

---

# 8. Deployment

### Prompt

> Prepare the application for deployment using Render, Vercel, PostgreSQL, Alembic migrations, environment variables, and production settings.

### AI Output

Generated deployment steps.

### Manual Validation

Successfully deployed:

- Backend → Render
- Frontend → Vercel
- Database → Neon PostgreSQL

Verified:

- Swagger API
- Health endpoint
- Dashboard APIs
- CRUD operations
- Production connectivity

---

# 9. Manual Verification

The following were manually tested:

- Employee CRUD
- Project CRUD
- Seat allocation
- Seat release
- Dashboard statistics
- CSV upload
- Employee search
- Project mapping
- AI assistant
- Production deployment
- REST APIs
- Swagger documentation

---

# Technologies Used

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- AsyncIO

## Frontend

- React
- Vite
- TypeScript
- React Query
- React Router
- CSS

## Deployment

- Render
- Vercel
- Neon PostgreSQL

---

# AI Usage Declaration

AI was used as a development assistant to accelerate implementation, generate boilerplate code, suggest architecture, and assist with debugging.

All generated code was reviewed, modified where required, tested locally, and validated before deployment.

The final application—including debugging, production deployment, API integration, database configuration, and testing—was completed and verified manually by the candidate.
