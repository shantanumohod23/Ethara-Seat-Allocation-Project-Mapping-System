# Ethara Seat Allocation & Project Mapping System

Full-stack assessment project for managing Ethara employee seating, project mapping, new-joiner allocation, utilization dashboards, and natural-language seat queries.

## Features

- Employee CRUD with unique employee code/email and soft deactivation.
- Project creation, listing, detail view, update, and project employee lookup.
- Seat inventory with floor, zone, bay, seat number, and status.
- Seat allocation and release rules:
  - one active seat per employee;
  - one active employee per seat;
  - reserved, occupied, and maintenance seats cannot be allocated;
  - released seats become available again.
- New-joiner seat suggestions using project-team floor/zone proximity.
- Search and filter support for employees and seats.
- Dashboard APIs for summary, project utilization, and floor utilization.
- Rule-based AI assistant fallback at `POST /api/v1/ai/query`.
- Deterministic seed generator for 5,000 employees, 5,500 seats, 11 projects, 4,900 active allocations, 500 available seats, 100 reserved seats, and 50 onboarding employees pending allocation.
- React dashboard with employee search, utilization panels, available seats, and assistant query UI.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, Vite, TypeScript, Tailwind CSS, Axios |
| Backend | FastAPI, SQLAlchemy async ORM, Alembic, Pydantic |
| Database | PostgreSQL |
| Local infra | Docker Compose |

## Project Structure

```text
ethara-seat-allocation/
  backend/                 FastAPI app, models, schemas, services, migrations
  frontend/                React Vite app
  docs/                    Architecture notes
  docker-compose.yml       Local PostgreSQL
  .env.example             Backend and frontend environment values
  AI_PROMPTS.md            AI usage and validation notes
```

## Local Setup

1. Copy environment values:

```bash
cp .env.example .env
```

2. Start PostgreSQL:

```bash
docker compose up -d
```

3. Install backend dependencies and run migrations:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

4. Install frontend dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

## Required API Endpoints

| Area | Endpoint |
| --- | --- |
| Employees | `POST /api/v1/employees`, `GET /api/v1/employees`, `GET /api/v1/employees/{id}`, `PUT /api/v1/employees/{id}`, `DELETE /api/v1/employees/{id}` |
| Projects | `POST /api/v1/projects`, `GET /api/v1/projects`, `GET /api/v1/projects/{id}`, `PUT /api/v1/projects/{id}`, `GET /api/v1/projects/{id}/employees` |
| Seats | `POST /api/v1/seats`, `GET /api/v1/seats`, `GET /api/v1/seats/{id}`, `PUT /api/v1/seats/{id}`, `GET /api/v1/seats/available` |
| Allocation | `POST /api/v1/seats/allocate`, `POST /api/v1/seats/release`, `POST /api/v1/seats/release/{allocation_id}`, `GET /api/v1/seats/suggestions/{employee_id}`, `GET /api/v1/seats/allocations` |
| Dashboard | `GET /api/v1/dashboard/summary`, `GET /api/v1/dashboard/project-utilization`, `GET /api/v1/dashboard/floor-utilization` |
| Assistant | `POST /api/v1/ai/query` |

Example assistant request:

```json
{
  "query": "Where is my seat? My email is employee00001@ethara.ai"
}
```

## Deployment Notes

- Deploy the backend to Render, Railway, or Fly.io with PostgreSQL.
- Deploy the frontend to Vercel or Netlify.
- Set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, and `VITE_API_BASE_URL` in the platform environment.
- Run `alembic upgrade head` before `python -m app.seed` in the deployed backend environment.

## Verification Status

- Static Python compilation passes for `backend/app` and Alembic migrations using the bundled runtime.
- Full FastAPI import, API tests, and frontend build require installing project dependencies in this workspace.
