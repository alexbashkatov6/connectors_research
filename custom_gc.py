from copy import copy

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Ellips(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_path = QPainterPath()
        self._base_path.addEllipse(QRectF(100, 100, 100, 200))

        self._pen = QPen(Qt.black)
        self._pen.setWidthF(5)

        self.setPath(self._base_path)
        self.setPen(self._pen)


class HedgehogPoint(QGraphicsPathItem):
    # хедж-хог
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ellipse = Ellips()
        self._ellipse.setParentItem(self)


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addItem(HedgehogPoint())


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
