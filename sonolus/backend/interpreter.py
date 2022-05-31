import functools
import operator
import random
from math import (
    floor,
    ceil,
    log,
    copysign,
    pi,
    sin,
    cos,
    tan,
    sinh,
    cosh,
    tanh,
    asin,
    atan2,
    atan,
    acos,
)
from typing import Callable

from sonolus.backend.cfg import CFG
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.evaluation import evaluate_statement
from sonolus.backend.ir import (
    TempRef,
    IRNode,
    IRGet,
    Ref,
    SSARef,
    IRConst,
    IRSet,
    IRComment,
    IRFunc,
)
from sonolus.backend.optimization.get_temp_ref_sizes import get_temp_ref_sizes
from sonolus.frontend.statement import Statement


class CFGInterpreter:
    def __init__(
        self,
        *,
        blocks: dict[TempRef | int, list[float]] = None,
        functions: dict[str, Callable[[list[float]], float]] = None,
        allow_uninitialized_reads: bool = False,
        seed=None,
    ):
        if functions is None:
            functions = {}
        if blocks is None:
            blocks = {}

        self.functions = functions
        self.blocks = blocks
        self.allow_uninitialized = allow_uninitialized_reads

        if seed is not None:
            self.random = random.Random(seed)
        else:
            self.random = random.Random()

    def run(self, cfg: CFG):
        cfg_node = cfg.entry_node
        edges = {
            node: {edge.condition: edge.to_node for edge in cfg.edges_by_from[node]}
            for node in traverse_cfg(cfg)
        }
        while True:
            for node in cfg_node.body:
                self.run_node(node)
            if cfg_node.test is None:
                test = 0
            else:
                test = self.run_node(cfg_node.test)
            targets = edges[cfg_node]
            if not targets:
                if cfg_node.is_exit:
                    return test
                else:
                    return 0
            elif test in targets:
                cfg_node = targets[test]
            elif None in targets:
                cfg_node = targets[None]
            else:
                return 0

    def run_node(self, node: IRNode) -> float:
        match node:
            case IRGet(location):
                ref = self.get_block(location.ref)
                index = int(location.base + self.run_node(location.offset))
                if self.allow_uninitialized:
                    if ref not in self.blocks:
                        self.blocks[ref] = [0] * (index + 1)
                    elif index >= len(self.blocks[ref]):
                        self.blocks[ref] += [0] * (index + 1 - len(self.blocks[ref]))
                return self.blocks[ref][index]
            case IRSet(location, value):
                ref = self.get_block(location.ref)
                index = int(location.base + self.run_node(location.offset))
                if self.allow_uninitialized:
                    if ref not in self.blocks:
                        self.blocks[ref] = [0] * (index + 1)
                    elif index >= len(self.blocks[ref]):
                        self.blocks[ref] += [0] * (index + 1 - len(self.blocks[ref]))
                self.blocks[ref][index] = self.run_node(value)
                return 0
            case IRFunc(name, args):
                if name in self.functions:
                    return self.functions[name]([self.run_node(arg) for arg in args])
                else:
                    return self.run_builtin(name, args)
            case IRComment():
                return 0
            case IRConst(value):
                return value

    def run_builtin(self, name: str, args: list[IRNode]) -> float:
        match name:
            case "Execute":
                args = [self.run_node(arg) for arg in args]
                return args[-1]
            case "Execute0":
                for arg in args:
                    self.run_node(arg)
                return 0
            case "If":
                if self.run_node(args[0]):
                    return self.run_node(args[1])
                else:
                    return self.run_node(args[2])
            case "Switch":
                test = self.run_node(args[0])
                for i in range(1, len(args), 2):
                    if test == self.run_node(args[i]):
                        return self.run_node(args[i + 1])
                return 0
            case "SwitchWithDefault":
                test = self.run_node(args[0])
                for i in range(1, len(args) - 1, 2):
                    if test == self.run_node(args[i]):
                        return self.run_node(args[i + 1])
                return self.run_node(args[-1])
            case "SwitchInteger":
                test = self.run_node(args[0])
                for i in range(1, len(args)):
                    if test == i:
                        return self.run_node(args[i])
                return 0
            case "SwitchIntegerWithDefault":
                test = self.run_node(args[0])
                for i in range(1, len(args) - 1):
                    if test == i:
                        return self.run_node(args[i])
                return self.run_node(args[-1])
            case "While":
                while self.run_node(args[0]):
                    self.run_node(args[1])
                return 0
            case "Add":
                return self.reduce_args(args, operator.add)
            case "Subtract":
                return self.reduce_args(args, operator.sub)
            case "Multiply":
                return self.reduce_args(args, operator.mul)
            case "Divide":
                return self.reduce_args(args, operator.truediv)
            case "Mod":
                return self.reduce_args(args, operator.mod)
            case "Power":
                return self.reduce_args(args, operator.pow)
            case "Log":
                return log(self.run_node(args[0]))
            case "Equal":
                return float(self.run_node(args[0]) == self.run_node(args[1]))
            case "NotEqual":
                return float(self.run_node(args[0]) != self.run_node(args[1]))
            case "Greater":
                return float(self.run_node(args[0]) > self.run_node(args[1]))
            case "GreaterOr":
                return float(self.run_node(args[0]) >= self.run_node(args[1]))
            case "Less":
                return float(self.run_node(args[0]) < self.run_node(args[1]))
            case "LessOr":
                return float(self.run_node(args[0]) <= self.run_node(args[1]))
            case "And":
                for arg in args:
                    if not self.run_node(arg):
                        return 0
                return 1
            case "Or":
                for arg in args:
                    if self.run_node(arg):
                        return 1
                return 0
            case "Not":
                return int(not self.run_node(args[0]))
            case "Min":
                return min(self.run_node(arg) for arg in args)
            case "Max":
                return max(self.run_node(arg) for arg in args)
            case "Abs":
                return abs(self.run_node(args[0]))
            case "Sign":
                return copysign(1, self.run_node(args[0]))
            case "Ceil":
                return ceil(self.run_node(args[0]))
            case "Floor":
                return floor(self.run_node(args[0]))
            case "Round":
                return round(self.run_node(args[0]))
            case "Frac":
                return self.run_node(args[0]) % 1
            case "Trunc":
                return int(self.run_node(args[0]))
            case "Degree":
                return self.run_node(args[0]) * 180 / pi
            case "Radian":
                return self.run_node(args[0]) * pi / 180
            case "Sin":
                return sin(self.run_node(args[0]))
            case "Cos":
                return cos(self.run_node(args[0]))
            case "Tan":
                return tan(self.run_node(args[0]))
            case "Sinh":
                return sinh(self.run_node(args[0]))
            case "Cosh":
                return cosh(self.run_node(args[0]))
            case "Tanh":
                return tanh(self.run_node(args[0]))
            case "Arcsin":
                return asin(self.run_node(args[0]))
            case "Arccos":
                return acos(self.run_node(args[0]))
            case "Arctan":
                return atan(self.run_node(args[0]))
            case "Arctan2":
                return atan2(self.run_node(args[0]), self.run_node(args[1]))
            case "Clamp":
                x, a, b = [self.run_node(arg) for arg in args]
                return max(min(x, b), a)
            case "Lerp":
                a, b, x = [self.run_node(arg) for arg in args]
                return a + x * (b - a)
            case "LerpClamped":
                a, b, x = [self.run_node(arg) for arg in args]
                return a + min(max(x, 0), 1) * (b - a)
            case "Unlerp":
                a, b, x = [self.run_node(arg) for arg in args]
                return (x - a) / (b - a)
            case "UnlerpClamped":
                a, b, x = [self.run_node(arg) for arg in args]
                return min(max((x - a) / (b - a), 0), 1)
            case "Remap":
                a, b, c, d, x = [self.run_node(arg) for arg in args]
                return c + (d - c) * ((x - a) / (b - a))
            case "RemapClamped":
                a, b, c, d, x = [self.run_node(arg) for arg in args]
                return c + (d - c) * min(max((x - a) / (b - a), 0), 1)
            case "Smoothstep":
                a, b, x = [self.run_node(arg) for arg in args]
                if x <= 0:
                    return a
                elif x >= 1:
                    return b
                else:
                    return a + (b - a) * (x * x * (3 - 2 * x))
            case "Random":
                lo, hi = [self.run_node(arg) for arg in args]
                return random.uniform(lo, hi)
            case "RandomInteger":
                lo, hi = [self.run_node(arg) for arg in args]
                return random.randrange(lo, hi)
            case "Judge":
                src, dst, min1, max1, min2, max2, min3, max3 = [
                    self.run_node(arg) for arg in args
                ]
                diff = src - dst
                if min1 <= diff <= max1:
                    return 1
                elif min2 <= diff <= max2:
                    return 2
                elif min3 <= diff <= max3:
                    return 3
                else:
                    return 0
            case "JudgeSimple":
                src, dst, max1, max2, max3 = [self.run_node(arg) for arg in args]
                diff = abs(src - dst)
                if diff <= max1:
                    return 1
                elif diff <= max2:
                    return 2
                elif diff <= max3:
                    return 3
                else:
                    return 0
            case _:
                raise ValueError(f"Unknown function: {name}.")

    def reduce_args(
        self, args: list[IRNode], op: Callable[[float, float], float]
    ) -> float:
        args = [self.run_node(arg) for arg in args]
        return functools.reduce(op, args)

    def get_block(self, ref: Ref):
        match ref:
            case TempRef() | int():
                return ref
            case IRNode():
                return self.run_node(ref)
            case SSARef():
                raise NotImplementedError("SSA references not supported.")
            case _:
                raise ValueError(f"Unexpected reference type: {ref}.")


def run_statement(
    statement: Statement, *, blocks: dict[TempRef | int, list[float]] = None, **kwargs
):
    return run_cfg(evaluate_statement(statement), blocks=blocks, **kwargs)


def run_cfg(cfg: CFG, *, blocks: dict[TempRef | int, list[float]] = None, **kwargs):
    if blocks is None:
        blocks = {}
    for ref, size in get_temp_ref_sizes(cfg).items():
        if ref not in blocks:
            blocks[ref] = [0] * size
    interpreter = CFGInterpreter(blocks=blocks, **kwargs)
    return interpreter.run(cfg)


def run_ir(ir: IRNode, *, blocks: dict[TempRef | int, list[float]] = None, **kwargs):
    if blocks is None:
        blocks = {}
    interpreter = CFGInterpreter(blocks=blocks, **kwargs)
    return interpreter.run_node(ir)
