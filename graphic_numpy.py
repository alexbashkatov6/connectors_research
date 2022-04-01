import numpy as np
import scipy
from scipy.spatial.transform import Rotation as R
import bezier
from matplotlib import pyplot as plt


class Point2D:
    def __init__(self, x, y):
        self.coords = np.array([x, y])


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

        r = R.from_rotvec(np.pi/2 * np.array([0, 0, 1]))
        print(r.apply([1, 2, 0]))

    test_3 = True
    if test_3:
        nodes = np.asfortranarray([
            [0.0, 1.0, 1.0],
            [0.0, 0.1, 0.5],
        ])
        curve = bezier.Curve.from_nodes(nodes)  # , degree=2

        print(curve)
        print(curve.length)

        curve.plot(100)
        plt.show()

        x = np.linspace(0, 1, 50)
        y = curve.evaluate_multi(x)[1]
        print("y", y)
        # plt.title("Графики") # заголовок
        # plt.xlabel("x") # ось абсцисс
        # plt.ylabel("y") # ось ординат
        # plt.grid()      # включение отображение сетки
        # plt.plot(x, y)  # построение графика