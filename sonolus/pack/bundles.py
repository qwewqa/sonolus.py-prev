from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from sonolus.pack.resource import Resource, RemoteResource, JsonResource
from sonolus.server.items import (
    LevelItem,
    UseItem,
    SkinItem,
    BackgroundItem,
    EffectItem,
    ParticleItem,
    EngineItem,
)
from sonolus.server.server import SonolusServer
from sonolus.server.srl import EffectClip

LocalizationText = dict[str, str]


class Use(BaseModel):
    useDefault: bool = True
    item: str | None = None

    @classmethod
    def from_item(cls, item: UseItem) -> Use:
        return cls(
            useDefault=item.useDefault, item=item.item.name if item.item else None
        )


class LevelInfo(BaseModel):
    version: int
    rating: float
    engine: str
    useSkin: Use
    useBackground: Use
    useEffect: Use
    useParticle: Use
    title: LocalizationText
    artists: LocalizationText
    author: LocalizationText
    description: LocalizationText
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: LevelItem,
        localization: str = "en",
        description: str = "",
    ) -> LevelInfo:
        return cls(
            version=item.version,
            rating=item.rating,
            engine=item.engine.name,
            useSkin=Use.from_item(item.useSkin),
            useBackground=Use.from_item(item.useBackground),
            useEffect=Use.from_item(item.useEffect),
            useParticle=Use.from_item(item.useParticle),
            title={localization: item.title},
            artists={localization: item.artists},
            author={localization: item.author},
            description={localization: description},
        )


@dataclass
class LevelBundle:
    info: LevelInfo
    cover: Resource
    bgm: Resource
    preview: Resource
    data: Resource

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.cover.save(path / "cover")
        self.bgm.save(path / "bgm")
        self.preview.save(path / "preview")
        self.data.save(path / "data")

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: LevelItem,
        localization: str = "en",
        description: str = "",
    ):
        return cls(
            info=LevelInfo.from_item(item, localization, description),
            cover=RemoteResource(server, item.cover),
            bgm=RemoteResource(server, item.bgm),
            preview=RemoteResource(server, item.preview),
            data=RemoteResource(server, item.data),
        )


class SkinInfo(BaseModel):
    version: int
    title: LocalizationText
    subtitle: LocalizationText
    author: LocalizationText
    description: LocalizationText
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: SkinItem,
        localization: str = "en",
        description: str = "",
    ) -> SkinInfo:
        return cls(
            version=item.version,
            title={localization: item.title},
            subtitle={localization: item.subtitle},
            author={localization: item.author},
            description={localization: description},
        )


@dataclass
class SkinBundle:
    info: SkinInfo
    thumbnail: Resource
    data: Resource
    texture: Resource

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.thumbnail.save(path / "thumbnail")
        self.data.save(path / "data")
        self.texture.save(path / "texture")

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: SkinItem,
        localization: str = "en",
        description: str = "",
    ):
        return cls(
            info=SkinInfo.from_item(item, localization, description),
            thumbnail=RemoteResource(server, item.thumbnail),
            data=RemoteResource(server, item.data),
            texture=RemoteResource(server, item.texture),
        )


class BackgroundInfo(BaseModel):
    version: int
    title: LocalizationText
    subtitle: LocalizationText
    author: LocalizationText
    description: LocalizationText
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: BackgroundItem,
        localization: str = "en",
        description: str = "",
    ) -> BackgroundInfo:
        return cls(
            version=item.version,
            title={localization: item.title},
            subtitle={localization: item.subtitle},
            author={localization: item.author},
            description={localization: description},
        )


@dataclass
class BackgroundBundle:
    info: BackgroundInfo
    thumbnail: Resource
    data: Resource
    image: Resource
    configuration: Resource

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.thumbnail.save(path / "thumbnail")
        self.data.save(path / "data")
        self.image.save(path / "image")
        self.configuration.save(path / "configuration")

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: BackgroundItem,
        localization: str = "en",
        description: str = "",
    ):
        return cls(
            info=BackgroundInfo.from_item(item, localization, description),
            thumbnail=RemoteResource(server, item.thumbnail),
            data=RemoteResource(server, item.data),
            image=RemoteResource(server, item.image),
            configuration=RemoteResource(server, item.configuration),
        )


