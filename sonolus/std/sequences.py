from __future__ import annotations

from typing import overload, Callable, Iterable, Sequence

from sonolus.engine.functions.sls_func import New, convert_value
from sonolus.engine.statements.array import Array
from sonolus.engine.statements.control_flow import If
from sonolus.engine.statements.other_iterators import MappingIterator, FilteringIterator
from sonolus.engine.statements.generic_struct import generic_function
from sonolus.engine.statements.iterator import *
from sonolus.engine.statements.primitive import Number, Boolean
from sonolus.engine.statements.statement import Statement
from sonolus.engine.statements.struct import Struct
from sonolus.engine.statements.value import Value
from sonolus.std.number import NumMax, NumMin

__all__ = (
    "Range",
    "Len",
    "Iter",
    "Next",
    "Enumerate",
    "Map",
    "SeqMap",
    "Filter",
    "SeqFilter",
    "Count",
    "Any",
    "All",
    "Max",
    "Min",
    "Reduce",
    "Empty",
    "NotEmpty",
    "SizeLimitedArray",
)

T = TypeVar("T")
R = TypeVar("R")


@sls_func
def Map(
    f: Callable[[T], R], iterable: SlsIterable[T], /
) -> SlsIterable[R] | Iterable[R]:
    iterator = Iter(iterable)
    return MappingIterator[type(iterator), type(f(Next(iterator))), f].from_iterator(
        Iter(iterable)
    )


@sls_func
def SeqMap(
    f: Callable[[T], R], sequence: SlsSequence[T], /
) -> SlsSequence[R] | Sequence[R]:
    result = SizeLimitedArray[type(f(sequence[0])), sequence._max_size_()].alloc()
    result.size @= Len(sequence)
    for i, v in Enumerate(sequence):
        result[i] @= f(v)
    return result


@sls_func
def Filter(
    f: Callable[[T], Boolean], iterable: SlsIterable[T], /
) -> SlsIterable[T] | Iterable[T]:
    iterator = Iter(iterable)
    return FilteringIterator[type(iterator), f].from_iterator(iterator)


@sls_func
def SeqFilter(
    f: Callable[[T], Boolean], sequence: SlsSequence[T], /
) -> SlsSequence[T] | Sequence[T]:
    result = SizeLimitedArray[
        sequence._contained_type_(), sequence._max_size_()
    ].alloc()
    result.size @= 0
    for v in sequence:
        if f(v):
            result.append_unsafe(v)
    return result


@overload
def Count(iterator: SlsIterable, /) -> Number:
    pass


@overload
def Count(f: Callable[[T], Boolean], iterator: SlsIterable, /) -> Number:
    pass


@sls_func(ast=False)
def Count(*args):
    match len(args):
        case 1:
            if isinstance(args[0], SlsSequence):
                return Len(args[0])
            return _count_simple(*args)
        case 2:
            return _count_cond(*args)
        case _:
            raise TypeError(
                f"Count() takes 1 or 2 arguments but {len(args)} were given."
            )


@sls_func
def _count_simple(iterable: SlsIterable[T], /, _ret: Number = New) -> Number:
    count = Number.new(0)
    for _ in Iter(iterable):
        count += 1
    return count


@sls_func
def _count_cond(
    f: Callable[[T], Boolean], iterable: SlsIterable[T], /, _ret: Number = New
) -> Number:
    count = Number.new(0)
    for v in Iter(iterable):
        if f(v):
            count += 1
    return count


@sls_func
def Any(
    f: Callable[[T], Boolean], iterable: SlsIterable[T], /, _ret: Boolean = New
) -> Number:
    for v in Iter(iterable):
        if f(v):
            return True
    return False


@sls_func
def All(
    f: Callable[[T], Boolean], iterable: SlsIterable[T], /, _ret: Boolean = New
) -> Number:
    for v in Iter(iterable):
        if not f(v):
            return False
    return True


@overload
def Max(
    iterable: SlsIterable[T], /, *, key: Callable[[T], Any] = None, default: T = None
) -> T:
    pass


@overload
def Max(arg1: T, arg2: T, /, *args: T, key: Callable[[T], Any] = None) -> T:
    pass


