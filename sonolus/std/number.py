import math

from sonolus.frontend.sls_func import sls_func
from sonolus.frontend.primitive import Num, invoke_builtin

__all__ = (
    "Num",
    "log",
    "sign",
    "ceil",
    "floor",
    "frac",
    "trunc",
    "degree",
    "radian",
    "sin",
    "cos",
    "tan",
    "sinh",
    "cosh",
    "Tanh",
    "asin",
    "acos",
    "atan",
    "atan2",
    "clamp",
    "lerp",
    "lerp_clamped",
    "unlerp",
    "unlerp_clamped",
    "remap",
    "remap_clamped",
    "smoothstep",
    "random",
    "random_integer",
    "judge",
    "judge_simple",
    "pi",
)


@sls_func(ast=False)
def log(n: Num, /) -> Num:
    return invoke_builtin("Log", [n], Num)


@sls_func(ast=False)
def num_min(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Min", [a, b], Num)


@sls_func(ast=False)
def num_max(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Max", [a, b], Num)


@sls_func(ast=False)
def sign(n: Num, /) -> Num:
    return invoke_builtin("Sign", [n], Num)


@sls_func(ast=False)
def ceil(n: Num, /) -> Num:
    return invoke_builtin("Ceil", [n], Num)


@sls_func(ast=False)
def floor(n: Num, /) -> Num:
    return invoke_builtin("Floor", [n], Num)


@sls_func(ast=False)
def frac(n: Num, /) -> Num:
    return invoke_builtin("Frac", [n], Num)


@sls_func(ast=False)
def trunc(n: Num, /) -> Num:
    return invoke_builtin("Trunc", [n], Num)


@sls_func(ast=False)
def degree(n: Num, /) -> Num:
    return invoke_builtin("Degree", [n], Num)


@sls_func(ast=False)
def radian(n: Num, /) -> Num:
    return invoke_builtin("Radian", [n], Num)


@sls_func(ast=False)
def sin(n: Num, /) -> Num:
    return invoke_builtin("Sin", [n], Num)


@sls_func(ast=False)
def cos(n: Num, /) -> Num:
    return invoke_builtin("Cos", [n], Num)


@sls_func(ast=False)
def tan(n: Num, /) -> Num:
    return invoke_builtin("Tan", [n], Num)


@sls_func(ast=False)
def sinh(n: Num, /) -> Num:
    return invoke_builtin("Sinh", [n], Num)


@sls_func(ast=False)
def cosh(n: Num, /) -> Num:
    return invoke_builtin("Cosh", [n], Num)


@sls_func(ast=False)
def Tanh(n: Num, /) -> Num:
    return invoke_builtin("Tanh", [n], Num)


@sls_func(ast=False)
def asin(n: Num, /) -> Num:
    return invoke_builtin("Arcsin", [n], Num)


@sls_func(ast=False)
def acos(n: Num, /) -> Num:
    return invoke_builtin("Arccos", [n], Num)


@sls_func(ast=False)
def atan(n: Num, /) -> Num:
    return invoke_builtin("Arctan", [n], Num)


@sls_func(ast=False)
def atan2(y: Num, x: Num) -> Num:
    return invoke_builtin("Arctan2", [y, x], Num)


@sls_func(ast=False)
def clamp(x: Num, a: Num, b: Num, /) -> Num:
    return invoke_builtin("Clamp", [x, a, b], Num)


@sls_func(ast=False)
def lerp(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Lerp", [a, b, x], Num)


@sls_func(ast=False)
def lerp_clamped(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("LerpClamped", [a, b, x], Num)


@sls_func(ast=False)
def unlerp(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Unlerp", [a, b, x], Num)


@sls_func(ast=False)
def unlerp_clamped(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("UnlerpClamped", [a, b, x], Num)


@sls_func(ast=False)
def remap(a: Num, b: Num, c: Num, d: Num, x: Num, /) -> Num:
    return invoke_builtin("Remap", [a, b, c, d, x], Num)


@sls_func(ast=False)
def remap_clamped(a: Num, b: Num, c: Num, d: Num, x: Num, /) -> Num:
    return invoke_builtin("RemapClamped", [a, b, c, d, x], Num)


@sls_func(ast=False)
def smoothstep(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Smoothstep", [a, b, x], Num)


@sls_func(ast=False)
def random(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Random", [a, b], Num)


@sls_func(ast=False)
def random_integer(a: Num, b: Num, /) -> Num:
    return invoke_builtin("RandomInteger", [a, b], Num)


@sls_func(ast=False)
def judge(
    src: Num,
    dst: Num,
    min1: Num,
    max1: Num,
    min2: Num,
    max2: Num,
    min3: Num,
    max3: Num,
) -> Num:
    return invoke_builtin("Judge", [src, dst, min1, max1, min2, max2, min3, max3], Num)


@sls_func(ast=False)
def judge_simple(src: Num, dst: Num, max1: Num, max2: Num, max3: Num) -> Num:
    return invoke_builtin("JudgeSimple", [src, dst, max1, max2, max3], Num)


pi = math.pi
