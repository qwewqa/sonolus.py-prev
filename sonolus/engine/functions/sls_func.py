import functools
import inspect
from types import FunctionType
from typing import Callable, TypeVar, get_type_hints, TYPE_CHECKING, Any

from sonolus.engine.functions.ast_function import process_ast_function
from sonolus.engine.statements.statement import Statement
from sonolus.engine.statements.value import Value

T = TypeVar("T", bound=Callable)


def sls_func(fn: T = None, *, ast: bool = True) -> T:
    def wrap(fn):
        return _lazy_process(fn, ast)

    if fn is None:
        return wrap

    return wrap(fn)


def _lazy_process(fn, ast):
    processed = None
    started = False

    @functools.wraps(fn)
    def get_processed():
        nonlocal processed
        nonlocal started
        if processed is None:
            if started:
                raise RuntimeError("Recursive function calls are not supported.")
            started = True
            if ast:
                processed = _process_function(process_ast_function(fn))
            else:
                processed = _process_function(fn)
        return processed

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        return get_processed()(*args, **kwargs)

    wrapped.__wrapped__ = fn
    wrapped._get_processed_ = get_processed

    return wrapped


class _New:
    """
    When used as a default function argument, causes a new value to be created by calling .new() on the
    parameter type whenever the default argument is used.
    """


New: Any = _New


def _process_function(fn):
    from sonolus.engine.statements.control_flow import Execute

    hints = get_type_hints(fn)
    signature = inspect.signature(fn)

    def get_converter(hint):
        if hasattr(hint, "_convert_"):
            return hint._convert_
        return lambda x: x

    ret_param = False
    converters = {}

    for param_name, parameter in signature.parameters.items():
        hint = hints.get(param_name)
        converters[param_name] = get_converter(hint)
        if param_name == "_ret":
            ret_param = True
        if parameter.default is New and not Value.is_value_class(hint):
            raise ValueError(
                "Parameters with defaults must be annotated with a Value type."
            )

    return_converter = get_converter(hints.get("return"))

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        for k, v in bound.arguments.items():
            if k not in hints:
                pass
            if v is New:
                bound.arguments[k] = hints[k].new()
        bound = signature.bind(*bound.args, **bound.kwargs)
        evaluated_arguments = []

        for name, value in bound.arguments.items():
            param = signature.parameters[name]
            converter = converters[name]
            match param.kind:
                case param.VAR_KEYWORD:
                    for kwarg_name, kwarg_value in value.items():
                        kwarg_value = converter(kwarg_value)
                        evaluated_arguments.append(kwarg_value)
                        value[kwarg_name] = kwarg_value
                case param.VAR_POSITIONAL:
                    converted = tuple(converter(v) for v in value)
                    bound.arguments[name] = converted
                    evaluated_arguments.extend(converted)
                case _:
                    converted = converter(value)
                    bound.arguments[name] = converted
                    evaluated_arguments.append(converted)

        evaluated_arguments = [
            arg for arg in evaluated_arguments if isinstance(arg, Statement)
        ]

        result = fn(*bound.args, **bound.kwargs)

        if ret_param:
            ret_value = bound.arguments["_ret"]
            return return_converter(Execute(*evaluated_arguments, result, ret_value))
        elif isinstance(result, FunctionType):

            @functools.wraps(result)
            def wrapper(*args, **kwargs):
                return return_converter(result(*args, **kwargs))

            wrapper._statement_ = Execute(*evaluated_arguments)
            return wrapper
        else:
            return return_converter(Execute(*evaluated_arguments, result))

    return wrapped


def convert_value(value: Statement | float | bool):
    match value:
        case Statement() as expr:
            return expr
        case bool() as boolean:
            from sonolus.engine.statements.primitive import Boolean

            return Boolean(boolean)
        case int() | float() as number:
            from sonolus.engine.statements.primitive import Number

            return Number(number)
        case _:
            return value
