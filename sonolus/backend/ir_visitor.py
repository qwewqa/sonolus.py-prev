from sonolus.backend.cfg import CfgNode
from sonolus.backend.cfg_traversal import traverse_cfg
from sonolus.backend.ir import IRFunc, IRGet, IRSet, Location


class IRVisitor:
    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method)
        return visitor(node)

    def visit_Cfg(self, cfg):
        for cfg_node in traverse_cfg(cfg):
            self.visit(cfg_node)

    def visit_CfgNode(self, node):
        for n in node.body:
            self.visit(n)
        if node.test is not None:
            self.visit(node.test)

    def visit_IRConst(self, node):
        pass

    def visit_IRComment(self, node):
        pass

    def visit_IRFunc(self, node):
        for arg in node.args:
            self.visit(arg)

    def visit_IRGet(self, node):
        self.visit(node.location)

    def visit_IRSet(self, node):
        self.visit(node.location)
        self.visit(node.value)

    def visit_Location(self, location):
        self.visit(location.offset)


class IRTransformer(IRVisitor):
    def visit_Cfg(self, cfg):
        raise NotImplementedError()

    def visit_CfgNode(self, node):
        body = [self.visit(n) for n in node.body]
        if node.test is not None:
            test = self.visit(node.test)
        else:
            test = None
        return CfgNode(
            body, test, node.annotations, node.phi, node.is_entry, node.is_exit
        )

    def visit_IRConst(self, node):
        return node

    def visit_IRComment(self, node):
        return node

    def visit_IRFunc(self, node):
        return IRFunc(node.name, [self.visit(arg) for arg in node.args])

    def visit_IRGet(self, node):
        return IRGet(self.visit(node.location))

    def visit_IRSet(self, node):
        return IRSet(self.visit(node.location), self.visit(node.value))

    def visit_Location(self, location):
        return Location(
            location.ref, self.visit(location.offset), location.base, location.span
        )
