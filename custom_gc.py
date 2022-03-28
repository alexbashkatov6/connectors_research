from copy import copy
import math

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

POINTS_SIZE = 40
THORN_WIDTH = 5
THORN_LENGTH = 30


class Ellips(QGraphicsPathItem):
    def __init__(self, x: int, y: int, *args, **kwargs):
        # self._x: int = x
        # self._y: int = y
        super().__init__(*args, **kwargs)
        self._base_path = QPainterPath()
        self._base_path.addEllipse(QRectF(x, y, POINTS_SIZE, POINTS_SIZE))

        self.setPath(self._base_path)
        self.setBrush(QBrush(Qt.black))
        # self.setFlags(QGraphicsItem.ItemIsMovable)  #  | QGraphicsItem.ItemIsSelectable

        # self._pen = QPen(Qt.black)
        # self._pen.setWidthF(5)
        # self.setPen(self._pen)


class Thorn(QGraphicsPathItem):
    def __init__(self, x: int, y: int, angle: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        x_end = x + math.cos(math.radians(-angle)) * THORN_LENGTH
        y_end = x + math.sin(math.radians(-angle)) * THORN_LENGTH
        poly = QPolygonF(
                [
                    QPointF(x, y),
                    QPointF(x_end, y_end)
                ])

        self._pen = QPen(Qt.black)
        self._pen.setWidthF(THORN_WIDTH)

        self._base_path = QPainterPath()
        self._base_path.addPolygon(poly)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))
        # self.setFlags(QGraphicsItem.ItemIsMovable)  #  | QGraphicsItem.ItemIsSelectable


class HedgehogPoint(QGraphicsPathItem):
    # хедж-хог
    def __init__(self, x: int, y: int, angles: list[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        angles = angles or []

        self._base_path = QPainterPath()

        self._ellipse = Ellips(x, y)
        self._ellipse.setParentItem(self)
        self._base_path.addPath(self._ellipse.path())

        for angle in angles:
            self._thorn = Thorn(x+POINTS_SIZE/2, y+POINTS_SIZE/2, angle)
            self._thorn.setParentItem(self)
            self._base_path.addPath(self._thorn.path())

        self.setPath(self._base_path)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.addItem(HedgehogPoint(100, 100, [0, 90, 180]))
        self.addItem(HedgehogPoint(200, 200, [45, 135, 270]))


class CustomView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.rotate(-45)
        # self.scale(0.5, 0.5)


class CustomMW(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(40, 40, 1840, 980)
        self.scene = CustomGC(0, 0, 1800, 900)
        self.view = CustomView(self.scene)
        self.setCentralWidget(self.view)
