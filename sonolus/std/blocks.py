from __future__ import annotations

import warnings
from enum import Enum
from typing import Type, TypeVar, overload

from .boolean import *
from .draw import *
from .number import *
from .point import *
from .types import *
from ..backend.ir import MemoryBlock

__all__ = (
    "MemoryBlock",
    "LevelDataStruct",
    "LevelUIStruct",
    "UIHorizontalAlign",
    "LevelUIElement",
    "LevelUIConfigurationEntry",
    "LevelUIConfigurationStruct",
    "LevelScoreStruct",
    "LevelLifeStruct",
    "TouchDataStruct",
    "GetLevelMemory",
    "GetLevelData",
    "GetCustomLevelData",
    "GetLevelOptions",
    "GetLevelTransform",
    "GetLevelBackground",
    "GetLevelUI",
    "GetLevelUIConfiguration",
    "GetLevelScore",
    "GetLevelLife",
    "GetEngineRom",
    "GetTemporaryData",
    "LevelData",
    "LevelTransform",
    "LevelBackground",
    "LevelUI",
    "LevelUIConfiguration",
    "LevelScore",
    "LevelLife",
    "TouchData",
)

T = TypeVar("T", bound=Value)


class LevelDataStruct(Struct):
    time: Number
    delta_time: Number
    aspect_ratio: Number
    audio_offset: Number
    input_offset: Number
    render_scale: Number
    anit_aliasing: Number


class UIHorizontalAlign(int, Enum):
    Left = -1
    Center = 0
    Right = 1


class LevelUIElement(Struct):
    anchor: Point
    pivot: Point
    width: Number
    height: Number
    rotation: Number = 0
    alpha: Number = 1
    horizontal_align: Number = UIHorizontalAlign.Center
    background: Boolean = False


class LevelUIStruct(Struct):
    menu: LevelUIElement
    judgement: LevelUIElement
    combo_value: LevelUIElement
    combo_text: LevelUIElement
    primary_metric_bar: LevelUIElement
    primary_metric_value: LevelUIElement
    secondary_metric_bar: LevelUIElement
    secondary_metric_value: LevelUIElement


class LevelUIConfigurationEntry(Struct):
    scale: Number
    alpha: Number


class LevelUIConfigurationStruct(Struct):
    menu: LevelUIConfigurationEntry
    judgement: LevelUIConfigurationEntry
    combo: LevelUIConfigurationEntry
    primary_metric: LevelUIConfigurationEntry
    secondary_metric: LevelUIConfigurationEntry


class LevelScoreStruct(Struct):
    perfect_multiplier: Number
    great_multiplier: Number
    good_multiplier: Number
    consecutive_perfect_multiplier: Number
    consecutive_perfect_step: Number
    consecutive_perfect_cap: Number
    consecutive_great_multiplier: Number
    consecutive_great_step: Number
    consecutive_great_cap: Number
    consecutive_good_multiplier: Number
    consecutive_good_step: Number
    consecutive_good_cap: Number


class LevelLifeStruct(Struct):
    consecutive_perfect_increment: Number
    consecutive_perfect_step: Number
    consecutive_great_increment: Number
    consecutive_great_step: Number
    consecutive_good_increment: Number
    consecutive_good_step: Number


class TouchDataStruct(Struct):
    id: Number
    started: Boolean
    ended: Boolean
    time: Number
    start_time: Number
    position: Point
    start_position: Point
    delta_position: Point
    velocity_vector: Point
    velocity_magnitude: Number
    velocity_angle: Number


def GetLevelMemory(type_: Type[T], /) -> T:
    if type_._size_ > 255:
        warnings.warn(f"Type {type_} may be too large for level memory.")
    return Pointer[type_](MemoryBlock.LEVEL_MEMORY, 0).deref()


@overload
def GetLevelData() -> LevelDataStruct:
    ...


@overload
def GetLevelData(type_: Type[T]) -> T:
    ...


def GetLevelData(type_: Type[T] = LevelDataStruct, /) -> T:
    if type_._size_ > 255:
        warnings.warn(f"Type {type_} may be too large for level data.")
    return Pointer[type_](MemoryBlock.LEVEL_DATA, 0).deref()


