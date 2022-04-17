import math

from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.primitive import Number, invoke_builtin

__all__ = (
    "Number",
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
def Log(n: Number, /) -> Number:
    return invoke_builtin("Log", [n], Number)


@sls_func(ast=False)
def NumMin(a: Number = 0, b: Number = 1, /) -> Number:
    return invoke_builtin("Min", [a, b], Number)


@sls_func(ast=False)
def NumMax(a: Number = 0, b: Number = 1, /) -> Number:
    return invoke_builtin("Max", [a, b], Number)


@sls_func(ast=False)
def Abs(n: Number, /) -> Number:
    return invoke_builtin("Abs", [n], Number)


@sls_func(ast=False)
def Sign(n: Number, /) -> Number:
    return invoke_builtin("Sign", [n], Number)


@sls_func(ast=False)
def Ceil(n: Number, /) -> Number:
    return invoke_builtin("Ceil", [n], Number)


@sls_func(ast=False)
def Floor(n: Number, /) -> Number:
    return invoke_builtin("Floor", [n], Number)


@sls_func(ast=False)
def Round(n: Number, /) -> Number:
    return invoke_builtin("Round", [n], Number)


@sls_func(ast=False)
def Frac(n: Number, /) -> Number:
    return invoke_builtin("Frac", [n], Number)


@sls_func(ast=False)
def Trunc(n: Number, /) -> Number:
    return invoke_builtin("Trunc", [n], Number)


@sls_func(ast=False)
def Degree(n: Number, /) -> Number:
    return invoke_builtin("Degree", [n], Number)


@sls_func(ast=False)
def Radian(n: Number, /) -> Number:
    return invoke_builtin("Radian", [n], Number)


@sls_func(ast=False)
def Sin(n: Number, /) -> Number:
    return invoke_builtin("Sin", [n], Number)


@sls_func(ast=False)
def Cos(n: Number, /) -> Number:
    return invoke_builtin("Cos", [n], Number)


@sls_func(ast=False)
def Tan(n: Number, /) -> Number:
    return invoke_builtin("Tan", [n], Number)


@sls_func(ast=False)
def Sinh(n: Number, /) -> Number:
    return invoke_builtin("Sinh", [n], Number)


@sls_func(ast=False)
def Cosh(n: Number, /) -> Number:
    return invoke_builtin("Cosh", [n], Number)


@sls_func(ast=False)
def Tanh(n: Number, /) -> Number:
    return invoke_builtin("Tanh", [n], Number)


@sls_func(ast=False)
def Arcsin(n: Number, /) -> Number:
    return invoke_builtin("Arcsin", [n], Number)


@sls_func(ast=False)
def Arccos(n: Number, /) -> Number:
    return invoke_builtin("Arccos", [n], Number)


@sls_func(ast=False)
def Arctan(n: Number, /) -> Number:
    return invoke_builtin("Arctan", [n], Number)


@sls_func(ast=False)
def Arctan2(y: Number, x: Number) -> Number:
    return invoke_builtin("Arctan2", [y, x], Number)


@sls_func(ast=False)
def Clamp(x: Number, a: Number, b: Number, /) -> Number:
    return invoke_builtin("Clamp", [x, a, b], Number)


@sls_func(ast=False)
def Lerp(a: Number, b: Number, x: Number, /) -> Number:
    return invoke_builtin("Lerp", [a, b, x], Number)


@sls_func(ast=False)
def LerpClamped(a: Number, b: Number, x: Number, /) -> Number:
    return invoke_builtin("LerpClamped", [a, b, x], Number)


@sls_func(ast=False)
def Unlerp(a: Number, b: Number, x: Number, /) -> Number:
    return invoke_builtin("Unlerp", [a, b, x], Number)


@sls_func(ast=False)
def UnlerpClamped(a: Number, b: Number, x: Number, /) -> Number:
    return invoke_builtin("UnlerpClamped", [a, b, x], Number)


@sls_func(ast=False)
def Remap(a: Number, b: Number, c: Number, d: Number, x: Number, /) -> Number:
    return invoke_builtin("Remap", [a, b, c, d, x], Number)


@sls_func(ast=False)
def RemapClamped(a: Number, b: Number, c: Number, d: Number, x: Number, /) -> Number:
    return invoke_builtin("RemapClamped", [a, b, c, d, x], Number)


@sls_func(ast=False)
def Smoothstep(a: Number, b: Number, x: Number, /) -> Number:
    return invoke_builtin("Smoothstep", [a, b, x], Number)


@sls_func(ast=False)
def Random(a: Number = 0, b: Number = 1, /) -> Number:
    return invoke_builtin("Random", [a, b], Number)


@sls_func(ast=False)
def RandomInteger(a: Number, b: Number, /) -> Number:
    return invoke_builtin("RandomInteger", [a, b], Number)


@sls_func(ast=False)
def Judge(
    src: Number,
    dst: Number,
    min1: Number,
    max1: Number,
    min2: Number,
    max2: Number,
    min3: Number,
    max3: Number,
) -> Number:
    return invoke_builtin(
        "Judge", [src, dst, min1, max1, min2, max2, min3, max3], Number
    )


@sls_func(ast=False)
def JudgeSimple(src: Number, dst: Number, max1: Number, max2: Number, max3: Number):
    return invoke_builtin("Judget", [src, dst, max1, max2, max3])


Pi = math.pi
