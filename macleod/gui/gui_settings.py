from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import macleod.Filemgt as filemgt
import os

class MacleodSettings(QDialog):
    def __init__(self, parent=None):
        super(MacleodSettings, self).__init__(parent)
        self.setWindowTitle("Macleod Settings")
        root_dir_path = filemgt.read_config('system', 'path')

        # root directory settings
        root_dir_label = QLabel()
        root_dir_label.setText("Project Root Directory:")
        self.root_dir_edit = QLineEdit()
        self.root_dir_edit.setText(root_dir_path)

        # buttons
        ok_button = QPushButton()
        cancel_button = QPushButton()
        ok_button.setText("OK")
        cancel_button.setText("Cancel")
        ok_button.clicked.connect(self.ok_event)
        cancel_button.clicked.connect(self.close)

        # layout
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout(self)
        main_layout.addWidget(root_dir_label)
        main_layout.addWidget(self.root_dir_edit)
        main_layout.addLayout(button_layout, Qt.AlignRight)
        button_layout.addWidget(ok_button, 0, Qt.AlignRight)
        button_layout.addWidget(cancel_button, 0, Qt.AlignRight)
        self.setLayout(main_layout)

    def ok_event(self):
        if not os.path.isdir(self.root_dir_edit.text()):
            self.root_dir_edit.clear()
            return

        filemgt.edit_config('system', 'path', self.root_dir_edit.text(), filemgt.config_file)
        self.close()