@sls_func(ast=False)
def Max(*args, **kwargs):
    """
    If given a single iterable, returns a copy of the maximum value in the iterable.
    If given multiple values, returns a copy of the maximum of those values.
    """
    if len(args) == 0:
        raise TypeError("Max() takes at least 1 argument (0 given)")
    elif len(args) == 1:
        iterable = args[0]
        key = kwargs.pop("key", None)
        default = kwargs.pop("default", type(Iter(iterable)._item_()).new())
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
        and all(isinstance(arg, (Number, int, float)) for arg in args)
        and not kwargs
    ):
        return NumMax(*args)
    else:
        args = [convert_value(arg) for arg in args]
        key = kwargs.pop("key", None)
        if kwargs:
            raise TypeError(
                f"Max() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return Execute(
                max_value := args[0].copy(),
                *(If(v > max_value, max_value << v) for v in args[1:]),
                max_value,
            )
        else:
            return Execute(
                max_value := args[0].copy(),
                max_key := key(max_value),
                *(
                    Execute(
                        keyed := key(v),
                        If(keyed > max_key, Execute(max_value << v, max_key << keyed)),
                    )
                    for v in args[1:]
                ),
                max_value,
            )


@sls_func
def _max_iterable(iterable: SlsIterable[T], /, *, _ret):
    if Empty(iterable):
        return
    iterator = Iter(iterable)
    max_value = Next(iterator).copy()
    for v in iterator:
        if v > max_value:
            max_value @= v
    return max_value


@sls_func
def _max_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if Empty(iterable):
        return
    iterator = Iter(iterable)
    max_value = Next(iterator).copy()
    max_key = key(max_value).copy()
    for v in iterator:
        keyed = key(v)
        if keyed > max_key:
            max_value @= v
            max_key @= keyed
    return max_value


@overload
def Min(
    iterable: SlsIterable[T], /, *, key: Callable[[T], Any] = None, default: T = None
) -> T:
    pass


@overload
def Min(arg1: T, arg2: T, /, *args: T, key: Callable[[T], Any] = None) -> T:
    pass


@sls_func(ast=False)
def Min(*args, **kwargs):
    """
    If given a single iterable, returns a copy of the minimum value in the iterable.
    If given multiple values, returns a copy of the minimum of those values.
    """
    if len(args) == 0:
        raise TypeError("Min() takes at least 1 argument (0 given)")
    elif len(args) == 1:
        iterable = args[0]
        key = kwargs.pop("key", None)
        default = kwargs.pop("default", type(Iter(iterable)._item_()).new())
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
        and all(isinstance(arg, (Number, int, float)) for arg in args)
        and not kwargs
    ):
        return NumMin(*args)
    else:
        args = [convert_value(arg) for arg in args]
        key = kwargs.pop("key", None)
        if kwargs:
            raise TypeError(
                f"Min() got an unexpected keyword argument {list(kwargs.keys())[0]}"
            )
        if key is None:
            return Execute(
                min_value := args[0].copy(),
                *(If(v < min_value, min_value << v) for v in args[1:]),
                min_value,
            )
        else:
            return Execute(
                min_value := args[0].copy(),
                min_key := key(min_value),
                *(
                    Execute(
                        keyed := key(v),
                        If(keyed < min_key, Execute(min_value << v, min_key << keyed)),
                    )
                    for v in args[1:]
                ),
                min_value,
            )


@sls_func
def _min_iterable(iterable: SlsIterable[T], /, *, _ret):
    if Empty(iterable):
        return
    iterator = Iter(iterable)
    min_value = Next(iterator).copy()
    for v in iterator:
        if v < min_value:
            min_value @= v
    return min_value


@sls_func
def _min_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if Empty(iterable):
        return
    iterator = Iter(iterable)
    min_value = Next(iterator).copy()
    min_key = key(min_value).copy()
    for v in iterator:
        keyed = key(v)
        if keyed < min_key:
            min_value @= v
            min_key @= keyed
    return min_value


