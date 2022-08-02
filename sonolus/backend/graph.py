from __future__ import annotations

import base64
import json
import textwrap
import zlib
from dataclasses import dataclass

from sonolus.backend.cfg import CFG
from sonolus.backend.cfg_traversal import traverse_preorder, traverse_postorder
from sonolus.backend.ir import IRNode, SSARef


def get_flat_cfg(cfg: CFG) -> FlatCfg:
    nodes = [*traverse_preorder(cfg)]
    no_exit = False
    if cfg.entry_node != cfg.exit_node:
        if cfg.exit_node in nodes:
            nodes.remove(cfg.exit_node)
        if cfg.edges_by_to[cfg.exit_node]:
            nodes.append(cfg.exit_node)
        else:
            no_exit = True
    node_indexes = {node: i for i, node in enumerate(nodes)}
    flat_nodes = []
    for i, node in enumerate(nodes):
        match [*cfg.edges_by_from[node]]:
            case []:
                test = node.test
                target = None
            case [edge]:
                test = None
                target = node_indexes[edge.to_node]
            case [*edges]:
                test = node.test
                target = {edge.condition: node_indexes[edge.to_node] for edge in edges}
            case other:
                raise ValueError(f"Invalid edge: {other}.")
        flat_nodes.append(
            FlatCfgNode(
                i,
                node.body,
                test,
                target,
                {
                    phi.target: {node_indexes[k]: v for k, v in phi.values.items()}
                    for phi in node.phi
                },
            )
        )
    if no_exit:
        flat_nodes.append(FlatCfgNode(len(flat_nodes), [], None, None, {}))
    return FlatCfg(flat_nodes)


@dataclass
class FlatCfg:
    blocks: list[FlatCfgNode]

    def __str__(self):
        body = textwrap.indent(
            "\n".join(f"{i}: {node}" for i, node in enumerate(self.blocks)), "    "
        )
        return f"graph {{\n{body}\n}}"

    def mermaid(self):
        def quote(s: str):
            return '"<pre>' + s.replace("\n", "<br/>") + '</pre>"'

        def fmt(nodes):
            if nodes:
                return "\n".join(str(n) for n in nodes)
            else:
                return "{}"

        entries = ["Entry([Entry]) --> 0"]
        for i, node in enumerate(self.blocks):
            phi = [
                f"phi %{k.name} <- {', '.join(f'{n}: {r}' for n, r in v.items())}"
                for k, v in node.phi.items()
            ]
            entries.append(f"{i}[{quote(fmt([f'#{i}'] + phi + node.body))}]")
            entries.append(f"style {i} text-align:left")
            match node.target:
                case None:
                    if node.test is None:
                        entries.append(f"{i} --> Exit")
                    else:
                        entries.append(f"{i}_{{{{{quote(fmt([node.test]))}}}}}")
                        entries.append(f"{i} --> {i}_")
                        entries.append(f"{i}_ --> |result| Exit")
                case {0: f_branch, None: t_branch, **other} if not other:
                    entries.append(f"{i}_{{{{{quote(fmt([node.test]))}}}}}")
                    entries.append(f"{i} --> {i}_")
                    entries.append(f"{i}_ --> |true| {t_branch}")
                    entries.append(f"{i}_ --> |false| {f_branch}")
                case dict() as tgt:
                    entries.append(f"{i}_{{{{{quote(fmt([node.test]))}}}}}")
                    entries.append(f"{i} --> {i}_")
                    for k, v in tgt.items():
                        if k is None:
                            k = "default"
                        entries.append(f"{i}_ --> |{k}| {v}")
                case int() as tgt:
                    entries.append(f"{i} --> {tgt}")
                case _:
                    raise ValueError(f"Unexpected graph node configuration: {node}.")
        entries.append("Exit([Exit])")

        body = textwrap.indent("\n".join(entries), "    ")
        return f"graph\n{body}"

    def mermaid_svg_url(self):
        return f"https://mermaid.ink/svg/{self._encode_mermaid()}"

    def mermaid_img_url(self):
        return f"https://mermaid.ink/img/{self._encode_mermaid()}"

    def _encode_mermaid(self):
        payload = json.dumps({"code": self.mermaid()})
        return "pako:" + base64.urlsafe_b64encode(
            zlib.compress(payload.encode("utf-8"), 9)
        ).decode("ascii")


@dataclass(eq=False)
class FlatCfgNode:
    index: int
    body: list[IRNode]
    test: IRNode | None
    target: dict[float | None, int] | int | None
    phi: dict[SSARef, dict[int, SSARef]]

    def targets(self) -> list[int]:
        match self.target:
            case dict() as tgts:
                return [*tgts.values()]
            case int() as tgt:
                return [tgt]
            case _:
                return []

    def __str__(self):
        phi = [
            f"phi %{k.name} <- {', '.join(f'{n}: {r}' for n, r in v.items())}"
            for k, v in self.phi.items()
        ]
        body = (
            "{\n" + ",\n".join(f"    {entry}" for entry in phi + self.body) + "\n}"
            if self.body
            else "{}"
        )
        match self.target:
            case None:
                if self.test is None:
                    return f"{body} -> !"
                return f"{body} -> {self.test} !"
            case {0: f_branch, None: t_branch, **other} if not other:
                return f"{body} -> {self.test} ? {t_branch} : {f_branch}"
            case dict() as tgt:
                return f"{body} -> {self.test} ? {tgt}"
            case int() as tgt:
                return f"{body} -> {tgt}"
            case _:
                raise RuntimeError("Unexpected target.")
