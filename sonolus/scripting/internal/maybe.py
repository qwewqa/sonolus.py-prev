from __future__ import annotations

from typing import Generic, TypeVar, NamedTuple, Type, Callable

from sonolus.scripting.internal.generic_struct import GenericStruct, generic_method
from sonolus.scripting.internal.primitive import Bool
from sonolus.scripting.internal.sls_func import sls_func
from sonolus.scripting.internal.struct import Struct
from sonolus.scripting.internal.value import convert_value

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
        return cls(True, value)

    @generic_method
    @classmethod
    @sls_func
    def nothing(cls) -> Maybe[T]:
        return cls(False)

    @classmethod
    def new(cls, value: T | None = None) -> Maybe[T]:
        if value is None:
            return +cls.nothing()
        return +cls.some(value)

    @classmethod
    def take_if(cls, value: T, condition: Bool, /) -> Maybe[T]:
        if cls is Maybe:
            return cls[type(value)](condition, value)
        else:
            if not isinstance(value, cls.type_vars.T):
                raise TypeError(f"{value} is not an instance of {cls.type_vars.T}.")
            return cls(condition, value)

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
        # For symmetry with unwrap_or, we return a copy of the value.
        return self._value.copy()

    @generic_method
    @sls_func
    def unwrap_direct(self) -> T:
        return self._value

    @generic_method
    @sls_func
    def unwrap_or(self, default: T) -> T:
        return self._value if self._exists else default

    @generic_method
    @sls_func
    def _assign_(self, value: Maybe[T]):
        if value.is_some:
            self._exists @= True
            self._value @= value._value
        else:
            self._exists @= False

    @classmethod
    def _convert_(cls, value) -> Maybe[T]:
        match value:
            case cls():
                return value
            case Maybe() if value.type_vars.T is _NothingDummy:
                return cls(False)._set_parent_(value)
            case cls.type_vars.T():
                return cls.some(value)
            case None:
                return cls.nothing()
            case _:
                return NotImplemented


class _Some:
    def __call__(self, value: T) -> Maybe[T]:
        value = convert_value(value)
        return Maybe[type(value)].some(value)

    def __getitem__(self, item: Type[T]) -> Callable[[T], Maybe[T]]:
        return Maybe[item].some


class _NothingDummy(Struct):
    pass


class _Nothing:
    def __call__(self) -> Maybe:
        return Maybe[_NothingDummy].nothing()

    def __getitem__(self, item: Type[T]) -> Callable[[], Maybe[T]]:
        return Maybe[item].nothing


Some = _Some()
Nothing = _Nothing()
