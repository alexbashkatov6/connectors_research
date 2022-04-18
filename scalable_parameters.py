from __future__ import annotations

import math
from numbers import Real
from dataclasses import dataclass
from sympy import Point2D

from custom_enum import CustomEnum


def bounded_scale_function(scale: Real, base_scale: Real = 1) -> float:
    assert float(base_scale) > 0
    return float(scale) if scale <= base_scale else float(base_scale)


class ScaleBehavior(CustomEnum):
    unscalable = 0
    bounded_scale = 1
    scalable = 2


class ScalableParameter:
    def __init__(self, behavior: ScaleBehavior, base_value: Real = None):
        self.behavior = behavior
        self._base_value = base_value
        self._value = None
        self.scale = 1

    @property
    def base_value(self):
        return self._base_value

    @base_value.setter
    def base_value(self, val):
        self._base_value = val

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, val):
        self._scale = val
        if self.behavior == ScaleBehavior.unscalable:
            self._value = self.base_value
        elif self.behavior == ScaleBehavior.bounded_scale:
            self._value = self.base_value * bounded_scale_function(self._scale)
        elif self.behavior == ScaleBehavior.scalable:
            self._value = self.base_value * self._scale

    @property
    def value(self) -> Real:
        return self._value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.value)

    def __str__(self):
        return "{}".format(self.value)

    def __add__(self, other):
        if isinstance(other, Real):
            return self.value + other
        elif isinstance(other, ScalableParameter):
            return self.value + other.value
        else:
            assert False

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Real):
            return self.value - other
        elif isinstance(other, ScalableParameter):
            return self.value - other.value
        else:
            assert False

    def __rsub__(self, other):
        if isinstance(other, Real):
            return -self.value + other
        elif isinstance(other, ScalableParameter):
            return -self.value + other.value
        else:
            assert False

    def __mul__(self, other):
        if isinstance(other, Real):
            return self.value * other
        elif isinstance(other, ScalableParameter):
            return self.value * other.value
        else:
            assert False

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Real):
            return self.value / other
        elif isinstance(other, ScalableParameter):
            return self.value / other.value
        else:
            assert False

    def __rtruediv__(self, other):
        if isinstance(other, Real):
            return other / self.value
        elif isinstance(other, ScalableParameter):
            return other.value / self.value
        else:
            assert False

    def __pow__(self, other):
        if isinstance(other, Real):
            return self.value ** other
        elif isinstance(other, ScalableParameter):
            return self.value ** other.value
        else:
            assert False

    def __rpow__(self, other):
        if isinstance(other, Real):
            return other ** self.value
        elif isinstance(other, ScalableParameter):
            return other.value ** self.value
        else:
            assert False


# @dataclass
# class RelativePlacement:
#     x: Real = 0
#     y: Real = 0
#     angle: Real = 0
#     reversed_orientation: bool = False  # if y-axis is reversed

def bool_to_plus_minus_1(b: bool) -> int:
    return 1 if b else -1


class RelativePlacement:
    def __init__(self, x: Real = 0, y: Real = 0, angle: Real = 0, direct_orientation: bool = True):
        self.x: Real = x
        self.y: Real = y
        self.angle: Real = angle
        self.direct_orientation: bool = direct_orientation  # if y-axis is reversed

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(self.__class__.__name__, self.x, self.y, self.angle, self.direct_orientation)

    def reverse(self) -> RelativePlacement:
        dir_coef = bool_to_plus_minus_1(self.direct_orientation)
        x = - self.x * math.cos(self.angle) - self.y * math.sin(self.angle)
        y = (self.x * math.sin(self.angle) - self.y * math.cos(self.angle)) * dir_coef
        angle = -self.angle * dir_coef
        dir_or = self.direct_orientation
        return RelativePlacement(x, y, angle, dir_or)


# class LocalCsPlacement(CustomEnum):
#     center = 0
#     tangent = 1
#     corner = 2


""" 2 main cs:

    1. for build - scene cs
    2. for view - corner cs

"""


