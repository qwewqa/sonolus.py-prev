from __future__ import annotations

import json
from typing import TypeVar, Generic
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from pydantic import BaseModel
from pydantic.generics import GenericModel

from sonolus.server.items import (
    LevelItem,
    SkinItem,
    BackgroundItem,
    EffectItem,
    ParticleItem,
    EngineItem,
    ItemList,
    ItemDetails,
)
from sonolus.server.search import Search
from sonolus.server.srl import SRL


class SonolusServer:
    def __init__(self, url: str):
        if url[-1] != "/":
            url += "/"
        self.url = url

    def info(self, localization: str = "en") -> ServerInfo:
        return ServerInfo(**self.get_json("/info", localization=localization))

    def levels(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[LevelItem]:
        return ItemList[LevelItem](
            **self.get_json(
                "/levels/list", page=page, localization=localization, **search
            )
        )

    def level(self, name: str, localization: str = "en") -> ItemDetails[LevelItem]:
        return ItemDetails[LevelItem](
            **self.get_json(f"/levels/{name}", localization=localization)
        )

    def skins(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[SkinItem]:
        return ItemList[SkinItem](
            **self.get_json(
                "/skins/list", page=page, localization=localization, **search
            )
        )

    def skin(self, name: str, localization: str = "en") -> ItemDetails[SkinItem]:
        return ItemDetails[SkinItem](
            **self.get_json(f"/skins/{name}", localization=localization)
        )

    def backgrounds(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[BackgroundItem]:
        return ItemList[BackgroundItem](
            **self.get_json(
                "/backgrounds/list", page=page, localization=localization, **search
            )
        )

    def background(
        self, name: str, localization: str = "en"
    ) -> ItemDetails[BackgroundItem]:
        return ItemDetails[BackgroundItem](
            **self.get_json(f"/backgrounds/{name}", localization=localization)
        )

    def effects(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[EffectItem]:
        return ItemList[EffectItem](
            **self.get_json(
                "/effects/list", page=page, localization=localization, **search
            )
        )

    def effect(self, name: str, localization: str = "en") -> ItemDetails[EffectItem]:
        return ItemDetails[EffectItem](
            **self.get_json(f"/effects/{name}", localization=localization)
        )

    def particles(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[ParticleItem]:
        return ItemList[ParticleItem](
            **self.get_json(
                "/particles/list", page=page, localization=localization, **search
            )
        )

    def particle(
        self, name: str, localization: str = "en"
    ) -> ItemDetails[ParticleItem]:
        return ItemDetails[ParticleItem](
            **self.get_json(f"/particles/{name}", localization=localization)
        )

    def engines(
        self, page: int = 0, localization: str = "en", **search: str
    ) -> ItemList[EngineItem]:
        return ItemList[EngineItem](
            **self.get_json(
                "/engines/list", page=page, localization=localization, **search
            )
        )

    def engine(self, name: str, localization: str = "en") -> ItemDetails[EngineItem]:
        return ItemDetails[EngineItem](
            **self.get_json(f"/engines/{name}", localization=localization)
        )

    def download_srl(self, srl: SRL) -> bytes:
        return self.get_bytes(srl.url)

    def get_json(self, url: str, **kwargs):
        return json.load(urlopen(self.request(f"{url}?{urlencode(kwargs)}")))

    def get_bytes(self, url: str) -> bytes:
        return urlopen(self.request(url)).read()

    def request(self, url):
        return Request(self.join_url(url), headers={"User-Agent": "Mozilla/5.0"})

    def join_url(self, url: str):
        if url[0] == "/":
            return self.url + url[1:]
        return url


TItem = TypeVar("TItem")


class Section(GenericModel, Generic[TItem]):
    items: list[TItem]
    search: Search


class ServerInfo(BaseModel):
    levels: Section[LevelItem]
    skins: Section[SkinItem]
    backgrounds: Section[BackgroundItem]
    effects: Section[EffectItem]
    particles: Section[ParticleItem]
    engines: Section[EngineItem]
