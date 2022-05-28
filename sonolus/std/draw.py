from __future__ import annotations

from enum import Enum

from sonolus.engine.primitive import invoke_builtin, Num, Bool
from .function import sls_func
from .point import Point
from .types import Struct, Array, Void

__all__ = (
    "Quad",
    "Draw",
    "DrawCurvedL",
    "DrawCurvedR",
    "DrawCurvedLR",
    "DrawCurvedB",
    "DrawCurvedT",
    "DrawCurvedBT",
    "SpawnParticleEffect",
    "MoveParticleEffect",
    "DestroyParticleEffect",
    "HasSkinSprite",
    "HasParticleEffect",
    "SpriteId",
    "ParticleEffectId",
)


class Quad(Struct):
    bl: Point
    tl: Point
    tr: Point
    br: Point

    @property
    @sls_func(ast=False)
    def coords(self):
        return Array[Num, 8](
            self.bl.x,
            self.bl.y,
            self.tl.x,
            self.tl.y,
            self.tr.x,
            self.tr.y,
            self.br.x,
            self.br.y,
        )

    @classmethod
    @sls_func
    def centered_rectangle(
        cls, center: Point, half_width: Num, half_height: Num
    ) -> Quad:
        return cls.rectangle(
            center.x - half_width,
            center.x + half_width,
            center.y + half_height,
            center.y - half_height,
        )

    @classmethod
    @sls_func
    def rectangle(cls, left: Num, right: Num, top: Num, bottom: Num):
        return cls.new(
            bl=Point(left, bottom),
            tl=Point(left, top),
            tr=Point(right, top),
            br=Point(right, bottom),
        )


@sls_func(ast=False)
def Draw(id: Num, quad: Quad, z: Num, a: Num) -> Void:
    return invoke_builtin("Draw", [id, *quad.coords, z, a])


@sls_func(ast=False)
def DrawCurvedL(id: Num, quad: Quad, z: Num, a: Num, n: Num, l: Point) -> Void:
    return invoke_builtin("DrawCurvedL", [id, *quad.coords, z, a, n, l.x, l.y])


@sls_func(ast=False)
def DrawCurvedR(id: Num, quad: Quad, z: Num, a: Num, n: Num, r: Point) -> Void:
    return invoke_builtin("DrawCurvedR", [id, *quad.coords, z, a, n, r.x, r.y])


@sls_func(ast=False)
def DrawCurvedLR(
    id: Num, quad: Quad, z: Num, a: Num, n: Num, l: Point, r: Point
) -> Void:
    return invoke_builtin(
        "DrawCurvedLR", [id, *quad.coords, z, a, n, l.x, l.y, r.x, r.y]
    )


@sls_func(ast=False)
def DrawCurvedB(id: Num, quad: Quad, z: Num, a: Num, n: Num, b: Point) -> Void:
    return invoke_builtin("DrawCurvedB", [id, *quad.coords, z, a, n, b.x, b.y])


@sls_func(ast=False)
def DrawCurvedT(id: Num, quad: Quad, z: Num, a: Num, n: Num, t: Point) -> Void:
    return invoke_builtin("DrawCurvedT", [id, *quad.coords, z, a, n, t.x, t.y])


@sls_func(ast=False)
def DrawCurvedBT(
    id: Num, quad: Quad, z: Num, a: Num, n: Num, b: Point, t: Point
) -> Void:
    return invoke_builtin(
        "DrawCurvedBT", [id, *quad.coords, z, a, n, b.x, b.y, t.x, t.y]
    )


@sls_func(ast=False)
def SpawnParticleEffect(id: Num, quad: Quad, t: Num, loop: Bool = False) -> Num:
    return invoke_builtin("SpawnParticleEffect", [id, *quad.coords, t, loop], Num)


@sls_func(ast=False)
def MoveParticleEffect(id: Num, quad: Quad) -> Void:
    return invoke_builtin("MoveParticleEffect", [id, *quad.coords])


@sls_func(ast=False)
def DestroyParticleEffect(id: Num) -> Void:
    return invoke_builtin("DestroyParticleEffect", [id])


@sls_func(ast=False)
def HasSkinSprite(id: Num) -> Bool:
    return invoke_builtin("HasSkinSprite", [id], Bool)