class SceneCS:
    def __init__(self, init_placement: RelativePlacement = None, parent_cs: SceneCS = None):
        """ if cs is base, init_placement is relative to corner view cs, else - in base """
        self.is_base_scene_cs = False
        self._view_position: RelativePlacement = None
        self.relative_scene_position: RelativePlacement = None
        self.absolute_scene_position: RelativePlacement = None
        if parent_cs is None:
            self.is_base_scene_cs = True
            self._view_position: RelativePlacement = init_placement
            self.relative_scene_position = RelativePlacement()
            self.absolute_scene_position = RelativePlacement()
        else:
            parent_cs.child_cs.append(self)
            self.parent_cs = parent_cs
            self.relative_scene_position: RelativePlacement = init_placement
            self.absolute_scene_position = self.eval_absolute_position()
        self.child_cs = []

    def view_changed(self, central_point: Point2D, delta_scale: Real):
        cp_in_corner_position = None

    @property
    def view_position(self):
        return self._view_position

    def eval_absolute_position(self) -> RelativePlacement:
        rel: RelativePlacement = self.relative_scene_position
        parent_abs: RelativePlacement = self.parent_cs.absolute_scene_position
        x = parent_abs.x + math.cos(parent_abs.angle) * rel.x - math.sin(parent_abs.angle) * rel.y * bool_to_plus_minus_1(parent_abs.direct_orientation)
        y = parent_abs.y + math.sin(parent_abs.angle) * rel.x + math.cos(parent_abs.angle) * rel.y * bool_to_plus_minus_1(parent_abs.direct_orientation)
        angle = parent_abs.angle + rel.angle * bool_to_plus_minus_1(parent_abs.direct_orientation)
        direct_orientation = bool_to_plus_minus_1(parent_abs.direct_orientation) * \
                             bool_to_plus_minus_1(rel.direct_orientation)
        return RelativePlacement(x, y, angle, direct_orientation)


class GraphicItemCS_old:
    def __init__(self, rp_in_corner: RelativePlacement):  # base_cs: GraphicItemCS = None
        # self.is_base_cs = False
        # if base_cs is None:
        #     self.is_base_cs = True
        # self.base_cs: GraphicItemCS = base_cs
        self.rp_in_corner: RelativePlacement = rp_in_corner
        self.scale_in_corner = 1
        self.prims: dict[Primitive, RelativePlacement] = {}
        self.child_cs: dict[Primitive, RelativePlacement] = {}

    def transform(self, central_point: Point2D, delta_scale: Real):
        """ central point in scene cs """
        pass
        # for cs in self.child_cs:
        #     cs.transform(central_point, scale)

    def in_corner_cs(self):
        """ coordinates in corner cs """
        pass


class Primitive:
    pass


class Ring(Primitive):
    def __init__(self, r: Real = None, h: Real = None):
        self.r = ScalableParameter(ScaleBehavior(ScaleBehavior.scalable), r)
        self.h = ScalableParameter(ScaleBehavior(ScaleBehavior.unscalable), h)

    def to_path(self, rp: RelativePlacement, scale: Real):
        pass

    def to_gr_item(self, rp: RelativePlacement, scale: Real):
        pass

# , coord: RelativePlacement = None
# , place_cs: LocalCsPlacement = LocalCsPlacement(LocalCsPlacement.center)


if __name__ == "__main__":
    test_1 = False
    if test_1:
        p1 = ScalableParameter(ScaleBehavior(ScaleBehavior.bounded_scale), 10)  # unscalable
        p1.scale = 0.5
        print(p1)
        p2 = ScalableParameter(ScaleBehavior(ScaleBehavior.scalable), 2)
        p1.scale = 2
        print(p1 * p2)
        print(p1 + p2)

        pr_ = RelativePlacement(6, 4, math.pi/4, False)
        print(pr_.reverse())

    test_2 = True
    if test_2:
        cs_base = SceneCS(RelativePlacement(1, 1))
        cs_1 = SceneCS(RelativePlacement(9, 6, math.atan(3/4)), cs_base)
        cs_2 = SceneCS(RelativePlacement(10, 5, math.pi/2 - math.atan(3/4)), cs_1)
        print(cs_2.absolute_scene_position)
