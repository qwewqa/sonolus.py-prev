from enum import Enum

from .function import sls_func
from .number import Number
from .boolean import Boolean
from .types import Void
from sonolus.engine.statements.primitive import invoke_builtin

__all__ = (
    "Play",
    "PlayScheduled",
    "HasEffectClip",
    "EffectClipId",
)


@sls_func(ast=False)
def Play(id: Number, dist: Number) -> Void:
    return invoke_builtin("Play", [id, dist])


@sls_func(ast=False)
def PlayScheduled(id: Number, t: Number, dist: Number) -> Void:
    return invoke_builtin("PlayScheduled", [id, t, dist])


@sls_func(ast=False)
def HasEffectClip(id: Number) -> Boolean:
    return invoke_builtin("HasEffectClip", [id], Boolean)


class EffectClipId(int, Enum):
    MISS = 0
    PERFECT = 1
    GREAT = 2
    GOOD = 3

    MISS_ALTERNATIVE = 1000
    PERFECT_ALTERNATIVE = 1001
    GREAT_ALTERNATIVE = 1002
    GOOD_ALTERNATIVE = 1003

    STAGE = 10000
