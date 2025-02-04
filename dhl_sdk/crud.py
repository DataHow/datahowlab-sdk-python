# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

"""API Results Handling Module

This module provides utility functions to handle and manage 
results obtained from the API. 

Classes:
    - CRUDClient: A utility class for handling CRUD requests for API entities
    - Result: A utility class for handling paginated API results
      and iterating through them.
"""

from collections import deque
from typing import Any, Generic, Optional, Protocol, TypeVar

from requests import Response


class Client(Protocol):
    def post(self, path: str, json_data: Any) -> Response:
        ...

    def put(self, path: str, data: Any, content_type: str) -> Response:
        ...

    def get(self, path: str, query_params: Optional[dict[str, str]] = None) -> Response:
        ...


class DataBaseClient(Protocol):
    """Protocol for Clients that interact with the DB, like DataHowLabClient"""

    _client: Client


T = TypeVar("T")


class Constructor(Protocol[T]):
    def __call__(self, **kwargs) -> T:
        ...


class CRUDClient(Generic[T]):
    """Utility class for handling CRUD requests for API entities"""

    def __init__(self, client: Client, base_url: str, constructor: Constructor[T]):
        self._client = client
        self._base_url = base_url
        self._constructor = constructor

    def get(self, entity_id: str) -> T:
        """Get an entity by its ID from the API"""
        response = self._client.get(f"{self._base_url}/{entity_id}")
        entity = response.json()
        entity = self._constructor(**entity, client=self._client)

        return entity

    def create(self, data: dict[str, Any]) -> T:
        """Create an entity in the API"""
        response = self._client.post(self._base_url, json_data=data)
        entity = response.json()
        entity = self._constructor(**entity, client=self._client)

        return entity

    def list(
        self, offset: int, limit: int, query_params: Optional[dict[str, str]] = None
    ) -> tuple[list[T], int]:
        query_params = query_params or {}
        query_params |= {
            "offset": str(offset),
            "limit": str(limit),
            "archived": "false",
            "sortBy[createdAt]": "desc",
        }

        response = self._client.get(self._base_url, query_params=query_params)
        total = int(response.headers.get("x-total-count"))
        entities = [
            self._constructor(**entity, client=self._client)
            for entity in response.json()
        ]

        return entities, total


class Result(Generic[T]):
    """Utility class for handling paginated API results"""

    def __init__(
        self,
        limit: int,
        query_params: Optional[dict[str, str]],
        requests: CRUDClient[T],
        offset: int = 0,
    ):
        self._data = deque()
        self.limit = limit
        self.offset = offset
        self._total = None
        self._query_params = query_params
        self._requests = requests

    def __iter__(self) -> "Result[T]":
        return self

    def __next__(self) -> T:
        if not self._data:
            self._fetch_next()
        return self._data.popleft()

    def __len__(self) -> int:
        if self._total is None:
            _, total = self._requests.list(
                0,
                0,
                self._query_params,
            )
            self._total = total
        return self._total

    def _fetch_next(self) -> None:
        entities, total = self._requests.list(
            self.offset,
            self.limit,
            self._query_params,
        )

        self.offset += self.limit
        self._data.extend(entities)
        self._total = total

        if len(self._data) == 0:
            raise StopIteration("No results available in the API")

    def is_empty(self) -> bool:
        """Check if the result is empty"""
        return self._total == 0
