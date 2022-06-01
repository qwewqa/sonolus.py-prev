from __future__ import annotations

from enum import Enum

from .function import sls_func
from .number import Num
from .boolean import Bool
from .types import Void
from sonolus.frontend.struct import Struct
from sonolus.frontend.primitive import invoke_builtin

__all__ = (
    "Play",
    "PlayScheduled",
    "HasEffectClip",
    "EffectClipId",
    "CustomEffectClipId",
    "Clip",
)


class Clip(Struct):
    id: Num

    @sls_func
    def play(self, dist: Num = 0):
        return Play(self.id, dist)

    @sls_func
    def play_scheduled(self, time: Num, dist: Num = 0):
        return PlayScheduled(self.id, time, dist)

    @property
    @sls_func
    def available(self) -> Bool:
        return HasEffectClip(self.id)

    @sls_func
    def __add__(self, other: Clip) -> Clip:
        return Clip(self.id + other.id)

    @sls_func
    def __sub__(self, other: Clip) -> Clip:
        return Clip(self.id - other.id)

    @classmethod
    def _convert_(cls, value):
        match value:
            case Num():
                return cls(id=value)
            case _:
                return super()._convert_(value)

    @classmethod
    def miss(cls) -> Clip:
        return cls(id=EffectClipId.MISS)

    @classmethod
    def perfect(cls) -> Clip:
        return cls(id=EffectClipId.PERFECT)

    @classmethod
    def great(cls) -> Clip:
        return cls(id=EffectClipId.GREAT)

    @classmethod
    def good(cls) -> Clip:
        return cls(id=EffectClipId.GOOD)

    @classmethod
    def miss_alternative(cls) -> Clip:
        return cls(id=EffectClipId.MISS_ALTERNATIVE)

    @classmethod
    def perfect_alternative(cls) -> Clip:
        return cls(id=EffectClipId.PERFECT_ALTERNATIVE)

    @classmethod
    def great_alternative(cls) -> Clip:
        return cls(id=EffectClipId.GREAT_ALTERNATIVE)

    @classmethod
    def good_alternative(cls) -> Clip:
        return cls(id=EffectClipId.GOOD_ALTERNATIVE)

    @classmethod
    def stage(cls) -> Clip:
        return cls(id=EffectClipId.STAGE)

    @classmethod
    def custom(cls, engine_id: Num, clip_id: Num) -> Clip:
        return cls(id=CustomEffectClipId(engine_id, clip_id))


@sls_func(ast=False)
def Play(id: Num, dist: Num) -> Void:
    return invoke_builtin("Play", [id, dist])


@sls_func(ast=False)
def PlayScheduled(id: Num, t: Num, dist: Num) -> Void:
    return invoke_builtin("PlayScheduled", [id, t, dist])


@sls_func(ast=False)
def HasEffectClip(id: Num) -> Bool:
    return invoke_builtin("HasEffectClip", [id], Bool)


def CustomEffectClipId(engine_id: Num, clip_id: Num) -> Num:
    return 100000 + engine_id * 100 + clip_id


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
