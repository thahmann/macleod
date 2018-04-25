from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal
import macleod.Filemgt as filemgt
import configparser
import os

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400


class MacleodTool(QDialog):
    def __init__(self, parent=None):
        super(MacleodTool, self).__init__(parent)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Macleod Tools")
