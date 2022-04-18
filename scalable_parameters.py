from __future__ import annotations
from numbers import Real
from dataclasses import dataclass

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


@dataclass
class RelativePlacement:
    x: Real = 0
    y: Real = 0
    angle: Real = 0
    reversed_orientation: bool = False


class LocalCsPlacement(CustomEnum):
    center = 0
    tangent = 1
    corner = 2


class Primitive:
    pass


class Ring(Primitive):
    def __init__(self, r: Real = None, h: Real = None, coord: RelativePlacement = None,
                 place_cs: LocalCsPlacement = LocalCsPlacement(LocalCsPlacement.center)):
        self.r = ScalableParameter(ScaleBehavior(ScaleBehavior.scalable), r)
        self.h = ScalableParameter(ScaleBehavior(ScaleBehavior.unscalable), h)


if __name__ == "__main__":
    p1 = ScalableParameter(ScaleBehavior(ScaleBehavior.bounded_scale), 10)  # unscalable
    p1.scale = 0.5
    print(p1)
    p2 = ScalableParameter(ScaleBehavior(ScaleBehavior.scalable), 2)
    p1.scale = 2
    print(p1 * p2)
    print(p1 + p2)
