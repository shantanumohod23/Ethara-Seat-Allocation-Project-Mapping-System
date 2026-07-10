# Ethara Seat Allocation & Project Mapping System

> A modern full-stack workspace management application built for the Ethara Full Stack Developer Assessment.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

The **Ethara Seat Allocation & Project Mapping System** is a full-stack web application designed to manage employees, projects, workspaces, and seat allocations within an organization.

The system enables administrators to:

- Manage employees and projects
- Allocate employees to seats
- Track workspace occupancy
- Search employees and seat assignments
- View utilization analytics
- Interact with an AI-powered assistant for workspace queries

The project follows modern software engineering practices with a clean architecture, RESTful APIs, responsive frontend, and cloud deployment.

---

## Live Demo

### Frontend

**Vercel**

> https://ethara-seat-allocation-project-mapp-zeta.vercel.app

### Backend

**Render**

> https://ethara-seat-allocation-project-mapping-uduk.onrender.com/

### API Documentation

Swagger UI

> https://ethara-seat-allocation-project-mapping-uduk.onrender.com/docs#/

### Health Check

> https://ethara-seat-allocation-project-mapping-uduk.onrender.com/health

---

# Features

## Employee Management

- Create employees
- Update employee details
- Soft delete employees
- Search employees
- Pagination
- Sorting
- Filtering
- CSV Import

---

## Project Management

- Create projects
- Update projects
- Assign employees
- Track project utilization

---

## Seat Management

- Manage workspace seats
- Available
- Occupied
- Reserved
- Floor-wise organization
- Zone and Bay mapping

---

## Seat Allocation

- Allocate employees
- Release allocations
- Prevent duplicate seat assignments
- Automatic seat status updates

---

## Dashboard

Real-time dashboard displaying

- Total Employees
- Total Seats
- Occupied Seats
- Available Seats
- Reserved Seats
- Pending New Joiners
- Project Utilization
- Floor Occupancy

---

## AI Assistant

Natural language workspace assistant capable of answering questions such as:

- Where is Employee00001 seated?
- Show available seats on Floor 3
- Which project has the highest utilization?
- List employees in Indigo project

---

# Tech Stack

## Frontend

- React 18
- TypeScript
- Vite
- TanStack Query
- React Router
- Tailwind CSS
- Axios

---

## Backend

- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- Async PostgreSQL
- psycopg2
- asyncpg

---

## Database

- PostgreSQL
- Neon Database

---

## Deployment

Frontend

- Vercel

Backend

- Render

Database

- Neon PostgreSQL

---

# Architecture

```text
                React + Vite
                      │
                      │ REST API
                      ▼
                FastAPI Backend
                      │
                SQLAlchemy ORM
                      │
                      ▼
                PostgreSQL (Neon)
```

---

# Project Structure

```
ethara-seat-allocation/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── README.md
├── AI_PROMPTS.md
└── LICENSE
```

---

# API Overview

## Employees

- GET /employees
- POST /employees
- GET /employees/{id}
- PUT /employees/{id}
- DELETE /employees/{id}
- POST /employees/upload-csv

---

## Projects

- GET /projects
- POST /projects
- PUT /projects/{id}

---

## Seats

- GET /seats
- GET /seats/available

---

## Allocations

- POST /allocations
- DELETE /allocations/{id}

---

## Dashboard

- GET /dashboard/summary
- GET /dashboard/project-utilization
- GET /dashboard/floor-utilization

---

## AI Assistant

- POST /assistant/query

---

# Local Setup

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ethara-seat-allocation.git

cd ethara-seat-allocation
```

---

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
alembic upgrade head
```

Seed demo data

```bash
python -m app.seed
```

Run server

```bash
uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Environment Variables

Backend

```
DATABASE_URL=

SECRET_KEY=

CORS_ORIGINS=

DEBUG=

ENVIRONMENT=

LOG_LEVEL=
```

Frontend

```
VITE_API_BASE_URL=
```

---

# Sample Dataset

The project includes generated demo data:

| Resource | Count |
|----------|------:|
| Employees | 5,000 |
| Seats | 5,500 |
| Occupied Seats | 4,900 |
| Available Seats | 500 |
| Reserved Seats | 100 |
| Projects | 11 |

---

# AI Usage

Artificial Intelligence was used throughout development for:

- System architecture planning
- Backend scaffolding
- API design
- Frontend development
- SQLAlchemy optimization
- Debugging
- Deployment assistance
- Documentation generation

Complete prompts are available in:

```
AI_PROMPTS.md
```

---

# Future Improvements

- Authentication & Authorization
- Role-Based Access Control (RBAC)
- Interactive Floor Map
- Real-time Seat Updates using WebSockets
- Email Notifications
- AI Seat Recommendation Engine
- Audit Logs
- Export Reports
- Analytics Dashboard

---

# Screenshots

## Dashboard

<img width="1895" height="838" alt="image" src="https://github.com/user-attachments/assets/7752f6bb-8f98-47ea-89c5-18f24c5bfa56" />


---

## Employees

<img width="1536" height="1024" alt="employee" src="https://github.com/user-attachments/assets/cf4ee5f6-b57e-4700-ac5c-4b9c7856cdd4" />


---

## Projects

<img width="1890" height="853" alt="image" src="https://github.com/user-attachments/assets/81b92074-80ce-47ff-b47d-520389ab4eff" />


---

## Seats

<img width="1892" height="848" alt="image" src="https://github.com/user-attachments/assets/90d8eef7-be8b-445e-94b5-2cbd91fc8b36" />


---

## AI Assistant

<img width="1897" height="868" alt="image" src="https://github.com/user-attachments/assets/94b20758-391e-4a0f-9f5d-0eab808d31a5" />


---

# License

This project is licensed under the MIT License.

---

# Author

**Shantanu Mohod**

GitHub

https://github.com/shantanumohod23

LinkedIn

https://linkedin.com/in/shantanumohod

---

