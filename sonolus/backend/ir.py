from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, TypeAlias


class IRNode:
    def constant(self) -> Optional[float]:
        return None


@dataclass(eq=False)
class IRConst(IRNode):
    """IR for a constant value."""

    value: float | int

    def constant(self) -> Optional[float]:
        return float(self.value)

    def __str__(self):
        if self.value == int(self.value):
            return str(int(self.value))
        return f"{self.value}"


@dataclass(eq=False)
class IRComment(IRNode):
    message: str

    def constant(self) -> Optional[float]:
        return 0

    def __str__(self):
        return f"/* {self.message} */"


@dataclass(eq=False)
class IRFunc(IRNode):
    """
    IR for a function call.

    Functions may not have arguments with any side effects.
    Only top-level functions may have side effects.
    Top-level functions are are not the argument to any other function, or an offset
    of a location, but may be the value in a Set node.
    """

    name: str
    args: list[IRValueType] = field(default_factory=list)

    def __str__(self):
        entries = [str(arg) for arg in self.args]
        if len(entries) > 3 or any("\n" in entry for entry in entries):
            body = "\n" + textwrap.indent(",\n".join(entries), "    ") + "\n"
        else:
            body = ", ".join(entries)
        return f"{self.name}({body})"


@dataclass(eq=False)
class IRGet(IRNode):
    """IR for accessing a memory location."""

    location: Location

    def __str__(self):
        return f"{self.location}"


@dataclass(eq=False)
class IRSet(IRNode):
    """IR for modifying a memory location."""

    location: Location
    value: IRValueType

    def __str__(self):
        return f"{self.location} <- {self.value}"


IRValueType: TypeAlias = IRFunc | IRGet | IRConst


@dataclass(frozen=True)
class TempRef:
    # name should follow the same limitations as standard Python variable names.
    # Internally, names may contain other characters.
    name: str

    def __str__(self):
        return f"{self.name}"


@dataclass(frozen=True)
class SSARef:
    name: str

    def __str__(self):
        return f"{self.name}"


class MemoryBlock(IntEnum):
    LEVEL_MEMORY = 0
    LEVEL_DATA = 1
    LEVEL_OPTION = 2
    LEVEL_TRANSFORM = 3
    LEVEL_BACKGROUND = 4
    LEVEL_UI = 5
    LEVEL_BUCKET = 6
    LEVEL_SCORE = 7
    LEVEL_LIFE = 8
    LEVEL_UI_CONFIGURATION = 9

    ENTITY_INFO_ARRAY = 10
    ENTITY_DATA_ARRAY = 11
    ENTITY_SHARED_MEMORY_ARRAY = 12

    ENTITY_INFO = 20
    ENTITY_MEMORY = 21
    ENTITY_DATA = 22
    ENTITY_INPUT = 23
    ENTITY_SHARED_MEMORY = 24

    ARCHETYPE_LIFE = 30

    ENGINE_ROM = 50

    TEMPORARY_MEMORY = 100
    TEMPORARY_DATA = 101


MEMORY_BLOCK_VALUES = frozenset(MemoryBlock)

Ref = SSARef | TempRef | IRNode | int


@dataclass(eq=False)
class Location:
    ref: Ref
    offset: IRValueType
    base: int  # added to offset to get the actual index
    span: int | None  # 0 <= offset < span if span is not None. Should always be set for temporary locations.

    def __str__(self):
        if self.offset.constant() is not None:
            index = str(int(self.offset.constant() + self.base))
        elif self.base == 0:
            if self.span is None:
                index = f"0:?#{self.offset}"
            else:
                index = f"0:{self.span}#{self.offset}"
        else:
            if self.span is None:
                index = f"{self.base}:?#{self.offset}"
            else:
                index = f"{self.base}:{self.base + self.span}#{self.offset}"
        if isinstance(self.ref, TempRef) and self.base == 0 and self.span == 1:
            return f"@{self.ref}"
        elif isinstance(self.ref, SSARef):
            return f"%{self.ref}"
        elif isinstance(self.ref, int) and self.ref in MEMORY_BLOCK_VALUES:
            return f"@Block$${MemoryBlock(self.ref).name}[{index}]"
        elif (
            isinstance(self.ref, IRConst) and self.ref.constant() in MEMORY_BLOCK_VALUES
        ):
            return f"@Block$${MemoryBlock(self.ref.constant()).name}[{index}]"
        else:
            return f"@{self.ref}[{index}]"
