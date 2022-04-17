from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.primitive import Boolean, invoke_builtin

__all__ = (
    "Boolean",
    "And",
    "Or",
    "Not",
)


@sls_func(ast=False)
def And(*args: Boolean) -> Boolean:
    return invoke_builtin("And", [*args], Boolean)


@sls_func(ast=False)
def Or(*args: Boolean) -> Boolean:
    return invoke_builtin("Or", [*args], Boolean)


@sls_func(ast=False)
def Not(b: Boolean) -> Boolean:
    return invoke_builtin("Not", [b], Boolean)
