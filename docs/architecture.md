# Architecture — Ethara Seat Allocation & Project Mapping System

## Overview

This application follows **clean architecture** with a clear separation between presentation (frontend), application/API (routes + services), and persistence (models + database). Dependencies always point inward: HTTP handlers depend on services; services depend on models and the database — never the reverse.

Designed to scale to ~5,000 employees with room for pagination, indexing, and caching at the service layer.

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                       │
│  pages → components → hooks → api/endpoints → types         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (Axios)
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│  api/v1/endpoints → services → models → db                   │
│         ↕ schemas (Pydantic DTOs, boundary layer)             │
└──────────────────────────┬──────────────────────────────────┘
                           │ SQLAlchemy (async)
┌──────────────────────────▼──────────────────────────────────┐
│                    PostgreSQL                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Root Level

| Path | Purpose |
| ---- | ------- |
| `README.md` | Project overview, tech stack, and quick-start guide |
| `.env.example` | Template for environment variables (never commit secrets) |
| `.gitignore` | Excludes virtualenvs, node_modules, secrets, and build artifacts |
| `docker-compose.yml` | Local PostgreSQL instance for development |
| `docs/` | Architecture and design documentation |

---

## Backend (`backend/`)

The backend is a self-contained Python package. All application code lives under `backend/app/`.

### `backend/requirements.txt` & `requirements-dev.txt`

Production and development Python dependencies. Split keeps production images lean.

### `backend/alembic/` & `alembic.ini`

Database migration tooling. Alembic tracks schema changes independently of application code.

| Path | Purpose |
| ---- | ------- |
| `alembic/env.py` | Migration runtime — connects Alembic to SQLAlchemy metadata |
| `alembic/script.py.mako` | Template for auto-generated migration files |
| `alembic/versions/` | Timestamped migration scripts (empty until first migration) |

### `backend/app/main.py`

FastAPI application factory and middleware registration. Single entry point for Uvicorn.

### `backend/app/core/`

**Cross-cutting application configuration** — settings, logging, and future auth/security.

| File | Purpose |
| ---- | ------- |
| `config.py` | Pydantic Settings — reads from environment (DB URL, CORS, secrets) |
| `logging.py` | Structured logging setup for production observability |

> **Why separate?** Configuration is consumed by every layer but belongs to none. Keeping it in `core/` avoids circular imports.

### `backend/app/db/`

**Database infrastructure** — connection pooling, session lifecycle, and the declarative base.

| File | Purpose |
| ---- | ------- |
| `base.py` | SQLAlchemy `DeclarativeBase` and shared mixins (timestamps, soft-delete) |
| `session.py` | Async engine, session factory, and `get_db()` dependency |

> **Why separate from models?** Session management is infrastructure. Models should not know how connections are created.

### `backend/app/models/`

**SQLAlchemy ORM models** — database table definitions and relationships.

| File | Domain entity |
| ---- | ------------- |
| `employee.py` | Employee records (~5,000 rows) |
| `project.py` | Projects / engagements |
| `seat.py` | Seat inventory (physical or logical) |
| `seat_allocation.py` | Join entity: employee ↔ seat ↔ project |

> **Why separate from schemas?** ORM models reflect storage shape (nullable columns, FK constraints). Pydantic schemas reflect API contracts. Mixing them couples your API to your database schema.

### `backend/app/schemas/`

**Pydantic DTOs** — request validation and response serialization.

| File | Purpose |
| ---- | ------- |
| `common.py` | Shared primitives: pagination params, ID wrappers, error shapes |
| `employee.py` | `EmployeeCreate`, `EmployeeUpdate`, `EmployeeRead` |
| `project.py` | Project input/output schemas |
| `seat.py` | Seat input/output schemas |
| `seat_allocation.py` | Allocation input/output schemas |

### `backend/app/services/`

**Business logic layer** — the heart of clean architecture.

Services orchestrate:
- Validation rules (e.g., one active seat per employee)
- Transaction boundaries
- Query composition and pagination for large datasets
- Cross-entity operations (allocate seat + update project mapping)

| File | Responsibility |
| ---- | -------------- |
| `employee_service.py` | Employee CRUD and search |
| `project_service.py` | Project lifecycle |
| `seat_service.py` | Seat inventory management |
| `seat_allocation_service.py` | Allocation rules and conflict detection |

> **Why separate from routes?** Routes should be thin HTTP adapters. Services are reusable from CLI scripts, background jobs, or tests without HTTP context.

### `backend/app/api/`

**HTTP transport layer** — FastAPI routers and dependency injection.

| Path | Purpose |
| ---- | ------- |
| `deps.py` | Shared FastAPI dependencies (DB session, pagination params) |
| `v1/router.py` | Aggregates all v1 endpoint routers under `/api/v1` |
| `v1/endpoints/employees.py` | Employee HTTP handlers |
| `v1/endpoints/projects.py` | Project HTTP handlers |
| `v1/endpoints/seats.py` | Seat HTTP handlers |
| `v1/endpoints/seat_allocations.py` | Allocation HTTP handlers |

