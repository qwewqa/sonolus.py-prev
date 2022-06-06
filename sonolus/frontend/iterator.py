from __future__ import annotations

from typing import (
    Protocol,
    runtime_checkable,
    TypeVar,
    NamedTuple,
    Generic,
    Iterator,
    Type,
)

from sonolus.frontend.sls_func import sls_func
from sonolus.frontend.control_flow import Execute
from sonolus.frontend.generic_struct import GenericStruct
from sonolus.frontend.primitive import Bool, Num
from sonolus.frontend.tuple import TupleStruct
from sonolus.frontend.void import Void

T = TypeVar("T")


@runtime_checkable
class SlsIterable(Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        ...

    def __iter__(self) -> Iterator[T]:
        # Dummy to satisfy type checkers in for loops
        raise TypeError("Calling __iter__() is not supported on this SlsIterable.")


@runtime_checkable
class SlsEnumerable(SlsIterable[T], Protocol[T]):
    def _enumerate_(self) -> SlsIterator[TupleStruct[Num, T]]:
        ...


@runtime_checkable
class SlsIterator(SlsIterable[T], Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        return self

    def _has_item_(self) -> Bool:
        ...

    def _item_(self) -> T:
        ...

    def _advance_(self) -> Void:
        ...


@runtime_checkable
class SlsSequence(SlsEnumerable[T], Protocol[T]):
    def _len_(self) -> Num:
        ...

    def _contained_type_(self) -> Type[T]:
        ...

    def _max_size_(self) -> int:
        ...

    def __getitem__(self, item) -> T:
        ...

    def _iter_(self):
        return SequenceIterator.for_sequence(self)

    def _enumerate_(self):
        return IndexedSequenceIterator.for_sequence(self)

    @classmethod
    def _convert_(cls, sequence):
        match sequence:
            case cls():
                return sequence
            case [*values]:
                from sonolus.frontend.array import Array

                return Array.of(*values)
            case _:
                return NotImplemented


TSequence = TypeVar("TSequence")


class SequenceIteratorTypeVars(NamedTuple):
    TSequence: type


class SequenceIterator(
    SlsIterator[TSequence],
    GenericStruct,
    Generic[TSequence],
    type_vars=SequenceIteratorTypeVars,
):
    sequence: TSequence
    index: Num
    stop: Num

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SlsSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, +Num(), Len(seq))

    def _iter_(self):
        return self

    @sls_func
    def _has_item_(self):
        return self.index < self.stop

    @sls_func
    def _item_(self):
        return self.sequence[self.index]

    @sls_func
    def _advance_(self):
        self.index += 1


class IndexedSequenceIterator(
    SlsIterator[TSequence],
    GenericStruct,
    Generic[TSequence],
    type_vars=SequenceIteratorTypeVars,
):
    sequence: TSequence
    index: Num
    stop: Num

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SlsSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, +Num(), Len(seq))

    def _iter_(self):
        return self

    @sls_func
    def _has_item_(self):
        return self.index < self.stop

    @sls_func
    def _item_(self):
        value = self.sequence[self.index]
        return TupleStruct[Num, type(value)](self.index.copy(), value)

    @sls_func
    def _advance_(self):
        self.index += 1


TIterator = TypeVar("TIterator", bound=Iterator)


class IndexedIteratorWrapperTypeVars(NamedTuple):
    TIterator: type


class IndexedIteratorWrapper(
    SlsIterator,
    GenericStruct,
    Generic[TIterator],
    type_vars=IndexedIteratorWrapperTypeVars,
):
    iterator: TIterator
    index: Num

    @sls_func
    def _has_item_(self):
        return self.iterator._has_item_()

    def _iter_(self):
        return self

    @sls_func
    def _item_(self):
        index = self.index.copy()
        value = self.iterator._item_()
        return TupleStruct[Num, type(value)](index, value)

    @sls_func
    def _advance_(self):
        self.index += 1

    @classmethod
    def for_iterator(cls, i, /):
        return cls(i, +Num())


def Len(v: SlsSequence, /):
    return v._len_()


def Iter(seq: SlsIterable[T], /) -> SlsIterator[T]:
    if isinstance(seq, SlsIterable):
        return seq._iter_()
    raise TypeError(f"Value {seq} is not an Iterable.")


def Next(iterator: SlsIterator[T], /) -> T:
    if isinstance(iterator, SlsIterator):
        return Execute(result := iterator._item_(), iterator._advance_(), result)
    raise TypeError(f"Value {iterator} is not a SonoIterator.")


def Enumerate(seq: SlsIterable[T], /) -> SlsIterator[TupleStruct[Num, T]]:
    if hasattr(seq, "_enumerate_"):
        return seq._enumerate_()
    iterator = Iter(seq)
    return IndexedIteratorWrapper[type(iterator)].for_iterator(iterator)