def GetCustomLevelData(type_: Type[T], /) -> T:
    if type_._size_ > 255 - LevelDataStruct._size_:
        warnings.warn(f"Type {type_} may be too large for level data.")
    return Pointer[type_](MemoryBlock.LEVEL_DATA, LevelDataStruct._size_).deref()


def GetLevelOptions(type_: Type[T], /) -> T:
    return Pointer[type_](MemoryBlock.LEVEL_OPTION, 0).deref()


@overload
def GetLevelTransform() -> Array[Number, 4, 4]:
    ...


@overload
def GetLevelTransform(type_: Type[T]) -> T:
    ...


def GetLevelTransform(type_: Type[T] = Array[Array[Number, 4], 4], /) -> T:
    if type_._size_ != 16:
        warnings.warn(f"Type {type_} may have an incorrect size for level transform.")
    return Pointer[type_](MemoryBlock.LEVEL_MEMORY, 0).deref()


@overload
def GetLevelBackground() -> Quad:
    ...


@overload
def GetLevelBackground(type_: Type[T]) -> T:
    ...


def GetLevelBackground(type_: Type[T] = Quad, /) -> T:
    if type_._size_ != 8:
        warnings.warn(f"Type {type_} may have an incorrect size for level background.")
    return Pointer[type_](MemoryBlock.LEVEL_BACKGROUND, 0).deref()


@overload
def GetLevelUI() -> LevelUIStruct:
    ...


@overload
def GetLevelUI(type_: Type[T]) -> T:
    ...


def GetLevelUI(type_: Type[T] = LevelUIStruct, /) -> T:
    if type_._size_ != 80:
        warnings.warn(f"Type {type_} may have an incorrect size for level ui.")
    return Pointer[type_](MemoryBlock.LEVEL_UI, 0).deref()


@overload
def GetLevelUIConfiguration() -> LevelUIConfigurationStruct:
    ...


@overload
def GetLevelUIConfiguration(type_: Type[T]) -> T:
    ...


def GetLevelUIConfiguration(type_: Type[T] = LevelUIConfigurationStruct, /) -> T:
    if type_._size_ != 10:
        warnings.warn(
            f"Type {type_} may have an incorrect size for level ui configuration."
        )
    return Pointer[type_](MemoryBlock.LEVEL_UI_CONFIGURATION, 0).deref()


@overload
def GetLevelScore() -> LevelScoreStruct:
    ...


@overload
def GetLevelScore(type_: Type[T]) -> T:
    ...


def GetLevelScore(type_: Type[T] = LevelScoreStruct, /) -> T:
    if type_._size_ != 12:
        warnings.warn(f"Type {type_} may have an incorrect size for level score.")
    return Pointer[type_](MemoryBlock.LEVEL_SCORE, 0).deref()


@overload
def GetLevelLife() -> LevelLifeStruct:
    ...


@overload
def GetLevelLife(type_: Type[T]) -> T:
    ...


def GetLevelLife(type_: Type[T] = LevelLifeStruct, /) -> T:
    if type_._size_ != 6:
        warnings.warn(f"Type {type_} may have an incorrect size for level life.")
    return Pointer[type_](MemoryBlock.LEVEL_LIFE, 0).deref()


def GetEngineRom(type_: Type[T], /) -> T:
    return Pointer[type_](MemoryBlock.ENGINE_ROM, 0).deref()


@overload
def GetTemporaryData() -> TouchDataStruct:
    ...


@overload
def GetTemporaryData(type_: Type[T]) -> T:
    ...


def GetTemporaryData(type_: Type[T] = TouchDataStruct, /) -> T:
    if type_._size_ != 15:
        warnings.warn(f"Type {type_} may have an incorrect size for temporary data.")
    return Pointer[type_](MemoryBlock.TEMPORARY_DATA, 0).deref()


LevelData = GetLevelData(LevelDataStruct)
LevelTransform = GetLevelTransform(Array[Number, 4, 4])
LevelBackground = GetLevelBackground(Quad)
LevelUI = GetLevelUI(LevelUIStruct)
LevelUIConfiguration = GetLevelUIConfiguration(LevelUIConfigurationStruct)
LevelScore = GetLevelScore(LevelScoreStruct)
LevelLife = GetLevelLife(LevelLifeStruct)
TouchData = GetTemporaryData(TouchDataStruct)
