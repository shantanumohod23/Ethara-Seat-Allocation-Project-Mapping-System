"""
Assessment seed data generator.

Run:
    python -m app.seed
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.employee import Employee
from app.models.enums import (
    AllocationStatus,
    EmploymentStatus,
    ProjectStatus,
    SeatStatus,
)
from app.models.project import Project
from app.models.seat import Seat
from app.models.seat_allocation import SeatAllocation


PROJECT_NAMES = [
    "Indigo",
    "Indreed",
    "Mydreed",
    "Preed",
    "Serfy",
    "Oreed",
    "Bedegreed",
    "Opreed",
    "Serry",
    "Kaary",
    "Mered",
]

DEPARTMENTS = [
    "Engineering",
    "HR",
    "Admin",
    "Growth",
    "Operations",
    "Finance",
]

ROLES = [
    "Associate",
    "Senior Associate",
    "Lead",
    "Manager",
    "Analyst",
]


async def seed():
    async with AsyncSessionLocal() as db:

        existing = (
            await db.execute(select(Project.id).limit(1))
        ).scalar_one_or_none()

        if existing:
            print("Database already seeded.")
            return

        # ----------------------------
        # Projects
        # ----------------------------

        projects = []

        for i, name in enumerate(PROJECT_NAMES):
            projects.append(
                Project(
                    project_code=name.upper()[:12],
                    name=name,
                    description=f"Ethara workspace allocation group for {name}",
                    manager_name=f"{name} Manager",
                    status=ProjectStatus.ACTIVE,
                    start_date=date(2024, 1, 1) + timedelta(days=i * 10),
                )
            )

        db.add_all(projects)
        await db.flush()

        # ----------------------------
        # Seats
        # ----------------------------

        seats = []

        zones = [f"Zone {c}" for c in "ABCDEFGHIJ"]

        for floor in range(1, 6):
            for zone in zones:
                for bay in range(1, 12):
                    for seat in range(1, 11):

                        status = SeatStatus.AVAILABLE

                        # last 100 reserved
                        if len(seats) >= 5400:
                            status = SeatStatus.RESERVED

                        seats.append(
                            Seat(
                                floor=str(floor),
                                zone=zone,
                                bay=f"Bay {bay}",
                                seat_number=f"{zone[-1]}{bay}-{seat:02d}",
                                status=status,
                            )
                        )

        db.add_all(seats)
        await db.flush()

        # ----------------------------
        # Employees
        # ----------------------------

        employees = []

        for i in range(5000):

            employment = EmploymentStatus.ACTIVE

            if i >= 4950:
                employment = EmploymentStatus.ONBOARDING

            employees.append(
                Employee(
                    employee_code=f"EMP-{i+1:05d}",
                    email=f"employee{i+1:05d}@ethara.ai",
                    first_name=f"Employee{i+1:05d}",
                    last_name=f"Ethara{(i % 500):03d}",
                    department=DEPARTMENTS[i % len(DEPARTMENTS)],
                    job_title=ROLES[i % len(ROLES)],
                    joining_date=date(2024, 1, 1)
                    + timedelta(days=i % 900),
                    employment_status=employment,
                    project_id=projects[i % len(projects)].id,
                )
            )

        db.add_all(employees)
        await db.flush()

        # ------------------------------------------------
        # COMMIT PROJECTS + SEATS + EMPLOYEES FIRST
        # ------------------------------------------------

        await db.commit()

    # ====================================================
    # NEW TRANSACTION
    # ====================================================

    async with AsyncSessionLocal() as db:

        employees = (
            await db.execute(select(Employee).order_by(Employee.id))
        ).scalars().all()

        seats = (
            await db.execute(select(Seat).order_by(Seat.id))
        ).scalars().all()

        allocations = []

        for i in range(4900):

            allocations.append(
                SeatAllocation(
                    employee_id=employees[i].id,
                    seat_id=seats[i].id,
                    project_id=employees[i].project_id,
                    status=AllocationStatus.ACTIVE,
                    notes="Initial assessment seed allocation.",
                )
            )

        db.add_all(allocations)

        # INSERT allocations first
        await db.flush()

        # AFTER trigger succeeds
        # mark seats occupied

        for i in range(4900):
            seats[i].status = SeatStatus.OCCUPIED

        await db.commit()

    print(
        "Seed completed successfully.\n"
        "Projects : 11\n"
        "Seats    : 5500\n"
        "Employees: 5000\n"
        "Allocated: 4900\n"
        "Available: 500\n"
        "Reserved : 100\n"
        "Onboarding employees: 50"
    )


async def reset_and_seed():

    async with AsyncSessionLocal() as db:

        await db.execute(delete(SeatAllocation))
        await db.execute(delete(Employee))
        await db.execute(delete(Seat))
        await db.execute(delete(Project))

        await db.commit()

    await seed()


if __name__ == "__main__":
    asyncio.run(seed())