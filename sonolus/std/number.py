import math

from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.primitive import Num, invoke_builtin

__all__ = (
    "Num",
    "Log",
    "Abs",
    "Sign",
    "Ceil",
    "Floor",
    "Round",
    "Frac",
    "Trunc",
    "Degree",
    "Radian",
    "Sin",
    "Cos",
    "Tan",
    "Sinh",
    "Cosh",
    "Tanh",
    "Arcsin",
    "Arccos",
    "Arctan",
    "Arctan2",
    "Clamp",
    "Lerp",
    "LerpClamped",
    "Unlerp",
    "UnlerpClamped",
    "Remap",
    "RemapClamped",
    "Smoothstep",
    "Random",
    "RandomInteger",
    "Judge",
    "JudgeSimple",
    "Pi",
)


@sls_func(ast=False)
def Log(n: Num, /) -> Num:
    return invoke_builtin("Log", [n], Num)


@sls_func(ast=False)
def NumMin(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Min", [a, b], Num)


@sls_func(ast=False)
def NumMax(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Max", [a, b], Num)


@sls_func(ast=False)
def Abs(n: Num, /) -> Num:
    return invoke_builtin("Abs", [n], Num)


@sls_func(ast=False)
def Sign(n: Num, /) -> Num:
    return invoke_builtin("Sign", [n], Num)


@sls_func(ast=False)
def Ceil(n: Num, /) -> Num:
    return invoke_builtin("Ceil", [n], Num)


@sls_func(ast=False)
def Floor(n: Num, /) -> Num:
    return invoke_builtin("Floor", [n], Num)


@sls_func(ast=False)
def Round(n: Num, /) -> Num:
    return invoke_builtin("Round", [n], Num)


@sls_func(ast=False)
def Frac(n: Num, /) -> Num:
    return invoke_builtin("Frac", [n], Num)


@sls_func(ast=False)
def Trunc(n: Num, /) -> Num:
    return invoke_builtin("Trunc", [n], Num)


@sls_func(ast=False)
def Degree(n: Num, /) -> Num:
    return invoke_builtin("Degree", [n], Num)


@sls_func(ast=False)
def Radian(n: Num, /) -> Num:
    return invoke_builtin("Radian", [n], Num)


@sls_func(ast=False)
def Sin(n: Num, /) -> Num:
    return invoke_builtin("Sin", [n], Num)


@sls_func(ast=False)
def Cos(n: Num, /) -> Num:
    return invoke_builtin("Cos", [n], Num)


@sls_func(ast=False)
def Tan(n: Num, /) -> Num:
    return invoke_builtin("Tan", [n], Num)


@sls_func(ast=False)
def Sinh(n: Num, /) -> Num:
    return invoke_builtin("Sinh", [n], Num)


@sls_func(ast=False)
def Cosh(n: Num, /) -> Num:
    return invoke_builtin("Cosh", [n], Num)


@sls_func(ast=False)
def Tanh(n: Num, /) -> Num:
    return invoke_builtin("Tanh", [n], Num)


@sls_func(ast=False)
def Arcsin(n: Num, /) -> Num:
    return invoke_builtin("Arcsin", [n], Num)


@sls_func(ast=False)
def Arccos(n: Num, /) -> Num:
    return invoke_builtin("Arccos", [n], Num)


@sls_func(ast=False)
def Arctan(n: Num, /) -> Num:
    return invoke_builtin("Arctan", [n], Num)


@sls_func(ast=False)
def Arctan2(y: Num, x: Num) -> Num:
    return invoke_builtin("Arctan2", [y, x], Num)


@sls_func(ast=False)
def Clamp(x: Num, a: Num, b: Num, /) -> Num:
    return invoke_builtin("Clamp", [x, a, b], Num)


@sls_func(ast=False)
def Lerp(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Lerp", [a, b, x], Num)


@sls_func(ast=False)
def LerpClamped(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("LerpClamped", [a, b, x], Num)


@sls_func(ast=False)
def Unlerp(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Unlerp", [a, b, x], Num)


@sls_func(ast=False)
def UnlerpClamped(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("UnlerpClamped", [a, b, x], Num)


@sls_func(ast=False)
def Remap(a: Num, b: Num, c: Num, d: Num, x: Num, /) -> Num:
    return invoke_builtin("Remap", [a, b, c, d, x], Num)


@sls_func(ast=False)
def RemapClamped(a: Num, b: Num, c: Num, d: Num, x: Num, /) -> Num:
    return invoke_builtin("RemapClamped", [a, b, c, d, x], Num)


@sls_func(ast=False)
def Smoothstep(a: Num, b: Num, x: Num, /) -> Num:
    return invoke_builtin("Smoothstep", [a, b, x], Num)


@sls_func(ast=False)
def Random(a: Num = 0, b: Num = 1, /) -> Num:
    return invoke_builtin("Random", [a, b], Num)


@sls_func(ast=False)
def RandomInteger(a: Num, b: Num, /) -> Num:
    return invoke_builtin("RandomInteger", [a, b], Num)


@sls_func(ast=False)
def Judge(
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
def JudgeSimple(src: Num, dst: Num, max1: Num, max2: Num, max3: Num):
    return invoke_builtin("Judget", [src, dst, max1, max2, max3])


Pi = math.pi
