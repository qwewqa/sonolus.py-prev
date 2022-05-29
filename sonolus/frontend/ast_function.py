from __future__ import annotations

import inspect
import itertools
import textwrap
from ast import *
from typing import TypeVar, Callable, Any

T = TypeVar("T", bound=Callable)


def process_ast_function(fn):
    import sonolus.frontend.control_flow as cf
    from sonolus.frontend.control_flow import Execute, ExecuteVoid
    from sonolus.frontend.primitive import Bool, Num
    from sonolus.frontend.void import Void
    from sonolus.frontend.iterator import Iter

    source_file = inspect.getsourcefile(fn)
    lines, lnum = inspect.getsourcelines(fn)
    tree = parse(textwrap.dedent("".join(lines)))
    increment_lineno(tree, lnum - 1)
    try:
        signature = inspect.signature(fn)
        ret_param_name = "_ret" if "_ret" in signature.parameters else None
        transformed = _AstFunctionTransformer(ret_param_name).visit(tree)
    except ValueError as e:
        # Shorten the traceback.
        raise ValueError(*e.args)

    fix_missing_locations(transformed)

    closure = inspect.getclosurevars(fn)

    gbl = {}
    gbl.update(vars(inspect.getmodule(fn)))
    gbl.update(fn.__globals__)  # Necessary for type annotations.
    gbl.update(closure.globals)
    gbl.update(closure.nonlocals)
    gbl.update(closure.builtins)
    loc = {}

    gbl.update(
        {
            "_Boolean_": Bool,
            "_Number_": Num,
            "_Execute_": Execute,
            "_ExecuteVoid_": ExecuteVoid,
            "_Void_": Void,
            "_Break_": cf.Break,
            "_Continue_": cf.Continue,
            "_Return_": cf.Return,
            "_If_": cf.If,
            "_While_": cf.While,
            "_For_": cf.For,
            "_Iter_": Iter,
            "_And_": Bool.and_,
            "_Or_": Bool.or_,
            "_Not_": Bool.not_,
            "_In_": lambda a, b: Execute(a, b, b.__contains__(a)),
        }
    )

    compiled = compile(transformed, source_file, "exec")
    exec(compiled, gbl, loc)
    generated_fn = loc[fn.__name__]
    generated_fn._generated_src_ = unparse(transformed)
    return generated_fn


