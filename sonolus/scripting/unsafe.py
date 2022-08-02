from typing import TypeVar, Type

from sonolus.scripting.internal.struct import Struct
from sonolus.scripting.internal.value import transmute, _new_temp_loc

__all__ = ("transmute", "Unknown", "new_temp")

T = TypeVar("T")


class Unknown(Struct):
    def transmute(self, type_: Type[T]) -> T:
        return transmute(self, type_)


def new_temp(name: str) -> Unknown:
    return Unknown._create_(_new_temp_loc(name))
