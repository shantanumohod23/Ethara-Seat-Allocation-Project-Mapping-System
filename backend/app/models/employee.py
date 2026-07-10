"""Employee ORM model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import EmploymentStatus

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.seat_allocation import SeatAllocation


class Employee(Base, TimestampMixin):
    """
    Workforce record.

    Seat assignment is never stored here — current and historical placements
    are tracked exclusively through ``SeatAllocation`` rows.

    ``project_id`` reflects the employee's current project assignment.
    ``SeatAllocation.project_id`` captures the project at the time of each
    seat assignment and is preserved as historical context.
    """

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    employee_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        comment="Internal workforce identifier (e.g. EMP-0042).",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Corporate email; must be unique across all employees.",
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    joining_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date the employee joined the organization.",
    )
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(
            EmploymentStatus,
            name="employment_status",
            native_enum=True,
            create_constraint=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=EmploymentStatus.ACTIVE,
        server_default=EmploymentStatus.ACTIVE.value,
        comment="Only ACTIVE employees should receive new seat allocations.",
    )
    project_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        comment="Current project assignment; independent of allocation history.",
    )

    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="assigned_employees",
        foreign_keys=[project_id],
    )
    allocations: Mapped[list[SeatAllocation]] = relationship(
        "SeatAllocation",
        back_populates="employee",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_employees_department", "department"),
        Index("ix_employees_employment_status", "employment_status"),
        Index("ix_employees_project_id", "project_id"),
        Index("ix_employees_last_name_first_name", "last_name", "first_name"),
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} code={self.employee_code!r}>"
