from __future__ import annotations
from numbers import Real

from custom_enum import CustomEnum


def bounded_scale_function(scale: Real, base_scale: Real = 1) -> float:
    assert float(base_scale) > 0
    return float(scale) if scale <= base_scale else float(base_scale)


class ScaleBehavior(CustomEnum):
    unscalable = 0
    bounded_scale = 1
    scalable = 2


class ScalableParameter:
    def __init__(self, behavior: ScaleBehavior):
        self.behavior = behavior
        self._base_value = None
        self._value = None
        self._scale = 1

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
    def value(self):
        return self._value

    def __add__(self, other):
        pass

    def __radd__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __rsub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __rmul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def __pow__(self, other):
        pass

    def __rpow__(self, other):
        pass


class CustomEllipse:
    def __init__(self):
        self.r = 1
        self.h = ScalableParameter(ScaleBehavior(ScaleBehavior.scalable))
