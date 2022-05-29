from dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from typing import Literal, TYPE_CHECKING, TypeVar, ClassVar

from sonolus.backend.ir import MemoryBlock, Location, IRConst
from sonolus.frontend.primitive import Num, Bool


class OptionName(str, Enum):
    OFFSET_AUDIO = "#OFFSET_AUDIO"
    OFFSET_INPUT = "#OFFSET_INPUT"
    SPEED = "#SPEED"
    AUTO = "#AUTO"
    MIRROR = "#MIRROR"
    RANDOM = "#RANDOM"
    HIDDEN = "#HIDDEN"
    EFFECT = "#EFFECT"
    UI = "#UI"
    UI_SIZE = "#UI_SIZE"
    UI_ALPHA = "#UI_ALPHA"
    UI_MENU = "#UI_MENU"
    UI_MENU_SIZE = "#UI_MENU_SIZE"
    UI_MENU_ALPHA = "#UI_MENU_ALPHA"
    UI_JUDGMENT = "#UI_JUDGMENT"
    UI_JUDGMENT_SIZE = "#UI_JUDGMENT_SIZE"
    UI_JUDGMENT_ALPHA = "#UI_JUDGMENT_ALPHA"
    UI_COMBO = "#UI_COMBO"
    UI_COMBO_SIZE = "#UI_COMBO_SIZE"
    UI_COMBO_ALPHA = "#UI_COMBO_ALPHA"
    UI_SCORE = "#UI_SCORE"
    UI_SCORE_SIZE = "#UI_SCORE_SIZE"
    UI_SCORE_ALPHA = "#UI_SCORE_ALPHA"
    STAGE = "#STAGE"
    STAGE_SIZE = "#STAGE_SIZE"
    STAGE_ALPHA = "#STAGE_ALPHA"
    STAGE_TILT = "#STAGE_TILT"
    STAGE_COVER_HORIZONTAL = "#STAGE_COVER_HORIZONTAL"
    STAGE_COVER_VERTICAL = "#STAGE_COVER_VERTICAL"
    STAGE_COVER_ALPHA = "#STAGE_COVER_ALPHA"
    STAGE_ASPECTRATIO_LOCK = "#STAGE_ASPECTRATIO_LOCK"
    STAGE_EFFECT = "#STAGE_EFFECT"
    STAGE_EFFECT_SIZE = "#STAGE_EFFECT_SIZE"
    STAGE_EFFECT_ALPHA = "#STAGE_EFFECT_ALPHA"
    LANE = "#LANE"
    LANE_SIZE = "#LANE_SIZE"
    LANE_ALPHA = "#LANE_ALPHA"
    LANE_EFFECT = "#LANE_EFFECT"
    LANE_EFFECT_SIZE = "#LANE_EFFECT_SIZE"
    LANE_EFFECT_ALPHA = "#LANE_EFFECT_ALPHA"
    JUDGELINE = "#JUDGELINE"
    JUDGELINE_SIZE = "#JUDGELINE_SIZE"
    JUDGELINE_ALPHA = "#JUDGELINE_ALPHA"
    JUDGELINE_EFFECT = "#JUDGELINE_EFFECT"
    JUDGELINE_EFFECT_SIZE = "#JUDGELINE_EFFECT_SIZE"
    JUDGELINE_EFFECT_ALPHA = "#JUDGELINE_EFFECT_ALPHA"
    SLOT = "#SLOT"
    SLOT_SIZE = "#SLOT_SIZE"
    SLOT_ALPHA = "#SLOT_ALPHA"
    SLOT_EFFECT = "#SLOT_EFFECT"
    SLOT_EFFECT_SIZE = "#SLOT_EFFECT_SIZE"
    SLOT_EFFECT_ALPHA = "#SLOT_EFFECT_ALPHA"
    NOTE = "#NOTE"
    NOTE_SPEED = "#NOTE_SPEED"
    NOTE_SIZE = "#NOTE_SIZE"
    NOTE_ALPHA = "#NOTE_ALPHA"
    NOTE_EFFECT = "#NOTE_EFFECT"
    NOTE_EFFECT_SIZE = "#NOTE_EFFECT_SIZE"
    NOTE_EFFECT_ALPHA = "#NOTE_EFFECT_ALPHA"
    MARKER = "#MARKER"
    MARKER_SIZE = "#MARKER_SIZE"
    MARKER_ALPHA = "#MARKER_ALPHA"
    CONNECTOR = "#CONNECTOR"
    CONNECTOR_SIZE = "#CONNECTOR_SIZE"
    CONNECTOR_ALPHA = "#CONNECTOR_ALPHA"
    SIMLINE = "#SIMLINE"
    SIMLINE_SIZE = "#SIMLINE_SIZE"
    SIMLINE_ALPHA = "#SIMLINE_ALPHA"


def slider_option(
    *,
    name: str,
    standard: bool,
    scope: str | None = None,
    default: float,
    min: float,
    max: float,
    step: float,
    display: Literal["number", "percentage"],
) -> Num:
    return SliderOption(  # type: ignore
        name=name,
        standard=standard,
        scope=scope,
        default=default,
        min=min,
        max=max,
        step=step,
        display=display,
    )


def toggle_option(
    *,
    name: str,
    standard: bool,
    scope: str | None = None,
    default: bool,
) -> Bool:
    return ToggleOption(  # type: ignore
        name=name, standard=standard, scope=scope, default=default
    )


@dataclass(kw_only=True)
class Option:
    name: str
    standard: bool
    scope: str | None = None


@dataclass(kw_only=True)
class SliderOption(Option):
    default: float
    min: float
    max: float
    step: float
    display: Literal["number", "percentage"]

    _data_type_ = Num


@dataclass(kw_only=True)
class ToggleOption(Option):
    default: bool

    _data_type_ = Bool


class OptionConfig:
    _option_entries_: dict[str, Option]

    def __init_subclass__(cls, **kwargs):
        members = cls.__dict__
        option_entries = {}
        offset = 0
        for k, v in members.items():
            if (
                k.startswith("__")
                or callable(k)
                or isinstance(k, (staticmethod, classmethod))
            ):
                continue
            if not isinstance(v, (ToggleOption, SliderOption)):
                raise TypeError("Expected all class members to be option types.")
            option_entries[k] = v
            option_type = v._data_type_
            setattr(
                cls,
                k,
                option_type._create_(
                    Location(MemoryBlock.LEVEL_OPTION, IRConst(0), offset, None)
                )._standalone_(),
            )
            offset += option_type._size_
        cls._option_entries_ = option_entries
