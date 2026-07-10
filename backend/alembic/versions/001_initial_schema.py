"""Initial database schema for Ethara seat allocation system."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RESERVED_SEAT_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION prevent_reserved_seat_allocation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' AND EXISTS (
        SELECT 1
        FROM seats
        WHERE id = NEW.seat_id
          AND status IN ('reserved', 'maintenance', 'occupied')
    ) THEN
        RAISE EXCEPTION
            'Cannot create active allocation for unavailable seat (seat_id=%)',
            NEW.seat_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

RESERVED_SEAT_TRIGGER = """
CREATE TRIGGER trg_prevent_reserved_seat_allocation
BEFORE INSERT OR UPDATE OF seat_id, status ON seat_allocations
FOR EACH ROW
EXECUTE FUNCTION prevent_reserved_seat_allocation();
"""


def upgrade() -> None:
    project_status = ENUM(
        "active",
        "inactive",
        "completed",
        name="project_status",
        create_type=False,
    )
    seat_status = ENUM(
        "available",
        "occupied",
        "reserved",
        "maintenance",
        name="seat_status",
        create_type=False,
    )
    allocation_status = ENUM(
        "active",
        "released",
        "cancelled",
        name="allocation_status",
        create_type=False,
    )

    project_status.create(op.get_bind(), checkfirst=True)
    seat_status.create(op.get_bind(), checkfirst=True)
    allocation_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "employees",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("employee_code", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("job_title", sa.String(length=150), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_employees"),
        sa.UniqueConstraint("employee_code", name="uq_employees_employee_code"),
        sa.UniqueConstraint("email", name="uq_employees_email"),
    )
    op.create_index("ix_employees_department", "employees", ["department"])
    op.create_index("ix_employees_is_active", "employees", ["is_active"])
    op.create_index(
        "ix_employees_last_name_first_name",
        "employees",
        ["last_name", "first_name"],
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("project_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            project_status,
            server_default="active",
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
        sa.UniqueConstraint("project_code", name="uq_projects_project_code"),
    )
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_name", "projects", ["name"])

    op.create_table(
        "seats",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("seat_number", sa.String(length=20), nullable=False),
        sa.Column("floor", sa.String(length=20), nullable=False),
        sa.Column("zone", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            seat_status,
            server_default="available",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_seats"),
        sa.UniqueConstraint(
            "floor",
            "zone",
            "seat_number",
            name="uq_seats_floor_zone_seat_number",
        ),
    )
    op.create_index("ix_seats_floor_zone", "seats", ["floor", "zone"])
    op.create_index("ix_seats_status", "seats", ["status"])

    op.create_table(
        "seat_allocations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.BigInteger(), nullable=False),
        sa.Column("seat_id", sa.BigInteger(), nullable=False),
        sa.Column("project_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            allocation_status,
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "allocated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(status = 'active' AND released_at IS NULL) OR "
            "(status != 'active' AND released_at IS NOT NULL)",
            name="ck_seat_allocations_status_released_at",
        ),
        sa.CheckConstraint(
            "released_at IS NULL OR released_at >= allocated_at",
            name="ck_seat_allocations_released_after_allocated",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_seat_allocations_employee_id_employees",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_seat_allocations_project_id_projects",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seat_id"],
            ["seats.id"],
            name="fk_seat_allocations_seat_id_seats",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_seat_allocations"),
    )
    op.create_index(
        "ix_seat_allocations_allocated_at",
        "seat_allocations",
        ["allocated_at"],
    )
    op.create_index(
        "ix_seat_allocations_employee_id",
        "seat_allocations",
        ["employee_id"],
    )
    op.create_index(
        "ix_seat_allocations_employee_status",
        "seat_allocations",
        ["employee_id", "status"],
    )
    op.create_index(
        "ix_seat_allocations_project_id",
        "seat_allocations",
        ["project_id"],
    )
    op.create_index(
        "ix_seat_allocations_seat_id",
        "seat_allocations",
        ["seat_id"],
    )
    op.create_index(
        "ix_seat_allocations_status",
        "seat_allocations",
        ["status"],
    )
    op.create_index(
        "uq_seat_allocations_active_employee",
        "seat_allocations",
        ["employee_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "uq_seat_allocations_active_seat",
        "seat_allocations",
        ["seat_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.execute(RESERVED_SEAT_TRIGGER_FUNCTION)
    op.execute(RESERVED_SEAT_TRIGGER)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_prevent_reserved_seat_allocation "
        "ON seat_allocations;"
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_reserved_seat_allocation();")

    op.drop_index("uq_seat_allocations_active_seat", table_name="seat_allocations")
    op.drop_index("uq_seat_allocations_active_employee", table_name="seat_allocations")
    op.drop_index("ix_seat_allocations_status", table_name="seat_allocations")
    op.drop_index("ix_seat_allocations_seat_id", table_name="seat_allocations")
    op.drop_index("ix_seat_allocations_project_id", table_name="seat_allocations")
    op.drop_index(
        "ix_seat_allocations_employee_status",
        table_name="seat_allocations",
    )
    op.drop_index("ix_seat_allocations_employee_id", table_name="seat_allocations")
    op.drop_index("ix_seat_allocations_allocated_at", table_name="seat_allocations")
    op.drop_table("seat_allocations")

    op.drop_index("ix_seats_status", table_name="seats")
    op.drop_index("ix_seats_floor_zone", table_name="seats")
    op.drop_table("seats")

    op.drop_index("ix_projects_name", table_name="projects")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_table("projects")

    op.drop_index("ix_employees_last_name_first_name", table_name="employees")
    op.drop_index("ix_employees_is_active", table_name="employees")
    op.drop_index("ix_employees_department", table_name="employees")
    op.drop_table("employees")

    sa.Enum(name="allocation_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="seat_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="project_status").drop(op.get_bind(), checkfirst=True)
