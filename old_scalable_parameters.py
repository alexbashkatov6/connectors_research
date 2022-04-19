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


def bool_to_plus_minus_1(b: bool) -> int:
    return 1 if b else -1


def plus_minus_1_to_bool(i: int) -> bool:
    return i == 1


class RelativePlacement:
    def __init__(self, x: Real = 0, y: Real = 0, angle: Real = 0, direct_orientation: bool = True, scale_policy: ScaleBehavior = None):
        self.x: Real = x
        self.y: Real = y
        self.angle: Real = angle
        self.direct_orientation: bool = direct_orientation  # if y-axis is reversed

    @property
    def params(self) -> tuple[Real, Real, Real, bool]:
        return self.x, self.y, self.angle, self.direct_orientation

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(self.__class__.__name__, *self.params)

    def reverse(self) -> RelativePlacement:
        dir_coef = bool_to_plus_minus_1(self.direct_orientation)
        x = - self.x * math.cos(self.angle) - self.y * math.sin(self.angle)
        y = (self.x * math.sin(self.angle) - self.y * math.cos(self.angle)) * dir_coef
        angle = -self.angle * dir_coef
        dir_or = self.direct_orientation
        return RelativePlacement(x, y, angle, dir_or)


def absolute_rp(base_cs_absolute_rp: RelativePlacement, local_rp_: RelativePlacement, scale_in_base_cs: Real = 1):
    x = base_cs_absolute_rp.x + math.cos(base_cs_absolute_rp.angle) * local_rp_.x * scale_in_base_cs - math.sin(base_cs_absolute_rp.angle) * local_rp_.y * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation) * scale_in_base_cs
    y = base_cs_absolute_rp.y + math.sin(base_cs_absolute_rp.angle) * local_rp_.x * scale_in_base_cs + math.cos(base_cs_absolute_rp.angle) * local_rp_.y * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation) * scale_in_base_cs
    angle = base_cs_absolute_rp.angle + local_rp_.angle * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation)
    direct_orientation = plus_minus_1_to_bool(bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation) * \
                                              bool_to_plus_minus_1(local_rp_.direct_orientation))
    return RelativePlacement(x, y, angle, direct_orientation)


def local_rp(base_cs_absolute_rp: RelativePlacement, absolute_rp_: RelativePlacement, scale_in_base_cs: Real = 1):
    """ absolute point to local cs given by absolute rp"""
    x = (absolute_rp_.x - base_cs_absolute_rp.x) * math.cos(base_cs_absolute_rp.angle) / scale_in_base_cs + \
        (absolute_rp_.y - base_cs_absolute_rp.y) * math.sin(base_cs_absolute_rp.angle) / scale_in_base_cs
    y = - (absolute_rp_.x - base_cs_absolute_rp.x) * math.sin(base_cs_absolute_rp.angle) / scale_in_base_cs * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation) + \
        (absolute_rp_.y - base_cs_absolute_rp.y) * math.cos(base_cs_absolute_rp.angle) / scale_in_base_cs * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation)
    angle = (absolute_rp_.angle - base_cs_absolute_rp.angle) * bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation)
    direct_orientation = plus_minus_1_to_bool(bool_to_plus_minus_1(base_cs_absolute_rp.direct_orientation) * \
                                              bool_to_plus_minus_1(absolute_rp_.direct_orientation))
    return RelativePlacement(x, y, angle, direct_orientation)


class SceneCS:
    def __init__(self, rp: RelativePlacement = None, parent_cs: SceneCS = None):
        """ if cs is base, init_placement is relative to corner view cs, else - in base """
        self.is_base_scene_cs = False
        self.relative_scene_position: RelativePlacement = None
        self.absolute_scene_position: RelativePlacement = None
        if parent_cs is None:
            self.is_base_scene_cs = True
            self.absolute_scene_position = RelativePlacement()
        else:
            parent_cs.child_cs.append(self)
            self.parent_cs = parent_cs
            self.relative_scene_position: RelativePlacement = rp
            self.eval_absolute_scene_position()
        self.child_cs = []

    def eval_absolute_scene_position(self) -> None:
        """ eval not for base """
        self.absolute_scene_position = absolute_rp(self.parent_cs.absolute_scene_position, self.relative_scene_position)

    def all_children(self) -> list[SceneCS]:
        children = []
        for child in self.child_cs:
            children.append(child)
        for child in self.child_cs:
            children.extend(child.all_children())
        return children


