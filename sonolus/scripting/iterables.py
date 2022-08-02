from __future__ import annotations

from typing import overload, Callable, Any

from typing_extensions import Self

from sonolus.scripting.internal.sls_func import convert_literal
from sonolus.scripting.internal.array import Array
from sonolus.scripting.internal.control_flow import If
from sonolus.scripting.internal.generic_struct import generic_method
from sonolus.scripting.internal.iterator import *
from sonolus.scripting.internal.primitive import Num, Bool
from sonolus.scripting.internal.statement import run_discarding
from sonolus.scripting.internal.struct import Struct
from sonolus.scripting import Maybe, Nothing, Some
from sonolus.scripting.number import num_max, num_min
from sonolus.scripting.values import alloc, new

__all__ = (
    "Range",
    "len_of",
    "iter_of",
    "next_of",
    "indexed_of",
    "select",
    "select_seq",
    "where",
    "where_seq",
    "count_of",
    "any_of",
    "all_of",
    "max_of",
    "min_of",
    "reduce",
    "is_empty",
    "is_not_empty",
    "Vector",
    "sequence_iterator",
    "indexed_sequence_iterator",
)

T = TypeVar("T")
R = TypeVar("R")


# The map/filter functions are already Python builtins,
# so instead we use select/where.
# Similarly, _of suffixes are added to other functions
# to avoid name conflicts with vanilla Python.


@sls_func
def select(f: Callable[[T], R], iterable: SlsIterable[T], /) -> SlsIterator[R]:
    iterator = iter_of(iterable)
    return MappingIterator[
        type(iterator), type(run_discarding(lambda: f(next_of(iterator)))), f
    ].from_iterator(iter_of(iterable))


@sls_func
def select_seq(f: Callable[[T], R], sequence: SlsSequence[T], /) -> SlsSequence[R]:
    result = Vector[
        type(run_discarding(lambda: f(sequence[0]))), sequence._max_size_()
    ].alloc()
    result.size @= len_of(sequence)
    for i, v in indexed_of(sequence):
        result[i] @= f(v)
    return result


@sls_func
def where(f: Callable[[T], Bool], iterable: SlsIterable[T], /) -> SlsIterator[T]:
    iterator = iter_of(iterable)
    return FilteringIterator[type(iterator), f].from_iterator(iterator)


@sls_func
def where_seq(f: Callable[[T], Bool], sequence: SlsSequence[T], /) -> SlsSequence[T]:
    result = alloc(Vector[sequence._contained_type_(), sequence._max_size_()])
    result.size @= 0
    for v in sequence:
        if f(v):
            result.append_unsafe(v)
    return result


@overload
def count_of(iterator: SlsIterable, /) -> Num:
    pass


@overload
def count_of(f: Callable[[T], Bool], iterator: SlsIterable, /) -> Num:
    pass


@sls_func(ast=False)
def count_of(*args):
    match len(args):
        case 1:
            if isinstance(args[0], SlsSequence):
                return len_of(args[0])
            return _count_simple(*args)
        case 2:
            return _count_cond(*args)
        case _:
            raise TypeError(
                f"Count() takes 1 or 2 arguments but {len(args)} were given."
            )


@sls_func
def _count_simple(iterable: SlsIterable[T], /, _ret=new()) -> Num:
    count = +Num(0)
    for _ in iter_of(iterable):
        count += 1
    return count


@sls_func
def _count_cond(f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret=new()) -> Num:
    count = +Num(0)
    for v in iter_of(iterable):
        if f(v):
            count += 1
    return count


@sls_func
def any_of(f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret=new()) -> Bool:
    for v in iter_of(iterable):
        if f(v):
            return True
    return False


@sls_func
def all_of(f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret=new()) -> Bool:
    for v in iter_of(iterable):
        if not f(v):
            return False
    return True


@overload
def max_of(
    iterable: SlsIterable[T], /, *, key: Callable[[T], Any] = None, default: T = None
) -> T:
    pass


@overload
def max_of(arg1: T, arg2: T, /, *args: T, key: Callable[[T], Any] = None) -> T:
    pass


