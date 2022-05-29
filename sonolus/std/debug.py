from sonolus.backend.callback import DEBUG_CALLBACK_TYPE
from sonolus.backend.cfg import CFG
from sonolus.backend.evaluation import evaluate_statement, CompilationInfo
from sonolus.backend.graph import get_flat_cfg
from sonolus.backend.ir import IRComment
from sonolus.frontend.primitive import Num, Bool, invoke_builtin
from sonolus.frontend.statement import Statement
from sonolus.frontend.void import Void
from sonolus.std.function import sls_func

__all__ = (
    "IsDebug",
    "DebugPause",
    "DebugLog",
    "Comment",
    "get_generated_src",
    "debug_compilation",
    "evaluate_function",
    "visualize",
)


@sls_func(ast=False)
def IsDebug() -> Bool:
    return invoke_builtin("IsDebug", [], Bool)


@sls_func(ast=False)
def DebugPause() -> Void:
    return invoke_builtin("DebugPause", [])


@sls_func(ast=False)
def DebugLog(n: Num | Bool, /) -> Void:
    if isinstance(n, (int, float, bool)):
        n = Num(n)
    if not isinstance(n, (Num, Bool)):
        raise TypeError(f"Expected number or boolean, got {type(n)}.")
    return invoke_builtin("DebugLog", [n])


def Comment(message) -> Void:
    return Void(IRComment(str(message)))


def get_generated_src(fn, /):
    return fn._get_processed_()._generated_src_


def debug_compilation():
    return CompilationInfo(DEBUG_CALLBACK_TYPE, {})


def evaluate_function(fn, /):
    """
    Compiles the given function and returns the result.
    The function may be standalone or a callback, but must not have any parameters without a default value,
    excluding the self parameter for callbacks.
    """
    with debug_compilation():
        if isinstance(fn, Statement):
            return evaluate_statement(fn)
        elif callable(fn) and hasattr(fn, "_script_"):
            return evaluate_statement(fn(fn._script_.create_for_evaluation()))
        elif callable(fn):
            return evaluate_statement(fn())
        else:
            raise TypeError("Unsupported function.")


def visualize(fn, /):
    if isinstance(fn, CFG):
        return get_flat_cfg(fn)
    return get_flat_cfg(evaluate_function(fn))