@sls_func(ast=False)
def HasParticleEffect(id: Num) -> Bool:
    return invoke_builtin("HasParticleEffect", [id], Bool)


class SpriteId(int, Enum):
    NOTE_HEAD_NEUTRAL = 1000
    NOTE_HEAD_RED = 1001
    NOTE_HEAD_GREEN = 1002
    NOTE_HEAD_BLUE = 1003
    NOTE_HEAD_YELLOW = 1004
    NOTE_HEAD_PURPLE = 1005
    NOTE_HEAD_CYAN = 1006

    NOTE_TICK_NEUTRAL = 2000
    NOTE_TICK_RED = 2001
    NOTE_TICK_GREEN = 2002
    NOTE_TICK_BLUE = 2003
    NOTE_TICK_YELLOW = 2004
    NOTE_TICK_PURPLE = 2005
    NOTE_TICK_CYAN = 2006

    NOTE_TAIL_NEUTRAL = 3000
    NOTE_TAIL_RED = 3001
    NOTE_TAIL_GREEN = 3002
    NOTE_TAIL_BLUE = 3003
    NOTE_TAIL_YELLOW = 3004
    NOTE_TAIL_PURPLE = 3005
    NOTE_TAIL_CYAN = 3006

    NOTE_CONNECTION_NEUTRAL = 11000
    NOTE_CONNECTION_RED = 11001
    NOTE_CONNECTION_GREEN = 11002
    NOTE_CONNECTION_BLUE = 11003
    NOTE_CONNECTION_YELLOW = 11004
    NOTE_CONNECTION_PURPLE = 11005
    NOTE_CONNECTION_CYAN = 11006

    NOTE_CONNECTION_NEUTRAL_SEAMLESS = 11100
    NOTE_CONNECTION_RED_SEAMLESS = 11101
    NOTE_CONNECTION_GREEN_SEAMLESS = 11102
    NOTE_CONNECTION_BLUE_SEAMLESS = 11103
    NOTE_CONNECTION_YELLOW_SEAMLESS = 11104
    NOTE_CONNECTION_PURPLE_SEAMLESS = 11105
    NOTE_CONNECTION_CYAN_SEAMLESS = 11106

    SIMULTANEOUS_CONNECTION_NEUTRAL = 12000
    SIMULTANEOUS_CONNECTION_RED = 12001
    SIMULTANEOUS_CONNECTION_GREEN = 12002
    SIMULTANEOUS_CONNECTION_BLUE = 12003
    SIMULTANEOUS_CONNECTION_YELLOW = 12004
    SIMULTANEOUS_CONNECTION_PURPLE = 12005
    SIMULTANEOUS_CONNECTION_CYAN = 12006

    SIMULTANEOUS_CONNECTION_NEUTRAL_SEAMLESS = 12100
    SIMULTANEOUS_CONNECTION_RED_SEAMLESS = 12101
    SIMULTANEOUS_CONNECTION_GREEN_SEAMLESS = 12102
    SIMULTANEOUS_CONNECTION_BLUE_SEAMLESS = 12103
    SIMULTANEOUS_CONNECTION_YELLOW_SEAMLESS = 12104
    SIMULTANEOUS_CONNECTION_PURPLE_SEAMLESS = 12105
    SIMULTANEOUS_CONNECTION_CYAN_SEAMLESS = 12106

    DIRECTIONAL_MARKER_NEUTRAL = 21000
    DIRECTIONAL_MARKER_RED = 21001
    DIRECTIONAL_MARKER_GREEN = 21002
    DIRECTIONAL_MARKER_BLUE = 21003
    DIRECTIONAL_MARKER_YELLOW = 21004
    DIRECTIONAL_MARKER_PURPLE = 21005
    DIRECTIONAL_MARKER_CYAN = 21006

    SIMULTANEOUS_MARKER_NEUTRAL = 22000
    SIMULTANEOUS_MARKER_RED = 22001
    SIMULTANEOUS_MARKER_GREEN = 22002
    SIMULTANEOUS_MARKER_BLUE = 22003
    SIMULTANEOUS_MARKER_YELLOW = 22004
    SIMULTANEOUS_MARKER_PURPLE = 22005
    SIMULTANEOUS_MARKER_CYAN = 22006

    STAGE_MIDDLE = 40000

    STAGE_LEFT_BORDER = 40001
    STAGE_RIGHT_BORDER = 40002
    STAGE_TOP_BORDER = 40004
    STAGE_BOTTOM_BORDER = 40008
    STAGE_LEFT_BORDER_SEAMLESS = 40101
    STAGE_RIGHT_BORDER_SEAMLESS = 40102
    STAGE_TOP_BORDER_SEAMLESS = 40104
    STAGE_BOTTOM_BORDER_SEAMLESS = 40108

    STAGE_TOP_LEFT_CORNER = 40005
    STAGE_TOP_RIGHT_CORNER = 40006
    STAGE_BOTTOM_LEFT_CORNER = 40009
    STAGE_BOTTOM_RIGHT_CORNER = 40010

    LANE = 40100
    LANE_SEAMLESS = 40110

    LANE_ALTERNATIVE = 40200
    LANE_ALTERNATIVE_SEAMLESS = 40210

    JUDGMENT_LINE = 41000
    NOTE_SLOT = 41001

    STAGE_COVER = 42000


