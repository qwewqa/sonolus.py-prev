from __future__ import annotations

from typing import Generic, TypeVar, NamedTuple

from sonolus.frontend.generic_struct import GenericStruct, generic_method

__all__ = ("Maybe",)

from sonolus.frontend.primitive import Bool
from sonolus.frontend.sls_func import sls_func

T = TypeVar("T")


class MaybeTypeVars(NamedTuple):
    T: type


class Maybe(GenericStruct, Generic[T], type_vars=MaybeTypeVars):
    _exists: Bool
    _value: T

    @generic_method
    @classmethod
    @sls_func
    def some(cls, value: T) -> Maybe[T]:
        result = cls._allocate_()
        result._exists @= True
        result._value @= value
        return result

    @generic_method
    @classmethod
    @sls_func
    def nothing(cls) -> Maybe[T]:
        result = cls._allocate_()
        result._exists @= False
        return result

    @property
    @sls_func
    def is_some(self) -> Bool:
        return self._exists

    @property
    @sls_func
    def is_nothing(self) -> Bool:
        return not self._exists

    @generic_method
    @sls_func
    def unwrap(self) -> T:
        return self._value

    @generic_method
    @sls_func
    def _assign_(self, value: Maybe[T]):
        if value.is_some:
            self._exists @= True
            self._value @= value._value
        else:
            self._exists @= False
