"""Seat ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import SeatStatus

if TYPE_CHECKING:
    from app.models.seat_allocation import SeatAllocation


class Seat(Base, TimestampMixin):
    """
    Physical or logical seat in the office.

    Location is normalized as floor + zone + bay + seat_number rather than a
    denormalized free-text address.
    """

    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    seat_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Seat label within a floor/zone/bay (e.g. A-042).",
    )
    floor: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Floor identifier (e.g. 3, L1, Ground).",
    )
    zone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Zone or wing within the floor (e.g. North, Zone-A).",
    )
    bay: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Bay or cluster within the zone (e.g. Bay-1, Cluster-B).",
    )
    status: Mapped[SeatStatus] = mapped_column(
        Enum(
            SeatStatus,
            name="seat_status",
            native_enum=True,
            create_constraint=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=SeatStatus.AVAILABLE,
        server_default=SeatStatus.AVAILABLE.value,
        comment="Reserved seats are blocked from active allocation via DB trigger.",
    )

    allocations: Mapped[list[SeatAllocation]] = relationship(
        "SeatAllocation",
        back_populates="seat",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "floor",
            "zone",
            "bay",
            "seat_number",
            name="uq_seats_floor_zone_bay_seat_number",
        ),
        Index("ix_seats_floor_zone_bay", "floor", "zone", "bay"),
        Index("ix_seats_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Seat id={self.id} floor={self.floor!r} "
            f"zone={self.zone!r} bay={self.bay!r} number={self.seat_number!r}>"
        )
