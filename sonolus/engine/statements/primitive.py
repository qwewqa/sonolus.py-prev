from __future__ import annotations

import warnings
from typing import Optional, Any, TYPE_CHECKING, Sequence, Type, TypeAlias

from sonolus.backend.evaluator import evaluate_ir
from sonolus.backend.ir import (
    IRSet,
    IRNode,
    IRGet,
    IRConst,
    IRFunc,
    Location,
    IRValueType,
)
from sonolus.engine.functions.sls_func import sls_func
from sonolus.backend.compiler import CompilationInfo
from sonolus.engine.statements.control_flow import Execute, If
from sonolus.engine.statements.value import Value
from sonolus.engine.statements.void import Void


class Primitive(Value):
    _size_: int = 1

    def __init__(self, value=0):
        self._value_ = value
        self._check_readable()

    def _assign_(self, value: Primitive) -> Void:
        value = self._convert_(value)
        match self._value_:
            case Location() as loc:
                self._check_writable()
                return Void(IRSet(loc, value.ir()))._set_parent_(Execute(self, value))
            case _:
                raise ValueError("Cannot assign to a constant.")

    def _flatten_(self) -> list[IRNode]:
        return [self.ir()]

    def constant(self):
        match self._value_:
            case int() | float() | bool() as constant:
                return constant
            case IRNode() as node:
                return evaluate_ir(node)
            case _:
                return None

    def ir(self) -> IRValueType:
        match self._value_:
            case Location() as loc:
                return IRGet(loc)
            case int() | float() | bool() as constant:
                return IRConst(float(constant))
            case IRNode() as node:
                return node
            case _:
                raise TypeError("Unexpected value.")

    def __eq__(self, other):
        other = self._convert_(other)
        truthiness = self is other
        result = (
            Boolean._create_(IRFunc("Equal", [self.ir(), other.ir()]))
            ._set_parent_(Execute(self, other))
            .copy()
        )
        result.override_truthiness = truthiness
        return result

    def __ne__(self, other):
        other = self._convert_(other)
        truthiness = self is not other
        result = (
            Boolean._create_(IRFunc("NotEqual", [self.ir(), other.ir()]))
            ._set_parent_(Execute(self, other))
            .copy()
        )
        result.override_truthiness = truthiness
        return result

    def __hash__(self):
        return id(self)

    @classmethod
    def _create_(cls, value: Location | Any):
        result: cls = super()._create_(value)  # type: ignore
        result._check_readable()
        return result

    def _check_readable(self):
        if CompilationInfo._current is None:
            return
        if not isinstance(self._value_, Location):
            return
        callback_type = CompilationInfo._current.callback
        if (
            isinstance(self._value_.ref, int)
            and self._value_.ref not in callback_type.readable_blocks
        ):
            warnings.warn(
                f"Potential invalid read from block {self._value_.ref} in callback {callback_type.name}."
            )

    def _check_writable(self):
        if CompilationInfo._current is None:
            return
        if not isinstance(self._value_, Location):
            return
        callback_type = CompilationInfo._current.callback
        if (
            isinstance(self._value_.ref, int)
            and self._value_.ref not in callback_type.writable_blocks
        ):
            warnings.warn(
                f"Potential invalid write to block {self._value_.ref} in callback {callback_type.name}."
            )

    @classmethod
    def _convert_(cls, value):
        match value:
            case cls():
                return value
            case _:
                return cls(value)


class Boolean(Primitive):
    _is_concrete_ = True

    def __init__(self, value=False, override_truthiness: Optional[bool] = None):
        if not isinstance(value, bool) and value not in (0, 1):
            raise TypeError("Expected a bool.")
        super().__init__(value)
        self.override_truthiness = override_truthiness

    @classmethod
    def _create_(cls, value: Location | Any):
        result = super()._create_(value)
        result.override_truthiness = None
        return result

    def __bool__(self):
        return True if self.override_truthiness is None else self.override_truthiness

    def and_(self, other):
        lhs = Boolean._convert_(self)
        rhs = Boolean._convert_(other)
        result = Execute(
            result := Boolean.new(), If(lhs, result << rhs, result << False), result
        )
        result.override_float_value = bool(lhs.constant() and rhs.constant())
        return result

    def or_(self, other):
        lhs = Boolean._convert_(self)
        rhs = Boolean._convert_(other)
        result = Execute(
            result := Boolean.new(), If(lhs, result << True, result << rhs), result
        )
        result.override_float_value = bool(lhs.constant() or rhs.constant())
        return result

    @classmethod
    def not_(cls, value):
        if isinstance(value, cls):
            return ~value
        else:
            return not Value

    @sls_func(ast=False)
    def __and__(self, other):
        return invoke_builtin("And", [self, other], Boolean)

    @sls_func(ast=False)
    def __rand__(self, other):
        return invoke_builtin("And", [other, self], Boolean)

    @sls_func(ast=False)
    def __or__(self, other):
        return invoke_builtin("Or", [self, other], Boolean)

    @sls_func(ast=False)
    def __ror__(self, other):
        return invoke_builtin("Or", [other, self], Boolean)

    @sls_func(ast=False)
    def __invert__(self) -> Boolean:
        # Note: differs from typical Python behavior (which treats bools as numbers)
        result = invoke_builtin("Not", [self], Boolean)
        result.override_float_value = (
            not self.override_truthiness
            if self.override_truthiness is not None
            else None
        )
        return result


