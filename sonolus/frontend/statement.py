from __future__ import annotations

from typing import TypeVar

from sonolus.backend.evaluation import Scope

TStatement = TypeVar("TStatement", bound="Statement")


class Statement:
    _parent_statement_: Statement | None = None
    _is_standalone_: bool = False

    def _evaluate_(self, scope: Scope) -> Scope:
        return scope

    def _set_parent_(self: TStatement, parent: Statement) -> TStatement:
        if self._parent_statement_ is not None:
            raise ValueError("Statement already has a parent.")
        self._parent_statement_ = parent
        return self
