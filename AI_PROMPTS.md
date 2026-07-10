# AI Tool Usage Report

This project was developed using AI-assisted development (Cursor, Claude, OpenAI ChatGPT/Codex). AI was used to accelerate planning, implementation, debugging, and documentation. All generated code was manually reviewed, modified where necessary, tested locally, and validated before deployment.

---

# 1. Prompt Used for Planning

## Prompt

> Build the Ethara Seat Allocation & Project Mapping System from the provided assessment document. Identify the required entities, relationships, backend APIs, dashboard metrics, frontend pages, AI assistant capabilities, deployment architecture, documentation requirements, and overall project folder structure. Follow production-ready software engineering practices.

---

# 2. Prompt Used for Backend

## Prompt

> Generate a FastAPI backend using SQLAlchemy Async ORM, Pydantic models, Alembic migrations, and PostgreSQL. Create REST APIs for Employees, Projects, Seats, Seat Allocations, Dashboard statistics, CSV upload, and an AI assistant endpoint. Follow a layered architecture with routers, services, schemas, and models.

---

# 3. Prompt Used for Database Design

## Prompt

> Design a normalized PostgreSQL database for employees, projects, seats, and seat allocations. Include proper foreign keys, unique constraints, indexes, seat statuses, project mapping, allocation history, onboarding employees, and business rules preventing duplicate active seat allocations.

---

# 4. Prompt Used for Frontend

## Prompt

> Build a React + Vite + TypeScript frontend matching the assessment requirements. Create pages for Dashboard, Employees, Projects, Seats, Allocations, and an AI Assistant. Connect all pages with the FastAPI backend using REST APIs and display real-time dashboard metrics.

---

# 5. Prompt Used for AI Assistant

## Prompt

> Implement a lightweight rule-based assistant that answers workspace questions without requiring an external LLM. Support queries such as employee seat lookup, available seats, project allocation, floor occupancy, and project utilization.

---

# 6. Prompt Used for Debugging

## Prompt

> Review the entire repository for runtime issues, missing dependencies, incorrect API routes, migration problems, PostgreSQL connection issues, frontend integration bugs, deployment errors, CORS configuration, and production environment setup. Suggest fixes while preserving existing functionality.

---

# 7. Prompt Used for Deployment

## Prompt

> Prepare the application for production deployment. Configure environment variables, PostgreSQL connection, Alembic migrations, Render backend deployment, Vercel frontend deployment, CORS settings, API documentation, README, and deployment verification steps.

---

# What AI Generated Correctly

AI successfully generated:

- Overall project architecture
- FastAPI project structure
- SQLAlchemy models
- Pydantic schemas
- CRUD API endpoints
- Dashboard API structure
- React frontend components
- Initial dashboard layout
- Seed data generator
- Swagger/OpenAPI documentation
- Deployment instructions
- README documentation

---

# What AI Generated Incorrectly

Several generated components required manual correction:

- PostgreSQL connection configuration required fixes for production.
- Seat status enum was missing the **Occupied** state.
- Some API route ordering caused endpoint conflicts.
- Seed generator produced large transactions that required batching.
- Frontend API configuration required production URL changes.
- Render deployment initially failed because of missing dependencies (`psycopg2-binary`).
- CORS configuration required updates for the deployed frontend.
- Environment variable configuration required corrections for production.

---

# What Candidate Manually Fixed

The following work was completed manually:

- Fixed PostgreSQL authentication and connection issues.
- Updated Alembic configuration.
- Corrected database URL handling.
- Fixed seed data generation and batching.
- Added missing seat status values.
- Updated backend API routing.
- Fixed frontend API integration.
- Corrected production environment variables.
- Configured Render deployment.
- Configured Vercel deployment.
- Fixed CORS errors between frontend and backend.
- Verified CRUD operations.
- Improved README documentation.
- Improved project structure and deployment readiness.

---

# How Candidate Verified Correctness

The application was manually verified by:

- Running Alembic migrations successfully.
- Executing the seed script and confirming:
  - 11 projects
  - 5,500 seats
  - 5,000 employees
  - 4,900 active allocations
  - 500 available seats
  - 100 reserved seats
  - 50 onboarding employees
- Testing CRUD APIs using Swagger.
- Testing employee creation, update, deletion, and search.
- Testing project management.
- Testing seat allocation and release.
- Testing dashboard statistics.
- Testing AI assistant responses.
- Testing CSV upload functionality.
- Deploying the backend to Render.
- Deploying the frontend to Vercel.
- Verifying API connectivity between frontend and backend.
- Confirming successful production deployment.
