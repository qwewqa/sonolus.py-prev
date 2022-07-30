from __future__ import annotations

from typing import TypeVar, Type, ClassVar, Any, ParamSpec, Callable

from sonolus.backend.evaluation import CompilationInfo
from sonolus.backend.ir import IRNode, Location, TempRef, IRConst
from sonolus.frontend.statement import Statement, StatementAttributes

T = TypeVar("T", bound="Value")
TValue = TypeVar("TValue", bound="Value")
P = ParamSpec("P")


class Value(Statement):
    _is_concrete_: ClassVar[bool] = False
    _size_: ClassVar[int] = 0
    _value_: Location | Any = None

    # This should return Void in implementations,
    # but pyright will give incorrect results if this isn't specified this way.
    def _assign_(self: TValue, value) -> TValue:
        """
        Mutates this value in-place to the given value.
        """
        raise NotImplementedError

    def _dup_(self: TValue, parent: Statement) -> TValue:
        """
        Returns a shallow copy of this value with the same underlying value.
        """
        return self._create_(self._value_, self._attributes_)._set_parent_(parent)

    def _flatten_(self) -> list[IRNode]:
        """
        Returns this value as a list of IRNodes with the same length as _size_.
        Used to populate Spawn() arguments.
        """
        raise NotImplementedError

    @classmethod
    def _from_flat_(cls: Type[TValue], flat: list[IRNode]) -> TValue:
        """
        Creates a value from a list of IRNodes.
        """
        raise NotImplementedError

    def _dump_(self) -> Any:
        """
        Returns some representation of this value.
        Raises an exception if this value is not a constant.
        The returned value supports value equality comparison.
        """
        pass

    def _set_static_(self: TValue, value=True) -> TValue:
        """
        Marks this value static and returns it.
        Standalone values are not evaluated by the compiler, so this is for values
        that don't require any initialization and do not have any side effects.
        This is primarily for constants and dereferenced values of constant pointers.
        """
        self._attributes_.is_static = value
        return self

    @classmethod
    def _create_(
        cls: Type[TValue], value: Location | Any, attributes: StatementAttributes = None
    ) -> TValue:
        """
        Returns a new instance of this class as an alternative to __init__,
        which may take other arguments.
        """
        result = cls.__new__(cls)
        Value.__init__(result, attributes=attributes)
        result._value_ = value
        return result

    @classmethod
    def _allocate_(cls: Type[TValue], initial_value: Value | None = None) -> TValue:
        """
        Returns a new allocated instance of this class that has been initialized to the given value.
        """
        result = cls._create_(_new_temp_loc(cls.__name__))
        if initial_value is not None:
            return result._dup_(result._assign_(initial_value))
        else:
            return result

    @classmethod
    def _default_(cls: Type[TValue]) -> TValue:
        """
        Returns a new static instance of the default value of this class.
        """
        return cls()._set_static_()

    @classmethod
    def _convert_(cls: Type[TValue], value) -> TValue:
        """
        Converts the given value to this type.
        Returns NotImplemented if the conversion is not supported.
        """
        if cls is Value:
            from sonolus.frontend.sls_func import convert_literal

            return convert_literal(value)

        if isinstance(value, cls):
            return value
        else:
            return NotImplemented

    def _convert_to_(self, type_: Type[T]) -> T:
        """
        Converts this value to the given type.
        Returns NotImplemented if the conversion is not supported.

        This method may still be recognized for non Value subtypes.
        """
        return NotImplemented

    def _const_evaluate_(self: T, runner: Callable[[IRNode], float]) -> T:
        """
        Evaluates this value as a constant.
        """
        raise NotImplementedError

    def copy(self: TValue) -> TValue:
        return self._allocate_(self)

    def __pos__(self: TValue) -> TValue:
        """
        Shorthand for copy().
        """
        return self.copy()

    @staticmethod
    def is_value_class(cls: type):
        return isinstance(cls, type) and issubclass(cls, Value) and cls._is_concrete_

    def __imatmul__(self: TValue, other):
        """
        See _assign_.
        """
        return self._dup_(self._assign_(other))

    def __matmul__(self, other):
        """
        See _assign_.
        This is an alternative to @= in places where an expression is required.
        """
        return self._assign_(other)

    # The following is so subclasses don't have to manually implement inplace operators.

    def __iadd__(self, other):
        return self._dup_(self._assign_(self + other))

    def __iand__(self, other):
        return self._dup_(self._assign_(self & other))

    def __ifloordiv__(self, other):
        return self._dup_(self._assign_(self // other))

    def __ilshift__(self, other):
        return self._dup_(self._assign_(self << other))

    def __imod__(self, other):
        return self._dup_(self._assign_(self % other))

    def __imul__(self, other):
        return self._dup_(self._assign_(self * other))

    def __ior__(self, other):
        return self._dup_(self._assign_(self | other))

    def __ipow__(self, other):
        return self._dup_(self._assign_(self**other))

    def __irshift__(self, other):
        return self._dup_(self._assign_(self >> other))

    def __isub__(self, other):
        return self._dup_(self._assign_(self - other))

    def __itruediv__(self, other):
        return self._dup_(self._assign_(self / other))

    def __ixor__(self, other):
        return self._dup_(self._assign_(self ^ other))


def convert_value(value, target_type: Type[T]) -> T:
    if not Value.is_value_class(target_type):
        raise TypeError(f"Cannot convert to {target_type}, expected a Value class.")
    result = NotImplemented
    if hasattr(value, "_convert_to_"):
        result = value._convert_to_(target_type)
    if result is NotImplemented:
        result = target_type._convert_(value)
    if result is NotImplemented:
        raise TypeError(f"Cannot convert {value} to {target_type}.")
    return result


def Transmute(value: Value, type_: Type[TValue], /) -> TValue:
    if not isinstance(value._value_, Location):
        raise TypeError(f"Cannot transmute unallocated value {value}.")
    return type_._create_(value._value_, value._attributes_)._set_parent_(value)


def _new_temp_loc(name: str):
    return Location(_new_temp_ref(name), IRConst(0), 0, 1)


def _new_temp_ref(name: str):
    refs = CompilationInfo.get().refs
    index = refs.get(name, 0)
    refs[name] = index + 1
    return TempRef(f"{name}__{index}")
