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
    "Equal": lambda a, b: a == b,
    "NotEqual": lambda a, b: a != b,
    "Greater": lambda a, b: a > b,
    "GreaterOr": lambda a, b: a >= b,
    "Less": lambda a, b: a < b,
    "LessOr": lambda a, b: a <= b,
    "Floor": lambda a: math.floor(a),
    "Ceil": lambda a: math.ceil(a),
    "Round": lambda a: round(a),
    "Trunc": lambda a: int(a),
    "Frac": lambda a: a % 1,
    "Min": lambda a, b: min(a, b),
    "Max": lambda a, b: max(a, b),
    "If": lambda a, b, c: b if a else c,
    "And": lambda *args: int(args and reduce(operator.and_, args)) or 1,
    "Or": lambda *args: int(args and reduce(operator.or_, args)) or 1,
    "Not": lambda a: int(not a),
    "Abs": lambda a: abs(a),
}
