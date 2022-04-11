from __future__ import annotations

import numpy as np
from typing import Callable
import scipy
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize, Bounds
import bezier
from matplotlib import pyplot as plt
from sympy import Point2D, Line2D, Ray2D
import math
from numbers import Real
import time

from cubic_curvature import deltas_optimization

# code example: https://github.com/reiniscimurs/Bezier-Curve/commit/ee845f740261dd7a923b85c5e23173c9cdf7fcf6


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
        self.pnt_start = pnt_start
        self.pnt_end = pnt_end
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.start_dir_point = pnt_start
        self.end_dir_point = pnt_end
        self.init_dir_points()
        if TIME_EVALUATION:
            self.sum_time_float_eval = 0
            self.sum_time_min_eval = 0

    def init_dir_points(self):
        self.eval_dir_points(self.start_approximation)

    def eval_dir_points(self, deltas: tuple[Real, Real]):
        self.start_dir_point = Point2D(self.pnt_start.x + deltas[0] * math.cos(self.angle_start.angle_0_2pi),
                                       self.pnt_start.y + deltas[0] * math.sin(self.angle_start.angle_0_2pi))
        self.end_dir_point = Point2D(self.pnt_end.x + deltas[1] * math.cos(self.angle_end.angle_0_2pi),
                                     self.pnt_end.y + deltas[1] * math.sin(self.angle_end.angle_0_2pi))

    def nodes_for_print(self) -> np.ndarray:
        return np.array([[float(p_.x) for p_ in self.points],
                         [float(p_.y) for p_ in self.points]])

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

    def max_k(self, granuality=100):
        'Calculate maximal curvature of the cubic Bezier curve.'
        k = 0
        t_max = 0
        for t in range(0, granuality+1):
            t = t / granuality
            new_k = self.k_f_t(t)
            if new_k > k:
                k = new_k
                t_max = t
        return k, t_max

    def k_f_t(self, t: Real):
        if TIME_EVALUATION:
            start_time = time.time()
        x_d = 3 * ((1 - t) ** 2) * (float(self.p1.x) - float(self.p0.x)) + \
              6 * (1 - t) * t * (float(self.p2.x) - float(self.p1.x)) + \
              3 * (t ** 2) * (float(self.p3.x) - float(self.p2.x))
        y_d = 3 * ((1 - t) ** 2) * (float(self.p1.y) - float(self.p0.y)) + \
              6 * (1 - t) * t * (float(self.p2.y) - float(self.p1.y)) + \
              3 * (t ** 2) * (float(self.p3.y) - float(self.p2.y))
        x_dd = 6 * (1 - t) * (float(self.p2.x) - 2 * float(self.p1.x) + float(self.p0.x)) + \
               6 * t * (float(self.p3.x) - 2 * float(self.p2.x) + float(self.p1.x))
        y_dd = 6 * (1 - t) * (float(self.p2.y) - 2 * float(self.p1.y) + float(self.p0.y)) + \
               6 * t * (float(self.p3.y) - 2 * float(self.p2.y) + float(self.p1.y))
        # print("params", x_d, y_d, x_dd, y_dd)
        # print("delta ktf = ", time.time()-start_time)
        if TIME_EVALUATION:
            self.sum_time_float_eval += (time.time() - start_time)
        return abs(x_d*y_dd - y_d*x_dd)/math.pow(x_d**2 + y_d**2, 3/2)

    def curv_optimizer(self, deltas: tuple[Real, Real]):
        self.eval_dir_points(deltas)
        # self.start_dir_point = Point2D(self.pnt_start.x + deltas[0] * math.cos(self.angle_start.angle_0_2pi),
        #                                self.pnt_start.y + deltas[0] * math.sin(self.angle_start.angle_0_2pi))
        # self.end_dir_point = Point2D(self.pnt_end.x + deltas[1] * math.cos(self.angle_end.angle_0_2pi),
        #                              self.pnt_end.y + deltas[1] * math.sin(self.angle_end.angle_0_2pi))
        return self.max_k()[0]

    def old_optimize_curvature(self):
        deltas0 = np.array(self.start_approximation)
        if TIME_EVALUATION:
            start_time = time.time()
        # res = minimize(self.curv_optimizer, deltas0, bounds=Bounds([(1e-2)*self.base_distance, (1e-2)*self.base_distance],
        #                                                            [np.inf, np.inf]), method='Powell',
        #                options={'xtol': 1e-1*self.base_distance, "ftol": 1e+10*self.base_distance})  # , "ftol": 1e+5
        res = minimize(self.curv_optimizer, deltas0, bounds=[((1e-2)*self.base_distance, np.inf), ((1e-2)*self.base_distance, np.inf)],
                                                                   method='Powell',
                       options={'xtol': 1e-1*self.base_distance, "ftol": np.inf})  # , "ftol": 1e+5, tol=1e-1*self.base_distance
        # res = minimize(self.curv_optimizer, deltas0, method='CG')
        print("end of")
        if TIME_EVALUATION:
            self.sum_time_min_eval += (time.time() - start_time)
        return res

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
        return res


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

    test_5 = True
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
                                      Angle(-math.pi/2), Angle(math.pi/2))
        ]
        cc = curves[6]
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

    test_6 = False
    if test_6:
        cc = UniversalConnectionCurve(Point2D(0, 0), Point2D(10, 10),
                                      Angle(math.atan(0.5)), Angle(-0.5*math.pi-math.atan(0.5)))
        cc.eval_dir_points((2.026, 7.129))
        print(cc.max_k())
        print(cc.k_f_t(0.5))
        curve = bezier.Curve.from_nodes(cc.nodes_for_print())
        curve.plot(100)
        plt.show()
