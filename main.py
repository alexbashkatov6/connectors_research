import sys
import traceback

from PyQt5.QtWidgets import QApplication  # , QGraphicsScene, QGraphicsView, QMainWindow
from PyQt5.QtCore import QObject

from custom_gc import CustomMW  # CustomGC, CustomView,


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


sys.excepthook = excepthook


class Director(QObject):
    def __init__(self):
        super().__init__()
        self.mw = CustomMW()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    d = Director()
    d.mw.show()

    sys.exit(app.exec_())