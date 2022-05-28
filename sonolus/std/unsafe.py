from typing import TypeVar, Type

from sonolus.engine.struct import Struct
from sonolus.engine.value import Transmute, _new_temp_loc

__all__ = ("Transmute", "Unknown", "NewTemp")

T = TypeVar("T")


class Unknown(Struct):
    def transmute(self, type_: Type[T]) -> T:
        return Transmute(self, type_)


def NewTemp(name: str) -> Unknown:
    return Unknown._create_(_new_temp_loc(name))
