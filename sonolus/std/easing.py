from sonolus.frontend.primitive import invoke_builtin, Num
from sonolus.std.function import sls_func

__all__ = (
    "ease_in_sine",
    "ease_in_quad",
    "ease_in_cubic",
    "ease_in_quart",
    "ease_in_quint",
    "ease_in_expo",
    "ease_in_circ",
    "ease_in_back",
    "ease_in_elastic",
    "ease_out_sine",
    "ease_out_quad",
    "ease_out_cubic",
    "ease_out_quart",
    "ease_out_quint",
    "ease_out_expo",
    "ease_out_circ",
    "ease_out_back",
    "ease_out_elastic",
    "ease_in_out_sine",
    "ease_in_out_quad",
    "ease_in_out_cubic",
    "ease_in_out_quart",
    "ease_in_out_quint",
    "ease_in_out_expo",
    "ease_in_out_circ",
    "ease_in_out_back",
    "ease_in_out_elastic",
    "ease_out_in_sine",
    "ease_out_in_quad",
    "ease_out_in_cubic",
    "ease_out_in_quart",
    "ease_out_in_quint",
    "ease_out_in_expo",
    "ease_out_in_circ",
    "ease_out_in_back",
    "ease_out_in_elastic",
)


@sls_func(ast=False)
def ease_in_sine(n: Num, /) -> Num:
    return invoke_builtin("EaseInSine", [n], Num)


@sls_func(ast=False)
def ease_in_quad(n: Num, /) -> Num:
    return invoke_builtin("EaseInQuad", [n], Num)


@sls_func(ast=False)
def ease_in_cubic(n: Num, /) -> Num:
    return invoke_builtin("EaseInCubic", [n], Num)


@sls_func(ast=False)
def ease_in_quart(n: Num, /) -> Num:
    return invoke_builtin("EaseInQuart", [n], Num)


@sls_func(ast=False)
def ease_in_quint(n: Num, /) -> Num:
    return invoke_builtin("EaseInQuint", [n], Num)


@sls_func(ast=False)
def ease_in_expo(n: Num, /) -> Num:
    return invoke_builtin("EaseInExpo", [n], Num)


@sls_func(ast=False)
def ease_in_circ(n: Num, /) -> Num:
    return invoke_builtin("EaseInCirc", [n], Num)


@sls_func(ast=False)
def ease_in_back(n: Num, /) -> Num:
    return invoke_builtin("EaseInBack", [n], Num)


@sls_func(ast=False)
def ease_in_elastic(n: Num, /) -> Num:
    return invoke_builtin("EaseInElastic", [n], Num)


@sls_func(ast=False)
def ease_out_sine(n: Num, /) -> Num:
    return invoke_builtin("EaseOutSine", [n], Num)


@sls_func(ast=False)
def ease_out_quad(n: Num, /) -> Num:
    return invoke_builtin("EaseOutQuad", [n], Num)


@sls_func(ast=False)
def ease_out_cubic(n: Num, /) -> Num:
    return invoke_builtin("EaseOutCubic", [n], Num)


@sls_func(ast=False)
def ease_out_quart(n: Num, /) -> Num:
    return invoke_builtin("EaseOutQuart", [n], Num)


@sls_func(ast=False)
def ease_out_quint(n: Num, /) -> Num:
    return invoke_builtin("EaseOutQuint", [n], Num)


@sls_func(ast=False)
def ease_out_expo(n: Num, /) -> Num:
    return invoke_builtin("EaseOutExpo", [n], Num)


@sls_func(ast=False)
def ease_out_circ(n: Num, /) -> Num:
    return invoke_builtin("EaseOutCirc", [n], Num)


@sls_func(ast=False)
def ease_out_back(n: Num, /) -> Num:
    return invoke_builtin("EaseOutBack", [n], Num)


@sls_func(ast=False)
def ease_out_elastic(n: Num, /) -> Num:
    return invoke_builtin("EaseOutElastic", [n], Num)


@sls_func(ast=False)
def ease_in_out_sine(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutSine", [n], Num)


@sls_func(ast=False)
def ease_in_out_quad(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutQuad", [n], Num)


@sls_func(ast=False)
def ease_in_out_cubic(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutCubic", [n], Num)


@sls_func(ast=False)
def ease_in_out_quart(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutQuart", [n], Num)


@sls_func(ast=False)
def ease_in_out_quint(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutQuint", [n], Num)


@sls_func(ast=False)
def ease_in_out_expo(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutExpo", [n], Num)


@sls_func(ast=False)
def ease_in_out_circ(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutCirc", [n], Num)


@sls_func(ast=False)
def ease_in_out_back(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutBack", [n], Num)


@sls_func(ast=False)
def ease_in_out_elastic(n: Num, /) -> Num:
    return invoke_builtin("EaseInOutElastic", [n], Num)


@sls_func(ast=False)
def ease_out_in_sine(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInSine", [n], Num)


@sls_func(ast=False)
def ease_out_in_quad(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInQuad", [n], Num)


@sls_func(ast=False)
def ease_out_in_cubic(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInCubic", [n], Num)


@sls_func(ast=False)
def ease_out_in_quart(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInQuart", [n], Num)


@sls_func(ast=False)
def ease_out_in_quint(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInQuint", [n], Num)


@sls_func(ast=False)
def ease_out_in_expo(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInExpo", [n], Num)


@sls_func(ast=False)
def ease_out_in_circ(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInCirc", [n], Num)


@sls_func(ast=False)
def ease_out_in_back(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInBack", [n], Num)


@sls_func(ast=False)
def ease_out_in_elastic(n: Num, /) -> Num:
    return invoke_builtin("EaseOutInElastic", [n], Num)
