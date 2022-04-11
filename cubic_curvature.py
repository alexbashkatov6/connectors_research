import math
import time
from scipy.optimize import minimize
import numpy as np


def cubic_curvature(t, deltas, x0, y0, x3, y3, ang0, ang3):
    delta1, delta2 = deltas
    return 0.666666666666667*\
((3*delta1*t*math.sin(ang0) - 2*delta1*math.sin(ang0) - 3*delta2*t*math.sin(ang3) + delta2*math.sin(ang3) + 2*t*y0 - 2*t*y3 - y0 + y3)
*(3*delta1*t**2*math.cos(ang0) - 4*delta1*t*math.cos(ang0) + delta1*math.cos(ang0) - 3*delta2*t**2*math.cos(ang3) + 2*delta2*t*math.cos(ang3) + 2*t**2*x0 - 2*t**2*x3 - 2*t*x0 + 2*t*x3)
- (3*delta1*t*math.cos(ang0) - 2*delta1*math.cos(ang0) - 3*delta2*t*math.cos(ang3) + delta2*math.cos(ang3) + 2*t*x0 - 2*t*x3 - x0 + x3)
*(3*delta1*t**2*math.sin(ang0) - 4*delta1*t*math.sin(ang0) + delta1*math.sin(ang0) - 3*delta2*t**2*math.sin(ang3) + 2*delta2*t*math.sin(ang3) + 2*t**2*y0 - 2*t**2*y3 - 2*t*y0 + 2*t*y3))\
/((3*delta1*t**2*math.sin(ang0) - 4*delta1*t*math.sin(ang0) + delta1*math.sin(ang0) - 3*delta2*t**2*math.sin(ang3) + 2*delta2*t*math.sin(ang3) + 2*t**2*y0 - 2*t**2*y3 - 2*t*y0 + 2*t*y3)**2
+ (3*delta1*t**2*math.cos(ang0) - 4*delta1*t*math.cos(ang0) + delta1*math.cos(ang0) - 3*delta2*t**2*math.cos(ang3) + 2*delta2*t*math.cos(ang3) + 2*t**2*x0 - 2*t**2*x3 - 2*t*x0 + 2*t*x3)**2)**1.5

def inversed_curvature(*args):
    return -cubic_curvature(*args)

# print(inversed_curvature(0.5,
#                       (706.719, 706.719), 0, 0, 1e+3, 1e+3,
#                       math.atan(0.5), -0.5*math.pi-math.atan(0.5)))

def max_curvature(*args):
    # print("args = ", args)
    start_time = time.time()
    res = minimize(inversed_curvature, 0.5, args=args, method="Powell", bounds=[(0, 1)])
    return -res.fun, res.x
    # print("eval time = ", time.time()-start_time)
    # print("res = ", res)

# print(inversed_curvature(0.5, 0, 0, 1e+3, 1e+3,
#                       math.atan(0.5), -0.5*math.pi-math.atan(0.5),
#                       706.719, 706.719))

# print(max_curvature((706.719, 706.719), 0, 0, 1e+3, 1e+3,
#                       math.atan(0.5), -0.5*math.pi-math.atan(0.5)))

# print(inversed_curvature(0.5, 0, 0, 1e+3, 1e+3,
#                       math.atan(0.5), -0.5*math.pi-math.atan(0.5),
#                       706.719, 706.719))
def intermediate_max_curvature(*args):
    return max_curvature(*args)[0]

def deltas_optimization(*args):
    dist = ((args[0]-args[2])**2 + (args[1]-args[3])**2)**0.5
    # start_time = time.time()
    res = minimize(intermediate_max_curvature, x0=np.array([3e-1*dist, 3e-1*dist]), args=args, method="Nelder-Mead",
                   bounds=[(1e-2*dist, np.inf), (1e-2*dist, np.inf)],
                        options={'xtol': 1e-1*dist, "ftol": np.inf})  #
    # print("eval time = ", time.time()-start_time)
    return res
# np.array([3e-1*dist, 3e-1*dist])

# print(deltas_optimization(0, 0, 1e+3, 1e+3,
#                           math.atan(0.5), -0.5 * math.pi - math.atan(0.5)))
