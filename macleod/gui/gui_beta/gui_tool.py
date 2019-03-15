from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal
import macleod.Filemgt as filemgt
from bin import clif_converter
import os

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400


class MacleodTool(QDialog):
    def __init__(self, parent=None):
        super(MacleodTool, self).__init__(parent)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Macleod Tools")

class Export(MacleodTool):
    def __init__(self, parent=None, current_dir=None):
        super(Export, self).__init__(parent)
        self.setWindowTitle("Export")
        self.resize(WINDOW_WIDTH, self.height())
        self.setParent(parent)
        self.current_dir = current_dir

        self.consolidate = QCheckBox(parent)

        self.path = QLineEdit(parent)
        self.file_dialog_button = QPushButton(parent)
        self.file_dialog_button.setText("...")
        self.file_dialog_button.setFixedWidth(WINDOW_WIDTH/20)
        sub_layout = QHBoxLayout(parent)
        sub_layout.addWidget(self.path)
        sub_layout.addWidget(self.file_dialog_button)
        self.file_dialog_button.pressed.connect(self.__launch_file_dialog)

        # exit buttons
        exit_buttons = QDialogButtonBox(parent)
        exit_buttons.addButton(QDialogButtonBox.Ok)
        exit_buttons.addButton(QDialogButtonBox.Cancel)
        exit_buttons.button(QDialogButtonBox.Ok).clicked.connect(self.ok_event)
        exit_buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.close)

        layout = QFormLayout(parent)
        layout.addRow("Output Path: ", sub_layout)
        layout.addRow("Include all imports? ", self.consolidate)
        layout.addWidget(exit_buttons)
        self.setLayout(layout)

    def ok_event(self):
        file, file_ext = os.path.splitext(self.path.text())
        options = ""
        options += "-cumulate" if self.consolidate.isChecked() else ""
        clif_converter.convert_single_clif_file(os.path.normpath(self.path.text()), file_ext, not(self.consolidate.isChecked()))

        self.close()

    def __launch_file_dialog(self):
        text = QFileDialog.getSaveFileName(self, "Save File", str(self.current_dir),
                                           "LADR (*.ladr);; TPTP (*.tptp)")
        if text is None or text[0] is None:
            return

        self.path.setText(text[0])