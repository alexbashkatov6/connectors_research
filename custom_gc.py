from copy import copy

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class CustomMW(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)