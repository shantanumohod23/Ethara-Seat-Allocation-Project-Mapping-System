"""Extend schema: employment status, employee project mapping, seat bay."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "002_assessment_schema"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

employment_status_enum = ENUM(
    "active",
    "inactive",
    "onboarding",
    "resigned",
    name="employment_status",
    create_type=False,
)


def upgrade() -> None:
    employment_status_enum.create(op.get_bind(), checkfirst=True)

    # --- employees ---
    op.add_column(
        "employees",
        sa.Column(
            "joining_date",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
    )
    op.add_column(
        "employees",
        sa.Column(
            "employment_status",
            employment_status_enum,
            server_default="active",
            nullable=False,
        ),
    )
    op.add_column(
        "employees",
        sa.Column("project_id", sa.BigInteger(), nullable=True),
    )

    op.execute(
        """
        UPDATE employees
        SET employment_status = CASE
            WHEN is_active = true THEN 'active'::employment_status
            ELSE 'inactive'::employment_status
        END
        """
    )

    op.create_foreign_key(
        "fk_employees_project_id_projects",
        "employees",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_employees_employment_status", "employees", ["employment_status"])
    op.create_index("ix_employees_project_id", "employees", ["project_id"])

    op.drop_index("ix_employees_is_active", table_name="employees")
    op.drop_column("employees", "is_active")

    op.alter_column("employees", "joining_date", server_default=None)

    # --- projects ---
    op.add_column(
        "projects",
        sa.Column("manager_name", sa.String(length=200), nullable=True),
    )
    op.create_index("ix_projects_manager_name", "projects", ["manager_name"])

    # --- seats ---
    op.add_column(
        "seats",
        sa.Column(
            "bay",
            sa.String(length=50),
            server_default="default",
            nullable=False,
        ),
    )
    op.drop_constraint("uq_seats_floor_zone_seat_number", "seats", type_="unique")
    op.create_unique_constraint(
        "uq_seats_floor_zone_bay_seat_number",
        "seats",
        ["floor", "zone", "bay", "seat_number"],
    )
    op.drop_index("ix_seats_floor_zone", table_name="seats")
    op.create_index("ix_seats_floor_zone_bay", "seats", ["floor", "zone", "bay"])
    op.alter_column("seats", "bay", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_seats_floor_zone_bay", table_name="seats")
    op.create_index("ix_seats_floor_zone", "seats", ["floor", "zone"])
    op.drop_constraint("uq_seats_floor_zone_bay_seat_number", "seats", type_="unique")
    op.create_unique_constraint(
        "uq_seats_floor_zone_seat_number",
        "seats",
        ["floor", "zone", "seat_number"],
    )
    op.drop_column("seats", "bay")

    op.drop_index("ix_projects_manager_name", table_name="projects")
    op.drop_column("projects", "manager_name")

    op.add_column(
        "employees",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
    )
    op.execute(
        """
        UPDATE employees
        SET is_active = CASE
            WHEN employment_status = 'active'::employment_status THEN true
            ELSE false
        END
        """
    )
    op.drop_index("ix_employees_project_id", table_name="employees")
    op.drop_index("ix_employees_employment_status", table_name="employees")
    op.drop_constraint(
        "fk_employees_project_id_projects",
        "employees",
        type_="foreignkey",
    )
    op.drop_column("employees", "project_id")
    op.drop_column("employees", "employment_status")
    op.drop_column("employees", "joining_date")
    op.create_index("ix_employees_is_active", "employees", ["is_active"])
    op.alter_column("employees", "is_active", server_default=None)

    employment_status_enum.drop(op.get_bind(), checkfirst=True)
