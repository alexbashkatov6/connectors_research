from sympy import Point, are_similar, Line, Point3D, Line3D

# p1 = Point(1, 0)
# p2 = Point(1., 0.)
# p3 = Point(1.1, 0.)
# print(are_similar(p1, p2))
# print(are_similar(p2, p3))
# l1 = Line()
p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(-1, 2, 0)
l1, l2 = Line3D(p1, p2), Line3D(p2, p3)
print(l1.angle_between(l2))
