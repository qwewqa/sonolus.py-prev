from enum import Enum

from .function import sls_func
from .number import Num
from .boolean import Bool
from .types import Void
from sonolus.engine.primitive import invoke_builtin

__all__ = (
    "Play",
    "PlayScheduled",
    "HasEffectClip",
    "EffectClipId",
)


@sls_func(ast=False)
def Play(id: Num, dist: Num) -> Void:
    return invoke_builtin("Play", [id, dist])


@sls_func(ast=False)
def PlayScheduled(id: Num, t: Num, dist: Num) -> Void:
    return invoke_builtin("PlayScheduled", [id, t, dist])


@sls_func(ast=False)
def HasEffectClip(id: Num) -> Bool:
    return invoke_builtin("HasEffectClip", [id], Bool)


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
