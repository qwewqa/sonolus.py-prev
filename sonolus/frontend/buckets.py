from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sonolus.backend.ir import Location, MemoryBlock, IRConst
from sonolus.frontend.sls_func import sls_func
from sonolus.frontend.primitive import Num, invoke_builtin
from sonolus.frontend.struct import Struct


@dataclass
class Bucket:
    sprites: list[BucketSprite]

    def to_dict(self):
        return {"sprites": [sprite.to_dict() for sprite in self.sprites]}


@dataclass
class BucketSprite:
    id: int
    x: float
    y: float
    w: float
    h: float
    rotation: float = 0

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "rotation": self.rotation,
        }


class BucketData(Struct):
    min_perfect: Num
    max_perfect: Num
    min_great: Num
    max_great: Num
    min_good: Num
    max_good: Num

    @classmethod
    @sls_func
    def simple(cls, perfect, great, good):
        return BucketData(-perfect, perfect, -great, great, -good, good)

    @classmethod
    @sls_func
    def late(cls, perfect, great, good):
        return BucketData(0, perfect, 0, great, 0, good)

    @sls_func
    def __truediv__(self, other: Num) -> BucketData:
        return BucketData(
            self.min_perfect / other,
            self.max_perfect / other,
            self.min_great / other,
            self.max_great / other,
            self.min_good / other,
            self.max_good / other,
        )

    @sls_func
    def judge(self, src: Num, dst: Num) -> Num:
        return invoke_builtin(
            "Judge",
            [
                src,
                dst,
                self.min_perfect,
                self.max_perfect,
                self.min_great,
                self.max_great,
                self.min_good,
                self.max_good,
            ],
            Num,
        )

    @sls_func
    def judge_ms(self, src: Num, dst: Num) -> Num:
        return (self / 1000).judge(src, dst)


class _BucketDataWithMetadata(Protocol):
    index: int


def judgement_bucket(
    sprites: list[BucketSprite],
) -> BucketData | _BucketDataWithMetadata:
    return Bucket(sprites=sprites)  # type: ignore


class BucketConfig:
    _bucket_entries_: dict[str, Bucket]

    def __init_subclass__(cls, **kwargs):
        members = cls.__dict__
        bucket_entries = {}
        offset = 0
        index = 0
        for k, v in members.items():
            if (
                k.startswith("__")
                or callable(k)
                or isinstance(k, (staticmethod, classmethod))
            ):
                continue
            if not isinstance(v, Bucket):
                raise TypeError("Expected all class members to be buckets.")
            bucket_entries[k] = v
            accessor = BucketData._create_(
                Location(MemoryBlock.LEVEL_BUCKET, IRConst(0), offset, None),
            )._set_static_()
            accessor.index = index
            setattr(cls, k, accessor)
            offset += BucketData._size_
            index += 1
        cls._bucket_entries_ = bucket_entries
