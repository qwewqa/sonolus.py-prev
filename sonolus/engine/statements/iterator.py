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

from sonolus.engine.functions.sono_function import sono_function
from sonolus.engine.statements.control_flow import Execute
from sonolus.engine.statements.generic_struct import GenericStruct
from sonolus.engine.statements.primitive import Boolean, Number
from sonolus.engine.statements.void import Void

T = TypeVar("T")


@runtime_checkable
class SonoIterable(Protocol[T]):
    def _iter_(self) -> SonoIterator[T]:
        pass


@runtime_checkable
class SonoEnumerable(Protocol[T]):
    def _enumerate_(self) -> SonoIterator[IndexedEntry[T]]:
        pass


@runtime_checkable
class SonoIterator(Protocol[T]):
    def _iter_(self) -> SonoIterator[T]:
        pass

    def _has_item_(self) -> Boolean:
        pass

    def _item_(self) -> T:
        pass

    def _advance_(self) -> Void:
        pass


@runtime_checkable
class SonoSequence(Protocol[T]):
    def _len_(self) -> Number:
        pass

    def _contained_type_(self) -> Type[T]:
        pass

    def _max_size_(self) -> int:
        pass

    def __getitem__(self, item) -> T:
        pass

    def _iter_(self) -> SonoIterator[T]:
        pass

    def _enumerate_(self) -> SonoIterator[IndexedEntry[T]]:
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


class IndexedEntry(
    GenericStruct, Generic[TSequence], type_vars=SequenceIteratorTypeVars
):
    index: Number
    value: TSequence

    def __iter__(self):
        yield self.index
        yield self.value

    @sono_function(ast=False)
    def __getitem__(self, item: Number):
        const_index = item.constant()
        if const_index is None:
            raise ValueError(
                "IndexdEntry may only be subscripted with a compile time constant."
            )
        return [self.index, self.value][const_index]


class SequenceIterator(
    GenericStruct, Generic[TSequence], type_vars=SequenceIteratorTypeVars
):
    sequence: TSequence
    index: Number
    stop: Number

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SonoSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, Number.new(), Len(seq))

    def _iter_(self):
        return self

    @sono_function
    def _has_item_(self):
        return self.index < self.stop

    @sono_function
    def _item_(self):
        return self.sequence[self.index]

    @sono_function
    def _advance_(self):
        self.index += 1


class IndexedSequenceIterator(
    GenericStruct, Generic[TSequence], type_vars=SequenceIteratorTypeVars
):
    sequence: TSequence
    index: Number
    stop: Number

    @classmethod
    def for_sequence(cls, seq, /):
        if not (hasattr(seq, "__getitem__") and isinstance(seq, SonoSequence)):
            raise TypeError("Expected a sequence.")
        return cls[type(seq)](seq, Number.new(), Len(seq))

    def _iter_(self):
        return self

    @sono_function
    def _has_item_(self):
        return self.index < self.stop

    @sono_function
    def _item_(self):
        value = self.sequence[self.index]
        return IndexedEntry[type(value)](self.index.copy(), value)

    @sono_function
    def _advance_(self):
        self.index += 1


TIterator = TypeVar("TIterator", bound=Iterator)


class IndexedIteratorWrapperTypeVars(NamedTuple):
    TIterator: type


class IndexedIteratorWrapper(
    GenericStruct, Generic[TIterator], type_vars=IndexedIteratorWrapperTypeVars
):
    iterator: TIterator
    index: Number

    @sono_function
    def _has_item_(self):
        return self.iterator._has_item_()

    def _iter_(self):
        return self

    @sono_function
    def _item_(self):
        index = self.index.copy()
        value = self.iterator._item_()
        return IndexedEntry[type(value)](index, value)

    @sono_function
    def _advance_(self):
        self.index += 1

    @classmethod
    def for_iterator(cls, i, /):
        return cls(i, Number.new())


def Len(v: SonoSequence, /):
    return v._len_()


def Iter(seq: SonoIterable[T], /) -> Iterator[T] | SonoIterator[T]:
    if isinstance(seq, SonoIterable):
        return seq._iter_()
    raise TypeError(f"Value {seq} is not an Iterable.")


def Next(iterator: SonoIterator[T], /) -> T:
    if isinstance(iterator, SonoIterator):
        return Execute(result := iterator._item_(), iterator._advance_(), result)
    raise TypeError(f"Value {iterator} is not a SonoIterator.")


def Enumerate(
    seq: SonoIterable[T], /
) -> Iterator[Tuple[Number, T]] | SonoIterator[IndexedEntry[T]]:
    if hasattr(seq, "_enumerate_"):
        return seq._enumerate_()
    iterator = Iter(seq)
    return IndexedIteratorWrapper[type(iterator)].for_iterator(iterator)
