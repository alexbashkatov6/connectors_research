from __future__ import annotations
from copy import copy
import math
from dataclasses import dataclass

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPathItem, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsSceneMouseEvent, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainterPath, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF

from graphical_object import Angle, angle_rad_difference, BoundedCurve, Point2D, CECurveType

POINTS_SIZE = 40
THORN_WIDTH = 5  # 5
THORN_LENGTH = 30  # 30

THORN_LABEL_FONT_FAMILY = "times"
THORN_LABEL_FONT_SIZE = 10
THORN_LABEL_FONT = QFont(THORN_LABEL_FONT_FAMILY, THORN_LABEL_FONT_SIZE)

H_CLICK_BEZIER = 20


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
        self.x_end: int = x_start
        self.y_end: int = y_start
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
        self.x_end = self.x_start + math.cos(math.radians(-self.angle)) * THORN_LENGTH
        self.y_end = self.y_start + math.sin(math.radians(-self.angle)) * THORN_LENGTH
        poly = QPolygonF(
                [
                    QPointF(self.x_start, self.y_start),
                    QPointF(self.x_end, self.y_end)
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
        self.ellipse = None
        self.thorns = []
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
        self.ellipse = ellipse
        self._base_path.addPath(ellipse.path())

        for angle in self.angles:
            thorn = Thorn(self.x_center, self.y_center, angle)
            thorn.path_item.setParentItem(self.path_item)
            self.thorns.append(thorn)
            self._base_path.addPath(thorn.path())

        self.evaluate_thorn_labels()
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        self.path_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def evaluate_thorn_labels(self):
        """ if distance between two rays less then mean, label should be placed outside this angle """
        sizes = []
        widths = []
        heights = []
        radiuses = []
        rad_angles = []
        differences = []

        """ Stage 1. Differences """
        fm = QFontMetrics(THORN_LABEL_FONT)
        for i, angle in enumerate(self.angles):
            br = fm.boundingRect(str(i))
            w = br.width()
            widths.append(w)
            h = br.height()
            heights.append(h)
            sizes.append((w, h))
            radiuses.append(0.5 * (w ** 2 + h ** 2) ** 0.5)
            rad_angles.append(Angle(math.radians(angle)))
            if i != 0:
                differences.append(angle_rad_difference(rad_angles[i], rad_angles[i - 1]))
        differences.append(angle_rad_difference(rad_angles[0], rad_angles[-1]))

        """ Stage 2. Sides """
        sides = []  # +1 means label should be placed counterclockwise
        segm_count = len(self.angles)
        mean_angle = 2 * math.pi / segm_count
        for difference in differences:
            if (abs(difference) - mean_angle) * difference < 0:
                sides.append(1)
            else:
                sides.append(-1)
        sides = [sides[-1]] + sides[:-1]

        """ Stage 3. Centers """
        centers = []
        for i, thorn in enumerate(self.thorns):
            to_center_angle = thorn.angle + sides[i] * 90
            x_center = thorn.x_end + radiuses[i] * math.cos(math.radians(to_center_angle))
            y_center = thorn.y_end - radiuses[i] * math.sin(math.radians(to_center_angle))
            centers.append((x_center, y_center))

        """ Stage 4. Corners """
        corners = []
        for i, center in enumerate(centers):
            corners.append((center[0]-widths[i]/2, center[1]+heights[i]/2))
        for i, corner in enumerate(corners):
            tl = ThornLabel(*corner, i)
            self._base_path.addPath(tl.path())
            tl.path_item.setParentItem(self.path_item)


@dataclass
class ConnectCondition:
    x: int
    y: int
    angle: int


# class ConnectorShape(QGraphicsPathItem):
#     def __init__(self, base_connector: Connector):
#         super().__init__()
#         self.base_connector = base_connector
#
#     @property
#     def base_connector(self) -> Connector:
#         return self._base_connector
#
#     @base_connector.setter
#     def base_connector(self, c: Connector):
#         self._base_connector = c
#
#     def shape(self) -> QPainterPath:
#         base_path = copy(self.base_connector.path)
#         base_path.


class Connector:
    def __init__(self, start_cond: ConnectCondition, end_cond: ConnectCondition):
        self.start_cond = start_cond
        self.end_cond = end_cond
        self._path_item = QGraphicsPathItem()
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    def evaluate_path(self):
        self._base_path.clear()
        point_start = Point2D(self.start_cond.x, self.start_cond.y)
        angle_start = Angle(-math.radians(self.start_cond.angle))
        point_end = Point2D(self.end_cond.x, self.end_cond.y)
        angle_end = Angle(-math.radians(self.end_cond.angle))
        conn_curve = BoundedCurve(point_start, point_end, angle_start, angle_end)
        if conn_curve.geom_type != CECurveType.line_segment:
            self._base_path.moveTo(self.start_cond.x, self.start_cond.y)
            control_point = conn_curve.bezier_control_point
            self._base_path.quadTo(QPointF(control_point.x, control_point.y),
                                   QPointF(self.end_cond.x, self.end_cond.y))
        else:
            pass
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        pen = QPen(Qt.black)
        pen.setWidthF(THORN_WIDTH)
        self.path_item.setPen(pen)
        # self.path_item.shape()
        self.path_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)


    def path(self):
        return self._base_path


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.add_hp(200, 200, [45, 135, 270])
        self.add_hp(300, 500, [0, 90, 180])
        self.add_connector(ConnectCondition(200, 200, 270), ConnectCondition(300, 500, 180))

        # bp = QPainterPath()
        # bp.moveTo(100, 100)
        # bp.quadTo(QPointF(100, 100), QPointF(200, 300))
        # item = QGraphicsPathItem()
        # item.setPath(bp)
        # self.addItem(item)

    def add_hp(self, x, y, angles):
        self.addItem(HedgehogPoint(x, y, angles).path_item)

    def add_connector(self, cc1: ConnectCondition, cc2: ConnectCondition):
        self.addItem(Connector(cc1, cc2).path_item)


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
