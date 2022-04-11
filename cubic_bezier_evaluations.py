import sympy

""" Cubic curve optimization 
Given points is p0, p3, and tangent angles in this points
Need to evaluate delta1 from p0 and delta2 from p3 for max curvature minimization"""

t = sympy.Symbol('t')
x0 = sympy.Symbol('x0')
y0 = sympy.Symbol('y0')
x3 = sympy.Symbol('x3')
y3 = sympy.Symbol('y3')
ang0 = sympy.Symbol('ang0')
ang3 = sympy.Symbol('ang3')
delta1 = sympy.Symbol('delta1')
delta2 = sympy.Symbol('delta2')

x1 = x0 + delta1 * sympy.cos(ang0)
y1 = y0 + delta1 * sympy.sin(ang0)
x2 = x3 + delta2 * sympy.cos(ang3)
y2 = y3 + delta2 * sympy.sin(ang3)

x01 = x0 + (x1 - x0) * t
y01 = y0 + (y1 - y0) * t
x12 = x1 + (x2 - x1) * t
y12 = y1 + (y2 - y1) * t
x23 = x2 + (x3 - x2) * t
y23 = y2 + (y3 - y2) * t

xd1 = x01 + (x12 - x01) * t
yd1 = y01 + (y12 - y01) * t
xd2 = x12 + (x23 - x12) * t
yd2 = y12 + (y23 - y12) * t

x = xd1 + (xd2 - xd1) * t
y = yd1 + (yd2 - yd1) * t

x_dt = sympy.simplify(sympy.diff(x, t))
y_dt = sympy.simplify(sympy.diff(y, t))
x_dt2 = sympy.simplify(sympy.diff(x_dt, t))
y_dt2 = sympy.simplify(sympy.diff(y_dt, t))

curv = sympy.simplify((x_dt * y_dt2 - y_dt * x_dt2) / (x_dt**2 + y_dt**2)**1.5)

print(curv)
