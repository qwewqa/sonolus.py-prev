from __future__ import annotations

from typing import (
    Protocol,
    runtime_checkable,
    TypeVar,
    NamedTuple,
    Generic,
    Iterator,
    Tuple,
    Type,
)

from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.control_flow import Execute
from sonolus.engine.statements.generic_struct import GenericStruct
from sonolus.engine.statements.primitive import Boolean, Number
from sonolus.engine.statements.tuple import SlsTuple
from sonolus.engine.statements.void import Void

T = TypeVar("T")


@runtime_checkable
class SlsIterable(Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        pass

    def __iter__(self) -> Iterator[T]:
        # Dummy to satisfy type checkers in for loops
        pass


@runtime_checkable
class SlsEnumerable(Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        pass

    def _enumerate_(self) -> SlsIterator[SlsTuple[Number, T]]:
        pass

    def __iter__(self) -> Iterator[T]:
        pass


@runtime_checkable
class SlsIterator(Protocol[T]):
    def _iter_(self) -> SlsIterator[T]:
        pass

    def _has_item_(self) -> Boolean:
        pass

    def _item_(self) -> T:
        pass

    def _advance_(self) -> Void:
        pass

    def __iter__(self) -> Iterator[T]:
        pass


@runtime_checkable
class SlsSequence(Protocol[T]):
    def _len_(self) -> Number:
        pass

    def _contained_type_(self) -> Type[T]:
        pass

    def _max_size_(self) -> int:
        pass

    def __getitem__(self, item) -> T:
        pass

    def _iter_(self) -> SlsIterator[T]:
        pass

    def _enumerate_(self) -> SlsIterator[SlsTuple[Number, T]]:
        pass

    @classmethod
    def _convert_(cls, sequence):
        match sequence:
            case cls():
                return sequence
            case [*values]:
                from sonolus.engine.statements.array import Array

                return Array.of(*values)
            case _:
                raise TypeError(f"{sequence} is not a {cls.__name__}.")


TSequence = TypeVar("TSequence")


class SequenceIteratorTypeVars(NamedTuple):
    TSequence: type


class SequenceIterator(
    GenericStruct, Generic[TSequence], type_vars=SequenceIteratorTypeVars
):
    sequence: TSequence
    index: Number
    stop: Number

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SlsSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, Number.new(), Len(seq))

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

    def __iter__(self):
        raise TypeError("Cannot call __iter__ on an SlsIterable.")


class IndexedSequenceIterator(
    GenericStruct, Generic[TSequence], type_vars=SequenceIteratorTypeVars
):
    sequence: TSequence
    index: Number
    stop: Number

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SlsSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, Number.new(), Len(seq))

    def _iter_(self):
        return self

    @sls_func
    def _has_item_(self):
        return self.index < self.stop

    @sls_func
    def _item_(self):
        value = self.sequence[self.index]
        return SlsTuple[Number, type(value)](self.index.copy(), value)

    @sls_func
    def _advance_(self):
        self.index += 1

    def __iter__(self):
        raise TypeError("Cannot call __iter__ on an SlsIterable.")


TIterator = TypeVar("TIterator", bound=Iterator)


class IndexedIteratorWrapperTypeVars(NamedTuple):
    TIterator: type


class IndexedIteratorWrapper(
    GenericStruct, Generic[TIterator], type_vars=IndexedIteratorWrapperTypeVars
):
    iterator: TIterator
    index: Number

    @sls_func
    def _has_item_(self):
        return self.iterator._has_item_()

    def _iter_(self):
        return self

    @sls_func
    def _item_(self):
        index = self.index.copy()
        value = self.iterator._item_()
        return SlsTuple[Number, type(value)](index, value)

    @sls_func
    def _advance_(self):
        self.index += 1

    def __iter__(self):
        raise TypeError("Cannot call __iter__ on an SlsIterable.")

    @classmethod
    def for_iterator(cls, i, /):
        return cls(i, Number.new())


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


def Enumerate(seq: SlsIterable[T], /) -> SlsIterator[SlsTuple[Number, T]]:
    if hasattr(seq, "_enumerate_"):
        return seq._enumerate_()
    iterator = Iter(seq)
    return IndexedIteratorWrapper[type(iterator)].for_iterator(iterator)
