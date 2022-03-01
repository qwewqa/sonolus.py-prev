from __future__ import annotations

from abc import ABC

from sonolus.backend.cfg import Cfg


class OptimizationPass(ABC):
    requires: tuple[AnalysisPass, ...] = ()

    def run(self, cfg: Cfg):
        ...


class AnalysisPass(ABC):
    requires: tuple[AnalysisPass, ...] = ()

    @classmethod
    def analyze(cls, cfg: Cfg):
        ...


def run_optimization_passes(
    cfg: Cfg,
    passes: list[OptimizationPass],
):
    for opt_pass in passes:
        analyses = set()
        required_analyses = [*opt_pass.requires]
        while required_analyses:
            analysis = required_analyses.pop()
            unsatisfied_analyses = analysis.requires - analyses
            if unsatisfied_analyses:
                required_analyses.extend(unsatisfied_analyses)
                required_analyses.append(analysis)
            else:
                analyses.add(analysis)
                analysis.analyze(cfg)
        opt_pass.run(cfg)
    return cfg
