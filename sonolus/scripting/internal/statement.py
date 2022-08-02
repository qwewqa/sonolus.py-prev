from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TypeVar, Callable
from warnings import warn

from sonolus.backend.evaluation import Scope

TStatement = TypeVar("TStatement", bound="Statement")


class Statement:
    _parent_statement_: Statement | None = None
    _attributes_: StatementAttributes
    _was_evaluated_: bool = False

    __unevaluated_warning_shown = False

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, attributes: StatementAttributes = None):
        self._attributes_ = (
            attributes and dataclasses.replace(attributes) or StatementAttributes()
        )
        if _discarding:
            self._attributes_.is_discarded = True

    def _evaluate_(self, scope: Scope) -> Scope:
        return scope

    def _set_parent_(self: TStatement, parent: Statement) -> TStatement:
        if self._parent_statement_ is not None:
            raise ValueError("Statement already has a parent.")
        if parent is None:
            return self
        self._parent_statement_ = parent
        self._attributes_.is_static = False
        return self

    def __del__(self):
        if (
            not self._was_evaluated_
            and not self._attributes_.is_static
            and not self._attributes_.is_discarded
            and not Statement.__unevaluated_warning_shown
        ):
            warn("Some statement(s) were not evaluated.", RuntimeWarning)
            Statement.__unevaluated_warning_shown = True


@dataclass
class StatementAttributes:
    is_static: bool = False
    is_discarded: bool = False


_discarding = False


T = TypeVar("T", bound="Statement")


def run_discarding(fn: Callable[[], T]) -> T:
    global _discarding
    _discarding = True
    try:
        return fn()
    finally:
        _discarding = False
