import sympy

#curv_ds = sympy.simplify(sympy.diff(curv,s))
#curv_dt = sympy.simplify(sympy.diff(curv,t))
# expr.subs([(x, 2), (y, 4), (z, 0)])
# sympy.limit(sympy.sin(x)/x, x, 0)
# ((x**2 + x + 1) * (x**2 + x + 1)).as_poly()

# need symbols
t = sympy.Symbol('t')
x1 = sympy.Symbol('x1')
y1 = sympy.Symbol('y1')
x2 = sympy.Symbol('x2')
y2 = sympy.Symbol('y2')
kx = sympy.Symbol('kx')
ky = sympy.Symbol('ky')
s = sympy.Symbol('s')

# intersect point coords (on line k)
x3 = x1 + kx * s
y3 = y1 + ky * s

# parametric Point 1
xP1 = x3 * t + x1 * (1 - t)
yP1 = y3 * t + y1 * (1 - t)

# parametric Point 2
xP2 = x2 * t + x3 * (1 - t)
yP2 = y2 * t + y3 * (1 - t)

# parametric line between points P1 and P2
xP = xP2 * t + xP1 * (1 - t)
yP = yP2 * t + yP1 * (1 - t)

# derivation
xP_dt = sympy.simplify(sympy.diff(xP,t))
yP_dt = sympy.simplify(sympy.diff(yP,t))
xP_dt2 = sympy.simplify(sympy.diff(xP_dt,t))
yP_dt2 = sympy.simplify(sympy.diff(yP_dt,t))

# curvature
curv = sympy.simplify((xP_dt * yP_dt2 - yP_dt * xP_dt2) / (xP_dt**2 + yP_dt**2)**1.5)

#print(xP_dt)
#print(yP_dt)
#print(xP_dt2)
#print(yP_dt2)

print(curv)
