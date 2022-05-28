from collections import defaultdict

from sonolus.backend.ir import TempRef
from sonolus.backend.ir_visitor import IRVisitor


class _TempRefVisitor(IRVisitor):
    def __init__(self):
        self.sizes = defaultdict(int)

    def visit_Location(self, location):
        super().visit_Location(location)
        if isinstance(location.ref, TempRef):
            if location.span is None:
                raise ValueError("Expected a span for temp ref.")
            self.sizes[location.ref] = max(
                location.base + location.span, self.sizes[location.ref]
            )


def get_temp_ref_sizes(ir, /) -> dict[TempRef, int]:
    visitor = _TempRefVisitor()
    visitor.visit(ir)
    return visitor.sizes
