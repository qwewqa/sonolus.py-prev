from functools import reduce
from pathlib import Path
from typing import Collection, Literal
from urllib.error import HTTPError

from sonolus.pack.bundles import (
    LevelBundle,
    SkinBundle,
    BackgroundBundle,
    EffectBundle,
    ParticleBundle,
    EngineBundle,
)
from sonolus.server.items import ItemList, ItemDetails
from sonolus.server.server import SonolusServer

_DOWNLOAD_CATEGORIES = {
    "levels": ("levels", LevelBundle, SonolusServer.levels, SonolusServer.level),
    "skins": ("skins", SkinBundle, SonolusServer.skins, SonolusServer.skin),
    "backgrounds": ("backgrounds", BackgroundBundle, SonolusServer.backgrounds, SonolusServer.background),
    "effects": ("effects", EffectBundle, SonolusServer.effects, SonolusServer.effect),
    "particles": ("particles", ParticleBundle, SonolusServer.particles, SonolusServer.particle),
    "engines": ("engines", EngineBundle, SonolusServer.engines, SonolusServer.engine),
}

DownloadCategory = Literal["levels", "skins", "backgrounds", "effects", "particles", "engines"]


def download_server(
    server: SonolusServer,
    path: str | Path,
    *,
    localizations: Collection[str] = ("en",),
    categories: Collection[DownloadCategory] = ("levels", "skins", "backgrounds", "effects", "particles", "engines"),
    limit: int | None | Literal["homepage"] = "homepage",
) -> None:
    path = Path(path)

    info = server.info()

    for category in categories:
        name, bundle_type, get_list, get_item = _DOWNLOAD_CATEGORIES[category]
        category_path = path / name
        category_path.mkdir(parents=True, exist_ok=True)

        items: list
        if limit == "homepage":
            items = getattr(info, name).items
        else:
            items = []
            page = 0
            while True:
                page_items: ItemList = get_list(server, page=page)
                items.extend(page_items.items)
                page += 1
                if (limit is not None and len(items) >= limit) or (page >= page_items.pageCount):
                    break

        if isinstance(limit, int) and len(items) > limit:
            items = items[:limit]

        for item in items:
            try:
                details: dict[str, ItemDetails] = {l: get_item(server, item.name, localization=l) for l in localizations}
                bundles = [bundle_type.from_item(server, d.item, localization=l, description=d.description) for l, d in details.items()]
                bundle = reduce(lambda a, b: a.merge_localizations(b), bundles)
                bundle.save(category_path / item.name)
                print(f"Downloaded {category}/{item.name}")
            except (HTTPError, PermissionError) as e:
                print(f"Failed to download {category}/{item.name}: {e}")
