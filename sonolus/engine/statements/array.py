from __future__ import annotations

from typing import (
    ClassVar,
    Type,
    TypeVar,
    Generic,
    Sequence,
    Iterator,
    overload,
)

from sonolus.backend.ir import Location, TempRef
from sonolus.engine.functions.sls_func import convert_literal
from sonolus.engine.statements.control_flow import ExecuteVoid
from sonolus.engine.statements.iterator import (
    SequenceIterator,
    IndexedSequenceIterator,
    SlsIterator,
)
from sonolus.engine.statements.primitive import Number, Boolean
from sonolus.engine.statements.tuple import SlsTuple
from sonolus.engine.statements.value import Value, convert_value
from sonolus.engine.statements.void import Void

T = TypeVar("T")
U = TypeVar("U")


class Array(Value, Generic[T, U]):
    _typed_subclasses_: ClassVar[dict] = {}

    def __init__(self, *args, **kwargs):
        raise TypeError(
            "Array cannot be directly instantiated without a type and size."
        )

    def __class_getitem__(cls, contained_type):
        if isinstance(contained_type, TypeVar):
            return cls
        if isinstance(contained_type, tuple):
            contained_type, *sizes = contained_type
        else:
            sizes = ()
        if contained_type not in cls._typed_subclasses_:
            cls._typed_subclasses_[contained_type] = _create_typed_array_class(
                contained_type
            )
        result = cls._typed_subclasses_[contained_type]
        match sizes:
            case []:
                return result
            case [size]:
                return result[size]
            case [size, *others]:
                return Array[(result[size], *others)]

    @classmethod
    @overload
    def of(cls, *args: float) -> Array[Number]:
        pass

    @classmethod
    @overload
    def of(cls, *args: bool) -> Array[Boolean]:
        pass

    @classmethod
    @overload
    def of(cls, *args: T) -> Array[T]:
        pass

    @classmethod
    def of(cls, *args):
        """
        Returns an allocated Array with automatically determined type and size.
        """
        elements = [convert_literal(arg) for arg in args]
        types = {type(element) for element in elements}
        if len(types) != 1:
            raise TypeError("Array elements must be of the same type.")

        # Argument evaluation handled by Array.new
        return Array[types.pop(), len(elements)].new([*elements])

    def __getitem__(self, item) -> T:
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError

    def _len_(self) -> Number:
        raise NotImplementedError

    def _contained_type_(self) -> Type[T]:
        raise NotImplementedError

    def _max_size_(self) -> int:
        raise NotImplementedError

    def _iter_(self) -> SlsIterator[T]:
        raise NotImplementedError

    def _enumerate_(self) -> SlsIterator[SlsTuple[Number, T]]:
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


def _create_typed_array_class(type_: Type[Value]):
    if not Value.is_value_class(type_):
        raise TypeError("Expected a subclass of Value.")

    class TypedArray(Array):

        _sized_subclasses: ClassVar[dict] = {}
        contained_type: Type[Value] = type_

        def __class_getitem__(cls, size: int):
            if size not in cls._sized_subclasses:
                if not isinstance(size, int) and not size >= 0:
                    raise ValueError("Expected a non-negative integer size.")

                _size = size

                class SizedArray(TypedArray):
                    size = _size
                    _is_concrete_ = True
                    _size_ = size * type_._size_

                    def __init__(self, values=None):
                        if values is None:
                            values = [
                                self.contained_type._default_() for _ in range(size)
                            ]
                        if len(values) != self.size:
                            raise ValueError(
                                f"Expected {self.size} values, instead got {len(values)}."
                            )
                        self._value_ = tuple(
                            convert_value(v, self.contained_type) for v in values
                        )
                        self._parent_statement_ = ExecuteVoid(*self._value_)

                    def __getitem__(self, idx):
                        # If size > 0, then 0 <= idx < size.
                        # If size == 0, then idx may be any non-negative integer.
                        # Subscripting a zero length allocated array is well-defined
                        # and may be used for purposes such as implementing variable-length arrays.
                        # Subscripting a zero length temporary array is undefined.
                        idx = convert_value(idx, Number)
                        match self._value_:
                            case Location() as loc:
                                new_offset = Number._create_(
                                    loc.offset
                                ) + idx * Number._create_(self.contained_type._size_)
                                parent = ExecuteVoid(self, idx, new_offset)
                                if self.size > 0 and loc.span is not None:
                                    new_span = (
                                        loc.span
                                        + (self.size - 1) * self.contained_type._size_
                                    )
                                else:
                                    if isinstance(loc.ref, TempRef):
                                        raise ValueError(
                                            "Cannot subscript zero-length temporary array."
                                        )
                                    new_span = None
                                return self.contained_type._create_(
                                    Location(
                                        loc.ref,
                                        new_offset.ir(),
                                        loc.base,
                                        new_span,
                                    )
                                )._set_parent_(parent)
                            case tuple() as values:
                                if (constant_index := idx.ir().constant()) is not None:
                                    if int(constant_index) != constant_index:
                                        raise ValueError(
                                            "Array may only be subscripted with integers."
                                        )
                                    return values[int(constant_index)]
                                else:
                                    raise ValueError(
                                        "Cannot subscript non-allocated arrays with a non-constant index."
                                    )
                            case _:
                                raise ValueError("Unexpected value.")

                    def __len__(self):
                        return self.size

                    def __iter__(self):
                        for i in range(self.size):
                            yield self[i]

                    def _len_(self):
                        return self.size

                    def _iter_(self):
                        if isinstance(self._value_, tuple):
                            raise ValueError("Cannot iterate over a reference array.")
                        return SequenceIterator.for_sequence(self)

                    def _contained_type_(self):
                        return self.contained_type

                    def _max_size_(self):
                        return self.size

                    def _assign_(self, value) -> Void:
                        value = convert_value(value, type(self))
                        return Void()._set_parent_(
                            ExecuteVoid(
                                self,
                                value,
                                *(
                                    s._assign_(v)
                                    for s, v in zip(self.as_tuple(), value.as_tuple())
                                ),
                            )
                        )

                    def _flatten_(self):
                        return [
                            ele
                            for entry in self.as_tuple()
                            for ele in entry._flatten_()
                        ]

                    def _enumerate_(self):
                        if isinstance(self._value_, tuple):
                            raise ValueError("Cannot iterate over a reference array.")
                        return IndexedSequenceIterator.for_sequence(self)

                    def as_tuple(self):
                        if isinstance(self._value_, tuple):
                            return self._value_
                        else:
                            return tuple(self[i] for i in range(self.size))

                    @classmethod
                    def _convert_(cls, value):
                        match value:
                            case cls():
                                return value
                            case s if isinstance(s, Sequence):
                                return cls(*s)
                            case _:
                                return NotImplemented

                SizedArray.__name__ = f"Array_{type_.__name__}_{size}"
                SizedArray.__qualname__ = SizedArray.__name__

                cls._sized_subclasses[size] = SizedArray
            return cls._sized_subclasses[size]

        @classmethod
        def of(cls, *args):
            result = super().of(*args)
            if not isinstance(result, cls):
                raise TypeError(f"Cannot create {cls} from {args}.")
            return result

    TypedArray.__name__ = f"Array_{type_.__name__}"
    TypedArray.__qualname__ = TypedArray.__name__
    return TypedArray
