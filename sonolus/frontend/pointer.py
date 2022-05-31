from __future__ import annotations
from typing import Type, ClassVar, TypeVar, Generic

from sonolus.backend.ir import Location, IRNode, IRConst
from sonolus.frontend.primitive import Num
from sonolus.frontend.struct import Struct
from sonolus.frontend.value import Value

T = TypeVar("T")
TTarget = TypeVar("TTarget")


class Pointer(Struct, Generic[T]):
    block: Num
    index: Num

    _typed_subclasses_: ClassVar[dict[Type[Value], type]] = {}

    def __init_subclass__(cls, **kwargs):
        if cls.__module__ != Pointer.__module__:
            raise TypeError("Cannot subclass Pointer.")

    def __class_getitem__(cls, item):
        if item not in cls._typed_subclasses_:
            cls._typed_subclasses_[item] = _create_typed_pointer_class(item)
        return cls._typed_subclasses_[item]

    def deref_as(self, type_: Type[TTarget]) -> TTarget:
        if not Value.is_value_class(type_):
            raise TypeError("Can only dereference as a subclass of Value.")
        if (block := self.block.constant()) is not None and (
            index := self.index.constant()
        ) is not None and self._is_static_:
            return type_._create_(Location(block, IRConst(0), index, 1))._set_static_()
        return type_._create_(
            Location(self.block.ir(), self.index.ir(), 0, None)
        )._set_parent_(self)

    def deref(self) -> T:
        raise TypeError("Cannot deref an untyped pointer. Use deref_as instead.")

    @staticmethod
    def to(value: TTarget) -> Pointer[Type[TTarget]]:
        value_type = type(value)
        if not Value.is_value_class(value_type):
            raise TypeError("Expected an instance of Value.")
        location = value._value_
        if not isinstance(location, Location):
            raise TypeError("Pointers to unallocated values are not supported.")
        match location.ref:
            case int() as block:
                block = Num(block)
            case IRNode() as block:
                block = Num(block)
            case _:
                raise TypeError("Pointers to temporary variables are not supported.")
        return Pointer[value_type](block, location.offset)


def _create_typed_pointer_class(type_: Type[Value]):
    if not Value.is_value_class(type_):
        raise TypeError("Expected a subclass of Value.")

    class TypedPointer(Pointer):
        __name__ = f"TypedPointer_{type_.__name__}"

        contained_type: Type[Value] = type_

        def deref(self):
            return self.deref_as(self.contained_type)

        @classmethod
        def _convert_(cls, value):
            match value:
                case cls() as p:
                    return p
                case Pointer() as p:
                    return cls._create_(p._value_)._set_parent_(p)
                case _:
                    return NotImplemented

    TypedPointer.__name__ = f"Pointer_{type_.__name__}"
    TypedPointer.__qualname__ = TypedPointer.__name__

    return TypedPointer
