from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, ClassVar, Any
from urllib.parse import urlparse

from sonolus.server.server import SonolusServer
from sonolus.server.srl import SRL


class Resource(Protocol):
    format: str | None

    def load(self) -> bytes:
        ...

    def save(self, path: str | Path) -> None:
        path = Path(path)
        if self.format is not None:
            path = Path(f"{path}.{self.format}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.load())


@dataclass
class JsonResource(Resource):
    value: Any

    @property
    def format(self) -> str:
        return "json"

    def load(self) -> bytes:
        return json.dumps(self.value).encode("utf-8")


@dataclass
class BinaryResource(Resource):
    format: str | None
    value: bytes

    def load(self) -> bytes:
        return self.value


@dataclass
class LocalResource(Resource):
    path: str | Path

    @property
    def format(self) -> str:
        return Path(self.path).suffix[1:] or None

    def load(self) -> bytes:
        return open(self.path, "rb").read()


@dataclass
class RemoteResource(Resource):
    server: SonolusServer
    srl: SRL

    @property
    def format(self) -> str:
        return Path(urlparse(self.srl.url).path).suffix[1:] or None

    def load(self) -> bytes:
        return self.server.download_srl(self.srl)
