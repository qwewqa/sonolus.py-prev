from typing import Iterator

from sonolus.backend.cfg import CFG, CFGNode


def traverse_cfg(cfg: CFG) -> Iterator[CFGNode]:
    # Traverse the cfg in arbitrary order
    visited = set()
    queue = [cfg.entry_node]
    while queue:
        node = queue.pop()
        if node in visited:
            continue
        visited.add(node)
        yield node
        queue.extend([edge.to_node for edge in cfg.edges_by_from[node]])


def traverse_postorder(
    cfg: CFG, node: CFGNode = None, visited: set = None
) -> Iterator[CFGNode]:
    if node is None:
        node = cfg.entry_node
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    edges = sorted(cfg.edges_by_from[node])
    for edge in edges:
        yield from traverse_postorder(cfg, edge.to_node, visited)
    yield node


def traverse_preorder(
    cfg: CFG, node: CFGNode = None, visited: set = None
) -> Iterator[CFGNode]:
    if node is None:
        node = cfg.entry_node
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    edges = sorted(cfg.edges_by_from[node])
    yield node
    for edge in edges:
        yield from traverse_preorder(cfg, edge.to_node, visited)