class _AstFunctionTransformer(NodeTransformer):
    def __init__(self, ret_param_name):
        self.inside_function = False
        self.final_return = False
        self.function_name = ""
        self.ret_param_name = ret_param_name
        self.temp_var_index = 0

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if self.inside_function:
            raise ValueError("Nested function definitions are unsupported.")
        self.inside_function = True
        self.function_name = node.name
        body = list(node.body)
        final_stmt = body[-1]
        is_final_return = (
            isinstance(final_stmt, Return)
            and final_stmt.value is not None
            and self.ret_param_name is None
        )
        if is_final_return:
            self.final_return = True
            body[-1] = final_stmt.value
        else:
            body.append(Call(Name("_Void_", Load()), [], []))
        header = list(
            itertools.takewhile(lambda n: isinstance(n, (Import, ImportFrom)), body)
        )
        body = body[len(header) :]
        body = [
            *header,
            Return(
                Call(
                    Name("_Execute_" if is_final_return else "_ExecuteVoid_", Load()),
                    self.visit_nodes(body),
                    []
                    if is_final_return
                    else [keyword("labels", List(elts=[Str("_function")], ctx=Load()))],
                )
            ),
        ]
        result = FunctionDef(
            node.name, node.args, body, [], node.returns, node.type_comment
        )
        return copy_location(result, node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        raise ValueError("Async functions are not supported.")

    def visit_Return(self, node: Return) -> Any:
        if self.ret_param_name is None and self.final_return:
            # Terminal returns are already process by the time this function is called,
            # so node must be an early return.
            raise ValueError(
                "Early returns are not allowed in functions with a final return but no _ret parameter."
            )
        if node.value:
            if self.ret_param_name is None:
                raise ValueError(
                    "Early returns with a value are not allowed in functions with no _ret parameter."
                )
            args = [
                Call(
                    Attribute(Name(self.ret_param_name, Load()), "_assign_", Load()),
                    [self.visit(node.value)],
                    [],
                ),
                Call(Name("_Return_", Load()), [], []),
            ]
            return Call(Name("_ExecuteVoid_", Load()), args, [])
        else:
            return Call(Name("_Return_", Load()), [], [])

    def visit_ClassDef(self, node: ClassDef) -> Any:
        raise ValueError("Class definitions are not supported.")

    def visit_Delete(self, node: Delete) -> Any:
        raise ValueError("Delete statements are not supported.")

    def visit_Assign(self, node: Assign) -> Any:
        if len(node.targets) > 1 or not isinstance(node.targets[0], Name):
            raise ValueError("Complex assignments are not supported.")
        if node.targets[0].id == "_ret":
            raise ValueError("Cannot assign to _ret.")
        return self.visit_NamedExpr(NamedExpr(node.targets[0], node.value))

    def visit_AugAssign(self, node: AugAssign) -> Any:
        match node.op:
            case Add():
                op_name = "__iadd__"
            case Sub():
                op_name = "__isub__"
            case Mult():
                op_name = "__imul__"
            case MatMult():
                op_name = "__imatmul__"
            case Div():
                op_name = "__itruediv__"
            case Mod():
                op_name = "__imod__"
            case Pow():
                op_name = "__ipow__"
            case LShift():
                op_name = "__ilshift__"
            case RShift():
                op_name = "__irshift__"
            case BitOr():
                op_name = "__ior__"
            case BitXor():
                op_name = "__ixor__"
            case BitAnd():
                op_name = "__iand__"
            case FloorDiv():
                op_name = "__ifloordiv__"
            case _:
                raise ValueError(f"Unexpected operator {node.op}.")
        match node.target:
            case Attribute() as tgt:
                target = Attribute(tgt.value, tgt.attr, Load())
            case Name() as tgt:
                target = Name(tgt.id, Load())
            case Subscript() as tgt:
                target = Subscript(tgt.value, tgt.slice, Load())
            case _:
                raise ValueError(f"Unexpected target {node.target}.")
        return self.visit(Call(Attribute(target, op_name, Load()), [node.value], []))

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        if not node.value:
            return Call(Name("_Void_", Load()), [], [])
        return self.visit_Assign(Assign([node.target], node.value))

    def visit_For(self, node: For) -> Any:
        match node.target:
            case Name() as name:
                argnames = [name.id]
                unpack = False
            case Tuple(elts):
                argnames = []
                for el in elts:
                    if not isinstance(el, Name):
                        raise ValueError(
                            "For loops with complex unpacking targets are not supported."
                        )
                    argnames.append(el.id)
                unpack = True
            case _:
                raise ValueError(
                    "For loops with complex unpacking targets are not supported."
                )

        iter = self.visit(node.iter)
        body = self.visit_block(node.body)
        body = Lambda(
            args=arguments(
                posonlyargs=[],
                args=[arg(arg=name) for name in argnames],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=body,
        )
        orelse = self.scope_expr(self.visit_block(node.orelse))

        return Call(Name("_For_", Load()), [iter, body, orelse, Constant(unpack)], [])

    def visit_If(self, node: If) -> Any:
        test = self.visit(node.test)
        body = self.scope_expr(self.visit_block(node.body))
        orelse = self.scope_expr(self.visit_block(node.orelse))
        return copy_location(Call(Name("_If_", Load()), [test, body, orelse], []), node)

    def visit_With(self, node: With) -> Any:
        raise ValueError("With statements are not supported.")

    def visit_Match(self, node: Match) -> Any:
        raise ValueError("Match statements are not supported.")

    def visit_Raise(self, node: Raise) -> Any:
        raise ValueError("Raise statements are not supported.")

    def visit_Try(self, node: Try) -> Any:
        raise ValueError("Try statements are not supported.")

    def visit_Assert(self, node: Assert) -> Any:
        raise ValueError("Assert statements are not supported.")

    def visit_Import(self, node: Import) -> Any:
        raise ValueError(
            "Import statements must appear first and at the top level of ast functions."
        )

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        raise ValueError(
            "Import statements must appear first and at the top level of ast functions."
        )

    def visit_Global(self, node: Global) -> Any:
        return Constant(0)

    def visit_Nonlocal(self, node: Nonlocal) -> Any:
        return Constant(0)

    def visit_BoolOp(self, node: BoolOp) -> Any:
        if len(node.values) == 1:
            return self.visit(node.values[0])
        lhs = self.visit_BoolOp(BoolOp(node.op, node.values[:-1]))
        rhs = self.visit(node.values[-1])
        match node.op:
            case And():
                return Call(Name("_And_", Load()), [lhs, rhs], [])
            case Or():
                return Call(Name("_Or_", Load()), [lhs, rhs], [])

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        if not isinstance(node.target, Name):
            raise ValueError(
                f"Assignments to complex identifiers ({unparse(node)}) is not supported."
            )
        return NamedExpr(self.visit(node.target), self.visit(node.value))

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        if isinstance(node.op, Not):
            return Call(Name("_Not_", Load()), [self.visit(node.operand)], [])
        else:
            return self.generic_visit(node)

    def visit_IfExp(self, node: IfExp) -> Any:
        return Call(
            Name("_If_", Load()),
            [self.visit(node.test), self.visit(node.body), self.visit(node.orelse)],
            [],
        )

    def visit_Yield(self, node: Yield) -> Any:
        raise ValueError("Yield statements are not supported.")

    def visit_YieldFrom(self, node: YieldFrom) -> Any:
        raise ValueError("Yield from statements are not supported.")

    def visit_Compare(self, node: Compare) -> Any:
        if len(node.ops) == 1:
            if isinstance(node.ops[0], NotIn):
                return self.visit(
                    UnaryOp(Not(), Compare(node.left, [In()], node.comparators))
                )
            if isinstance(node.ops[0], In):
                return self.visit(
                    Call(Name("_In_", Load()), [node.left, node.comparators[0]], [])
                )
            return self.generic_visit(node)
        right_name = self.temp_identifier()
        right = NamedExpr(Name(right_name, Store()), node.comparators[0])
        lhs = Compare(node.left, [node.ops[0]], [right])
        rhs = Compare(Name(right_name, Load()), node.ops[1:], node.comparators[1:])
        return self.visit(BoolOp(And(), [lhs, rhs]))

    def visit_While(self, node: While) -> Any:
        test = self.visit(node.test)
        body = self.scope_expr(self.visit_block(node.body))
        orelse = self.scope_expr(self.visit_block(node.orelse))
        return Call(Name("_While_", Load()), [test, body, orelse], [])

    def visit_Pass(self, node: Pass) -> Any:
        return Call(Name("_Void_", Load()), [], [])

    def visit_Break(self, node: Return) -> Any:
        return Call(Name("_Break_", Load()), [], [])

    def visit_Continue(self, node: Return) -> Any:
        return Call(Name("_Continue_", Load()), [], [])

    def visit_nodes(self, nodes):
        return [copy_location(self.convert_statement(self.visit(n)), n) for n in nodes]

    def convert_statement(self, node):
        if isinstance(node, Expr):
            return copy_location(node.value, node)
        return node

    def scope_expr(self, node):
        return Call(func=self.expr_to_lambda(node), args=[], keywords=[])

    def expr_to_lambda(self, node):
        return Lambda(
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=node,
        )

    def visit_block(self, nodes):
        return Call(Name("_ExecuteVoid_", Load()), self.visit_nodes(nodes), [])

    def temp_identifier(self):
        index = self.temp_var_index
        self.temp_var_index += 1
        return f"_temp_{index}_"

    @staticmethod
    def combine_scopes(*args: dict):
        keys = {key for a in args for key in a.keys()}
        return {key: len({a.get(key) for a in args}) == 1 for key in keys}
