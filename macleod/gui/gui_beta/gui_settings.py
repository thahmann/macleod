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
        self._color_equals = self.__create_color_button("color_equals")
        self._color_predicate = self.__create_color_button("color_predicate")
        self._color_function = self.__create_color_button("color_function")
        self._color_connective = self.__create_color_button("color_connective")
        self._color_not = self.__create_color_button("color_not")
        self._color_quantifier = self.__create_color_button("color_quantifier")
        self._color_parentheses = self.__create_color_button("color_parentheses")
        self._color_find = self.__create_color_button("color_find")

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
        if self.__check_and_update_root_path():
            self.__update_colors()
            self.close()

    def __create_color_button(self, name):
        '''Generate a color button for a particular setting, returns the button.'''
        new_button = QColorButton(name, self)
        try :
            new_button.set_color(filemgt.read_config("gui", name))
        except configparser.NoOptionError:
            pass

        # This will be a blank color if the setting doesn't exist
        return new_button

    def __check_and_update_root_path(self):
        """Attempt to update in the conf file, returns False if the path is invalid"""
        if not os.path.isdir(self.root_dir_edit.text()):
            self.root_dir_edit.clear()
            self.root_dir_edit.setPlaceholderText("Invalid Path")
            return False
        filemgt.edit_config('system', 'path', self.root_dir_edit.text(), filemgt.config_file)
        return True

    def __update_colors(self):
        """
        Write every color in the settings to the conf files
        """

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
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal()

    def __init__(self, setting_name="", *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._setting_name = setting_name
        self.setMaximumWidth(32)
        self.pressed.connect(self.on_color_picker)

    def set_color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def on_color_picker(self):
        """
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.
        """

        dlg = QColorDialog(self)
        self.setStyleSheet("")
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.set_color(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.set_color(None)

        return super(QColorButton, self).mousePressEvent(e)

    def update_color(self):
        """
        Writes the colors out to the conf file
        """
        filemgt.edit_config("gui", self._setting_name, self.color(), filemgt.config_file)
