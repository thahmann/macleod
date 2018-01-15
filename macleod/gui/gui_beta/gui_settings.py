from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import macleod.Filemgt as filemgt
import os

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

class MacleodSettings(QDialog):
    def __init__(self, parent=None):
        super(MacleodSettings, self).__init__(parent)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Macleod Settings")
        root_dir_path = filemgt.read_config('system', 'path')
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.setSizePolicy(sp)

        # root directory settings
        root_dir_label = QLabel()
        root_dir_label.setText("Project Root Directory")

        self.root_dir_edit = QLineEdit()
        self.root_dir_edit.setText(root_dir_path)

        # exit buttons
        exit_buttons = QDialogButtonBox(self)
        exit_buttons.addButton(QDialogButtonBox.Ok)
        exit_buttons.addButton(QDialogButtonBox.Cancel)
        exit_buttons.button(QDialogButtonBox.Ok).clicked.connect(self.ok_event)
        exit_buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.close)

        # layout & tabs
        tab_controller = QTabWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tab_controller)

        highlighter_layout = QFormLayout(self)
        parser_layout = QFormLayout(self)
        parser_layout.addWidget(root_dir_label)
        parser_layout.addWidget(self.root_dir_edit)
        main_layout.addWidget(exit_buttons)
        parser_tab = QWidget(self)
        parser_tab.setLayout(parser_layout)
        highlighter_tab = QWidget(self)
        highlighter_tab.setLayout(highlighter_layout)
        tab_controller.addTab(parser_tab, "Parser Settings")
        tab_controller.addTab(highlighter_tab, "Highlighter Settings")
        self.setLayout(main_layout)

    def ok_event(self):
        if not os.path.isdir(self.root_dir_edit.text()):
            self.root_dir_edit.clear()
            return

        filemgt.edit_config('system', 'path', self.root_dir_edit.text(), filemgt.config_file)
        self.close()