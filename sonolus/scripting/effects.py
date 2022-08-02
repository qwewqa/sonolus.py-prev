from __future__ import annotations

from enum import Enum

from sonolus.scripting.internal.value import convert_value
from sonolus.scripting.function import sls_func
from sonolus.scripting.number import Num
from sonolus.scripting.boolean import Bool
from sonolus.scripting.values import Void
from sonolus.scripting.internal.struct import Struct
from sonolus.scripting.internal.primitive import invoke_builtin

__all__ = (
    "play",
    "play_scheduled",
    "has_effect_clip",
    "EffectClipId",
    "custom_effect_clip_id",
    "Clip",
)


class Clip(Struct):
    id: Num

    @sls_func
    def play(self, dist: Num = 0):
        return play(self.id, dist)

    @sls_func
    def play_scheduled(self, time: Num, dist: Num = 0):
        return play_scheduled(self.id, time, dist)

    @property
    @sls_func
    def available(self) -> Bool:
        return has_effect_clip(self.id)

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
        return cls(id=custom_effect_clip_id(engine_id, clip_id))


@sls_func(ast=False)
def play(id: Num | Clip, dist: Num) -> Void:
    if isinstance(id, Clip):
        id = id.id
    else:
        id = convert_value(id, Num)
    return invoke_builtin("Play", [id, dist])


@sls_func(ast=False)
def play_scheduled(id: Num | Clip, t: Num, dist: Num) -> Void:
    if isinstance(id, Clip):
        id = id.id
    else:
        id = convert_value(id, Num)
    return invoke_builtin("PlayScheduled", [id, t, dist])


@sls_func(ast=False)
def has_effect_clip(id: Num | Clip) -> Bool:
    if isinstance(id, Clip):
        id = id.id
    else:
        id = convert_value(id, Num)
    return invoke_builtin("HasEffectClip", [id], Bool)


def custom_effect_clip_id(engine_id: Num, clip_id: Num) -> Num:
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
