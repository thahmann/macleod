from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MacleodSettings(QDialog):
    def __init__(self, parent=None):
        super(MacleodSettings, self).__init__(parent)
        self.setWindowTitle("Macleod Settings")

        layout = QVBoxLayout(self)

        # root directory settings
        root_dir_label = QLabel()
        root_dir_label.setText("Project Root Directory:")
        root_dir = QPlainTextEdit()
        layout.addWidget(root_dir_label)
        layout.addWidget(root_dir)