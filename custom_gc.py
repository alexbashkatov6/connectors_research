from copy import copy
import math

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPathItem, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsSceneMouseEvent, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainterPath, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF

from graphical_object import Angle, angle_rad_difference

POINTS_SIZE = 40
THORN_WIDTH = 5
THORN_LENGTH = 30

THORN_LABEL_FONT_FAMILY = "times"
THORN_LABEL_FONT_SIZE = 40
THORN_LABEL_FONT = QFont(THORN_LABEL_FONT_FAMILY, THORN_LABEL_FONT_SIZE)


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
        y_end = self.y_start + math.sin(math.radians(-self.angle)) * THORN_LENGTH
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


class ThornLabel:
    def __init__(self, x: int, y: int, num: int):
        self.x: int = x
        self.y: int = y
        self.num: int = num
        self._path_item = QGraphicsPathItem()
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    def evaluate_path(self):
        self._base_path.clear()
        point = QPointF(self.x, self.y)
        font = THORN_LABEL_FONT
        text = str(self.num)
        self._base_path.addText(point, font, text)
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        self.path_item.setBrush(QBrush(Qt.black))

    def path(self):
        return self._base_path


class HedgehogPoint:
    # хедж-хог
    def __init__(self, x_center: int, y_center: int, angles: list[int] = None):
        """ angles in degrees """
        self.x_center: int = x_center
        self.y_center: int = y_center
        self.angles = angles or []
        assert len(self.angles) <= 3
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

        self.evaluate_thorn_labels()
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        self.path_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def evaluate_thorn_labels(self):
        sizes = []
        radiuses = []
        rad_angles = []
        differences = []
        fm = QFontMetrics(THORN_LABEL_FONT)
        # max_index = len(self.angles)-1
        for i, angle in enumerate(self.angles):
            br = fm.boundingRect(str(i))
            w = br.width()
            h = br.height()
            sizes.append((w, h))
            radiuses.append(0.5 * (w ** 2 + h ** 2) ** 0.5)
            rad_angles.append(Angle(math.radians(angle)))
            if i != 0:
                differences.append(angle_rad_difference(rad_angles[i], rad_angles[i - 1]))
        differences.append(angle_rad_difference(rad_angles[0], rad_angles[-1]))
        print(sizes)
        print(radiuses)
        print(rad_angles)
        print("0-2pi", [rad_angle.angle_0_2pi for rad_angle in rad_angles])
        print(differences)


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.add_hp(200, 200, [45, 135, 270])
        self.add_hp(300, 500, [0, 90, 180])

    def add_hp(self, x, y, angles):
        self.addItem(HedgehogPoint(x, y, angles).path_item)


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
