import functools
import inspect
from types import FunctionType
from typing import Callable, TypeVar, get_type_hints, overload

from sonolus.scripting.internal.ast_function import process_ast_function
from sonolus.scripting.internal.statement import Statement
from sonolus.scripting.internal.value import convert_value

T = TypeVar("T", bound=Callable)


@overload
def sls_func(fn: T, *, ast: bool = True, return_parameter: str = None) -> T:
    pass


@overload
def sls_func(*, ast: bool = True, return_parameter: str = None) -> Callable[[T], T]:
    pass


def sls_func(fn=None, *, ast: bool = True, return_parameter: str = None):
    def wrap(fn):
        return _lazy_process(fn, ast, return_parameter)

    if fn is None:
        return wrap

    return wrap(fn)


def _lazy_process(fn, ast, return_parameter):
    processed = None
    started = False

    @functools.wraps(fn)
    def get_processed():
        nonlocal processed
        nonlocal started
        nonlocal return_parameter
        if processed is None:
            signature = inspect.signature(fn)
            if return_parameter is None:
                if "_ret" in signature.parameters:
                    return_parameter = "_ret"
            else:
                if return_parameter not in signature.parameters:
                    raise ValueError(
                        f"Return parameter {return_parameter} not found in function signature."
                    )
            if started:
                raise RuntimeError("Recursive function calls are not supported.")
            started = True
            if ast:
                processed = _process_function(
                    process_ast_function(fn, return_parameter), return_parameter
                )
            else:
                processed = _process_function(fn, return_parameter)
        return processed

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            f = get_processed()
        except Exception as e:
            raise ValueError(f"Error processing function {fn}.") from e
        return f(*args, **kwargs)

    wrapped.__wrapped__ = fn
    wrapped._get_processed_ = get_processed

    return wrapped


def _process_function(fn, return_parameter: str | None):
    from sonolus.scripting.internal.control_flow import Execute

    hints = get_type_hints(fn)
    signature = inspect.signature(fn)

    def get_converter(hint):
        if hasattr(hint, "_convert_"):
            return lambda x: convert_value(x, hint)
        return lambda x: x

    converters = {}

    for param_name, parameter in signature.parameters.items():
        hint = hints.get(param_name)
        if param_name == return_parameter and hint is None:
            hint = hints.get("return")
        converters[param_name] = get_converter(hint)

    return_converter = get_converter(hints.get("return"))

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
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

        if return_parameter is not None:
            ret_value = bound.arguments[return_parameter]
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


def convert_literal(value: Statement | float | bool):
    """
    Converts python literal floats and booleans to their respective Value types.
    Otherwise, returns the value as-is.
    """
    match value:
        case bool() as boolean:
            from sonolus.scripting.internal.primitive import Bool

            return Bool(boolean)
        case int() | float() as number:
            from sonolus.scripting.internal.primitive import Num

            return Num(number)
        case _:
            return value