class ParticleEffectId(int, Enum):
    NOTE_CIRCULAR_TAP_BASE = 110000
    NOTE_CIRCULAR_TAP_RED = 110001
    NOTE_CIRCULAR_TAP_GREEN = 110002
    NOTE_CIRCULAR_TAP_BLUE = 110003
    NOTE_CIRCULAR_TAP_YELLOW = 110004
    NOTE_CIRCULAR_TAP_PURPLE = 110005
    NOTE_CIRCULAR_TAP_CYAN = 110006

    NOTE_CIRCULAR_ALTERNATIVE_BASE = 111000
    NOTE_CIRCULAR_ALTERNATIVE_RED = 111001
    NOTE_CIRCULAR_ALTERNATIVE_GREEN = 111002
    NOTE_CIRCULAR_ALTERNATIVE_BLUE = 111003
    NOTE_CIRCULAR_ALTERNATIVE_YELLOW = 111004
    NOTE_CIRCULAR_ALTERNATIVE_PURPLE = 111005
    NOTE_CIRCULAR_ALTERNATIVE_CYAN = 111006

    NOTE_CIRCULAR_HOLD_BASE = 112000
    NOTE_CIRCULAR_HOLD_RED = 112001
    NOTE_CIRCULAR_HOLD_GREEN = 112002
    NOTE_CIRCULAR_HOLD_BLUE = 112003
    NOTE_CIRCULAR_HOLD_YELLOW = 112004
    NOTE_CIRCULAR_HOLD_PURPLE = 112005
    NOTE_CIRCULAR_HOLD_CYAN = 112006

    NOTE_LINEAR_TAP_BASE = 120000
    NOTE_LINEAR_TAP_RED = 120001
    NOTE_LINEAR_TAP_GREEN = 120002
    NOTE_LINEAR_TAP_BLUE = 120003
    NOTE_LINEAR_TAP_YELLOW = 120004
    NOTE_LINEAR_TAP_PURPLE = 120005
    NOTE_LINEAR_TAP_CYAN = 120006

    NOTE_LINEAR_ALTERNATIVE_BASE = 121000
    NOTE_LINEAR_ALTERNATIVE_RED = 121001
    NOTE_LINEAR_ALTERNATIVE_GREEN = 121002
    NOTE_LINEAR_ALTERNATIVE_BLUE = 121003
    NOTE_LINEAR_ALTERNATIVE_YELLOW = 121004
    NOTE_LINEAR_ALTERNATIVE_PURPLE = 121005
    NOTE_LINEAR_ALTERNATIVE_CYAN = 121006

    NOTE_LINEAR_HOLD_BASE = 122000
    NOTE_LINEAR_HOLD_RED = 122001
    NOTE_LINEAR_HOLD_GREEN = 122002
    NOTE_LINEAR_HOLD_BLUE = 122003
    NOTE_LINEAR_HOLD_YELLOW = 122004
    NOTE_LINEAR_HOLD_PURPLE = 122005
    NOTE_LINEAR_HOLD_CYAN = 122006

    LANE_CIRCULAR = 310000
    LANE_LINEAR = 320000

    SLOT_CIRCULAR = 410000
    SLOT_LINEAR = 420000

    JUDGE_LINE_CIRCULAR = 510000
    JUDGE_LINE_LINEAR = 520000
