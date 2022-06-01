from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from sonolus.engine.engine import CompiledEngine
from sonolus.engine.level import CompiledLevel
from sonolus.pack.resource import (
    Resource,
    RemoteResource,
    JSONResource,
    EMPTY_PNG,
    EMPTY_MP3,
)
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

    def merge_localizations(self, other: LevelInfo) -> LevelInfo:
        return LevelInfo(
            version=self.version,
            rating=self.rating,
            engine=self.engine,
            useSkin=self.useSkin,
            useBackground=self.useBackground,
            useEffect=self.useEffect,
            useParticle=self.useParticle,
            title=self.title | other.title,
            artists=self.artists | other.artists,
            author=self.author | other.author,
            description=self.description | other.description,
            meta=self.meta,
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

    def merge_localizations(self, other: LevelBundle) -> LevelBundle:
        return LevelBundle(
            info=self.info.merge_localizations(other.info),
            cover=self.cover,
            bgm=self.bgm,
            preview=self.preview,
            data=self.data,
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

    def merge_localizations(self, other: SkinInfo) -> SkinInfo:
        return SkinInfo(
            version=self.version,
            title=self.title | other.title,
            subtitle=self.subtitle | other.subtitle,
            author=self.author | other.author,
            description=self.description | other.description,
            meta=self.meta,
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

    def merge_localizations(self, other: SkinBundle) -> SkinBundle:
        return SkinBundle(
            info=self.info.merge_localizations(other.info),
            thumbnail=self.thumbnail,
            data=self.data,
            texture=self.texture,
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

    def merge_localizations(self, other: BackgroundInfo) -> BackgroundInfo:
        return BackgroundInfo(
            version=self.version,
            title=self.title | other.title,
            subtitle=self.subtitle | other.subtitle,
            author=self.author | other.author,
            description=self.description | other.description,
            meta=self.meta,
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

    def merge_localizations(self, other: BackgroundBundle) -> BackgroundBundle:
        return BackgroundBundle(
            info=self.info.merge_localizations(other.info),
            thumbnail=self.thumbnail,
            data=self.data,
            image=self.image,
            configuration=self.configuration,
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

    def merge_localizations(self, other: EffectInfo) -> EffectInfo:
        return EffectInfo(
            version=self.version,
            title=self.title | other.title,
            subtitle=self.subtitle | other.subtitle,
            author=self.author | other.author,
            description=self.description | other.description,
            meta=self.meta,
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
        clip_data = data.get()
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
            data=JSONResource(clip_data),
            clips=clips,
        )

    def merge_localizations(self, other: EffectBundle) -> EffectBundle:
        return EffectBundle(
            self.info.merge_localizations(other.info),
            self.thumbnail,
            self.data,
            self.clips,
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

    def merge_localizations(self, other: ParticleInfo) -> ParticleInfo:
        return ParticleInfo(
            version=self.version,
            title=self.title | other.title,
            subtitle=self.subtitle | other.subtitle,
            author=self.author | other.author,
            description=self.description | other.description,
            meta=self.meta,
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

    def merge_localizations(self, other: ParticleBundle) -> ParticleBundle:
        return ParticleBundle(
            self.info.merge_localizations(other.info),
            self.thumbnail,
            self.data,
            self.texture,
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

    def merge_localizations(self, other: EngineInfo) -> EngineInfo:
        return EngineInfo(
            version=self.version,
            title=self.title | other.title,
            subtitle=self.subtitle | other.subtitle,
            author=self.author | other.author,
            description=self.description | other.description,
            skin=self.skin,
            background=self.background,
            effect=self.effect,
            particle=self.particle,
            meta=self.meta,
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

    def merge_localizations(self, other: EngineBundle) -> EngineBundle:
        return EngineBundle(
            self.info.merge_localizations(other.info),
            self.thumbnail,
            self.data,
            self.rom,
            self.configuration,
        )


def make_engine_bundle(
    engine: CompiledEngine,
    *,
    version: int = 5,
    title: LocalizationText,
    subtitle: LocalizationText,
    author: LocalizationText,
    description: LocalizationText,
    skin: str,
    background: str,
    effect: str,
    particle: str,
    meta: Any = None,
    thumbnail: Resource = EMPTY_PNG,
) -> EngineBundle:
    return EngineBundle(
        info=EngineInfo(
            version=version,
            title=title,
            subtitle=subtitle,
            author=author,
            description=description,
            skin=skin,
            background=background,
            effect=effect,
            particle=particle,
            meta=meta,
        ),
        thumbnail=thumbnail,
        data=JSONResource(engine.get_data()),
        rom=None,
        configuration=JSONResource(engine.get_configuration()),
    )


def make_level_bundle(
    level: CompiledLevel,
    *,
    version: int = 1,
    rating: float = 5,
    engine: str,
    use_skin: Use = Use(),
    use_background: Use = Use(),
    use_effect: Use = Use(),
    use_particle: Use = Use(),
    title: LocalizationText,
    artists: LocalizationText,
    author: LocalizationText,
    description: LocalizationText,
    meta: Any = None,
    cover: Resource = EMPTY_PNG,
    bgm: Resource = EMPTY_MP3,
    preview: Resource = EMPTY_MP3,
) -> LevelBundle:
    return LevelBundle(
        info=LevelInfo(
            version=version,
            rating=rating,
            engine=engine,
            useSkin=use_skin,
            useBackground=use_background,
            useEffect=use_effect,
            useParticle=use_particle,
            title=title,
            artists=artists,
            author=author,
            description=description,
            meta=meta,
        ),
        cover=cover,
        bgm=bgm,
        preview=preview,
        data=JSONResource(level.to_dict()),
    )