class Number(Primitive):
    """
    A floating-point number.
    NaN and infinities may be represented, but behavior is undefined
    for some operations.
    """

    _is_concrete_ = True

    def __init__(self, value=0, override_float_value: Optional[float] = None):
        if not isinstance(value, (int, float)):
            raise TypeError("Expected an int or float.")
        super().__init__(value)
        self.override_float_value = override_float_value

    @classmethod
    def _create_(cls, value: Location | Any):
        result = super()._create_(value)
        result.override_float_value = None
        return result

    def __int__(self):
        return int(float(self))

    def __float__(self):
        if self.override_float_value is not None:
            value = self.override_float_value
        elif const_value := self.constant():
            value = const_value
        else:
            raise ValueError("Number does not have an associated value.")
        return value

    def __index__(self):
        value = float(self)
        if not value.is_integer():
            raise ValueError("Number has a non-integer value.")
        return int(value)

    @sls_func(ast=False)
    def __add__(self: Number, other: Number):
        return invoke_builtin("Add", [self, other], Number)

    @sls_func(ast=False)
    def __radd__(self: Number, other: Number):
        return invoke_builtin("Add", [other, self], Number)

    @sls_func(ast=False)
    def __sub__(self: Number, other: Number):
        return invoke_builtin("Subtract", [self, other], Number)

    @sls_func(ast=False)
    def __rsub__(self: Number, other: Number):
        return invoke_builtin("Subtract", [other, self], Number)

    @sls_func(ast=False)
    def __mul__(self: Number, other: Number):
        return invoke_builtin("Multiply", [self, other], Number)

    @sls_func(ast=False)
    def __rmul__(self: Number, other: Number):
        return invoke_builtin("Multiply", [other, self], Number)

    @sls_func(ast=False)
    def __truediv__(self: Number, other: Number):
        return invoke_builtin("Divide", [self, other], Number)

    @sls_func(ast=False)
    def __rtruediv__(self: Number, other: Number):
        return invoke_builtin("Divide", [other, self], Number)

    @sls_func(ast=False)
    def __floordiv__(self: Number, other: Number):
        return invoke_builtin("Floor", [self / other], Number)

    @sls_func(ast=False)
    def __rfloordiv__(self: Number, other: Number):
        return invoke_builtin("Floor", [other / self], Number)

    @sls_func(ast=False)
    def __mod__(self: Number, other: Number):
        return invoke_builtin("Mod", [self, other], Number)

    @sls_func(ast=False)
    def __rmod__(self: Number, other: Number):
        return invoke_builtin("Mod", [other, self], Number)

    @sls_func(ast=False)
    def __pow__(self: Number, other: Number):
        return invoke_builtin("Power", [self, other], Number)

    @sls_func(ast=False)
    def __rpow__(self: Number, other: Number):
        return invoke_builtin("Power", [other, self], Number)

    @sls_func(ast=False)
    def __gt__(self: Number, other: Number) -> Boolean:
        return invoke_builtin("Greater", [self, other], Boolean)

    @sls_func(ast=False)
    def __ge__(self: Number, other: Number) -> Boolean:
        return invoke_builtin("GreaterOr", [self, other], Boolean)

    @sls_func(ast=False)
    def __lt__(self: Number, other: Number) -> Boolean:
        return invoke_builtin("Less", [self, other], Boolean)

    @sls_func(ast=False)
    def __le__(self: Number, other: Number) -> Boolean:
        return invoke_builtin("LessOr", [self, other], Boolean)

    @sls_func(ast=False)
    def __neg__(self):
        return 0 - self

    @sls_func(ast=False)
    def __iadd__(self: Number, other: Number):
        return self << self + other

    @sls_func(ast=False)
    def __isub__(self: Number, other: Number):
        return self << self - other

    @sls_func(ast=False)
    def __imul__(self: Number, other: Number):
        return self << self * other

    @sls_func(ast=False)
    def __itruediv__(self: Number, other: Number):
        return self << self / other

    @sls_func(ast=False)
    def __ifloordiv__(self: Number, other: Number):
        return self << self // other

    @sls_func(ast=False)
    def __imod__(self: Number, other: Number):
        return self << self % other

    @sls_func(ast=False)
    def __ipow__(self: Number, other: Number):
        return self << self**other

    @sls_func(ast=False)
    def to_boolean(self) -> Boolean:
        return self != 0


def invoke_builtin(
    name: str, arguments: Sequence[Primitive], type_: Type[Primitive] = None
) -> Any:
    node = IRFunc(name=name, args=[arg.ir() for arg in arguments])
    if type_ is None:
        return Void(node=node)._set_parent_(Execute(*arguments))
    else:
        return type_._allocate_(
            type_._create_(value=node)._set_parent_(Execute(*arguments))
        )


if TYPE_CHECKING:
    Number = Number | float
    Boolean = Boolean | bool