@sls_func(ast=False)
def Reduce(
    func: Callable[[R, T], R], iterable: SlsIterable[T], /, initializer: R = None
):
    """
    Returns a copy of the result of the reduction of the iterable using the given function.
    """
    if initializer is None:
        return _reduce_no_initializer(
            func, iterable, _ret=type(Iter(iterable)._item_()).new()
        )
    else:
        initializer = convert_value(initializer)
        return _reduce_with_initializer(func, iterable, _ret=initializer.copy())


@sls_func
def _reduce_no_initializer(
    f: Callable[[T, T], T], iterable: SlsIterable[T], /, *, _ret: T
):
    if Empty(iterable):
        return
    iterator = Iter(iterable)
    result = Next(iterator)
    for v in iterator:
        result @= f(result, v)
    return result


@sls_func
def _reduce_with_initializer(
    f: Callable[[R, T], R], iterable: SlsIterable[T], /, *, _ret: R
):
    # _ret acts as the initializer
    if Empty(iterable):
        return
    for v in Iter(iterable):
        _ret @= f(_ret, v)
    return


@sls_func
def Empty(iterable: SlsIterable[T]) -> Boolean:
    return not Iter(iterable)._has_item_()


@sls_func
def NotEmpty(iterable: SlsIterable[T]) -> Boolean:
    return Iter(iterable)._has_item_()


class Range(Struct):
    start: Number
    stop: Number
    step: Number

    @overload
    def __init__(self, stop: Number, /):
        pass

    @overload
    def __init__(self, start: Number, stop: Number, step: Number = None, /):
        pass

    def __init__(self, start, stop=None, step=1):
        if stop is None:
            stop = start
            start = 0
        super().__init__(start, stop, step)

    @sls_func
    def __len__(self, _ret: Number = New):
        if self.step > 0:
            return Max((self.stop - self.start - 1) // self.step + 1, 0)
        else:
            return Max((self.start - self.stop - 1) // -self.step + 1, 0)

    @sls_func
    def __contains__(self, item: Number, _ret: Boolean = New) -> Boolean:
        if self.step > 0:
            return (
                self.start <= item < self.stop and (item - self.start) % self.step == 0
            )
        else:
            return (
                self.start >= item > self.stop and (item - self.start) % self.step == 0
            )

    @sls_func
    def __getitem__(self, item: Number):
        return self.start + item * self.step

    def _iter_(self) -> SlsIterator[Number]:
        return SequenceIterator.for_sequence(self)

    def _enumerate_(self) -> SlsIterator[IndexedEntry[T]]:
        return IndexedSequenceIterator.for_sequence(self)

    @classmethod
    def _default_(cls) -> Range:
        return cls(0, 0, 1)

    def __iter__(self) -> Iterator[Number]:
        start = self.start.constant()
        stop = self.stop.constant()
        step = self.step.constant()
        if start is not None and stop is not None and step is not None:
            yield from range(start, stop, step)
        else:
            raise ValueError("Range is not statically iterable.")


class SizeLimitedArrayTypeVars(NamedTuple):
    T: type
    max_size: int


class SizeLimitedArray(GenericStruct, Generic[T], type_vars=SizeLimitedArrayTypeVars):
    size: Number
    # noinspection PyUnresolvedReferences
    values: Array[T, max_size]

    @generic_function
    @sls_func
    def append(self, value: T):
        if self.size >= self.type_vars.max_size:
            return
        self.append_unsafe(value)

    @generic_function
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

    @generic_function
    @sls_func
    def pop(self, _ret: T = New):
        if self.size == 0:
            return
        return self.pop_unsafe()

    @generic_function
    @sls_func
    def pop_unsafe(self, _ret: T = New):
        """
        Removes and returns the last element of the array without checking the size.
        May lead to undefined behavior if the current size is 0.
        """
        self.size -= 1
        return self.values[self.size]

    def _len_(self) -> Number:
        return self.size

    def _contained_type_(self) -> Type[T]:
        return self.type_vars.T

    def _max_size_(self) -> int:
        return self.type_vars.max_size

    def __getitem__(self, item) -> T:
        return self.values[item]

    def _iter_(self) -> SlsIterator[T]:
        return SequenceIterator.for_sequence(self)

    def _enumerate_(self) -> SlsIterator[IndexedEntry[T]]:
        return IndexedSequenceIterator.for_sequence(self)
