from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar, Generic, Protocol

from sonolus.frontend.script import ScriptMetadata
from sonolus.frontend.value import convert_value

T = TypeVar("T")


class _EntityScript(Protocol[T]):
    _metadata_: ScriptMetadata
    data: T


@dataclass
class Entity(Generic[T]):
    script: _EntityScript[T]
    data: T = None

    def __init__(self, script: _EntityScript[T], data: T = None):
        if data is None:
            data = script._metadata_.data_type._default_()
        else:
            data = convert_value(data, script._metadata_.data_type)

        self.script = script
        self.data = data

    def __iter__(self):
        yield self.script
        yield self.data


@dataclass
class CompiledLevel:
    entities: list[CompiledEntity]

    def to_dict(self):
        return {"entities": [entity.to_dict() for entity in self.entities]}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            entities=[CompiledEntity.from_dict(entity) for entity in data["entities"]]
        )

    @classmethod
    def load(cls, path):
        data = Path(path).read_bytes()
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        return cls.from_dict(json.loads(data.decode("utf-8")))

    def save(self, path):
        Path(path).write_bytes(
            gzip.compress(json.dumps(self.to_dict()).encode("utf-8"))
        )

    def save_uncompressed(self, path):
        Path(path).write_text(json.dumps(self.to_dict()))


@dataclass
class CompiledEntity:
    archetype: int
    data: CompiledEntityData

    def to_dict(self):
        return {"archetype": self.archetype, "data": self.data.to_dict()}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            archetype=data["archetype"], data=CompiledEntityData.from_dict(data["data"])
        )


@dataclass
class CompiledEntityData:
    index: int
    values: list[float]

    def to_dict(self):
        return {"index": self.index, "values": self.values}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(index=data["index"], values=data["values"])