class EffectInfo(BaseModel):
    version: int
    title: LocalizationText
    subtitle: LocalizationText
    author: LocalizationText
    description: LocalizationText
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: EffectItem,
        localization: str = "en",
        description: str = "",
    ) -> EffectInfo:
        return cls(
            version=item.version,
            title={localization: item.title},
            subtitle={localization: item.subtitle},
            author={localization: item.author},
            description={localization: description},
        )


@dataclass
class EffectBundle:
    info: EffectInfo
    thumbnail: Resource
    data: Resource
    clips: dict[int, Resource]

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.thumbnail.save(path / "thumbnail")
        self.data.save(path / "data")
        for cid, clip in self.clips.items():
            clip.save(path / str(cid))

    @staticmethod
    def unpack_clip_data(data: RemoteResource) -> dict:
        clip_data = data.load()
        if data.format is None:
            clip_data = gzip.decompress(clip_data)
        return json.loads(clip_data)

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: EffectItem,
        localization: str = "en",
        description: str = "",
    ):
        data = RemoteResource(server, item.data)
        clip_data = cls.unpack_clip_data(data)
        clips = {}
        for clip in clip_data["clips"]:
            clips[clip["id"]] = RemoteResource(server, EffectClip(**clip["clip"]))
            clip["clip"] = str(clip["id"])
        return cls(
            info=EffectInfo.from_item(item, localization, description),
            thumbnail=RemoteResource(server, item.thumbnail),
            data=JsonResource(clip_data),
            clips=clips,
        )


class ParticleInfo(BaseModel):
    version: int
    title: LocalizationText
    subtitle: LocalizationText
    author: LocalizationText
    description: LocalizationText
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: ParticleItem,
        localization: str = "en",
        description: str = "",
    ) -> ParticleInfo:
        return cls(
            version=item.version,
            title={localization: item.title},
            subtitle={localization: item.subtitle},
            author={localization: item.author},
            description={localization: description},
        )


@dataclass
class ParticleBundle:
    info: ParticleInfo
    thumbnail: Resource
    data: Resource
    texture: Resource

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.thumbnail.save(path / "thumbnail")
        self.data.save(path / "data")
        self.texture.save(path / "texture")

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: ParticleItem,
        localization: str = "en",
        description: str = "",
    ):
        return cls(
            info=ParticleInfo.from_item(item, localization, description),
            thumbnail=RemoteResource(server, item.thumbnail),
            data=RemoteResource(server, item.data),
            texture=RemoteResource(server, item.texture),
        )


class EngineInfo(BaseModel):
    version: int
    title: LocalizationText
    subtitle: LocalizationText
    author: LocalizationText
    description: LocalizationText
    skin: str
    background: str
    effect: str
    particle: str
    meta: Any = None

    @classmethod
    def from_item(
        cls,
        item: EngineItem,
        localization: str = "en",
        description: str = "",
    ) -> EngineInfo:
        return cls(
            version=item.version,
            title={localization: item.title},
            subtitle={localization: item.subtitle},
            author={localization: item.author},
            description={localization: description},
            skin=item.skin.name,
            background=item.background.name,
            effect=item.effect.name,
            particle=item.particle.name,
        )


@dataclass
class EngineBundle:
    info: EngineInfo
    thumbnail: Resource
    data: Resource
    rom: Resource | None
    configuration: Resource

    def save(self, path: str | Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "info.json").open("w") as f:
            f.write(self.info.json(exclude_none=True))
        self.thumbnail.save(path / "thumbnail")
        self.data.save(path / "data")
        if self.rom is not None:
            self.rom.save(path / "rom")
        self.configuration.save(path / "configuration")

    @classmethod
    def from_item(
        cls,
        server: SonolusServer,
        item: EngineItem,
        localization: str = "en",
        description: str = "",
    ):
        return cls(
            info=EngineInfo.from_item(item, localization, description),
            thumbnail=RemoteResource(server, item.thumbnail),
            data=RemoteResource(server, item.data),
            rom=RemoteResource(server, item.rom) if item.rom is not None else None,
            configuration=RemoteResource(server, item.configuration),
        )
