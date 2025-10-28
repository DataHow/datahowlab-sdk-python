from collections.abc import Iterator
from typing import Protocol, TypeVar, ParamSpec, cast

T = TypeVar("T")
P = ParamSpec("P")


class PaginatedGetter(Protocol[P, T]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[T]: ...


def paginate(getter_func: PaginatedGetter[P, T], *args: P.args, **kwargs: P.kwargs) -> Iterator[T]:
    """Internal method to handle pagination"""
    skip = 0
    limit = 10

    while True:
        items = cast(
            list[T],
            getter_func(
                *args,
                **kwargs,
                # Python does not seem to allow extra kwargs in Protocol with ParamSpec
                skip=skip,  # pyright: ignore[reportCallIssue]
                limit=limit,  # pyright: ignore[reportCallIssue]
            ),
        )

        if not items:
            break

        for item in items:
            yield item

        if len(items) < limit:
            break

        skip += limit
