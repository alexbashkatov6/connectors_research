from __future__ import annotations

import numpy as np
from typing import Callable
import scipy
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize, Bounds
import bezier
from matplotlib import pyplot as plt
from sympy import Point2D  # , Line2D, Ray2D
import math
from numbers import Real
import time

from cubic_curvature import deltas_optimization



# class Point2D:
#     def __init__(self, x, y):
#         self.coords = np.array([x, y])

TIME_EVALUATION = True


class Angle:
    def __init__(self, free_angle: Real):
        self.free_angle = float(free_angle)

    def __add__(self, other) -> Angle:
        assert isinstance(other, (Real, Angle)), 'Can add only angle or int/float'
        if isinstance(other, Real):
            other = Angle(other)
        return Angle(self.free_angle + other.free_angle)

    def __sub__(self, other) -> Angle:
        assert isinstance(other, (Real, Angle)), 'Can sub only angle or int/float'
        if isinstance(other, Real):
            other = Angle(other)
        return Angle(self.free_angle - other.free_angle)

    def __eq__(self, other):
        assert isinstance(other, (Real, Angle)), 'Can compare only angle or int/float'
        if isinstance(other, Real):
            other = Angle(other)
        return self.angle_mpi2_ppi2 == other.angle_mpi2_ppi2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{}({:1.7f})".format(self.__class__.__name__, self.angle_mpi2_ppi2)

    __str__ = __repr__

    @property
    def angle_0_2pi(self):
        """ radian value in interval [0, 2pi) """
        positive_angle = self.free_angle % (2 * math.pi)
        return positive_angle

    @property
    def deg_angle_0_360(self):
        """ degree value in interval [0, 360) """
        return self.angle_0_2pi * 180 / math.pi

    @property
    def angle_mpi2_ppi2(self):
        """ radian value in interval (-pi/2, pi/2] """
        positive_angle = self.free_angle % math.pi
        return positive_angle - math.pi if positive_angle > math.pi / 2 else positive_angle

    @property
    def deg_angle_m90_p90(self):
        """ degree value in interval (-90, 90] """
        return self.angle_mpi2_ppi2 * 180 / math.pi


def angle_rad_difference(a2: Angle, a1: Angle) -> float:
    """ signed difference between 2 angles """
    delta_in_2pi = a2.angle_0_2pi - a1.angle_0_2pi
    return delta_in_2pi if abs(delta_in_2pi) < math.pi else delta_in_2pi - math.copysign(2 * math.pi, delta_in_2pi)


class UniversalConnectionCurve:
    """ Based on cubic bezier curve CubicBezier """
    def __init__(self, pnt_start: Point2D, pnt_end: Point2D,
                 angle_start: Angle = None, angle_end: Angle = None):
        self._pnt_start = pnt_start
        self._pnt_end = pnt_end
        self._angle_start = angle_start
        self._angle_end = angle_end
        if TIME_EVALUATION:
            self.sum_time_float_eval = 0
            self.sum_time_min_eval = 0
        self.optimize_curvature()

    def eval_dir_points(self, deltas: tuple[Real, Real]):
        self.start_dir_point = Point2D(self.pnt_start.x + deltas[0] * math.cos(self.angle_start.angle_0_2pi),
                                       self.pnt_start.y + deltas[0] * math.sin(self.angle_start.angle_0_2pi))
        self.end_dir_point = Point2D(self.pnt_end.x + deltas[1] * math.cos(self.angle_end.angle_0_2pi),
                                     self.pnt_end.y + deltas[1] * math.sin(self.angle_end.angle_0_2pi))

    def nodes_for_print(self) -> np.ndarray:
        return np.array([[float(p_.x) for p_ in self.points],
                         [float(p_.y) for p_ in self.points]])

    @property
    def pnt_start(self) -> Point2D:
        return self._pnt_start

    @pnt_start.setter
    def pnt_start(self, val: Point2D):
        self._pnt_start = val
        self.optimize_curvature()

    @property
    def pnt_end(self) -> Point2D:
        return self._pnt_end

    @pnt_end.setter
    def pnt_end(self, val: Point2D):
        self._pnt_end = val
        self.optimize_curvature()

    @property
    def angle_start(self) -> Angle:
        return self._angle_start

    @angle_start.setter
    def angle_start(self, val: Angle):
        self._angle_start = val
        self.optimize_curvature()

    @property
    def angle_end(self) -> Angle:
        return self._angle_end

    @angle_end.setter
    def angle_end(self, val: Angle):
        self._angle_end = val
        self.optimize_curvature()

    @property
    def base_distance(self):
        return float(self.pnt_start.distance(self.pnt_end))

    @property
    def start_approximation(self):
        return 0.5 * self.base_distance, 0.5 * self.base_distance

    @property
    def points(self):
        return [self.p0, self.p1, self.p2, self.p3]

    @property
    def p0(self):
        return self.pnt_start

    @property
    def p1(self):
        return self.start_dir_point

    @property
    def p2(self):
        return self.end_dir_point

    @property
    def p3(self):
        return self.pnt_end

    def optimize_curvature(self):
        x0 = float(self.p0.x)
        y0 = float(self.p0.y)
        x3 = float(self.p3.x)
        y3 = float(self.p3.y)
        ang0 = self.angle_start.angle_0_2pi
        ang3 = self.angle_end.angle_0_2pi
        if TIME_EVALUATION:
            start_time = time.time()
        res = deltas_optimization(x0, y0, x3, y3, ang0, ang3)
        if TIME_EVALUATION:
            self.sum_time_min_eval += (time.time() - start_time)
        self.eval_dir_points(res.x)
        return res

    def plot(self):
        curve = bezier.Curve.from_nodes(self.nodes_for_print())
        curve.plot(100)
        plt.show()


