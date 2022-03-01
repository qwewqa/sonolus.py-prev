from collections import defaultdict

from sonolus.backend.cfg import Cfg
from sonolus.backend.cfg_traversal import traverse_cfg, traverse_postorder
from sonolus.backend.ir import TempRef, IRFunc
from sonolus.backend.ir_visitor import IRVisitor, IRTransformer
from sonolus.backend.optimization.basic_dead_code_elimination import EFFECTUAL_FUNCTIONS
from sonolus.backend.optimization.optimization_pass import OptimizationPass


class BasicDeadStoreElimination(OptimizationPass):
    def run(self, cfg: Cfg):
        visitor = AccessVisitor()
        for cfg_node in traverse_cfg(cfg):
            visitor.visit(cfg_node)
        transformer = DeadStoreTransformer(visitor.accesses)
        for cfg_node in [*traverse_postorder(cfg)]:
            cfg.replace_node(cfg_node, transformer.visit(cfg_node))


class AccessVisitor(IRVisitor):
    def __init__(self):
        self.accesses = defaultdict(lambda: 0)

    def visit_IRGet(self, node):
        super().visit_IRGet(node)
        if isinstance(node.location.ref, TempRef):
            self.accesses[node.location.ref] += 1


class DeadStoreTransformer(IRTransformer):
    def __init__(self, accesses):
        self.accessed = accesses

        # We use this to visit pruned nodes, and subtract the access count
        self.visitor = AccessVisitor()

    def visit_CfgNode(self, node):
        # We want to visit the body in reverse order
        node.body = node.body[::-1]
        node = super().visit_CfgNode(node)
        node.body = [n for n in reversed(node.body) if n is not None]
        return node

    def visit_IRSet(self, node):
        if isinstance(node.location.ref, TempRef):
            if (
                self.accessed[node.location.ref]
                - self.visitor.accesses[node.location.ref]
                == 0
            ):
                if (
                    isinstance(node.value, IRFunc)
                    and node.value.name in EFFECTUAL_FUNCTIONS
                ):
                    return node.value
                self.visitor.visit(node.value)
                return None
        return node
