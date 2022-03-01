from sonolus.backend.cfg import Cfg
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.ir import IRNode, IRFunc, IRGet, TempRef, IRConst, IRSet, Location
from sonolus.backend.optimization.get_temp_ref_sizes import get_temp_ref_sizes
from sonolus.backend.optimization.node_functions import constant_functions
from sonolus.backend.optimization.optimization_pass import OptimizationPass


class _UNDEF:
    def __repr__(self):
        return "$UNDEF$"


class _NAC:
    def __repr__(self):
        return "$NAC$"


class ConditionalConstantPropagation(OptimizationPass):
    UNDEF = _UNDEF()
    NAC = _NAC()

    def __init__(self):
        super().__init__()
        self.ref_sizes = None

    def run(self, cfg: Cfg):
        self.ref_sizes = get_temp_ref_sizes(cfg)

        for cfg_node in traverse_cfg(cfg):
            cfg_node.annotations["ccp_lattice_in"] = {}
            cfg_node.annotations["ccp_lattice_out"] = None

        queue = [cfg.entry_node]
        while queue:
            cfg_node = queue.pop()

            initial_lattice = cfg_node.annotations["ccp_lattice_in"]
            lattice = {k: [*v] for k, v in initial_lattice.items()}
            for n in cfg_node.body:
                self.visit_ir(n, lattice)

            if lattice != cfg_node.annotations["ccp_lattice_out"]:
                cfg_node.annotations["ccp_lattice_out"] = lattice
            else:
                continue

            # test should have no side effects
            test = cfg_node.test and self.visit_ir(cfg_node.test, lattice).constant()
            if cfg_node.is_exit:
                continue
            if test is not None:
                edges = {edge.condition: edge for edge in cfg.edges_by_from[cfg_node]}
                edge = edges.get(test) or edges[None]
                queue.append(edge.to_node)
                edge.to_node.annotations["ccp_lattice_in"] = self.meet_latices(
                    [lattice, edge.to_node.annotations["ccp_lattice_in"]]
                )
            else:
                for edge in cfg.edges_by_from[cfg_node]:
                    queue.append(edge.to_node)
                    edge.to_node.annotations["ccp_lattice_in"] = self.meet_latices(
                        [lattice, edge.to_node.annotations["ccp_lattice_in"]]
                    )

        for cfg_node in traverse_cfg(cfg):
            lattice = cfg_node.annotations["ccp_lattice_in"]
            cfg_node.body = [self.visit_ir(n, lattice) for n in cfg_node.body]
            if cfg_node.test is not None:
                cfg_node.test = self.visit_ir(cfg_node.test, lattice)
                test = cfg_node.test.constant()
                if test is not None:
                    edges = {
                        edge.condition: edge for edge in cfg.edges_by_from[cfg_node]
                    }
                    key = test if test in edges else None
                    for k, v in edges.items():
                        if k != key:
                            cfg.remove_edge(v)
            cfg_node.annotations.pop("ccp_lattice_in")
            cfg_node.annotations.pop("ccp_lattice_out")
        cfg.remove_dead_nodes()

    def visit_ir(self, node: IRNode, lattice: dict):
        match node:
            case IRFunc() as node:
                args = [self.visit_ir(arg, lattice) for arg in node.args]
                if node.name == "Multiply":
                    # Useful special case
                    const_args = [arg.constant() for arg in args]
                    if any(arg == 0 for arg in const_args):
                        return IRConst(0)
                if node.name in constant_functions:
                    const_args = [arg.constant() for arg in args]
                    if all(arg is not None for arg in const_args):
                        return IRConst(constant_functions[node.name](*const_args))
                return IRFunc(node.name, args)
            case IRGet() as node:
                loc = node.location
                values = self.get_ref_values(lattice, loc.ref)
                if values is not None:
                    if loc.span == 1:
                        offset = 0
                    else:
                        offset = self.visit_ir(loc.offset, lattice).constant()
                    if offset is None:
                        return node
                    offset = int(offset)
                    value = values[int(offset + loc.base)]
                    if isinstance(value, (int, float)):
                        return IRConst(value)
                    return IRGet(Location(loc.ref, IRConst(0), loc.base + offset, 1))
                return node
            case IRSet() as node:
                loc = node.location
                values = self.get_ref_values(lattice, loc.ref)
                value = self.visit_ir(node.value, lattice)
                const_value = value.constant()
                if const_value is None:
                    const_value = self.NAC
                if values is not None:
                    offset = self.visit_ir(loc.offset, lattice).constant()
                    if offset is not None:
                        offset = int(offset)
                        index = offset + loc.base
                        values[index] = const_value
                        return IRSet(
                            Location(loc.ref, IRConst(0), loc.base + offset, 1), value
                        )
                    else:
                        for i in range(loc.base, loc.base + loc.span):
                            current_value = values[i]
                            if current_value != const_value:
                                values[i] = self.NAC
                return IRSet(node.location, value)
            case _:
                return node

    def get_ref_values(self, lattice: dict, ref):
        if not isinstance(ref, TempRef):
            return None
        if ref not in lattice:
            lattice[ref] = [self.UNDEF] * self.ref_sizes[ref]
        return lattice[ref]

    def meet_latices(self, lattices: list[dict[TempRef, list]]):
        result = {}
        keys = set()
        for lattice in lattices:
            keys.update(lattice.keys())
        for key in keys:
            values = [
                lattice.get(key, [self.UNDEF] * self.ref_sizes[key])
                for lattice in lattices
            ]
            result[key] = [self.meet_values(v) for v in zip(*values)]
        return result

    def meet_values(self, values):
        values = set(values)
        if len(values) == 2 and self.UNDEF in values:
            values.remove(self.UNDEF)
            return values.pop()
        if len(values) == 1:
            return values.pop()
        return self.NAC