if __name__ == "__main__":
    test_1 = False
    if test_1:
        p = Point2D(1, 2)
        print(p.coords)
        print(p.coords.shape)
        print(p.coords[0])

    test_2 = False
    if test_2:
        x = [1, 2, 3]
        y = [4, 5, 6]
        print(np.cross(x, y))
        # np.angle
        r = R.from_rotvec(np.pi/2 * np.array([0, 0, 1]))
        print(r.apply([1, 2, 0]))

    test_3 = False
    if test_3:
        nodes = np.array([
            [0.0, 1.0, 1.0],
            [0.0, 0.1, 0.5],
        ])
        curve = bezier.Curve.from_nodes(nodes)  # , degree=2

        print(curve)
        print(curve.length)

        # x = 1
        # y = 0.1
        # symp_expr = curve.implicitize()
        # print(curve.implicitize())
        # print(type(curve.implicitize()))
        # print(str(curve.implicitize()))
        # print("eval", eval(str(curve.implicitize())))

        curve.plot(100)
        plt.show()

        # x = np.linspace(0, 1, 50)
        # y = curve.evaluate_multi(x)[1]
        # print("y", y)

        # plt.title("Графики") # заголовок
        # plt.xlabel("x") # ось абсцисс
        # plt.ylabel("y") # ось ординат
        # plt.grid()      # включение отображение сетки
        # plt.plot(x, y)  # построение графика

    test_4 = False
    if test_4:
        # pnt_1 =
        nodes = np.asfortranarray([
            [0.0, 1.0, 1.0],
            [0.0, 0.1, 0.5],
        ])

        print(1. == 1.00000000001)

    test_5 = False
    if test_5:
        curves = [
        UniversalConnectionCurve(Point2D(0e+0, 0e+0), Point2D(1e-3, 1e-3),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi-math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi+math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(0)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(math.pi)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(math.pi+math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(-math.atan(0.5)), Angle(math.pi-math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(2, 10),
                                      Angle(-math.pi/2), Angle(math.pi/2)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 0),
                                      Angle(0), Angle(math.pi))
        ]
        cc = curves[8]
        optim_result = cc.optimize_curvature()
        cc.eval_dir_points(tuple(optim_result.x))
        print("optim_result", optim_result)
        nfev = optim_result.nfev
        if TIME_EVALUATION:
            print("sum time float", cc.sum_time_float_eval)
            print("sum time mean float", cc.sum_time_float_eval/nfev)
            print("sum time min", cc.sum_time_min_eval)
        curve = bezier.Curve.from_nodes(cc.nodes_for_print())
        curve.plot(100)
        plt.show()

    test_6 = True
    if test_6:
        curves = [
        UniversalConnectionCurve(Point2D(0e+0, 0e+0), Point2D(1e+3, 1e+3),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi-math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi+math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(0)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(math.pi)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(math.pi+math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(-math.atan(0.5)), Angle(math.pi-math.atan(0.5))),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(2, 10),
                                      Angle(-math.pi/2), Angle(math.pi/2)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 1),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi)),
        UniversalConnectionCurve(Point2D(0, 0), Point2D(1, 0),
                                      Angle(0), Angle(math.pi))
        ]
        cc = curves[0]
        if TIME_EVALUATION:
            print("sum time float", cc.sum_time_float_eval)
            print("sum time min", cc.sum_time_min_eval)
        # cc.pnt_start = Point2D(0, 1)
        # cc.angle_end = Angle(math.atan(0.5))
        cc.plot()

        # curve = bezier.Curve.from_nodes(cc.nodes_for_print())
        # curve.plot(100)
        # plt.show()
