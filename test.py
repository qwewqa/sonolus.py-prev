from __future__ import annotations

from typing import NamedTuple, Generic, TypeVar, Iterator

from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.evaluator import IREvaluator
from sonolus.backend.optimization.aggregate_to_scalar import AggregateToScalar
from sonolus.backend.optimization.basic_dead_store_elimination import (
    BasicDeadStoreElimination,
)
from sonolus.backend.optimization.check_non_unique import CheckNonUniqueVisitor
from sonolus.backend.optimization.coalesce_flow import CoalesceFlow
from sonolus.backend.optimization.conditional_constant_propagation import (
    ConditionalConstantPropagation,
)
from sonolus.backend.optimization.basic_dead_code_elimination import (
    BasicDeadCodeElimination,
)
from sonolus.backend.optimization.optimization_pass import run_optimization_passes
from sonolus.backend.optimization.optmization_presets import DEFAULT_OPTIMIZATION_PRESET
from sonolus.engine.statements.value import Transmute
from sonolus.std import *
from sonolus.std.debug import *
from sonolus.std.unsafe import *

T = TypeVar("T")


class RingBufferTypeVars(NamedTuple):
    T: type
    size: int


class RingBuffer(GenericStruct, Generic[T], type_vars=RingBufferTypeVars):
    read_index: Number
    write_index: Number
    size: Number
    values: Array[T, size]

    @classmethod
    @sono_function
    def empty(cls):
        result = cls.alloc()
        result.read_index @= 0
        result.write_index @= 0
        result.size @= 0
        return result

    @property
    @sono_function
    def is_empty(self) -> bool:
        return self.size == 0

    @generic_function
    @sono_function
    def read(self, _ret: T = New) -> T:
        if self.is_empty:
            return
        result = self.values[self.read_index]
        self.read_index += 1
        self.read_index %= self.type_vars.size
        self.size -= 1
        return result

    @generic_function
    @sono_function
    def write(self, value: T):
        if self.size >= self.type_vars.size:
            return
        self.values[self.write_index] @= value
        self.write_index += 1
        self.write_index %= self.type_vars.size
        self.size += 1

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError

    @sono_function
    def _iter_(self):
        return self

    @sono_function
    def _len_(self):
        return self.size

    @sono_function
    def _contained_type_(self):
        return self.type_vars.T

    @sono_function
    def _has_item_(self):
        return self.size > 0

    @sono_function
    def _item_(self):
        return self.values[self.read_index]

    @sono_function
    def _advance_(self):
        self.read_index += 1
        self.read_index %= self.type_vars.size
        self.size -= 1


@sono_function
def main(_ret: Number = New):
    arr = Array.of(2, 10, 4, 6, 8)
    arr = Filter(lambda x: 3 <= x <= 8, arr)
    arr = Map(lambda x: Point(1 / x, -x), arr)
    pt = Max(arr, key=lambda p: p.magnitude())
    DebugLog(pt.x)  # 0.125
    DebugLog(pt.y)  # -8.0


@sono_function(ast=False)
def adder(value):
    @sono_function
    def add(x):
        return x + value

    return add


@sono_function
def a():
    DebugLog(1)
    return True


@sono_function
def b():
    DebugLog(2)
    return True


@sono_function
def c():
    DebugLog(3)
    return False


def _DebugLog(x):
    print(x[0])
    return 0


print(get_generated_src(main))
compiled = compile_function(main)
print(visualize(compiled).mermaid_svg_url())
compiled = run_optimization_passes(
    compiled,
    DEFAULT_OPTIMIZATION_PRESET,
)
check = CheckNonUniqueVisitor()
for cfg_node in traverse_cfg(compiled):
    check.visit(cfg_node)
compiled = visualize(compiled)
print(compiled)
print(compiled.mermaid_svg_url())
# compiled = run_optimization_passes(compiled, [ConstantFolding(), SimplifyFlow()])
print(compiled.mermaid_img_url())
IREvaluator(
    allow_vars=True, initial_blocks={1: [0] * 256}, functions={"DebugLog": _DebugLog}
).evaluate(compiled)
