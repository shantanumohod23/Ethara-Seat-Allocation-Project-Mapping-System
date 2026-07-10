"""Project ORM model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import ProjectStatus

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.seat_allocation import SeatAllocation


class Project(Base, TimestampMixin):
    """Client engagement or internal initiative mapped to seat allocations."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    project_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        comment="Short unique project identifier (e.g. PRJ-2024-001).",
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    manager_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Name of the project manager or delivery lead.",
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="project_status",
            native_enum=True,
            create_constraint=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        server_default=ProjectStatus.ACTIVE.value,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    assigned_employees: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="project",
        foreign_keys="Employee.project_id",
    )
    allocations: Mapped[list[SeatAllocation]] = relationship(
        "SeatAllocation",
        back_populates="project",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_projects_status", "status"),
        Index("ix_projects_name", "name"),
        Index("ix_projects_manager_name", "manager_name"),
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} code={self.project_code!r}>"
