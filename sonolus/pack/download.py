from pathlib import Path

from sonolus.pack.bundles import (
    LevelBundle,
    SkinBundle,
    BackgroundBundle,
    EffectBundle,
    ParticleBundle,
    EngineBundle,
)
from sonolus.server.server import SonolusServer


def download_homepage(
    server: SonolusServer,
    path: str | Path,
    localization: str = "en",
) -> None:
    path = Path(path)

    info = server.info(localization=localization)

    (path / "levels").mkdir(parents=True, exist_ok=True)
    (path / "skins").mkdir(parents=True, exist_ok=True)
    (path / "backgrounds").mkdir(parents=True, exist_ok=True)
    (path / "effects").mkdir(parents=True, exist_ok=True)
    (path / "particles").mkdir(parents=True, exist_ok=True)
    (path / "engines").mkdir(parents=True, exist_ok=True)

    for level in info.levels.items:
        level = server.level(level.name)
        LevelBundle.from_item(
            server, level.item, localization=localization, description=level.description
        ).save(path / "levels" / level.item.name)

    for skin in info.skins.items:
        skin = server.skin(skin.name)
        SkinBundle.from_item(
            server, skin.item, localization=localization, description=skin.description
        ).save(path / "skins" / skin.item.name)

    for background in info.backgrounds.items:
        background = server.background(background.name)
        BackgroundBundle.from_item(
            server,
            background.item,
            localization=localization,
            description=background.description,
        ).save(path / "backgrounds" / background.item.name)

    for effect in info.effects.items:
        effect = server.effect(effect.name)
        EffectBundle.from_item(
            server,
            effect.item,
            localization=localization,
            description=effect.description,
        ).save(path / "effects" / effect.item.name)

    for particle in info.particles.items:
        particle = server.particle(particle.name)
        ParticleBundle.from_item(
            server,
            particle.item,
            localization=localization,
            description=particle.description,
        ).save(path / "particles" / particle.item.name)

    for engine in info.engines.items:
        engine = server.engine(engine.name)
        EngineBundle.from_item(
            server,
            engine.item,
            localization=localization,
            description=engine.description,
        ).save(path / "engines" / engine.item.name)
