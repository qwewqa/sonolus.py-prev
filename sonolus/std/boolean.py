from sonolus.engine.functions.sono_function import sono_function
from sonolus.engine.statements.primitive import Boolean, invoke_builtin

__all__ = (
    "Boolean",
    "And",
    "Or",
    "Not",
)


@sono_function(ast=False)
def And(*args: Boolean) -> Boolean:
    return invoke_builtin("And", [*args], Boolean)


@sono_function(ast=False)
def Or(*args: Boolean) -> Boolean:
    return invoke_builtin("Or", [*args], Boolean)


@sono_function(ast=False)
def Not(b: Boolean) -> Boolean:
    return invoke_builtin("Not", [b], Boolean)