class SceneCSView:
    """ current view management """
    def __init__(self, base_scene_cs_position: RelativePlacement):
        self.base_scene_cs_position = base_scene_cs_position
        self.scale = 1

    def cs_view_position(self, cs: SceneCS):
        """ cs position on view window """
        return absolute_rp(self.base_scene_cs_position, cs.absolute_scene_position, self.scale)

    def translate_view(self, start_point_view_coords: Point2D, end_point_view_coords: Point2D):
        x, y, angle, direct_orientation = self.base_scene_cs_position.params
        new_x = x + float(end_point_view_coords.x) - float(start_point_view_coords.x)
        new_y = y + float(end_point_view_coords.y) - float(start_point_view_coords.y)
        self.base_scene_cs_position = RelativePlacement(new_x, new_y, angle, direct_orientation)

    def relative_zoom(self, center_point_view_coords: Point2D, delta_scale: Real):
        x, y, angle, direct_orientation = self.base_scene_cs_position.params
        x_center_point, y_center_point = float(center_point_view_coords.x), float(center_point_view_coords.y)
        delta_x_base = x_center_point - x
        delta_y_base = y_center_point - y
        new_x = x_center_point - delta_scale * delta_x_base
        new_y = y_center_point - delta_scale * delta_y_base
        self.base_scene_cs_position = RelativePlacement(new_x, new_y, angle, direct_orientation)
        self.scale *= delta_scale

    def coords_of_view_point_in_cs(self, p_view: Point2D, cs: SceneCS) -> Point2D:
        p_scene = (float(p_view.x)-self.base_scene_cs_position.x)/self.scale, \
                  (float(p_view.y)-self.base_scene_cs_position.y)/self.scale
        lrp = local_rp(cs.absolute_scene_position, RelativePlacement(*p_scene))
        return Point2D(lrp.x, lrp.y)

    def move_cs(self, cs: SceneCS, start_point_view_coords: Point2D, end_point_view_coords: Point2D):
        parent_cs = cs.parent_cs
        old_rel_params = cs.relative_scene_position.params
        pnt_start_move_in_parent_cs = self.coords_of_view_point_in_cs(start_point_view_coords, parent_cs)
        pnt_end_move_in_parent_cs = self.coords_of_view_point_in_cs(end_point_view_coords, parent_cs)
        new_x = old_rel_params[0] + float(pnt_end_move_in_parent_cs.x) - float(pnt_start_move_in_parent_cs.x)
        new_y = old_rel_params[1] + float(pnt_end_move_in_parent_cs.y) - float(pnt_start_move_in_parent_cs.y)
        new_rp = RelativePlacement(new_x, new_y, old_rel_params[2], old_rel_params[3])
        cs.relative_scene_position = new_rp
        cs.eval_absolute_scene_position()
        for child in cs.all_children():
            child.eval_absolute_scene_position()


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


class ElementaryItem:
    def __init__(self):
        self.main_cs = None


class ComposedItem:
    def __init__(self):
        self.main_cs = None


class GlobalItemManager:
    def __init__(self):
        self.base_cs_scene = SceneCS()
        self.view = SceneCSView(RelativePlacement(0, 0))
        self.composed_items = []

    def add_item(self, ci: ComposedItem, rp: RelativePlacement):
        pass


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
        cs_base = SceneCS()  # RelativePlacement(1, 1)
        cs_1 = SceneCS(RelativePlacement(9, 6, math.atan(3/4)), cs_base)
        cs_2 = SceneCS(RelativePlacement(10, 5, math.pi/2 - math.atan(3/4), False), cs_1)
        cs_3 = SceneCS(RelativePlacement(1, 2, math.pi/2), cs_2)

        cs_4 = SceneCS(RelativePlacement(10, 5, math.pi/2 - math.atan(3/4), False), cs_1)
        cs_5 = SceneCS(RelativePlacement(1, 2, math.pi/2), cs_2)
        print(cs_2.absolute_scene_position)
        cv = SceneCSView(RelativePlacement(4, 2))
        # cv.scale = 2
        # cv.translate_view(Point2D(0, 0), Point2D(3, 5))
        # cv.zoom_relative_view(Point2D(0, 0), 2)
        # print(cv.cs_view_position(cs_3))
        # print(local_rp(cs_1.absolute_scene_position, RelativePlacement(14, 16)))
        # print(cv.coords_of_view_point_in_cs(Point2D(18, 18), cs_1))
        # print(cs_base.all_children())

        cv.relative_zoom(Point2D(0, 0), 2)
        print("positions before cs_base = {}, \n cs_1 = {}, \n cs_2 = {}, \n cs_3 = {}, \n cs_4 = {}, \n cs_5 = {}".format(cv.cs_view_position(cs_base),
                                                                                               cv.cs_view_position(cs_1),
                                                                                               cv.cs_view_position(cs_2),
                                                                                               cv.cs_view_position(cs_3),
                                                                                               cv.cs_view_position(cs_4),
                                                                                               cv.cs_view_position(cs_5)))
        print("cs_1 before", cs_1.absolute_scene_position)
        cv.move_cs(cs_1, Point2D(0, 0), Point2D(1, 2))

        print("positions after cs_base = {}, \n cs_1 = {}, \n cs_2 = {}, \n cs_3 = {}, \n cs_4 = {}, \n cs_5 = {}".format(cv.cs_view_position(cs_base),
                                                                                               cv.cs_view_position(cs_1),
                                                                                               cv.cs_view_position(cs_2),
                                                                                               cv.cs_view_position(cs_3),
                                                                                               cv.cs_view_position(cs_4),
                                                                                               cv.cs_view_position(cs_5)))
        print("cs_1 efter", cs_1.absolute_scene_position)

    test_3 = False
    if test_3:
        m = GlobalItemManager()
