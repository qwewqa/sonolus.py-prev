from typing import TypeVar, NamedTuple, Callable, Generic

from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.generic_struct import GenericStruct
from sonolus.engine.statements.primitive import Boolean

TOut = TypeVar("TOut")
TSrc = TypeVar("TSrc")


class MappingIteratorTypeVars(NamedTuple):
    TSrc: type
    TOut: type
    map: Callable[[...], TOut]


class MappingIterator(GenericStruct, Generic[TSrc], type_vars=MappingIteratorTypeVars):
    source: TSrc

    @classmethod
    def from_iterator(cls, iterator):
        return cls(iterator)

    @sls_func
    def _iter_(self):
        return self

    @sls_func
    def _has_item_(self) -> Boolean:
        return self.source._has_item_()

    @sls_func
    def _item_(self):
        return self.type_vars.map(self.source._item_())

    @sls_func
    def _advance_(self) -> TOut:
        return self.source._advance_()

    def __iter__(self):
        raise TypeError("Cannot call __iter__ on an SlsIterator.")


class FilteringIteratorTypeVars(NamedTuple):
    TSrc: type
    filter: Callable[[...], Boolean]


class FilteringIterator(
    GenericStruct, Generic[TSrc], type_vars=FilteringIteratorTypeVars
):
    source: TSrc

    @classmethod
    @sls_func
    def from_iterator(cls, iterator):
        result = cls(iterator)
        result._advance_until_valid()
        return result

    @sls_func
    def _iter_(self):
        return self

    @sls_func
    def _has_item_(self) -> Boolean:
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

    def __iter__(self):
        raise TypeError("Cannot call __iter__ on an SlsIterator.")
