from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Any
from urllib.parse import urlparse

from sonolus.server.server import SonolusServer
from sonolus.server.srl import SRL


class Resource(Protocol):
    format: str | None

    def get(self) -> bytes:
        ...

    def save(self, path: str | Path) -> None:
        path = Path(path)
        if self.format is not None:
            path = Path(f"{path}.{self.format}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.get())


@dataclass
class JSONResource(Resource):
    value: Any

    @property
    def format(self) -> str:
        return "json"

    def get(self) -> bytes:
        return json.dumps(self.value).encode("utf-8")


@dataclass
class BinaryResource(Resource):
    format: str | None
    value: bytes

    def get(self) -> bytes:
        return self.value


@dataclass
class LocalResource(Resource):
    path: str | Path

    @property
    def format(self) -> str:
        return Path(self.path).suffix[1:] or None

    def get(self) -> bytes:
        return open(self.path, "rb").read()


@dataclass
class RemoteResource(Resource):
    server: SonolusServer
    srl: SRL

    @property
    def format(self) -> str:
        return Path(urlparse(self.srl.url).path).suffix[1:] or None

    def get(self) -> bytes:
        return self.server.download_srl(self.srl)


EMPTY_PNG = BinaryResource(
    format="png",
    value=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01",
)

EMPTY_MP3 = BinaryResource(
    format="mp3",
    value=b"\xff\xf3\x14\xc4\x00\x00\x00\x03H\x00\x00\x00\x00LAME3.96.1U\xff\xf3\x14\xc4\x0b\x00\x00\x03H\x00\x00\x00\x00UUUUUUUUUUU\xff\xf3\x14\xc4\x16\x00\x00\x03H\x00\x00\x00\x00UUUUUUUUUUU\xff\xf3\x14\xc4!\x00\x00\x03H\x00\x00\x00\x00UUUUUUUUUUU",
)
