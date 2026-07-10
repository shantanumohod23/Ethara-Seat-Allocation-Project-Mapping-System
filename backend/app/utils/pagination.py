"""Pagination and query utilities."""


def calculate_offset(page: int, page_size: int) -> int:
    """Convert 1-based page number to SQL offset."""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Return the total number of pages for a result set."""
    if total == 0:
        return 0
    return (total + page_size - 1) // page_size
