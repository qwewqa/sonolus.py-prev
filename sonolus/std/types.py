from typing import TypeVar, overload, Type

from sonolus.engine.functions.sls_func import convert_value
from sonolus.engine.statements.array import Array
from sonolus.engine.statements.generic_struct import GenericStruct, generic_function
from sonolus.engine.statements.pointer import Pointer
from sonolus.engine.statements.primitive import Boolean, Number
from sonolus.engine.statements.struct import Struct, Empty
from sonolus.engine.statements.tuple import SlsTuple
from sonolus.engine.statements.value import Value
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
)

T = TypeVar("T", bound=Value)


@overload
def new(value: float) -> Number:
    pass


@overload
def new(value: bool) -> Boolean:
    pass


@overload
def new(value: T) -> T:
    pass


@overload
def new(value: Type[T]) -> T:
    pass


def new(value):
    match value:
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
    

def alloc(type_: Type[T]) -> T:
    return type_._allocate_()
