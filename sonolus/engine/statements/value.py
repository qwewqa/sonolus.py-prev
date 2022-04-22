from __future__ import annotations

from typing import TypeVar, Type, ClassVar, Any, ParamSpec, Callable, overload

from sonolus.backend.compiler import CompilationInfo
from sonolus.backend.ir import IRNode, Location, TempRef, IRConst
from sonolus.engine.statements.statement import Statement

TValue = TypeVar("TValue", bound="Value")
P = ParamSpec("P")


class Value(Statement):
    _is_concrete_: ClassVar[bool] = False
    _size_: ClassVar[int] = 0
    _value_: Location | Any = None

    # If True, allocating is not allowed
    _ref_only_: ClassVar[bool] = False

    # This should return Void in implementations,
    # but pyright will give incorrect results if this isn't specified this way.
    def _assign_(self: TValue, value) -> TValue:
        """
        Mutates this value in-place to the given value.
        """
        raise NotImplementedError

    def _dup_(self: TValue) -> TValue:
        """
        Returns a shallow copy of this value with the same underlying value.
        """
        return self._create_(self._value_)

    def _flatten_(self) -> list[IRNode]:
        """
        Returns this value as a list of IRNodes with the same length as _size_.
        Used to populate Spawn() arguments.
        """
        raise NotImplementedError

    def _standalone_(self: TValue) -> TValue:
        """
        Marks this value standalone and returns it.
        Standalone values are not evaluated by the compiler, so this is for values
        that don't require any initialization and do not have any side effects.
        This is primarily for constants and dereferenced values of constant pointers.
        """
        self._is_standalone_ = True
        return self

    @classmethod
    def _create_(cls: Type[TValue], value: Location | Any) -> TValue:
        """
        Returns a new instance of this class as an alternative to __init__,
        which may take other arguments.
        """
        result = cls.__new__(cls)
        result._value_ = value
        return result

    @classmethod
    def _allocate_(cls: Type[TValue], initial_value: Value | None = None) -> TValue:
        """
        Returns a new allocated instance of this class that has been initialized to the given value.
        """
        if cls._ref_only_:
            raise TypeError(
                f"Cannot allocate a value of type {cls} because it is reference only."
            )
        result = cls._create_(_new_temp_loc(cls.__name__))
        if initial_value is not None:
            # Mind the _dup_
            # A value should not be its own parent.
            return result._dup_()._set_parent_(result._assign_(initial_value))
        else:
            return result

    @classmethod
    def _default_(cls: Type[TValue]) -> TValue:
        """
        Returns a new standalone instance of the default value of this class.
        """
        return cls()._standalone_()

    @classmethod
    def _convert_(cls: Type[TValue], value) -> TValue:
        if isinstance(value, cls):
            return value
        else:
            raise TypeError(f"Conversion from {type(value)} to {cls} not supported.")

    @classmethod
    @overload
    def new(cls: Callable[P, TValue], *args: P.args, **kwargs: P.kwargs) -> TValue:
        pass

    @classmethod
    @overload
    def new(cls: Callable[P, TValue], *args, **kwargs) -> TValue:
        pass

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Creates a new allocated instance of this class.
        Should not be overridden.
        """
        return cls._allocate_(cls(*args, **kwargs))  # type: ignore

    def copy(self: TValue) -> TValue:
        return self._allocate_(self)

    @staticmethod
    def is_value_class(cls: type):
        return isinstance(cls, type) and issubclass(cls, Value) and cls._is_concrete_

    def __imatmul__(self: TValue, other):
        """
        See _assign_.
        """
        return self._assign_(other)

    def __lshift__(self, other):
        """
        See _assign_.
        This is an alternative to @= in places where an expression is required.
        """
        return self._assign_(other)


def Transmute(value: Value, type_: Type[TValue], /) -> TValue:
    return type_._create_(value._value_)._set_parent_(value)


def _new_temp_loc(name: str):
    return Location(_new_temp_ref(name), IRConst(0), 0, 1)


def _new_temp_ref(name: str):
    refs = CompilationInfo.get().refs
    index = refs.get(name, 0)
    refs[name] = index + 1
    return TempRef(f"{name}__{index}")
