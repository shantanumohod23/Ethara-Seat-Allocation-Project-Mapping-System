# AI Prompts and Validation Notes

This project was developed with Codex assistance. The candidate remains responsible for reviewing, testing, and validating generated code.

## Prompt Used for Planning

Build the Ethara Seat Allocation & Project Mapping System from the assessment document. Identify the required entities, APIs, seed data, dashboard metrics, frontend views, AI assistant fallback, documentation, and deployment notes.

## Prompt Used for Backend

Create a FastAPI backend with SQLAlchemy async models, Pydantic schemas, services, and REST endpoints for employees, projects, seats, seat allocations, dashboard metrics, and a rule-based assistant.

## Prompt Used for Database Design

Design tables for employees, projects, seats, and seat_allocations. Enforce unique employee email/code, unique seat location, one active seat per employee, one active employee per seat, allocation history, project mapping, seat statuses, and release behavior.

## Prompt Used for Frontend

Create a React/Vite dashboard for Ethara operations with metric cards, employee search, available seats, project allocation, floor occupancy, and a natural-language assistant panel.

## Prompt Used for AI Assistant

Implement a fallback keyword/intent parser for questions such as "Where is my seat?", "Where is employee Amit seated?", "Show available seats on Floor 3", and "How many seats are occupied for Project Indigo?"

## Prompt Used for Debugging

Inspect repository state, find placeholder modules, compile backend Python files, check route ordering, and identify missing dependency installation as a runtime verification gap.

## Prompt Used for Deployment

Document deployment-ready setup for PostgreSQL, FastAPI, Alembic migrations, seed data, Vite frontend, environment variables, and Swagger API documentation.

## What AI Generated Correctly

- Backend domain structure with models, schemas, services, and versioned endpoints.
- Seat allocation rules and release behavior.
- Rule-based assistant fallback.
- Seed data generator sized to the assessment.
- A usable React dashboard first screen.
- README setup, API list, and deployment notes.

## What AI Generated Incorrectly or Needed Adjustment

- The initial repository was mostly scaffolding and empty endpoint/page files.
- Seat status originally omitted `occupied`; this was added to the enum and migration path.
- Seat allocation routes needed to be registered before dynamic seat detail routes to avoid path shadowing.
- Full runtime verification could not be completed until dependencies are installed locally.

## What Candidate Manually Fixed

- Confirmed the assessment requirements from the provided `.docx`.
- Reviewed generated service and route behavior for the core business rules.
- Added required documentation and validation notes.
- Kept the assistant as a deterministic fallback so the demo works without an external AI API key.

## How Correctness Was Verified

- Ran Python static compilation for `backend/app` and `backend/alembic/versions`.
- Confirmed the seed generator creates the required counts by construction:
  - 11 projects;
  - 5,500 seats across 5 floors and 10 zones;
  - 5,000 employees;
  - 4,900 occupied seats via active allocations;
  - 500 available seats;
  - 100 reserved seats;
  - 50 onboarding employees pending allocation.
- Checked backend route ordering so `/seats/allocate`, `/seats/available`, and allocation routes are not shadowed by `/seats/{seat_id}`.
- Noted remaining verification requiring dependency installation: FastAPI app import, API integration tests, frontend TypeScript build, and browser smoke test.
