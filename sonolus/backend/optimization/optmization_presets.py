from sonolus.backend.optimization.aggregate_to_scalar import AggregateToScalar
from sonolus.backend.optimization.allocate import Allocate
from sonolus.backend.optimization.arithmetic_simplification import (
    ArithmeticSimplification,
)
from sonolus.backend.optimization.basic_dead_store_elimination import (
    BasicDeadStoreElimination,
)
from sonolus.backend.optimization.coalesce_flow import CoalesceFlow
from sonolus.backend.optimization.conditional_constant_propagation import (
    ConditionalConstantPropagation,
)
from sonolus.backend.optimization.basic_dead_code_elimination import (
    BasicDeadCodeElimination,
)

DEFAULT_OPTIMIZATION_PRESET = [
    ConditionalConstantPropagation(),
    CoalesceFlow(),
    ArithmeticSimplification(),
    AggregateToScalar(),
    BasicDeadCodeElimination(),
    BasicDeadStoreElimination(),
    Allocate(),
]
