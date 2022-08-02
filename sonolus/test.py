from typing import ParamSpec, TypeVar, Callable, Any

from sonolus.backend.interpreter import run_value
from sonolus.scripting.internal.primitive import invoke_builtin
from sonolus.scripting.internal.value import Value
from sonolus.scripting.debug import debug_compilation

__all__ = (
    "run_function",
    "invoke_builtin",
    "dump_value",
)

T = TypeVar("T", bound=Value)
P = ParamSpec("P")


def run_function(
    fn: Callable[P, T],
    /,
    *args: P.args,
    _blocks_: dict | None = None,
    **kwargs: P.kwargs,
) -> T:
    with debug_compilation():
        return run_value(fn(*args, **kwargs), blocks=_blocks_)


def dump_value(value: Value) -> Any:
    return value._dump_()
