"""Assessment seed data generator.

Run with:
    python -m app.seed
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.employee import Employee
from app.models.enums import AllocationStatus, EmploymentStatus, ProjectStatus, SeatStatus
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
    "bedegreed",
    "Opreed",
    "Serry",
    "Kaary",
    "Mered",
]

DEPARTMENTS = ["Engineering", "HR", "Admin", "Growth", "Operations", "Finance"]
ROLES = ["Associate", "Senior Associate", "Lead", "Manager", "Analyst"]


async def seed() -> None:
    """Create deterministic demo data sized to the assessment."""
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Project.id).limit(1))).scalar_one_or_none()
        if existing is not None:
            print("Database already has data; skipping seed.")
            return

        projects = [
            Project(
                project_code=name.upper()[:12],
                name=name,
                description=f"Ethara workspace allocation group for {name}.",
                manager_name=f"{name} Manager",
                status=ProjectStatus.ACTIVE,
                start_date=date(2024, 1, 1) + timedelta(days=index * 10),
            )
            for index, name in enumerate(PROJECT_NAMES)
        ]
        db.add_all(projects)
        await db.flush()

        seats: list[Seat] = []
        zones = [f"Zone {letter}" for letter in "ABCDEFGHIJ"]
        for floor in range(1, 6):
            for zone_index, zone in enumerate(zones, start=1):
                for bay in range(1, 12):
                    for seat_index in range(1, 11):
                        absolute = len(seats) + 1
                        status = SeatStatus.AVAILABLE
                        # Keep only the last 100 seats reserved.
                        if absolute > 5400:
                            status = SeatStatus.RESERVED
                        seats.append(
                            Seat(
                                floor=str(floor),
                                zone=zone,
                                bay=f"Bay {bay}",
                                seat_number=f"{zone[-1]}{bay}-{seat_index:02d}",
                                status=status,
                            ),
                        )
        db.add_all(seats)
        await db.flush()

        employees: list[Employee] = []
        for index in range(1, 5001):
            project = projects[(index - 1) % len(projects)]
            status = EmploymentStatus.ACTIVE
            if index > 4950:
                status = EmploymentStatus.ONBOARDING
            employees.append(
                Employee(
                    employee_code=f"EMP-{index:05d}",
                    email=f"employee{index:05d}@ethara.ai",
                    first_name=f"Employee{index:05d}",
                    last_name=f"Ethara{(index % 500):03d}",
                    department=DEPARTMENTS[index % len(DEPARTMENTS)],
                    job_title=ROLES[index % len(ROLES)],
                    joining_date=date(2024, 1, 1) + timedelta(days=index % 900),
                    employment_status=status,
                    project_id=project.id,
                ),
            )
        db.add_all(employees)
        await db.flush()

        allocations = [
            SeatAllocation(
                employee_id=employees[index].id,
                seat_id=seats[index].id,
                project_id=employees[index].project_id,
                status=AllocationStatus.ACTIVE,
                notes="Initial assessment seed allocation.",
            )
            for index in range(4900)
        ]
        db.add_all(allocations)
        await db.commit()
        print(
            "Seeded 11 projects, 5,500 seats, 5,000 employees, "
            "4,900 active allocations, 500 available seats, 100 reserved seats, "
            "and 50 onboarding employees pending allocation."
        )


async def reset_and_seed() -> None:
    """Clear generated domain data and reseed. Useful for local demos."""
    async with AsyncSessionLocal() as db:
        await db.execute(delete(SeatAllocation))
        await db.execute(delete(Employee))
        await db.execute(delete(Seat))
        await db.execute(delete(Project))
        await db.commit()
    await seed()


if __name__ == "__main__":
    asyncio.run(seed())
