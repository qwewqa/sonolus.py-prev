from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Type, ClassVar

from sonolus.backend.ir import Location, IRNode
from sonolus.engine.control_flow import ExecuteVoid
from sonolus.engine.dataclass_transform import __dataclass_transform__
from sonolus.engine.value import Value, convert_value
from sonolus.engine.void import Void


@__dataclass_transform__(eq_default=True)
class Struct(Value):
    _struct_fields_: ClassVar[tuple[StructField, ...]]
    _constructor_signature_: ClassVar[inspect.Signature]

    def __init_subclass__(
        cls,
        _no_init_struct_: bool = False,
        _override_fields_: dict | None = None,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)
        if _no_init_struct_:
            return
        if hasattr(cls, "_struct_fields_"):
            raise TypeError("Subclassing of a Struct is not allowed.")
        if _override_fields_ is not None:
            hints = _override_fields_
        else:
            hints = inspect.get_annotations(cls, eval_str=True)
        fields = []
        offset = 0
        for index, (name, hint) in enumerate(hints.items()):
            if hint is ClassVar or getattr(hint, "__origin__", ()) is ClassVar:
                continue
            default = getattr(cls, name, hint._default_())
            if not Value.is_value_class(hint):
                raise TypeError(f"Expected subclasses of Value for field {name}.")
            field = StructField(name, hint, index, offset, default)
            fields.append(field)
            setattr(cls, name, field)
            offset += hint._size_
        params = [
            inspect.Parameter(
                field.name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=field.default,
            )
            for field in fields
        ]
        cls._constructor_signature_ = inspect.Signature(params)
        cls._struct_fields_ = tuple(fields)
        cls._size_ = offset
        cls._is_concrete_ = True

    def __init__(self, *args, **kwargs):
        bound: inspect.BoundArguments = self._constructor_signature_.bind(
            *args, **kwargs
        )
        bound.apply_defaults()
        self._value_ = tuple(
            convert_value(bound.arguments[field.name], field.type)
            for field in self._struct_fields_
        )
        self._parent_statement_ = ExecuteVoid(*self._value_)

    def _as_tuple_(self):
        if isinstance(self._value_, tuple):
            return self._value_
        else:
            return tuple(field.__get__(self) for field in self._struct_fields_)

    def _assign_(self, value) -> Void:
        value = convert_value(value, type(self))
        return Void.from_statement(
            ExecuteVoid(
                self,
                value,
                *(s._assign_(v) for s, v in zip(self._as_tuple_(), value._as_tuple_())),
            )
        )

    def _flatten_(self) -> list[IRNode]:
        return [ele for v in self._as_tuple_() for ele in v._flatten_()]


@dataclass
class StructField:
    name: str
    type: Type[Value]
    index: int
    offset: int
    default: Value

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        match instance._value_:
            case Location() as loc:
                return self.type._create_(
                    Location(loc.ref, loc.offset, loc.base + self.offset, loc.span),
                )._set_parent_(instance)
            case [*values]:
                return values[self.index]._dup_()._set_parent_(instance)
            case _:
                raise ValueError("Unexpected value.")


class Empty(Struct):
    pass