@sls_func(ast=False)
def max_of(*args, **kwargs):
    """
    If given a single iterable, returns a copy of the maximum value in the iterable.
    If given multiple values, returns a copy of the maximum of those values.
    """
    if len(args) == 0:
        raise TypeError("Max() takes at least 1 argument (0 given)")
    elif len(args) == 1:
        iterable = args[0]
        key = kwargs.pop("key", None)
        default = (
            (
                kwargs.pop(
                    "default",
                    None,
                )
                or type(run_discarding(lambda: iter_of(iterable)._item_()))
            )
            ._default_()
            .copy()
        )
        if kwargs:
            raise TypeError(
                f"Max() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return _max_iterable(iterable, _ret=default)
        else:
            return _max_iterable_key(iterable, key=key, _ret=default)
    elif (
        len(args) == 2
        and all(isinstance(arg, (Num, int, float)) for arg in args)
        and not kwargs
    ):
        return num_max(*args)
    else:
        args = [convert_literal(arg) for arg in args]
        key = kwargs.pop("key", None)
        if kwargs:
            raise TypeError(
                f"Max() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return Execute(
                max_value := args[0].copy(),
                *(If(v > max_value, max_value @ v) for v in args[1:]),
                max_value,
            )
        else:
            return Execute(
                max_value := args[0].copy(),
                max_key := key(max_value),
                *(
                    Execute(
                        keyed := key(v),
                        If(keyed > max_key, Execute(max_value @ v, max_key @ keyed)),
                    )
                    for v in args[1:]
                ),
                max_value,
            )


@sls_func
def _max_iterable(iterable: SlsIterable[T], /, *, _ret):
    if is_empty(iterable):
        return
    iterator = iter_of(iterable)
    max_value = next_of(iterator).copy()
    for v in iterator:
        if v > max_value:
            max_value @= v
    return max_value


@sls_func
def _max_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if is_empty(iterable):
        return
    iterator = iter_of(iterable)
    max_value = next_of(iterator).copy()
    max_key = key(max_value).copy()
    for v in iterator:
        keyed = key(v)
        if keyed > max_key:
            max_value @= v
            max_key @= keyed
    return max_value


@overload
def min_of(
    iterable: SlsIterable[T], /, *, key: Callable[[T], Any] = None, default: T = None
) -> T:
    pass


@overload
def min_of(arg1: T, arg2: T, /, *args: T, key: Callable[[T], Any] = None) -> T:
    pass


@sls_func(ast=False)
def min_of(*args, **kwargs):
    """
    If given a single iterable, returns a copy of the minimum value in the iterable.
    If given multiple values, returns a copy of the minimum of those values.
    """
    if len(args) == 0:
        raise TypeError("Min() takes at least 1 argument (0 given)")
    elif len(args) == 1:
        iterable = args[0]
        key = kwargs.pop("key", None)
        default = (
            (
                kwargs.pop(
                    "default",
                    None,
                )
                or type(run_discarding(lambda: iter_of(iterable)._item_()))
            )
            ._default_()
            .copy()
        )
        if kwargs:
            raise TypeError(
                f"Min() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return _min_iterable(iterable, _ret=default)
        else:
            return _min_iterable_key(iterable, key=key, _ret=default)
    elif (
        len(args) == 2
        and all(isinstance(arg, (Num, int, float)) for arg in args)
        and not kwargs
    ):
        return num_min(*args)
    else:
        args = [convert_literal(arg) for arg in args]
        key = kwargs.pop("key", None)
        if kwargs:
            raise TypeError(
                f"Min() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return Execute(
                min_value := args[0].copy(),
                *(If(v < min_value, min_value @ v) for v in args[1:]),
                min_value,
            )
        else:
            return Execute(
                min_value := args[0].copy(),
                min_key := key(min_value),
                *(
                    Execute(
                        keyed := key(v),
                        If(keyed < min_key, Execute(min_value @ v, min_key @ keyed)),
                    )
                    for v in args[1:]
                ),
                min_value,
            )


@sls_func
def _min_iterable(iterable: SlsIterable[T], /, *, _ret):
    if is_empty(iterable):
        return
    iterator = iter_of(iterable)
    min_value = next_of(iterator).copy()
    for v in iterator:
        if v < min_value:
            min_value @= v
    return min_value


@sls_func
def _min_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if is_empty(iterable):
        return
    iterator = iter_of(iterable)
    min_value = next_of(iterator).copy()
    min_key = key(min_value).copy()
    for v in iterator:
        keyed = key(v)
        if keyed < min_key:
            min_value @= v
            min_key @= keyed
    return min_value


@sls_func(ast=False)
def reduce(
    func: Callable[[R, T], R], iterable: SlsIterable[T], /, initializer: R = None
) -> R:
    """
    Returns a copy of the result of the reduction of the iterable using the given function.
    """
    if initializer is None:
        return _reduce_no_initializer(
            func,
            iterable,
            _ret=type(run_discarding(lambda: iter_of(iterable)._item_()))
            ._default_()
            .copy(),
        )
    else:
        initializer = convert_literal(initializer)
        return _reduce_with_initializer(func, iterable, initializer=initializer.copy())


@sls_func
def _reduce_no_initializer(
    f: Callable[[T, T], T], iterable: SlsIterable[T], /, *, _ret: T
):
    if is_empty(iterable):
        return
    iterator = iter_of(iterable)
    result = next_of(iterator)
    for v in iterator:
        result @= f(result, v)
    return result


@sls_func(return_parameter="initializer")
def _reduce_with_initializer(
    f: Callable[[R, T], R], iterable: SlsIterable[T], /, *, initializer: R
):
    if is_empty(iterable):
        return
    for v in iter_of(iterable):
        initializer @= f(initializer, v)
    return


@sls_func
def is_empty(iterable: SlsIterable[T]) -> Bool:
    return not iter_of(iterable)._has_item_()


@sls_func
def is_not_empty(iterable: SlsIterable[T]) -> Bool:
    return iter_of(iterable)._has_item_()


class Range(Struct, SlsSequence[Num]):
    start: Num
    stop: Num
    step: Num

    @overload
    def __init__(self, stop: Num, /):
        pass

    @overload
    def __init__(self, start: Num, stop: Num, step: Num = None, /):
        pass

    def __init__(self, start=0, stop=None, step=1):
        # Usually __init__ shouldn't be overwritten, but this enables
        # behavior to mimic the builtin range() function.
        if stop is None:
            stop = start
            start = 0
        super().__init__(start, stop, step)

    @sls_func
    def _len_(self, _ret=new()) -> Num:
        if self.step > 0:
            return max_of((self.stop - self.start - 1) // self.step + 1, 0)
        else:
            return max_of((self.start - self.stop - 1) // -self.step + 1, 0)

    def _contained_type_(self):
        return Num

    def _max_size_(self) -> int:
        raise NotImplementedError("Range does not have a max size.")

    @sls_func
    def __contains__(self, item: Num, _ret=new()) -> Bool:
        if self.step > 0:
            return (
                self.start <= item < self.stop and (item - self.start) % self.step == 0
            )
        else:
            return (
                self.start >= item > self.stop and (item - self.start) % self.step == 0
            )

    @sls_func
    def __getitem__(self, item: Num):
        return self.start + item * self.step

    def __iter__(self) -> Iterator[Num]:
        start = self.start.constant()
        stop = self.stop.constant()
        step = self.step.constant()
        if start is not None and stop is not None and step is not None:
            yield from range(start, stop, step)
        else:
            raise ValueError("Range is not statically iterable.")


class VectorTypeVars(NamedTuple):
    T: type
    max_size: int


class Vector(SlsSequence[T], GenericStruct, Generic[T], type_vars=VectorTypeVars):
    size: Num
    # noinspection PyUnresolvedReferences
    values: Array[T, max_size]

    @classmethod
    @sls_func
    def empty(cls: Self) -> Self:
        """
        Returns an empty mutable vector.
        """
        result = alloc(cls)
        result.size @= 0
        return result

    @generic_method
    @sls_func
    def append(self, value: T, _ret=new()) -> Bool:
        if self.size >= self.type_vars.max_size:
            return False
        self.append_unsafe(value)
        return True

    @generic_method
    @sls_func
    def append_unsafe(self, value: T):
        """
        Appends a value to the array without checking the size.
        Size is still incremented.
        May lead to undefined behavior if the current size is greater than
        or equal to the max size.
        """
        self.values[self.size] @= value
        self.size += 1

    @generic_method
    @sls_func
    def pop(self, _ret=new()) -> Maybe[T]:
        if self.size == 0:
            return Nothing()
        return Some(self.pop_unsafe())

    @generic_method
    @sls_func
    def pop_unsafe(self, _ret=new()) -> T:
        """
        Removes and returns the last element of the array without checking the size.
        May lead to undefined behavior if the current size is 0.
        """
        self.size -= 1
        return self.values[self.size]

    def _len_(self) -> Num:
        return self.size

    def _contained_type_(self) -> Type[T]:
        return self.type_vars.T

    def _max_size_(self) -> int:
        return self.type_vars.max_size

    def __getitem__(self, item) -> T:
        return self.values[item]

    # This could use a custom _assign_() that accounts for length,
    # but it's not clear at which point the overhead of a loop
    # is outweighed by a reduced number of assignments.


TOut = TypeVar("TOut")
TSrc = TypeVar("TSrc")


class MappingIteratorTypeVars(NamedTuple):
    TSrc: type
    TOut: type
    map: Callable[[...], TOut]


class MappingIterator(
    SlsIterator[TOut],
    GenericStruct,
    Generic[TSrc, TOut],
    type_vars=MappingIteratorTypeVars,
):
    source: TSrc

    @classmethod
    def from_iterator(cls, iterator):
        return cls(iterator)

    @sls_func
    def _has_item_(self) -> Bool:
        return self.source._has_item_()

    @sls_func
    def _item_(self):
        return self.type_vars.map(self.source._item_())

    @sls_func
    def _advance_(self) -> TOut:
        return self.source._advance_()


class FilteringIteratorTypeVars(NamedTuple):
    TSrc: type
    filter: Callable[[...], Bool]


class FilteringIterator(
    SlsIterator[TSrc], GenericStruct, Generic[TSrc], type_vars=FilteringIteratorTypeVars
):
    source: TSrc

    @classmethod
    @sls_func
    def from_iterator(cls, iterator):
        result = cls(iterator)
        result._advance_until_valid()
        return result

    @sls_func
    def _has_item_(self) -> Bool:
        return self.source._has_item_()

    @sls_func
    def _item_(self):
        return self.source._item_()

    @sls_func
    def _advance_(self):
        self.source._advance_()
        self._advance_until_valid()

    @sls_func
    def _advance_until_valid(self):
        while self.source._has_item_() and not self.type_vars.filter(
            self.source._item_()
        ):
            self.source._advance_()


sequence_iterator = SequenceIterator.for_sequence
indexed_sequence_iterator = IndexedSequenceIterator.for_sequence
