from __future__ import annotations

from typing import ClassVar, Generic, TYPE_CHECKING, Tuple

from typing_extensions import TypeVarTuple, Unpack

from sonolus.engine.functions.sls_func import convert_value
from sonolus.engine.statements.primitive import Number
from sonolus.engine.statements.struct import Struct
from sonolus.engine.statements.value import Value

Types = TypeVarTuple("Types")

if not TYPE_CHECKING:
    class Dummy:
        def __mro_entries__(self, bases):
            return ()

        def __getitem__(self, item):
            return self


    # This is to make type checkers recognize the correct types
    # after unpacking.
    Tuple = Dummy()


class SlsTuple(Tuple[Unpack[Types]], Struct, Generic[Unpack[Types]], _no_init_struct_=True):
    _subclass_cache = {}
    _types_: ClassVar[tuple[type, ...]] = None

    def __init_subclass__(cls, _types_=None, **kwargs):
        if _types_ is None:
            raise TypeError("Cannot subclass SlsTuple.")
        cls._types_ = _types_
        super().__init_subclass__(**kwargs)

    def __class_getitem__(cls, item):
        if not all(Value.is_value_class(t) for t in item):
            raise TypeError("SlsTuple can only contain Value classes.")
        if item not in cls._subclass_cache:
            fields = {f"field{i}": t for i, t in enumerate(item)}

            class Tuple(cls, _types_=item, _override_fields_=fields):
                pass

            Tuple.__name__ = f"{cls.__name__}_{'_'.join(t.__name__ for t in item)}"
            Tuple.__qualname__ = (
                f"{cls.__qualname__}_{'_'.join(t.__name__ for t in item)}"
            )

            cls._subclass_cache[item] = Tuple
        return cls._subclass_cache[item]

    @classmethod
    def of(cls, *args: Unpack[Types]) -> SlsTuple[Unpack[Types]]:
        """
        Returns an unallocated SlsTuple with automatically determined types.
        """
        values = [convert_value(arg) for arg in args]
        types = tuple(type(value) for value in values)
        result = SlsTuple[types](*values)
        if not isinstance(result, cls):
            # This may be false for typed subclasses.
            raise TypeError("Types of elements differ from given types.")
        return result

    def __init__(self, *args: Unpack[Types]):
        if self._types_ is None:
            raise TypeError("Cannot instantiate untyped SlsTuple directly.")
        super().__init__(*args)

    def __iter__(self):
        return iter(self._values_)

    def __getitem__(self, item):
        if isinstance(item, Number):
            item = item.constant()
        if not isinstance(item, int):
            raise TypeError("SlsTuple indices must be constant integers.")
        if not 0 <= item < len(self._types_):
            raise IndexError("SlsTuple index out of range.")
        return self._values_[item]

    @property
    def _values_(self) -> tuple[Unpack[Types]]:
        return tuple(getattr(self, f"field{i}") for i in range(len(self._types_)))
