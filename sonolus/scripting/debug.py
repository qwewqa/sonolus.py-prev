from sonolus.backend.callback import DEBUG_CALLBACK_TYPE
from sonolus.backend.cfg import CFG
from sonolus.backend.evaluation import evaluate_statement, CompilationInfo
from sonolus.backend.graph import get_flat_cfg
from sonolus.backend.ir import IRComment, IRFunc
from sonolus.scripting.internal.primitive import Num, Bool, invoke_builtin
from sonolus.scripting.internal.statement import Statement
from sonolus.scripting.internal.void import Void
from sonolus.scripting.function import sls_func

__all__ = (
    "is_debug",
    "debug_pause",
    "debug_log",
    "comment",
    "get_generated_src",
    "debug_compilation",
    "evaluate_function",
    "visualize",
)


is_debug: Bool = Bool._create_(IRFunc("IsDebug", []))._set_static_()


@sls_func(ast=False)
def debug_pause() -> Void:
    return invoke_builtin("DebugPause", [])


@sls_func(ast=False)
def debug_log(n: Num | Bool, /) -> Void:
    if isinstance(n, (int, float, bool)):
        n = Num(n)
    if not isinstance(n, (Num, Bool)):
        raise TypeError(f"Expected number or boolean, got {type(n)}.")
    return invoke_builtin("DebugLog", [n])


def comment(message) -> Void:
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
