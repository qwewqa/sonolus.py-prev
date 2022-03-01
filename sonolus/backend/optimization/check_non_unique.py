from sonolus.backend.ir_visitor import IRVisitor


class CheckNonUniqueVisitor(IRVisitor):
    def __init__(self):
        self.seen = set()

    def visit_IRFunc(self, node):
        super().visit_IRFunc(node)
        if node in self.seen:
            print(node)
        self.seen.add(node)

    def visit_IRConst(self, node):
        super().visit_IRConst(node)
        if node in self.seen:
            print(node)
        self.seen.add(node)

    def visit_IRGet(self, node):
        super().visit_IRGet(node)
        if node in self.seen:
            print(node)
        self.seen.add(node)

    def visit_IRSet(self, node):
        super().visit_IRSet(node)
        if node in self.seen:
            print(node)
        self.seen.add(node)
