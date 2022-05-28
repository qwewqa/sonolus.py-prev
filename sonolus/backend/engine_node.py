from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterable

from sonolus.backend.cfg import Cfg, CfgNode
from sonolus.backend.cfg_traversal import traverse_preorder
from sonolus.backend.ir_visitor import IRTransformer


@dataclass(frozen=True)
class ValueNode:
    value: float


@dataclass(frozen=True)
class FunctionNode:
    func: str
    args: tuple[SimpleNode, ...]


SimpleNode = ValueNode | FunctionNode


def finalize_cfg(cfg: Cfg) -> SimpleNode:
    nodes = [*traverse_preorder(cfg)]
    mapping = {node: i for i, node in enumerate(nodes)}
    if cfg.exit_node not in mapping:
        mapping[cfg.exit_node] = len(mapping)
    elif mapping[cfg.exit_node] != len(mapping) - 1:
        mapping[nodes[-1]], mapping[cfg.exit_node] = (
            mapping[cfg.exit_node],
            mapping[nodes[-1]],
        )
    nodes = [...] * len(mapping)
    transformer = FinalizeTransformer(cfg, mapping)
    for node, i in mapping.items():
        nodes[i] = transformer.visit(node)
    if len(nodes) == 1:
        return nodes[0]
    else:
        return FunctionNode("JumpLoop", tuple(nodes))


def get_engine_nodes(nodes: Iterable[SimpleNode]) -> tuple[list[dict], dict[SimpleNode, int]]:
    mapping = {}
    queue = [*nodes]
    while queue:
        node = queue.pop()
        if node not in mapping:
            mapping[node] = len(mapping)
            if isinstance(node, FunctionNode):
                queue.extend(reversed(node.args))
    nodes = [...] * len(mapping)
    for node, i in mapping.items():
        match node:
            case ValueNode():
                nodes[i] = {"value": node.value}
            case FunctionNode(func, args):
                nodes[i] = {"func": func, "args": [mapping[arg] for arg in args]}
    return nodes, mapping


class FinalizeTransformer(IRTransformer):
    node_indexes: dict[CfgNode, int]

    def __init__(self, cfg, mapping):
        self.cfg = cfg
        self.node_indexes = mapping

    def visit_CfgNode(self, node):
        body = [self.visit(n) for n in node.body]
        if node.test is not None:
            test = self.visit(node.test)
        else:
            test = ValueNode(-1)
        match {edge.condition: edge for edge in self.cfg.edges_by_from[node]}:
            case {}:
                terminal = test
            case {None: edge}:
                terminal = ValueNode(self.node_indexes[edge.to_node])
            case {None: t_branch, 0: f_branch}:
                terminal = FunctionNode(
                    "If",
                    (
                        test,
                        ValueNode(self.node_indexes[t_branch.to_node]),
                        ValueNode(self.node_indexes[f_branch.to_node]),
                    ),
                )
            case {**edges}:
                terminal = FunctionNode(
                    "Switch",
                    (
                        test,
                        *itertools.chain.from_iterable(
                            (condition, self.node_indexes[edge.to_node])
                            for condition, edge in edges.items()
                        ),
                    ),
                )
            case other:
                raise ValueError(f"Invalid edge: {other}.")
        return FunctionNode("Execute", tuple(body + [terminal]))

    def visit_IRConst(self, node):
        return ValueNode(node.value)

    def visit_IRComment(self, node):
        return ValueNode(0)

    def visit_IRFunc(self, node):
        return FunctionNode(node.name, tuple(self.visit(arg) for arg in node.args))

    def visit_IRGet(self, node):
        return FunctionNode("Get", self.visit(node.location))

    def visit_IRSet(self, node):
        return FunctionNode("Set", (*self.visit(node.location), self.visit(node.value)))

    def visit_Location(self, location):
        if isinstance(location.ref, (int, float)):
            ref = ValueNode(int(location.ref))
        else:
            ref = location.ref
        offset = self.visit(location.offset)
        if location.base != 0:
            if isinstance(offset, ValueNode):
                index = ValueNode(offset.value + location.base)
            else:
                index = FunctionNode("Add", (location.base, offset))
        else:
            index = offset
        return ref, index