> **Why versioned (`v1/`)?** Allows breaking API changes in `v2/` without disrupting existing clients.

### `backend/app/utils/`

**Stateless helper functions** — no business rules, no I/O.

| File | Purpose |
| ---- | ------- |
| `helpers.py` | General utilities |
| `pagination.py` | Offset/limit calculation, cursor encoding |

### `backend/tests/`

| Path | Purpose |
| ---- | ------- |
| `conftest.py` | Shared fixtures (test DB, async client, factory helpers) |
| `unit/` | Service-level tests with mocked DB |
| `integration/` | Full HTTP + database tests |

---

## Frontend (`frontend/`)

Feature-oriented React SPA with a layered data flow.

### Configuration & Build

| File | Purpose |
| ---- | ------- |
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Dev server, path aliases (`@/`), API proxy |
| `tsconfig.json` | TypeScript strict mode + path mapping |
| `tailwind.config.js` | Tailwind content paths and theme extensions |
| `postcss.config.js` | Tailwind + Autoprefixer pipeline |
| `index.html` | Vite entry HTML |

### `frontend/src/config/`

Runtime configuration (API base URL from `VITE_*` env vars).

### `frontend/src/types/`

**TypeScript interfaces** mirroring backend Pydantic schemas. Single source of truth for frontend data shapes.

### `frontend/src/api/`

**HTTP client layer** — Axios instance and per-resource endpoint functions.

| Path | Purpose |
| ---- | ------- |
| `client.ts` | Axios instance with interceptors, base URL, error handling |
| `endpoints/employees.ts` | Typed functions: `getEmployees()`, `createEmployee()`, etc. |
| `endpoints/projects.ts` | Project API calls |
| `endpoints/seats.ts` | Seat API calls |
| `endpoints/seatAllocations.ts` | Allocation API calls |

> **Why separate from hooks?** API functions are pure HTTP — testable without React. Hooks add caching, loading state, and invalidation.

### `frontend/src/hooks/`

**React Query hooks** — server state management.

Each hook wraps API endpoints with query keys, stale times, and mutation invalidation. Critical for 5,000-employee lists (pagination, background refetch).

### `frontend/src/pages/`

**Route-level views** — one page per major feature area.

| Page | Purpose |
| ---- | ------- |
| `DashboardPage.tsx` | Overview metrics and quick actions |
| `EmployeesPage.tsx` | Employee list and management |
| `ProjectsPage.tsx` | Project mapping |
| `SeatsPage.tsx` | Seat inventory |
| `AllocationsPage.tsx` | Seat allocation workflow |

### `frontend/src/components/`

**Reusable UI**, organized by scope:

| Folder | Purpose |
| ------ | ------- |
| `common/` | Buttons, tables, modals, form inputs |
| `layout/` | App shell: header, sidebar, page wrapper |
| `employees/` | Employee-specific tables, forms, filters |
| `projects/` | Project-specific components |
| `seats/` | Seat map / list components |
| `allocations/` | Allocation workflow UI |

> **Why feature folders?** Keeps related UI co-located. `common/` holds truly shared primitives.

### `frontend/src/routes/`

React Router configuration — maps URLs to pages, defines nested layouts.

### `frontend/src/providers/`

Global React context providers (React Query client, theme, etc.).

### `frontend/src/utils/`

Pure frontend helpers (date formatting, display formatters).

---

## Data Flow Example (future implementation)

```
User clicks "Allocate Seat"
  → AllocationsPage (page)
  → AllocationForm (component)
  → useCreateSeatAllocation() (hook)
  → seatAllocationsApi.create() (api/endpoints)
  → POST /api/v1/seat-allocations (backend endpoint)
  → SeatAllocationService.create() (service)
  → SeatAllocation model (SQLAlchemy)
  → PostgreSQL
```

---

## Naming Conventions

| Context | Convention | Example |
| ------- | ---------- | ------- |
| Python modules | snake_case | `seat_allocation_service.py` |
| Python classes | PascalCase | `SeatAllocationService` |
| API routes | kebab-case URLs | `/api/v1/seat-allocations` |
| TypeScript files | camelCase | `seatAllocations.ts` |
| React components | PascalCase | `AllocationsPage.tsx` |
| React hooks | camelCase with `use` prefix | `useSeatAllocations.ts` |

---

## Next Steps (not in scope yet)

1. Implement SQLAlchemy models with indexes for 5K+ rows
2. Create initial Alembic migration
3. Implement Pydantic schemas and service layer
4. Wire FastAPI routes with pagination
5. Scaffold React pages with React Query data fetching
