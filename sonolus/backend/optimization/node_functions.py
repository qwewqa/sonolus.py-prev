import math
import operator
from functools import reduce

constant_functions = {
    "Add": lambda *args: (args and reduce(operator.add, args)) or 0,
    "Subtract": lambda *args: (args and reduce(operator.sub, args)) or 0,
    "Multiply": lambda *args: (args and reduce(operator.mul, args)) or 0,
    "Divide": lambda *args: (args and reduce(operator.truediv, args)) or 0,
    "Mod": lambda *args: (args and reduce(operator.mod, args)) or 0,
    "Power": lambda *args: (args and reduce(operator.pow, args)) or 0,
    "Equal": lambda a, b: float(a == b),
    "NotEqual": lambda a, b: float(a != b),
    "Greater": lambda a, b: float(a > b),
    "GreaterOr": lambda a, b: float(a >= b),
    "Less": lambda a, b: float(a < b),
    "LessOr": lambda a, b: float(a <= b),
    "Floor": lambda a: math.floor(a),
    "Ceil": lambda a: math.ceil(a),
    "Round": lambda a: round(a),
    "Trunc": lambda a: int(a),
    "Frac": lambda a: a % 1,
    "Min": lambda a, b: min(a, b),
    "Max": lambda a, b: max(a, b),
    "If": lambda a, b, c: b if a else c,
    "And": lambda *args: float(bool(reduce(lambda a, b: a and b, args))) if args else 1,
    "Or": lambda *args: float(bool(reduce(lambda a, b: a or b, args))) if args else 0,
    "Not": lambda a: int(not a),
    "Abs": lambda a: abs(a),
}
