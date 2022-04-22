from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.primitive import Bool, invoke_builtin

__all__ = (
    "Bool",
    "And",
    "Or",
    "Not",
)


@sls_func(ast=False)
def And(*args: Bool) -> Bool:
    return invoke_builtin("And", [*args], Bool)


@sls_func(ast=False)
def Or(*args: Bool) -> Bool:
    return invoke_builtin("Or", [*args], Bool)


@sls_func(ast=False)
def Not(b: Bool) -> Bool:
    return invoke_builtin("Not", [b], Bool)
