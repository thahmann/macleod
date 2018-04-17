from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSignal
import macleod.Filemgt as filemgt
import configparser
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
        root_dir_label = QLabel("Project Root Directory")

        self.root_dir_edit = QLineEdit()
        self.root_dir_edit.setText(root_dir_path)

        # color settings
        self._color_equals = self._create_color_button("color_equals")
        self._color_predicate = self._create_color_button("color_predicate")
        self._color_function = self._create_color_button("color_function")
        self._color_connective = self._create_color_button("color_connective")
        self._color_not = self._create_color_button("color_not")
        self._color_quantifier = self._create_color_button("color_quantifier")
        self._color_parentheses = self._create_color_button("color_parentheses")
        self._color_find = self._create_color_button("color_find")

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
        highlighter_layout.addRow("Equals: ", self._color_equals)
        highlighter_layout.addRow("Predicates: ", self._color_predicate)
        highlighter_layout.addRow("Functions: ", self._color_function)
        highlighter_layout.addRow("Connectives: ", self._color_connective)
        highlighter_layout.addRow("Negation: ", self._color_not)
        highlighter_layout.addRow("Quantifiers: ", self._color_quantifier)
        highlighter_layout.addRow("Parentheses: ", self._color_parentheses)
        highlighter_layout.addRow("Find (Highlight): ", self._color_find)

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
        if self._check_and_update_root_path():
            self._update_colors()
            self.close()

    def _create_color_button(self, name):
        '''Generate a color button for a particular setting, returns the button.'''
        new_button = QColorButton(name, self)
        try :
            new_button.setColor(filemgt.read_config("gui", name))
        except configparser.NoOptionError:
            pass

        # This will be a blank color if the setting doesn't exist
        return new_button

    def _check_and_update_root_path(self):
        '''Attempt to update in the conf file, returns False if the path is invalid'''
        if not os.path.isdir(self.root_dir_edit.text()):
            self.root_dir_edit.clear()
            self.root_dir_edit.setPlaceholderText("Invalid Path")
            return False
        filemgt.edit_config('system', 'path', self.root_dir_edit.text(), filemgt.config_file)
        return True

    def _update_colors(self):
        self._color_equals.update_color()
        self._color_predicate.update_color()
        self._color_function.update_color()
        self._color_connective.update_color()
        self._color_not.update_color()
        self._color_quantifier.update_color()
        self._color_parentheses.update_color()
        self._color_find.update_color()


# taken from http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html
class QColorButton(QPushButton):
    '''
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    '''

    colorChanged = pyqtSignal()

    def __init__(self, setting_name="", *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._setting_name = setting_name
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        dlg = QColorDialog(self)
        self.setStyleSheet("")
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)

    def update_color(self):
        filemgt.edit_config("gui", self._setting_name, self.color(), filemgt.config_file)
