from __future__ import annotations

from typing import TypeVar, Generic, Callable, Any

from typing_extensions import Self

from sonolus.frontend.control_flow import Execute, If
from sonolus.frontend.iterator import SlsIterator, next_of, SlsSequence, SlsIterable
from sonolus.frontend.primitive import Num, Bool
from sonolus.frontend.sls_func import sls_func
from sonolus.frontend.statement import Statement, run_discarding
from sonolus.std.iterables import (
    select,
    where,
    count_of,
    any_of,
    all_of,
    max_of,
    min_of,
    reduce,
    is_empty,
    is_not_empty,
    Vector,
)
from sonolus.std.maybe import Some, Nothing, Maybe

__all__ = ("query", "seq_query")


T = TypeVar("T")
R = TypeVar("R")


class Query(Statement, Generic[T]):
    def __init__(self, iterator: SlsIterator[T], max_size: int | None):
        super().__init__()
        self._iterator = iterator
        self._max_size = max_size
        self._attributes_.is_static = True

    def select(self, f: Callable[[T], R], /) -> Self[R]:
        return type(self)(select(f, self._iterator), self._max_size)

    def map(self, f: Callable[[T], R], /) -> Self[R]:
        return self.select(f)

    def where(self, f: Callable[[T], Bool], /) -> Self[T]:
        return type(self)(where(f, self._iterator), self._max_size)

    def filter(self, f: Callable[[T], Bool], /) -> Self[T]:
        return self.where(f)

    def count(self, f: Callable[[T], Bool] | None = None, /) -> Num:
        if f is None:
            return count_of(self._iterator)
        else:
            return count_of(f, self._iterator)

    def any(self, f: Callable[[T], Bool], /) -> Bool:
        return any_of(f, self._iterator)

    def all(self, f: Callable[[T], Bool], /) -> Bool:
        return all_of(f, self._iterator)

    def max(self, *, key: Callable[[T], Any] = None, default: T = None) -> T:
        return max_of(self._iterator, key=key, default=default)

    def min(self, *, key: Callable[[T], Any] = None, default: T = None) -> T:
        return min_of(self._iterator, key=key, default=default)

    def reduce(self, f: Callable[[R, T], R], /, initializer: R = None):
        return reduce(f, self._iterator, initializer)

    def first(self, default: T = None) -> T:
        if default is None:
            default = self._contained_type()._default_()
        return self._first(default.copy())

    @sls_func
    def _first(self, _ret):
        for item in self._iterator:
            return item

    def last(self, default: T = None) -> T:
        if default is None:
            default = self._contained_type()._default_()
        return self._last(default.copy())

    @sls_func
    def _last(self, _ret):
        for item in self._iterator:
            _ret @= item

    def max_or_nothing(self, *, key: Callable[[T], Any] = None) -> Maybe[T]:
        return self._or_nothing(self.max(key=key))

    def min_or_nothing(self, *, key: Callable[[T], Any] = None) -> Maybe[T]:
        return self._or_nothing(self.min(key=key))

    def reduce_or_nothing(self, f: Callable[[R, T], R]) -> Maybe[R]:
        return self._or_nothing(self.reduce(f))

    def first_or_nothing(self) -> Maybe[T]:
        return self._or_nothing(self._first())

    def last_or_nothing(self) -> Maybe[T]:
        return self._or_nothing(self._last())

    def _or_nothing(self, value):
        return Execute(
            result := +Nothing[self._contained_type()](),
            If(self.is_not_empty(), result._assign_(Some(value))),
            result,
        )

    def iter(self):
        return self._iterator

    @sls_func
    def for_each(self, f: Callable[[T], Any], /):
        for item in self._iterator:
            f(item)

    def is_empty(self) -> Bool:
        return is_empty(self._iterator)

    def is_not_empty(self) -> Bool:
        return is_not_empty(self._iterator)

    def _contained_type(self):
        return type(run_discarding(lambda: next_of(self._iterator)))


class SeqQuery(Query[T]):
    # max_size must not be None

    def collect(self) -> SlsSequence[T]:
        return self._collect()

    @sls_func
    def _collect(self):
        results = Vector[self._contained_type(), self._max_size].empty()
        for item in self._iterator:
            # We know that we'll never exceed the max_size
            results.append_unsafe(item)
        return results


def query(v: SlsIterable[T], /) -> Query[T]:
    return Query(v._iter_(), max_size=None)


def seq_query(v: SlsSequence[T], /) -> SeqQuery[T]:
    return SeqQuery(v._iter_(), max_size=v._max_size_())
