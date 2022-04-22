from __future__ import annotations

from typing import TypeVar, overload, Type, Any, Callable

from sonolus.engine.statements.array import Array
from sonolus.engine.statements.generic_struct import GenericStruct, generic_function
from sonolus.engine.statements.pointer import Pointer
from sonolus.engine.statements.primitive import Boolean, Number
from sonolus.engine.statements.struct import Struct, Empty
from sonolus.engine.statements.tuple import SlsTuple
from sonolus.engine.statements.value import Value, convert_value
from sonolus.engine.statements.void import Void

__all__ = (
    "Value",
    "Struct",
    "SlsTuple",
    "Empty",
    "Array",
    "Pointer",
    "Void",
    "GenericStruct",
    "generic_function",
    "new",
    "alloc",
    "default_factory",
)

T = TypeVar("T", bound=Value)


@overload
def new() -> Any | _NewValue:
    pass


@overload
def new(value: float, /) -> Number:
    pass


@overload
def new(value: bool, /) -> Boolean:
    pass


@overload
def new(value: T, /) -> T:
    pass


@overload
def new(value: Type[T], /) -> T:
    pass


@overload
def new(value: list[float], /) -> Array[Number]:
    pass


@overload
def new(value: list[bool], /) -> Array[Boolean]:
    pass


@overload
def new(value: list[T], /) -> Array[T]:
    pass


def new(value=None, /):
    match value:
        case None:
            return _NewValue()
        case list():
            return Array.of(*value)
        case type() if Value.is_value_class(value):
            return value.new()
        case Value():
            return value.copy()
        case bool() as boolean:
            return Boolean.new(boolean)
        case int() | float() as number:
            return Number.new(number)
        case _:
            raise TypeError(f"Cannot create new value from {value}.")


def alloc(type_: Type[T], /) -> T:
    return type_._allocate_()


def default_factory(factory: Callable[[], Any]) -> Any:
    return _DefaultFactory(factory)


class _NewValue:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return type(self)(*(self.args + args), **(self.kwargs | kwargs))

    def _convert_to_(self, type_):
        return type_.new(*self.args, **self.kwargs)


class _DefaultFactory:
    def __init__(self, factory):
        self.factory = factory

    def _convert_to_(self, type_):
        return convert_value(self.factory(), type_)
