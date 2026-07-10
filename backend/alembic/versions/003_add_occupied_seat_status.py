"""Add occupied seat status.

Revision ID: 003_add_occupied_seat_status
Revises: 002_assessment_schema
"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_add_occupied_seat_status"
down_revision: Union[str, None] = "002_assessment_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("ALTER TYPE seat_status ADD VALUE IF NOT EXISTS 'occupied'")


def downgrade() -> None:
    # PostgreSQL enum values cannot be dropped safely without rebuilding the type.
    pass
