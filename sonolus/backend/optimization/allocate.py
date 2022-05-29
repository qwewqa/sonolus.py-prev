import dataclasses

from sonolus.backend.cfg import CFG
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.ir import TempRef, MemoryBlock
from sonolus.backend.ir_visitor import IRTransformer
from sonolus.backend.optimization.get_temp_ref_sizes import get_temp_ref_sizes
from sonolus.backend.optimization.optimization_pass import OptimizationPass

BASE_INDEX = 4095


class Allocate(OptimizationPass):
    def run(self, cfg: CFG):
        sizes = get_temp_ref_sizes(cfg)
        offset = -1
        mapping = {}
        for ref, size in sizes.items():
            offset += size
            mapping[ref] = BASE_INDEX - offset
        transformer = AllocateTransformer(mapping)
        for cfg_node in [*traverse_cfg(cfg)]:
            cfg.replace_node(cfg_node, transformer.visit(cfg_node))


class AllocateTransformer(IRTransformer):
    def __init__(self, mapping: dict[TempRef, int]):
        self.mapping = mapping

    def visit_Location(self, location):
        location = super().visit_Location(location)
        if isinstance(location.ref, TempRef):
            return dataclasses.replace(
                location,
                ref=MemoryBlock.TEMPORARY_MEMORY,
                base=self.mapping[location.ref] + location.base,
            )
        return location
