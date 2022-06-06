from __future__ import annotations

from typing import TypeVar
from warnings import warn

from sonolus.backend.evaluation import Scope

TStatement = TypeVar("TStatement", bound="Statement")


class Statement:
    _parent_statement_: Statement | None = None
    _is_static_: bool = False
    _was_evaluated_: bool = False

    __unevaluated_warning_shown = False

    def _evaluate_(self, scope: Scope) -> Scope:
        return scope

    def _set_parent_(self: TStatement, parent: Statement) -> TStatement:
        if self._parent_statement_ is not None:
            raise ValueError("Statement already has a parent.")
        if parent is None:
            return self
        self._parent_statement_ = parent
        self._is_static_ = False
        return self

    def _suppress_(self):
        if self._was_evaluated_:
            return self
        self._was_evaluated_ = True
        if self._parent_statement_ is not None:
            self._parent_statement_._suppress_()
        return self

    def __del__(self):
        if (
            not self._was_evaluated_
            and not self._is_static_
            and not Statement.__unevaluated_warning_shown
        ):
            warn("Some statement(s) were not evaluated.", RuntimeWarning)
            Statement.__unevaluated_warning_shown = True
