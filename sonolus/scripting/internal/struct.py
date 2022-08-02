from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Type, ClassVar, get_type_hints, get_origin

from sonolus.backend.ir import Location, IRNode
from sonolus.scripting.internal.control_flow import ExecuteVoid
from sonolus.scripting.internal.dataclass_transform import __dataclass_transform__
from sonolus.scripting.internal.primitive import invoke_builtin, Bool
from sonolus.scripting.internal.value import Value, convert_value
from sonolus.scripting.internal.void import Void


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
            hints = get_type_hints(cls)
        fields = []
        offset = 0
        index = 0
        for name, hint in hints.items():
            if name not in cls.__annotations__ and not _override_fields_:
                continue
            if hint is ClassVar or get_origin(hint) is ClassVar:
                continue
            default = getattr(cls, name, hint._default_())
            if not Value.is_value_class(hint):
                raise TypeError(f"Expected subclasses of Value for field {name}.")
            field = StructField(name, hint, index, offset, default)
            fields.append(field)
            setattr(cls, name, field)
            offset += hint._size_
            index += 1
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
        super().__init__()
        bound: inspect.BoundArguments = self._constructor_signature_.bind(
            *args, **kwargs
        )
        bound.apply_defaults()
        self._value_ = tuple(
            convert_value(bound.arguments[field.name], field.type)
            for field in self._struct_fields_
        )

        if all(v._attributes_.is_static for v in self._value_):
            self._attributes_.is_static = True
        else:
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

    @classmethod
    def _from_flat_(cls, flat):
        return cls(
            *(
                field.type._from_flat_(
                    flat[field.offset : field.offset + field.type._size_]
                )
                for field in cls._struct_fields_
            )
        )

    def _dump_(self):
        return {f.name: getattr(self, f.name) for f in self._struct_fields_}

    def _const_evaluate_(self, runner):
        self._was_evaluated_ = True
        return self._create_(
            tuple(v._const_evaluate_(runner) for v in self._as_tuple_())
        )

    def __eq__(self, other):
        other = convert_value(other, type(self))
        result = invoke_builtin(
            "And",
            [a.__eq__(b) for a, b in zip(self._as_tuple_(), other._as_tuple_())],
            Bool,
        )
        result.override_truthiness = self is other
        return result

    def __hash__(self):
        return id(self)

    def __str__(self):
        return f"{type(self).__name__}({', '.join(f'{f.name}={getattr(self, f.name)}' for f in self._struct_fields_)})"


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
                return (
                    self.type._create_(
                        Location(loc.ref, loc.offset, loc.base + self.offset, loc.span),
                        instance._attributes_,
                    )
                    ._set_parent_(
                        not instance._attributes_.is_static and instance or None
                    )
                    ._set_static_(instance._attributes_.is_static)
                )
            case [*values]:
                return (
                    values[self.index]
                    ._dup_(not instance._attributes_.is_static and instance or None)
                    ._set_static_(instance._attributes_.is_static)
                )
            case _:
                raise ValueError("Unexpected value.")


class Empty(Struct):
    pass
