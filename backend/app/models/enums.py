"""Shared enumeration types for ORM models."""

import enum


class ProjectStatus(str, enum.Enum):
    """Lifecycle state of a project."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class SeatStatus(str, enum.Enum):
    """Operational state of a physical seat."""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class AllocationStatus(str, enum.Enum):
    """Lifecycle state of a seat allocation record."""

    ACTIVE = "active"
    RELEASED = "released"
    CANCELLED = "cancelled"


class EmploymentStatus(str, enum.Enum):
    """Workforce employment lifecycle state."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ONBOARDING = "onboarding"
    RESIGNED = "resigned"
