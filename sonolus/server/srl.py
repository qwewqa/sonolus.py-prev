from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ResourceType(str, Enum):
    LevelCover = "LevelCover"
    LevelBgm = "LevelBgm"
    LevelPreview = "LevelPreview"
    LevelData = "LevelData"
    SkinThumbnail = "SkinThumbnail"
    SkinData = "SkinData"
    SkinTexture = "SkinTexture"
    BackgroundThumbnail = "BackgroundThumbnail"
    BackgroundData = "BackgroundData"
    BackgroundImage = "BackgroundImage"
    BackgroundConfiguration = "BackgroundConfiguration"
    EffectThumbnail = "EffectThumbnail"
    EffectData = "EffectData"
    EffectClip = "EffectClip"
    ParticleThumbnail = "ParticleThumbnail"
    ParticleData = "ParticleData"
    ParticleTexture = "ParticleTexture"
    EngineThumbnail = "EngineThumbnail"
    EngineData = "EngineData"
    EngineRom = "EngineRom"
    EngineConfiguration = "EngineConfiguration"


class SRL(BaseModel):
    type: ResourceType
    hash: str
    url: str

    def __hash__(self):
        return hash((self.type, self.hash, self.url))

    class Config:
        allow_mutation = False


class LevelCover(SRL):
    type: Literal["LevelCover"] = "LevelCover"


class LevelBgm(SRL):
    type: Literal["LevelBgm"] = "LevelBgm"


class LevelPreview(SRL):
    type: Literal["LevelPreview"] = "LevelPreview"


class LevelData(SRL):
    type: Literal["LevelData"] = "LevelData"


class SkinThumbnail(SRL):
    type: Literal["SkinThumbnail"] = "SkinThumbnail"


class SkinData(SRL):
    type: Literal["SkinData"] = "SkinData"


class SkinTexture(SRL):
    type: Literal["SkinTexture"] = "SkinTexture"


class BackgroundThumbnail(SRL):
    type: Literal["BackgroundThumbnail"] = "BackgroundThumbnail"


class BackgroundData(SRL):
    type: Literal["BackgroundData"] = "BackgroundData"


class BackgroundImage(SRL):
    type: Literal["BackgroundImage"] = "BackgroundImage"


class BackgroundConfiguration(SRL):
    type: Literal["BackgroundConfiguration"] = "BackgroundConfiguration"


class EffectThumbnail(SRL):
    type: Literal["EffectThumbnail"] = "EffectThumbnail"


class EffectData(SRL):
    type: Literal["EffectData"] = "EffectData"


class EffectClip(SRL):
    type: Literal["EffectClip"] = "EffectClip"


class ParticleThumbnail(SRL):
    type: Literal["ParticleThumbnail"] = "ParticleThumbnail"


class ParticleData(SRL):
    type: Literal["ParticleData"] = "ParticleData"


class ParticleTexture(SRL):
    type: Literal["ParticleTexture"] = "ParticleTexture"


class EngineThumbnail(SRL):
    type: Literal["EngineThumbnail"] = "EngineThumbnail"


class EngineData(SRL):
    type: Literal["EngineData"] = "EngineData"


class EngineRom(SRL):
    type: Literal["EngineRom"] = "EngineRom"


class EngineConfiguration(SRL):
    type: Literal["EngineConfiguration"] = "EngineConfiguration"


if __name__ == "__main__":
    for name in ResourceType:
        print(
            f"""\
class {name}(SRL):
    type: Literal["{name}"] = "{name}"
    """
        )
