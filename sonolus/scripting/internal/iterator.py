from __future__ import annotations

from abc import abstractmethod
from typing import (
    Protocol,
    runtime_checkable,
    TypeVar,
    NamedTuple,
    Generic,
    Iterator,
    Type,
)

from sonolus.scripting.internal.control_flow import Execute
from sonolus.scripting.internal.generic_struct import GenericStruct
from sonolus.scripting.internal.primitive import Bool, Num
from sonolus.scripting.internal.sls_func import sls_func
from sonolus.scripting.internal.tuple import TupleStruct
from sonolus.scripting.internal.void import Void

T = TypeVar("T")


@runtime_checkable
class SlsIterable(Protocol[T]):
    @abstractmethod
    def _iter_(self) -> SlsIterator[T]:
        ...

    def __iter__(self) -> Iterator[T]:
        # Dummy to satisfy type checkers in for loops
        raise TypeError("Calling __iter__() is not supported on this SlsIterable.")


@runtime_checkable
class SlsEnumerable(SlsIterable[T], Protocol[T]):
    @abstractmethod
    def _enumerate_(self) -> SlsIterator[TupleStruct[Num, T]]:
        ...


@runtime_checkable
class SlsIterator(SlsIterable[T], Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        return self

    @sls_func
    def _for_each_(self, body, else_):
        while self._has_item_():
            item = self._item_()
            self._advance_()
            body(item)
        else:
            else_()

    @abstractmethod
    def _has_item_(self) -> Bool:
        ...

    @abstractmethod
    def _item_(self) -> T:
        """
        Returns the current item.
        _has_item_() must be called before calling this function.
        """
        ...

    @abstractmethod
    def _advance_(self) -> Void:
        ...


@runtime_checkable
class SlsSequence(SlsEnumerable[T], Protocol[T]):
    @abstractmethod
    def _len_(self) -> Num:
        ...

    @abstractmethod
    def _contained_type_(self) -> Type[T]:
        ...

    @abstractmethod
    def _max_size_(self) -> int:
        ...

    @abstractmethod
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
                from sonolus.scripting.internal.array import Array

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
        return cls[type(seq)](seq, +Num(), len_of(seq))

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
        return cls[type(seq)](seq, +Num(), len_of(seq))

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


def len_of(v: SlsSequence, /):
    return v._len_()


def iter_of(seq: SlsIterable[T], /) -> SlsIterator[T]:
    if isinstance(seq, SlsIterable):
        return seq._iter_()
    raise TypeError(f"Value {seq} is not an Iterable.")


def next_of(iterator: SlsIterator[T], /) -> T:
    if isinstance(iterator, SlsIterator):
        return Execute(result := iterator._item_(), iterator._advance_(), result)
    raise TypeError(f"Value {iterator} is not a SonoIterator.")


def indexed_of(seq: SlsIterable[T], /) -> SlsIterator[TupleStruct[Num, T]]:
    if hasattr(seq, "_enumerate_"):
        return seq._enumerate_()
    iterator = iter_of(seq)
    return IndexedIteratorWrapper[type(iterator)].for_iterator(iterator)
