"""Reject allocation into unavailable seat statuses.

Revision ID: 004_extend_allocation_seat_status_trigger
Revises: 003_add_occupied_seat_status
"""

from typing import Sequence, Union

from alembic import op

revision: str = "004_extend_allocation_seat_status_trigger"
down_revision: Union[str, None] = "003_add_occupied_seat_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
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
        """,
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_reserved_seat_allocation()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.status = 'active' AND EXISTS (
                SELECT 1
                FROM seats
                WHERE id = NEW.seat_id
                  AND status = 'reserved'
            ) THEN
                RAISE EXCEPTION
                    'Cannot create active allocation for reserved seat (seat_id=%)',
                    NEW.seat_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
    )
