"""Seat allocation ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import AllocationStatus

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project
    from app.models.seat import Seat


class SeatAllocation(Base, TimestampMixin):
    """
    Allocation history record linking an employee, seat, and project.

    Each row represents one assignment episode. Closing an assignment sets
    ``status`` to ``released`` or ``cancelled`` and populates ``released_at``.
    A new row is created for re-assignments — the employee table never stores
    a current seat pointer.
    """

    __tablename__ = "seat_allocations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    seat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("seats.id", ondelete="RESTRICT"),
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Project the employee is mapped to while seated.",
    )

    status: Mapped[AllocationStatus] = mapped_column(
        Enum(
            AllocationStatus,
            name="allocation_status",
            native_enum=True,
            create_constraint=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=AllocationStatus.ACTIVE,
        server_default=AllocationStatus.ACTIVE.value,
    )
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when this assignment became effective.",
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when this assignment ended (release or cancellation).",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee: Mapped[Employee] = relationship(
        "Employee",
        back_populates="allocations",
    )
    seat: Mapped[Seat] = relationship(
        "Seat",
        back_populates="allocations",
    )
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="allocations",
    )

    __table_args__ = (
        # One ACTIVE allocation per employee.
        Index(
            "uq_seat_allocations_active_employee",
            "employee_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        # One ACTIVE allocation per seat.
        Index(
            "uq_seat_allocations_active_seat",
            "seat_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        CheckConstraint(
            "(status = 'active' AND released_at IS NULL) OR "
            "(status != 'active' AND released_at IS NOT NULL)",
            name="ck_seat_allocations_status_released_at",
        ),
        CheckConstraint(
            "released_at IS NULL OR released_at >= allocated_at",
            name="ck_seat_allocations_released_after_allocated",
        ),
        Index("ix_seat_allocations_employee_id", "employee_id"),
        Index("ix_seat_allocations_seat_id", "seat_id"),
        Index("ix_seat_allocations_project_id", "project_id"),
        Index("ix_seat_allocations_status", "status"),
        Index(
            "ix_seat_allocations_employee_status",
            "employee_id",
            "status",
        ),
        Index(
            "ix_seat_allocations_allocated_at",
            "allocated_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<SeatAllocation id={self.id} employee_id={self.employee_id} "
            f"seat_id={self.seat_id} status={self.status.value}>"
        )
