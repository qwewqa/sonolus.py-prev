from types import FunctionType
from typing import Callable, Sized, Iterable

from sonolus.backend.evaluation import Scope, DeadScope
from sonolus.frontend.sls_func import convert_literal
from sonolus.frontend.statement import Statement
from sonolus.frontend.value import Value, convert_value
from sonolus.frontend.void import Void


class ExecuteStatement(Statement):
    def __init__(self, statements: list[Statement], *, labels: list[str] | None = None):
        self.statements = statements
        self.labels = labels

    def _evaluate_(self, scope: Scope):
        if self.labels is None:
            for statement in self.statements:
                scope = scope.evaluate(statement)
            return scope
        else:
            after = scope.prepare_next()
            block = scope.child(self.labels)
            scope.jump(block)
            block = block.activate()
            for statement in self.statements:
                block = block.evaluate(statement)
            block.jump(after)
            after = after.activate()
            return after


class IfStatement(Statement):
    def __init__(self, test, then, else_):
        self.test = test
        self.then = then
        self.else_ = else_

    def _evaluate_(self, scope: Scope):
        scope = scope.evaluate(self.test)
        after = scope.prepare_next()
        then, else_ = scope.children(2)
        scope.jump_cond(self.test.ir(), {None: then, 0: else_})
        then = then.activate()
        then = then.evaluate(self.then)
        then.jump(after)
        else_ = else_.activate()
        else_ = else_.evaluate(self.else_)
        else_.jump(after)
        after = after.activate()
        return after


class WhileStatement(Statement):
    def __init__(self, test, body, else_):
        self.test = test
        self.body = body
        self.else_ = else_

    def _evaluate_(self, scope: Scope):
        after = scope.prepare_next()
        loop = scope.child(["_loop"])
        else_ = scope.child()
        scope.jump(loop)
        loop = loop.activate()
        start = loop
        loop = loop.evaluate(self.test)
        end = loop.prepare_next()
        body = loop.child()
        loop.jump_cond(self.test.ir(), {None: body, 0: else_})
        body = body.activate()
        body = body.evaluate(self.body)
        body.jump_back(start)
        else_ = else_.activate()
        else_ = else_.evaluate(self.else_)
        else_.jump(after)
        # End is actually inaccessible since body jumps back to start
        # and body doesn't have a label.
        end = end.activate()
        end.jump(after)
        after = after.activate()
        return after


class Break(Statement):
    def __init__(self, label="_loop"):
        self.label = label

    def _evaluate_(self, scope: Scope):
        scope.break_(self.label)
        return DeadScope()


class Continue(Statement):
    def __init__(self, label="_loop"):
        self.label = label

    def _evaluate_(self, scope: Scope):
        scope.continue_(self.label)
        return DeadScope()


def Return():
    return Break("_function")


def Execute(*args: Statement):
    if not args:
        return Void()
    args = [ensure_statement(arg) for arg in args]
    statement = ExecuteStatement(args)
    last = args[-1]
    if args and isinstance(last, Value):
        return last._dup_(statement)
    return statement


def ExecuteVoid(*args: Statement, labels: list[str] | None = None):
    args = [ensure_statement(arg) for arg in args]
    return ExecuteStatement(args, labels=labels)


def If(test, then, else_=None):
    from sonolus.frontend.primitive import Bool

    test = convert_value(test, Bool)
    then = convert_literal(then)
    else_ = convert_literal(else_)
    if else_ is None:
        else_ = Void()
    if type(then) == type(else_) and Value.is_value_class(type(then)):
        result = type(then)._allocate_()
        return result._set_parent_(
            IfStatement(test, result._assign_(then), result._assign_(else_))
        )
    return IfStatement(test, then, else_)


def While(test, body, else_=None):
    from sonolus.frontend.primitive import Bool

    test = convert_value(test, Bool)
    if else_ is None:
        else_ = Void()
    return WhileStatement(test, body, else_)


def For(iterator, /, body: Callable, else_=None, unpack: bool = False):
    from sonolus.frontend.iterator import Iter, SlsIterator

    if else_ is None:
        else_ = Void()
    try:
        iterator = Iter(iterator)
    except TypeError:
        pass
    if not isinstance(iterator, SlsIterator):
        if isinstance(iterator, Sized) and isinstance(iterator, Iterable):
            statements = []
            if unpack:
                for entry in iterator:
                    statements.append(body(*entry))
                else:
                    statements.append(else_)
            else:
                for entry in iterator:
                    statements.append(body(entry))
                else:
                    statements.append(else_)
            return ExecuteStatement(statements)
        raise TypeError("Expected a SonoIterator.")
    iterator_has_next = iterator._has_item_()
    iterator_item = iterator._item_()
    iterator_advance = iterator._advance_()
    if unpack:
        return ExecuteVoid(
            iterator,
            While(
                iterator_has_next,
                ExecuteVoid(iterator_item, iterator_advance, body(*iterator_item)),
                else_,
            ),
        )
    else:
        return ExecuteVoid(
            iterator,
            While(
                iterator_has_next,
                ExecuteVoid(iterator_item, iterator_advance, body(iterator_item)),
                else_,
            ),
        )


def ensure_statement(value):
    if hasattr(value, "_statement_"):
        return value._statement_
    if isinstance(value, FunctionType):
        # Allows for lambdas
        return Void()
    if isinstance(value, str):
        # Ignore strings, including docstrings
        return Void()
    if isinstance(value, (tuple, list)):
        return ExecuteVoid(*value)
    result = convert_literal(value)
    if not isinstance(result, Statement):
        raise TypeError(f"Expected a statement, instead got {value}.")
    return result
