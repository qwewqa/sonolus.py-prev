import itertools
import operator

from sonolus.backend.cfg import Cfg
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.ir import TempRef, Location, IRConst
from sonolus.backend.ir_visitor import IRVisitor, IRTransformer
from sonolus.backend.optimization.get_temp_ref_sizes import get_temp_ref_sizes
from sonolus.backend.optimization.optimization_pass import OptimizationPass


class AggregateToScalar(OptimizationPass):
    def run(self, cfg: Cfg):
        visitor = _AggregateAccessVisitor(cfg)
        for cfg_node in traverse_cfg(cfg):
            visitor.visit(cfg_node)
        transformer = _AggregateAccessTransformer(visitor.values)
        for cfg_node in [*traverse_cfg(cfg)]:
            cfg.replace_node(cfg_node, transformer.visit(cfg_node))


class _AggregateAccessVisitor(IRVisitor):
    def __init__(self, cfg):
        self.values = {
            ref: [True] * size for ref, size in get_temp_ref_sizes(cfg).items()
        }

    def visit_Location(self, location):
        ref = location.ref
        if not isinstance(ref, TempRef):
            return
        if location.offset.constant() is None and location.span != 1:
            base = location.base
            span = location.span
            self.values[ref][base : base + span] = [False] * span


class _AggregateAccessTransformer(IRTransformer):
    def __init__(self, values):
        values = {k: [*v] for k, v in values.items()}

        for ref, entry in values.items():
            if len(entry) == 1:
                entry[0] = ref, 0
                continue
            for can_split, indexes in itertools.groupby(
                enumerate(entry), key=operator.itemgetter(1)
            ):
                indexes = [*indexes]
                if can_split:
                    start, end = indexes[0][0], indexes[-1][0] + 1
                    entry[start:end] = [
                        (TempRef(f"{ref.name}${i}"), i) for i in range(start, end)
                    ]
                else:
                    start, end = indexes[0][0], indexes[-1][0] + 1
                    entry[start:end] = [
                        (TempRef(f"{ref.name}${start}_{end}"), start)
                    ] * (end - start)

        self.values = values

    def visit_Location(self, location):
        ref = location.ref
        if not isinstance(ref, TempRef):
            return location
        values = self.values[ref]
        if location.offset.constant() is not None:
            index = int(location.offset.constant() + location.base)
        else:
            # if offset isn't constant it won't matter where between base and base + span we are
            index = location.base
        new_ref, base_offset = values[index]
        return Location(
            new_ref, location.offset, location.base - base_offset, location.span
        )
