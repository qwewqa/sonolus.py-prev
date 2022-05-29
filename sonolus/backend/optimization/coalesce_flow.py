from sonolus.backend.cfg import CFG, CFGNode
from sonolus.backend.optimization.optimization_pass import OptimizationPass


class CoalesceFlow(OptimizationPass):
    def run(self, cfg: CFG):
        queue = [cfg.entry_node]
        visited = set()
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            edges = cfg.edges_by_from[node]
            if len(edges) != 1:
                for edge in edges:
                    queue.append(edge.to_node)
            else:
                edge = next(iter(edges))
                next_node = edge.to_node
                if next_node == node:
                    continue
                if len(cfg.edges_by_to[next_node]) != 1:
                    if not node.body:
                        cfg.remove_edge(edge)
                        cfg.replace_node(node, next_node)
                    queue.append(next_node)
                else:
                    new_node = CFGNode(
                        node.body + next_node.body,
                        next_node.test,
                        {},
                        node.phi,
                        node.is_entry,
                        next_node.is_exit,
                    )
                    cfg.remove_edge(edge)
                    cfg.replace_node(node, new_node)
                    cfg.replace_node(next_node, new_node)
                    queue.append(new_node)
