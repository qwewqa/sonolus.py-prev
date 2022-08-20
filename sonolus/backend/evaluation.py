from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from sonolus.backend.cfg import CFGNode, CFG, CFGEdge
from sonolus.backend.ir import IRNode

if TYPE_CHECKING:
    from sonolus.scripting.internal.statement import Statement
    from sonolus.backend.callback import CallbackType


def evaluate_statement(statement: Statement) -> CFG:
    from sonolus.scripting.internal.primitive import Primitive

    start = Scope().activate(entry=True)
    end = start.evaluate(statement)

    if isinstance(statement, Primitive):
        end.test = statement.ir()

    queue = collections.deque([start, end])
    scopes = set()
    while queue:
        scope = queue.popleft()
        if scope in scopes:
            continue
        scopes.add(scope)
        match scope.target:
            case dict() as targets:
                for target in targets.values():
                    queue.append(target)
            case Scope() as target:
                queue.append(target)

    mapping = {scope: CFGNode(scope.body, scope.test) for scope in scopes}
    cfg = CFG(mapping[start], mapping[end])

    mapping[start].is_entry = True
    mapping[end].is_exit = True

    for scope in scopes:
        cfg_node = mapping[scope]
        match scope.target:
            case dict() as targets:
                for condition, target in targets.items():
                    cfg.add_edge(
                        CFGEdge(cfg_node, mapping[target], condition=condition)
                    )
            case Scope() as target:
                cfg.add_edge(CFGEdge(cfg_node, mapping[target], condition=None))

    return cfg


@dataclass
class CompilationInfo:
    callback: CallbackType
    script_ids: dict
    refs: dict[str, int] = field(default_factory=dict)

    _current: ClassVar[CompilationInfo | None] = None

    @classmethod
    def get(cls) -> CompilationInfo:
        if cls._current is None:
            raise RuntimeError("No compilation is currently active.")
        return cls._current

    def __enter__(self):
        if CompilationInfo._current is not None:
            raise RuntimeError("A compilation is already active.")
        CompilationInfo._current = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CompilationInfo._current = None


@dataclass(eq=False, repr=False)
class Scope:
    labels: list[str] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    test: IRNode | None = None
    sources: list[Scope] = field(default_factory=list)
    soft_sources: list[Scope] = field(default_factory=list)
    target: dict[float | None, Scope] | Scope | None = None
    evaluated: set | None = None
    expired: set | None = None
    parent: Scope | None = None
    next: Scope | None = None
    activated: bool = False

    def activate(self, entry: bool = False):
        if not entry and not self.sources and not self.soft_sources:
            return DeadScope()
        if self.activated:
            raise RuntimeError("Scope is already used.")
        self.activated = True
        if not self.sources:
            self.evaluated = set()
            self.expired = set()
        else:
            self.evaluated = set(self.sources[0].evaluated)
            self.expired = set(self.sources[0].expired)
            for source in self.sources[1:]:
                self.expired |= self.evaluated ^ source.evaluated
                self.evaluated &= source.evaluated
                self.expired |= source.evaluated
                self.expired |= source.expired
            self.expired -= self.evaluated
        return self

    def evaluate(self, statement):
        scope = self
        if statement is None:
            return scope
        if statement._attributes_.is_static:
            return scope
        statement._was_evaluated_ = True
        scope = scope.evaluate(statement._parent_statement_)
        if statement in scope.evaluated:
            return scope
        if statement in scope.expired:
            raise RuntimeError(f"Statement {statement} used when potentially expired.")
        scope.evaluated.add(statement)
        return statement._evaluate_(scope)

    def add(self, node: IRNode):
        if self.next is not None:
            return
        self.body.append(node)

    def add_source(self, source: Scope):
        self.sources.append(source)

    def add_soft_source(self, source: Scope):
        self.soft_sources.append(source)

    def prepare_next(self) -> Scope:
        if self.next is not None:
            raise RuntimeError("Next is already set.")
        if self.labels:
            self.next = Scope(parent=self)
        else:
            self.next = Scope(parent=self.parent)
        return self.next

    def child(self, labels: list[str] = None):
        if labels is None:
            labels = []
        if self.next is None:
            raise RuntimeError("Scope does not have next.")
        if self.target is not None:
            raise RuntimeError("Scope already ended.")
        return Scope(labels, parent=self)

    def children(self, count: int):
        return [self.child() for _ in range(count)]

    def jump(self, target: Scope):
        if self.target is not None:
            raise RuntimeError("Scope already ended.")
        if target.activated:
            raise RuntimeError("Target is already activated.")
        self.target = target
        target.add_source(self)

    def jump_back(self, target: Scope):
        if self.target is not None:
            raise RuntimeError("Scope already ended.")
        self.target = target
        target.add_soft_source(self)

    def jump_cond(self, test: IRNode, target: dict[float | None, Scope]):
        if self.target is not None:
            raise RuntimeError("Scope already ended.")
        self.target = target
        self.test = test
        for tgt in target.values():
            tgt.add_source(self)

    def continue_(self, label: str | None):
        scope = self._find_scope(label)
        self.jump_back(scope)

    def break_(self, label: str | None):
        scope = self._find_scope(label)
        self.jump(scope.parent.next)

    def _find_scope(self, label: str | None):
        if label is None or label in self.labels:
            return self
        if self.parent is None:
            raise RuntimeError(f"No parent scope with label {label} found.")
        return self.parent._find_scope(label)


class DeadScope(Scope):
    def activate(self, _=...):
        return self

    def evaluate(self, statement):
        if statement is None:
            return self
        if statement._attributes_.is_static:
            return self
        statement._was_evaluated_ = True
        if (
            statement._parent_statement_
            and not statement._parent_statement_._was_evaluated_
        ):
            self.evaluate(statement._parent_statement_)
        statement._evaluate_(self)
        return self

    def add(self, node: IRNode):
        pass

    def add_source(self, source: Scope):
        raise RuntimeError("Scope is unreachable.")

    def prepare_next(self) -> Scope:
        return DeadScope()

    def child(self, labels: list[str] = None):
        return DeadScope()

    def jump(self, target: Scope):
        pass

    def jump_back(self, target: Scope):
        pass

    def jump_cond(self, test: IRNode, target: dict[float | None, Scope]):
        pass

    def continue_(self, label: str | None):
        pass

    def break_(self, label: str | None):
        pass
