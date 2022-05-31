from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
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

    def save(self, path):
        with open(path, "wb") as f:
            f.write(gzip.compress(json.dumps(self.to_dict()).encode("utf-8")))

    def save_uncompressed(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)


@dataclass
class CompiledEntity:
    archetype: int
    data: CompiledEntityData

    def to_dict(self):
        return {"archetype": self.archetype, "data": self.data.to_dict()}


@dataclass
class CompiledEntityData:
    index: int
    values: list[float]

    def to_dict(self):
        return {"index": self.index, "values": self.values}
