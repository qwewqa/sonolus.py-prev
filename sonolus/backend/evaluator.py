from __future__ import annotations

import functools
import operator
import warnings
from math import floor, ceil
from typing import Optional, Callable

import sonolus.backend.ir as ir
import sonolus.backend.graph as graph


class IREvaluator:
    def __init__(
        self,
        *,
        allow_vars=False,
        initial_blocks: dict = None,
        functions: dict[str, Callable[[list[float]], float | None]] = None,
    ):
        if functions is None:
            functions = {}

        self.allow_vars = allow_vars
        self.functions = functions
        if allow_vars:
            self.blocks = initial_blocks or {}
        else:
            self.blocks = None

    def evaluate(self, node: ir.IRNode | graph.FlatCfg) -> Optional[float]:
        """Evaluates the given node and returns a float if it can be evaluated and None otherwise."""
        match node:
            case graph.FlatCfg(nodes):
                index = 0
                while 0 <= index < len(nodes) and float(index).is_integer():
                    graph_node: graph.FlatCfgNode = nodes[index]
                    for node in graph_node.body:
                        result = self.evaluate(node)
                        if result is None:
                            return None
                    match graph_node:
                        case graph.FlatCfgNode(test=test, target={**targets}):
                            test_result = self.evaluate(test)
                            if test_result not in targets:
                                if None in targets:
                                    index = targets[None]
                                else:
                                    return None
                            else:
                                index = targets[test_result]
                        case graph.FlatCfgNode(test=None, target=None):
                            return 0
                        case graph.FlatCfgNode(
                            test=test, target=target
                        ) if target is not None:
                            index = target
                        case graph.FlatCfgNode(test=test, target=None):
                            return self.evaluate(test)
                        case _:
                            raise ValueError(
                                f"Unexpected graph node configuration: {graph_node}."
                            )
                return None
            case ir.IRGet(location):
                if not self.allow_vars:
                    return None
                ref = location.ref
                offset = self.evaluate(location.offset)
                if offset is None:
                    return None
                if ref not in self.blocks:
                    return None
                if location.span is not None and not (0 <= offset < location.span):
                    warnings.warn("Offset is outside of defined span.")
                return self.blocks[ref][int(offset) + location.base]
            case ir.IRSet(location, value):
                if not self.allow_vars:
                    return None
                ref = location.ref
                offset = self.evaluate(location.offset)
                if offset is None:
                    return None
                if ref not in self.blocks:
                    if isinstance(ref, ir.TempRef):
                        self.blocks[ref] = []
                    else:
                        self.blocks[ref] = [0] * 64000
                if isinstance(ref, ir.TempRef):
                    if location.span is None:
                        raise ValueError("Expected span to be set.")
                    size = location.base + location.span
                    if size > len(self.blocks[ref]):
                        self.blocks[ref] += [0] * (size - len(self.blocks[ref]))
                value = self.evaluate(value)
                if value is None:
                    return None
                if location.span is not None and not (0 <= offset < location.span):
                    warnings.warn("Offset is outside of defined span.")
                self.blocks[ref][int(offset) + location.base] = value
                return 0
            case ir.IRComment():
                return 0
            case ir.IRConst(value):
                return value
            case ir.IRFunc(name, args):
                match name:
                    case name if name in self.functions:
                        args = self._evaluate_arguments(args)
                        if args is None:
                            return None
                        return self.functions[name](args)
                    case "Add":
                        return self._reduce_args(args, operator.add)
                    case "Subtract":
                        return self._reduce_args(args, operator.sub)
                    case "Multiply":
                        return self._reduce_args(args, operator.mul)
                    case "Divide":
                        return self._reduce_args(args, operator.truediv)
                    case "Mod":
                        return self._reduce_args(args, operator.mod)
                    case "Power":
                        return self._reduce_args(args, operator.pow)
                    case "Equal":
                        return self._reduce_args(args, operator.eq)
                    case "NotEqual":
                        return self._reduce_args(args, operator.ne)
                    case "Greater":
                        return self._reduce_args(args, operator.gt)
                    case "GreaterOr":
                        return self._reduce_args(args, operator.ge)
                    case "Less":
                        return self._reduce_args(args, operator.lt)
                    case "LessOr":
                        return self._reduce_args(args, operator.le)

                    case "Floor":
                        value = self.evaluate(args[0])
                        if value is None:
                            return None
                        return floor(value)
                    case "Ceil":
                        value = self.evaluate(args[0])
                        if value is None:
                            return None
                        return ceil(value)

                    case "Round":
                        value = self.evaluate(args[0])
                        if value is None:
                            return None
                        return round(value)

                    case "Min":
                        args = self._evaluate_arguments(args)
                        if args is None:
                            return
                        return min(args)
                    case "Max":
                        args = self._evaluate_arguments(args)
                        if args is None:
                            return
                        return max(args)

                    case "If":
                        test, then, other = args
                        if test is None:
                            return None
                        elif test != 0:
                            return self.evaluate(then)
                        else:
                            return self.evaluate(other)
                    case "And":
                        for arg in args:
                            evaluated = self.evaluate(arg)
                            if evaluated is None:
                                return None
                            if evaluated == 0:
                                return 0
                        return 1
                    case "Or":
                        for arg in args:
                            evaluated = self.evaluate(arg)
                            if evaluated is None:
                                return None
                            if evaluated != 0:
                                return 1
                        return 1
                    case "Not":
                        arg = args[0]
                        evaluated = self.evaluate(arg)
                        if evaluated is None:
                            return None
                        if evaluated == 0:
                            return 1
                        return 0
                return None

    def _reduce_args(
        self, args: list[ir.IRNode], op: Callable[[float, float], float], default=None
    ):
        args = self._evaluate_arguments(args)
        if not args:
            return default
        if args is not None:
            return float(functools.reduce(op, args))
        else:
            return None

    def _evaluate_arguments(self, args: list[ir.IRNode]) -> Optional[list[float]]:
        results = []
        for arg in args:
            evaluated = self.evaluate(arg)
            if evaluated is None:
                return None
            results.append(evaluated)
        return results


def evaluate_ir(node: ir.IRNode | graph.FlatCfg):
    return IREvaluator().evaluate(node)
