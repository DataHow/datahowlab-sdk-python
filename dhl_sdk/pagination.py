"""Pagination support for list operations

This module provides iterator-based pagination for efficient handling of large result sets.
"""

from collections.abc import Callable, Iterator
from typing import TypeVar

T = TypeVar("T")


class PageIterator(Iterator[T]):
    """Iterator for paginated API results

    Automatically fetches additional pages as needed, enabling memory-efficient
    iteration over large result sets.

    Examples:
        >>> # Iterate over all products (fetches pages as needed)
        >>> for product in PageIterator(
        ...     fetch_page=lambda offset, limit: client._list_products_page(offset, limit),
        ...     page_size=100
        ... ):
        ...     print(product.code)

    Args:
        fetch_page: Callable that fetches a page of results.
                   Takes (offset: int, limit: int) and returns list[T]
        page_size: Number of items per page (default: 100)
        initial_offset: Starting offset (default: 0)
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], list[T]],
        page_size: int = 100,
        initial_offset: int = 0,
    ):
        self.fetch_page = fetch_page
        self.page_size = page_size
        self.offset = initial_offset
        self.current_page: list[T] = []
        self.current_index = 0
        self.exhausted = False

    def __iter__(self) -> "PageIterator[T]":
        return self

    def __next__(self) -> T:
        # If we've consumed all items in current page, fetch next page
        if self.current_index >= len(self.current_page):
            if self.exhausted:
                raise StopIteration

            # Fetch next page
            self.current_page = self.fetch_page(self.offset, self.page_size)
            self.current_index = 0

            # Check if we got a partial page (indicates last page)
            if len(self.current_page) < self.page_size:
                self.exhausted = True

            # Check if page is empty (no more results)
            if not self.current_page:
                raise StopIteration

            # Update offset for next fetch
            self.offset += len(self.current_page)

        # Return current item and advance index
        item = self.current_page[self.current_index]
        self.current_index += 1
        return item


def iter_all(
    items: list[T], iterator: PageIterator[T] | None
) -> list[T] | PageIterator[T]:
    """Helper to return either a list or iterator based on iter_all parameter

    Args:
        items: Initial page of results
        iterator: Optional iterator for fetching additional pages

    Returns:
        List if iter_all=False (backward compatible), PageIterator if iter_all=True
    """
    return iterator if iterator is not None else items
