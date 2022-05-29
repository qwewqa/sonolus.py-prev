from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Type

from sonolus.backend.evaluation import CompilationInfo, evaluate_statement
from sonolus.backend.engine_node import finalize_cfg, get_engine_nodes
from sonolus.backend.optimization.optimization_pass import run_optimization_passes
from sonolus.backend.optimization.optmization_presets import DEFAULT_OPTIMIZATION_PRESET
from sonolus.engine.ui import UIConfig
from sonolus.frontend.buckets import BucketConfig, Bucket
from sonolus.frontend.control_flow import Execute
from sonolus.frontend.options import OptionConfig, Option
from sonolus.frontend.primitive import Bool, Primitive, Num
from sonolus.frontend.script import Script


class Engine:
    def __init__(
            self,
            scripts: list[Type[Script]],
            buckets: Type[BucketConfig],
            options: Type[OptionConfig],
            ui: UIConfig,
    ):
        self.scripts = scripts
        self.buckets = buckets
        self.options = options
        self.ui = ui

    def compile(self, optimizations=DEFAULT_OPTIMIZATION_PRESET):
        script_ids = {script: i for i, script in enumerate(self.scripts)}
        nodes = []
        compiled = {}
        for script in self.scripts:
            instance = script.create_for_evaluation()
            callbacks = {}
            for callback_type, callback in script._metadata_.callbacks.items():
                compilation_info = CompilationInfo(
                    callback=callback_type,
                    script_ids=script_ids,
                )
                with compilation_info:
                    result = callback(instance)
                    if not isinstance(result, Primitive):
                        result = Execute(result, Num(0))
                    cfg = evaluate_statement(result)
                    cfg = run_optimization_passes(cfg, optimizations)
                    node = finalize_cfg(cfg)
                    callbacks[callback_type.name] = node, callback._callback_order_
                    nodes.append(node)
            compiled[script] = callbacks
        compiled_nodes, mapping = get_engine_nodes(nodes)
        scripts = [
            CompiledScript(
                callbacks={name: CompiledCallback(mapping[node], order) for name, (node, order) in
                           compiled[script].items()},
                input=script._metadata_.input,
            )
            for script in self.scripts
        ]
        return CompiledEngine(
            options=[*self.options._option_entries_.values()],
            ui=self.ui,
            buckets=[*self.buckets._bucket_entries_.values()],
            scripts=scripts,
            nodes=compiled_nodes,
        )


@dataclass
class CompiledEngine:
    options: list[Option]
    ui: UIConfig
    buckets: list[Bucket]
    scripts: list[CompiledScript]
    nodes: list[dict]

    def save(self, path):
        path = Path(path)
        with open(path / "EngineConfiguration", "wb") as f:
            f.write(gzip.compress(json.dumps(self.get_configuration()).encode("utf-8")))
        with open(path / "EngineData", "wb") as f:
            f.write(gzip.compress(json.dumps(self.get_data()).encode("utf-8")))

    def save_uncompressed(self, path):
        path = Path(path)
        with open(path / "EngineConfiguration.json", "w") as f:
            json.dump(self.get_configuration(), f)
        with open(path / "EngineData.json", "w") as f:
            json.dump(self.get_data(), f)

    def get_configuration(self):
        return {"options": [option.to_dict() for option in self.options], "ui": self.ui.to_dict()}

    def get_data(self):
        return {
            "buckets": [bucket.to_dict() for bucket in self.buckets],
            "archetypes": [{"script": i, "input": script.input} for i, script in enumerate(self.scripts)],
            "scripts": [script.to_dict() for script in self.scripts],
            "nodes": self.nodes,
        }


@dataclass
class CompiledScript:
    callbacks: dict[str, CompiledCallback]
    input: bool

    def to_dict(self):
        return {name: callback.to_dict() for name, callback in self.callbacks.items()}


@dataclass
class CompiledCallback:
    index: int
    order: int

    def to_dict(self):
        return {
            "index": self.index,
            "order": self.order,
        }
