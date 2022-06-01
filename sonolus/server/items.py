from __future__ import annotations

from typing import TypeVar, Generic, Literal

from pydantic import BaseModel
from pydantic.generics import GenericModel

from sonolus.server.search import Search
from sonolus.server.srl import (
    LevelCover,
    LevelBgm,
    LevelPreview,
    LevelData,
    SkinThumbnail,
    SkinData,
    SkinTexture,
    BackgroundThumbnail,
    BackgroundData,
    BackgroundImage,
    BackgroundConfiguration,
    EffectThumbnail,
    EffectData,
    ParticleThumbnail,
    ParticleData,
    ParticleTexture,
    EngineThumbnail,
    EngineData,
    EngineRom,
    EngineConfiguration,
)

TItem = TypeVar("TItem")


class ItemList(GenericModel, Generic[TItem]):
    pageCount: int
    items: list[TItem]
    search: Search


class ItemDetails(GenericModel, Generic[TItem]):
    item: TItem
    description: str
    recommended: list[TItem]


class UseItem(GenericModel, Generic[TItem]):
    useDefault: bool
    item: TItem | None = None


class LevelItem(BaseModel):
    name: str
    version: Literal[1]
    rating: float
    title: str
    artists: str
    author: str
    engine: EngineItem
    useSkin: UseItem[SkinItem]
    useBackground: UseItem[BackgroundItem]
    useEffect: UseItem[EffectItem]
    useParticle: UseItem[ParticleItem]
    cover: LevelCover
    bgm: LevelBgm
    preview: LevelPreview
    data: LevelData


class SkinItem(BaseModel):
    name: str
    version: Literal[2]
    title: str
    subtitle: str
    author: str
    thumbnail: SkinThumbnail
    data: SkinData
    texture: SkinTexture


class BackgroundItem(BaseModel):
    name: str
    version: Literal[2]
    title: str
    subtitle: str
    author: str
    thumbnail: BackgroundThumbnail
    data: BackgroundData
    image: BackgroundImage
    configuration: BackgroundConfiguration


class EffectItem(BaseModel):
    name: str
    version: Literal[2]
    title: str
    subtitle: str
    author: str
    thumbnail: EffectThumbnail
    data: EffectData


class ParticleItem(BaseModel):
    name: str
    version: Literal[1]
    title: str
    subtitle: str
    author: str
    thumbnail: ParticleThumbnail
    data: ParticleData
    texture: ParticleTexture


class EngineItem(BaseModel):
    name: str
    version: Literal[5]
    title: str
    subtitle: str
    author: str
    skin: SkinItem
    background: BackgroundItem
    effect: EffectItem
    particle: ParticleItem
    thumbnail: EngineThumbnail
    data: EngineData
    rom: EngineRom | None = None
    configuration: EngineConfiguration


LevelItem.update_forward_refs()
SkinItem.update_forward_refs()
BackgroundItem.update_forward_refs()
EffectItem.update_forward_refs()
ParticleItem.update_forward_refs()
EngineItem.update_forward_refs()
