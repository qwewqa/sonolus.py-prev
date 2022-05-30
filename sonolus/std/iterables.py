from __future__ import annotations

from typing import overload, Callable

from sonolus.frontend.sls_func import convert_literal
from sonolus.frontend.array import Array
from sonolus.frontend.control_flow import If
from sonolus.frontend.generic_struct import generic_method
from sonolus.frontend.iterator import *
from sonolus.frontend.primitive import Num, Bool
from sonolus.frontend.struct import Struct
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
    "IsEmpty",
    "IsNotEmpty",
    "SizeLimitedArray",
)

from sonolus.std.types import alloc, new

T = TypeVar("T")
R = TypeVar("R")


@sls_func
def Map(f: Callable[[T], R], iterable: SlsIterable[T], /) -> SlsIterable[R]:
    iterator = Iter(iterable)
    return MappingIterator[type(iterator), type(f(Next(iterator))), f].from_iterator(
        Iter(iterable)
    )


@sls_func
def SeqMap(f: Callable[[T], R], sequence: SlsSequence[T], /) -> SlsSequence[R]:
    result = SizeLimitedArray[type(f(sequence[0])), sequence._max_size_()].alloc()
    result.size @= Len(sequence)
    for i, v in Enumerate(sequence):
        result[i] @= f(v)
    return result


@sls_func
def Filter(f: Callable[[T], Bool], iterable: SlsIterable[T], /) -> SlsIterable[T]:
    iterator = Iter(iterable)
    return FilteringIterator[type(iterator), f].from_iterator(iterator)


@sls_func
def SeqFilter(f: Callable[[T], Bool], sequence: SlsSequence[T], /) -> SlsSequence[T]:
    result = alloc(SizeLimitedArray[sequence._contained_type_(), sequence._max_size_()])
    result.size @= 0
    for v in sequence:
        if f(v):
            result.append_unsafe(v)
    return result


@overload
def Count(iterator: SlsIterable, /) -> Num:
    pass


@overload
def Count(f: Callable[[T], Bool], iterator: SlsIterable, /) -> Num:
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
def _count_simple(iterable: SlsIterable[T], /, _ret: Num = new()) -> Num:
    count = Num.new(0)
    for _ in Iter(iterable):
        count += 1
    return count


@sls_func
def _count_cond(
    f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret: Num = new()
) -> Num:
    count = Num.new(0)
    for v in Iter(iterable):
        if f(v):
            count += 1
    return count


@sls_func
def Any(
    f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret: Bool = new()
) -> Bool:
    for v in Iter(iterable):
        if f(v):
            return True
    return False


@sls_func
def All(
    f: Callable[[T], Bool], iterable: SlsIterable[T], /, _ret: Bool = new()
) -> Bool:
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
        and all(isinstance(arg, (Num, int, float)) for arg in args)
        and not kwargs
    ):
        return NumMax(*args)
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
    if IsEmpty(iterable):
        return
    iterator = Iter(iterable)
    max_value = Next(iterator).copy()
    for v in iterator:
        if v > max_value:
            max_value @= v
    return max_value


@sls_func
def _max_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if IsEmpty(iterable):
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
        and all(isinstance(arg, (Num, int, float)) for arg in args)
        and not kwargs
    ):
        return NumMin(*args)
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
    if IsEmpty(iterable):
        return
    iterator = Iter(iterable)
    min_value = Next(iterator).copy()
    for v in iterator:
        if v < min_value:
            min_value @= v
    return min_value


@sls_func
def _min_iterable_key(iterable: SlsIterable[T], /, *, key: Callable, _ret):
    if IsEmpty(iterable):
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
        initializer = convert_literal(initializer)
        return _reduce_with_initializer(func, iterable, _ret=initializer.copy())


@sls_func
def _reduce_no_initializer(
    f: Callable[[T, T], T], iterable: SlsIterable[T], /, *, _ret: T
):
    if IsEmpty(iterable):
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
    if IsEmpty(iterable):
        return
    for v in Iter(iterable):
        _ret @= f(_ret, v)
    return


@sls_func
def IsEmpty(iterable: SlsIterable[T]) -> Bool:
    return not Iter(iterable)._has_item_()


@sls_func
def IsNotEmpty(iterable: SlsIterable[T]) -> Bool:
    return Iter(iterable)._has_item_()


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
    def __len__(self, _ret: Num = new()):
        if self.step > 0:
            return Max((self.stop - self.start - 1) // self.step + 1, 0)
        else:
            return Max((self.start - self.stop - 1) // -self.step + 1, 0)

    @sls_func
    def __contains__(self, item: Num, _ret: Bool = new()) -> Bool:
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


class SizeLimitedArrayTypeVars(NamedTuple):
    T: type
    max_size: int


class SizeLimitedArray(
    SlsSequence[T], GenericStruct, Generic[T], type_vars=SizeLimitedArrayTypeVars
):
    size: Num
    # noinspection PyUnresolvedReferences
    values: Array[T, max_size]

    @generic_method
    @sls_func
    def append(self, value: T):
        if self.size >= self.type_vars.max_size:
            return
        self.append_unsafe(value)

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
    def pop(self, _ret: T = new()):
        if self.size == 0:
            return
        return self.pop_unsafe()

    @generic_method
    @sls_func
    def pop_unsafe(self, _ret: T = new()):
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
