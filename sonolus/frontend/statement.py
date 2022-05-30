from __future__ import annotations

from typing import TypeVar

from sonolus.backend.evaluation import Scope, CompilationInfo

TStatement = TypeVar("TStatement", bound="Statement")


class Statement:
    _parent_statement_: Statement | None = None
    _is_standalone_: bool = False

    def __new__(cls, *args, **kwargs):
        result = object.__new__(cls)
        result._is_standalone_ = not CompilationInfo.active
        return result

    def _evaluate_(self, scope: Scope) -> Scope:
        return scope

    def _set_parent_(self: TStatement, parent: Statement) -> TStatement:
        if self._parent_statement_ is not None:
            raise ValueError("Statement already has a parent.")
        self._parent_statement_ = parent
        return self
