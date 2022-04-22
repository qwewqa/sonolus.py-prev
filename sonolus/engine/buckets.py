from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sonolus.backend.ir import Location, MemoryBlock, IRConst
from sonolus.engine.functions.sls_func import sls_func
from sonolus.engine.statements.primitive import Num
from sonolus.engine.statements.struct import Struct


@dataclass
class Bucket:
    sprites: list[BucketSprite]


@dataclass
class BucketSprite:
    id: int
    x: float
    y: float
    w: float
    h: float
    rotation: float = 0


class BucketStruct(Struct):
    min_perfect: Num
    max_perfect: Num
    min_great: Num
    max_great: Num
    min_good: Num
    max_good: Num

    @classmethod
    @sls_func
    def simple(cls, perfect, great, good):
        return BucketStruct(perfect, perfect, great, great, good, good)


class _BucketStructWithMetadata(Protocol):
    index: int


def judgement_bucket(
    sprites: list[BucketSprite],
) -> BucketStruct | _BucketStructWithMetadata:
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
            accessor = BucketStruct._create_(
                Location(MemoryBlock.LEVEL_BUCKET, IRConst(offset))
            )._standalone_()
            accessor.index = index
            setattr(cls, k, accessor)
            offset += BucketStruct._size_
            index += 1
        cls._bucket_entries_ = bucket_entries
