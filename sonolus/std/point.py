from __future__ import annotations

from .number import Num, Sin, Cos
from .types import Struct
from .function import sls_func

__all__ = ("Point",)


class Point(Struct):
    x: Num
    y: Num

    @sls_func(ast=False)
    def __add__(self, other: Point | Num) -> Point:
        if isinstance(other, Point):
            return Point.new(self.x + other.x, self.y + other.y)
        if isinstance(other, (Num, int, float)):
            return Point.new(self.x + other, self.y + other)
        return NotImplemented

    @sls_func(ast=False)
    def __sub__(self, other: Point | Num) -> Point:
        if isinstance(other, Point):
            return Point.new(self.x - other.x, self.y - other.y)
        if isinstance(other, (Num, int, float)):
            return Point.new(self.x - other, self.y - other)
        return NotImplemented

    @sls_func(ast=False)
    def __mul__(self, other: Point | Num) -> Point:
        if isinstance(other, Point):
            return Point.new(self.x * other.x, self.y * other.y)
        if isinstance(other, (Num, int, float)):
            return Point.new(self.x * other, self.y * other)
        return NotImplemented

    @sls_func(ast=False)
    def __truediv__(self, other: Point | Num) -> Point:
        if isinstance(other, Point):
            return Point.new(self.x / other.x, self.y / other.y)
        if isinstance(other, (Num, int, float)):
            return Point.new(self.x / other, self.y / other)
        return NotImplemented

    @sls_func(ast=False)
    def __floordiv__(self, other: Point | Num) -> Point:
        if isinstance(other, Point):
            return Point.new(self.x // other.x, self.y // other.y)
        if isinstance(other, (Num, int, float)):
            return Point.new(self.x // other, self.y // other)
        return NotImplemented

    @sls_func
    def __neg__(self) -> Point:
        return Point.new(-self.x, -self.y)

    @sls_func
    def magnitude(self) -> Num:
        return (self.x**2 + self.y**2) ** 0.5

    @sls_func
    def rotate(self, theta: Num, /) -> Point:
        s = Sin(theta)
        c = Cos(theta)
        return Point.new(self.x * c - self.y * s, self.x * s + self.y * c)

    @sls_func
    def rotate_about(self, theta: Num, pivot: Point):
        return (self - pivot).rotate(theta) + pivot

    @classmethod
    @sls_func
    def polar(cls, r: Num, theta: Num) -> Point:
        return cls.new(Cos(theta) * r, Sin(theta) * r)
