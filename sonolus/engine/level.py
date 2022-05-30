from __future__ import annotations

import gzip
import json
from dataclasses import dataclass


@dataclass
class Level:
    entities: list[Entity]

    def to_dict(self):
        return {
            "entities": [entity.to_dict() for entity in self.entities]
        }

    def save(self, path):
        with open(path, "wb") as f:
            f.write(gzip.compress(json.dumps(self.to_dict()).encode("utf-8")))

    def save_uncompressed(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)


@dataclass
class Entity:
    archetype: int
    data: EntityData

    def to_dict(self):
        return {
            "archetype": self.archetype,
            "data": self.data.to_dict()
        }


@dataclass
class EntityData:
    index: int
    values: list[float]

    def to_dict(self):
        return {
            "index": self.index,
            "values": self.values
        }
