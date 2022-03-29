from copy import copy
import math

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

POINTS_SIZE = 40
THORN_WIDTH = 5
THORN_LENGTH = 30


class Ellips:
    def __init__(self, x_center: int, y_center: int):
        self.x_center: int = x_center
        self.y_center: int = y_center
        self._path_item = QGraphicsPathItem()
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    def evaluate_path(self):
        self._base_path.clear()
        self._base_path.addEllipse(QRectF(self.x_center - POINTS_SIZE/2, self.y_center - POINTS_SIZE/2,
                                          POINTS_SIZE, POINTS_SIZE))
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        self.path_item.setBrush(QBrush(Qt.black))

    def path(self):
        return self._base_path


class Thorn:
    def __init__(self, x_start: int, y_start: int, angle: int):
        self.x_start: int = x_start
        self.y_start: int = y_start
        self.angle: int = angle
        self._path_item = QGraphicsPathItem()
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    def evaluate_path(self):
        self._base_path.clear()
        x_end = self.x_start + math.cos(math.radians(-self.angle)) * THORN_LENGTH
        y_end = self.x_start + math.sin(math.radians(-self.angle)) * THORN_LENGTH
        poly = QPolygonF(
                [
                    QPointF(self.x_start, self.y_start),
                    QPointF(x_end, y_end)
                ])
        self._base_path.addPolygon(poly)
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        pen = QPen(Qt.black)
        pen.setWidthF(THORN_WIDTH)
        self.path_item.setPen(pen)
        self.path_item.setBrush(QBrush(Qt.black))

    def path(self):
        return self._base_path


class HedgehogPoint:
    # хедж-хог
    def __init__(self, x_center: int, y_center: int, angles: list[int] = None):
        self.x_center: int = x_center
        self.y_center: int = y_center
        self.angles = angles or []
        self._path_item = QGraphicsPathItem()
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    def evaluate_path(self):
        self._base_path.clear()

        ellipse = Ellips(self.x_center, self.y_center)
        ellipse.path_item.setParentItem(self.path_item)
        self._base_path.addPath(ellipse.path())

        for angle in self.angles:
            thorn = Thorn(self.x_center, self.y_center, angle)
            thorn.path_item.setParentItem(self.path_item)
            self._base_path.addPath(thorn.path())

        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        self.path_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.addItem(HedgehogPoint(100, 100, [0, 90, 180]).path_item)
        self.addItem(HedgehogPoint(200, 200, [45, 135, 270]).path_item)


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
