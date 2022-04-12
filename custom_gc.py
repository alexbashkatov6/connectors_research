from __future__ import annotations
from copy import copy
from typing import Optional
import math
from dataclasses import dataclass

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPathItem, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsSceneMouseEvent, QGraphicsTextItem, QWidget, \
    QStyleOptionGraphicsItem, QStyle
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainterPath, QFont, QFontMetrics, QPainterPathStroker, QTransform, \
    QRegion, QPainter
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF

from sympy import Point2D
from graphic_numpy import Angle, angle_rad_difference, UniversalConnectionCurve

POINTS_SIZE = 10
THORN_WIDTH = 2  # 5
THORN_LENGTH = 20  # 30

THORN_LABEL_FONT_FAMILY = "times"
THORN_LABEL_FONT_SIZE = 10
THORN_LABEL_FONT = QFont(THORN_LABEL_FONT_FAMILY, THORN_LABEL_FONT_SIZE)

H_CLICK_BEZIER = 6


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


class HedgehogGraphicsPathItem(QGraphicsPathItem):

    def __init__(self, base_hp: HedgehogPoint):
        super().__init__()
        self.base_hp = base_hp
        self.start_pos = None

    def setPath(self, path: QPainterPath) -> None:
        super().setPath(path)
        ps = QPainterPathStroker()
        ps.setWidth(40)
        self._outshape = ps.createStroke(path)

    def shape(self) -> QPainterPath:
        return self._outshape

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None) -> None:
        my_option = QStyleOptionGraphicsItem()
        my_option.state &= ~QStyle.State_Selected
        super().paint(painter, my_option, widget)

    def mousePressEvent(self, e: QGraphicsSceneMouseEvent):
        super().mousePressEvent(e)
        self.start_pos = e.scenePos()

    def mouseReleaseEvent(self, e: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(e)
        self.start_pos = None

    def mouseMoveEvent(self, e: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(e)
        start_pos = self.start_pos
        end_pos = e.scenePos()
        self.start_pos = e.scenePos()
        self.base_hp.moved(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())


class HedgehogPoint:
    # хедж-хог
    def __init__(self, x_center: int, y_center: int, angles: list[int] = None):
        """ angles in degrees """
        self.x_center: int = x_center
        self.y_center: int = y_center
        self.angles = angles or []
        self.thorn_ends = []
        self.connectors: list[tuple[Connector, str]] = []  # [(cnct, "start")
        assert len(self.angles) <= 3
        self.ellipse = None
        self.thorns = []
        self._path_item = HedgehogGraphicsPathItem(self)
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    def moved(self, x0, y0, x_new, y_new):
        for cnct_cond in self.connectors:
            cnct, start_or_end = cnct_cond
            if start_or_end == "start":
                old_cond = cnct.start_cond
            else:
                old_cond = cnct.end_cond
            old_coords = old_cond.x, old_cond.y, old_cond.angle
            new_coords = old_coords[0] + x_new - x0, old_coords[1] + y_new - y0, old_coords[2]
            if start_or_end == "start":
                cnct.start_cond = ConnectCondition(*new_coords)
            else:
                cnct.end_cond = ConnectCondition(*new_coords)

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
            self.thorn_ends.append((thorn.x_end, thorn.y_end))
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


class ShapedQGraphicsPathItem(QGraphicsPathItem):

    def setPath(self, path: QPainterPath) -> None:
        super().setPath(path)
        ps = QPainterPathStroker()
        ps.setWidth(40)
        self._outshape = ps.createStroke(path)

    def shape(self) -> QPainterPath:
        return self._outshape

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None) -> None:
        my_option = QStyleOptionGraphicsItem()
        my_option.state &= ~QStyle.State_Selected
        super().paint(painter, my_option, widget)


class Connector:
    def __init__(self, start_cond: ConnectCondition, end_cond: ConnectCondition):
        self._start_cond = start_cond
        self._end_cond = end_cond
        self._path_item = ShapedQGraphicsPathItem()
        self._path_item.setZValue(-10)
        self._base_path = QPainterPath()
        self.evaluate_path()
        self.set_view_properties()

    @property
    def path_item(self):
        return self._path_item

    @property
    def start_cond(self):
        return self._start_cond

    @start_cond.setter
    def start_cond(self, val):
        self._start_cond = val
        self.evaluate_path()

    @property
    def end_cond(self):
        return self._end_cond

    @end_cond.setter
    def end_cond(self, val):
        self._end_cond = val
        self.evaluate_path()

    def evaluate_path(self):
        self._base_path.clear()
        point_start = Point2D(self.start_cond.x, self.start_cond.y)
        angle_start = Angle(-math.radians(self.start_cond.angle))
        point_end = Point2D(self.end_cond.x, self.end_cond.y)
        angle_end = Angle(-math.radians(self.end_cond.angle))
        conn_curve = UniversalConnectionCurve(point_start, point_end, angle_start, angle_end)
        control_point_1 = conn_curve.start_dir_point
        control_point_2 = conn_curve.end_dir_point
        self._base_path.moveTo(self.start_cond.x, self.start_cond.y)
        self._base_path.cubicTo(QPointF(control_point_1.x, control_point_1.y),
                                QPointF(control_point_2.x, control_point_2.y),
                                QPointF(self.end_cond.x, self.end_cond.y))
        self.path_item.setPath(self._base_path)

    def set_view_properties(self):
        pen = QPen(Qt.black)
        pen.setWidthF(THORN_WIDTH)
        self.path_item.setPen(pen)
        self.path_item.setFlags(QGraphicsItem.ItemIsSelectable)  # QGraphicsItem.ItemIsMovable |

    def path(self):
        return self._base_path


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBackgroundBrush(QBrush(Qt.white))
        hp_1 = self.add_hp(200, 200, [45, 135, 270])
        hp_2 = self.add_hp(300, 500, [0, 90, 180])
        cnct_12_22 = self.add_connector(hp_1, 2, hp_2, 2)

    def add_hp(self, x, y, angles) -> HedgehogPoint:
        hp = HedgehogPoint(x, y, angles)
        self.addItem(hp.path_item)
        return hp

    def add_connector(self, hp1: HedgehogPoint, num_point_1: int,
                      hp2: HedgehogPoint, num_point_2: int) -> Connector:
        cc1 = ConnectCondition(*hp1.thorn_ends[num_point_1], hp1.angles[num_point_1])
        cc2 = ConnectCondition(*hp2.thorn_ends[num_point_2], hp2.angles[num_point_2])
        cnct = Connector(cc1, cc2)
        hp1.connectors.append((cnct, "start"))
        hp2.connectors.append((cnct, "end"))
        self.addItem(cnct.path_item)
        return cnct


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
