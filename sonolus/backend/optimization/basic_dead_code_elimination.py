from sonolus.backend.cfg import CFG
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.ir import IRSet, IRFunc
from sonolus.backend.optimization.optimization_pass import OptimizationPass


class BasicDeadCodeElimination(OptimizationPass):
    def run(self, cfg: CFG):
        for cfg_node in traverse_cfg(cfg):
            cfg_node.body = [n for n in cfg_node.body if self.is_effectual(n)]
            edges = cfg.edges_by_from[cfg_node]
            if len(edges) == 1 and not cfg_node.is_exit:
                cfg_node.test = None

    def is_effectual(self, node):
        match node:
            case IRFunc(name):
                return name in EFFECTUAL_FUNCTIONS
            case IRSet():
                return True
            case _:
                return False


EFFECTUAL_FUNCTIONS = {
    "Draw",
    "DrawCurvedL",
    "DrawCurvedR",
    "DrawCurvedLR",
    "DrawCurvedB",
    "DrawCurvedT",
    "DrawCurvedBT",
    "Play",
    "PlayScheduled",
    "Spawn",
    "SpawnParticleEffect",
    "MoveParticleEffect",
    "DestroyParticleEffect",
    "DebugPause",
    "DebugLog",
}
