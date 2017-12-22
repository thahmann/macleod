import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from macleod.gui import gui_file_helper, gui_settings
import os
from macleod.logical import Symbol
from macleod.ClifModuleSet import ClifModuleSet
from macleod.parsing import Parser

class MacleodApplication(QApplication):
    def __init__(self, argv, output_backup):
        super(MacleodApplication, self).__init__(argv)
        self.output_backup = output_backup
    def closingDown(self):
        sys.stdout = self.output_backup
        super(MacleodApplication, self).closingDown()

class MacleodWindow(QMainWindow):
    def __init__(self, parent=None, standard_output=None):
        super(MacleodWindow, self).__init__(parent)
        self.setup_widgets()
        self.setup_layout()

    def setup_widgets(self):
        # file editing and tabs
        self.editor_pane = EditorPane(self)

        # project navigation
        self.project_explorer = ProjectExplorer(self)

        # informational sidebar
        self.info_bar = InformationSidebar(self)

        # output
        self.console = Console(self)

        main_menu = self.menuBar()

        # file menu and associated actions
        file_menu = main_menu.addMenu('File')

        new_action = QAction("New File", self)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.new_command)

        open_action = QAction("Open", self)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_command)
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_command)

        save_action = QAction("Save", self)
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save_command)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_command)

        saveas_action = QAction("Save As..", self)
        file_menu.addAction(saveas_action)
        saveas_action.triggered.connect(self.saveas_command)

        settings_action = QAction("Settings..", self)
        file_menu.addAction(settings_action)
        settings_action.triggered.connect(self.settings_command)

        # edit menu and associated actions
        run_menu = main_menu.addMenu('Run')

        parse_action = QAction("Parse", self)
        run_menu.addAction(parse_action)
        parse_action.triggered.connect(self.parse_command)

    def setup_layout(self):
        # group the editor with the console
        vertical_splitter = QSplitter(self)
        vertical_splitter.setOrientation(Qt.Vertical)
        vertical_splitter.addWidget(self.editor_pane)
        vertical_splitter.addWidget(self.console)
        vertical_splitter.setStretchFactor(0, 3)
        vertical_splitter.setStretchFactor(1, 1)

        # group
        horizontal_splitter = QSplitter(self)
        horizontal_splitter.addWidget(self.project_explorer)
        horizontal_splitter.addWidget(vertical_splitter)
        horizontal_splitter.addWidget(self.info_bar)
        horizontal_splitter.setStretchFactor(0, 1)
        horizontal_splitter.setStretchFactor(1, 4)
        horizontal_splitter.setStretchFactor(2, 1)
        self.setCentralWidget(horizontal_splitter)

    def open_command(self):
        filename = QFileDialog.getOpenFileName(self, "Open File", str(os.curdir),
                                               "Common Logic Files (*.clif);; All files (*)")

        if not filename[0]:
            return

        self.editor_pane.add_file(filename[0])

    def new_command(self):
        self.editor_pane.add_file()

    def save_command(self):
        text_widget = self.editor_pane.currentWidget()
        path = self.editor_pane.file_helper.get_path(text_widget)
        if path is None:
            return self.saveas_command()
        f = open(path, 'w')
        with f:
            f.write(text_widget.toPlainText())
        self.editor_pane.file_helper.update_clean_hash(text_widget, text_widget.toPlainText())
        return path


    def saveas_command(self):
        text_widget = self.editor_pane.currentWidget()
        filename = QFileDialog.getSaveFileName(self, "Save As..", str(os.curdir),
                                               "Common Logic Files (*.clif);; All files (*)")
        path = filename[0]
        if path == "":
            return None

        f = open(path, 'w')
        with f:
            f.write(text_widget.toPlainText())
        self.editor_pane.setTabText(self.editor_pane.currentIndex(), os.path.basename(path))
        self.editor_pane.file_helper.add_path(text_widget, path)
        self.editor_pane.file_helper.update_clean_hash(text_widget, text_widget.toPlainText())
        return path


    def parse_command(self):
        text_widget = self.editor_pane.currentWidget()
        path = self.save_command()
        if path is None:
            return

        self.console.flush()
        try:
            ontology = Parser.parse_file(path, os.path.dirname(path), os.path.basename(path))
            self.info_bar.populate_from_ontology(ontology)
        except Exception as e:
            print(e)

    def settings_command(self):
        settings = gui_settings.MacleodSettings(self)
        settings.show()


class EditorPane(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.setTabsClosable(True)
        self.untitled_file_counter = 1
        self.file_helper = gui_file_helper.GUI_file_helper()
        self.add_file()
        self.tabCloseRequested.connect(self.remove_tab)

    def add_file(self, path=None):
        file_title = "Untitled " + str(self.untitled_file_counter) if path is None else os.path.basename(path)
        file_data = ""
        if path is not None:
            try:
                f = open(path, 'r')
                with f:
                    file_data = f.read()
            except Exception as e:
                print(e)
                return

        new_tab = QTextEdit()
        new_tab.setLineWrapMode(QTextEdit.NoWrap)
        new_tab.setText(file_data)
        self.addTab(new_tab, file_title)
        self.setCurrentWidget(new_tab)

        self.file_helper.add_clean_hash(new_tab, new_tab.toPlainText())
        self.untitled_file_counter += 1
        if path is None:
            return
        self.file_helper.add_path(new_tab, path)

    def remove_tab(self, index):
        widget = self.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.removeTab(index)


class ProjectExplorer(QTreeView):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.setModel(self.model)

        # We don't need the columns other than the file names
        for i in range(1, self.model.columnCount()):
            self.hideColumn(i)
        self.setHeaderHidden(True)
        self.doubleClicked.connect(self.on_double_click)

    def on_double_click(self):
        index = self.selectedIndexes()[0]
        path = self.model.filePath(index)
        isdir = os.path.isdir(path)
        if isdir:
            return
        window.editor_pane.add_file(path)

class InformationSidebar(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.setHeaderLabel("Information")
        self.variables = QTreeWidgetItem()
        self.variables.setText(0, "Variables")
        self.predicates = QTreeWidgetItem()
        self.predicates.setText(0, "Predicates")
        self.functions = QTreeWidgetItem()
        self.functions.setText(0, "Functions")

        self.insertTopLevelItem(0, self.variables)
        self.insertTopLevelItem(0, self.predicates)
        self.insertTopLevelItem(0, self.functions)

    def populate_from_ontology(self, ontology):
        for axiom in ontology.axioms:
            self.recursive_search(axiom.sentence)

    def recursive_search(self, logical):
        for term in logical.terms:
            if isinstance(term, Symbol.Predicate) or isinstance(term, Symbol.Function):
                self.add_symbol(term)
                continue
            if isinstance(term, str):
                self.add_variable(term)
                continue
            self.recursive_search(term)

    def add_variable(self, var):
        variable = QTreeWidgetItem()
        variable.setText(0, var)
        self.variables.addChild(variable)

    def add_symbol(self, sym):
        symbol = QTreeWidgetItem()
        symbol.setText(0, str(sym))
        if isinstance(sym, Symbol.Function):
            symbol.setText(1, str(len(sym.variables)))
            self.functions.addChild(symbol)
        else:
            self.predicates.addChild(symbol)
        for variable in sym.variables:
            if isinstance(variable, Symbol.Predicate) or isinstance(variable, Symbol.Function):
                self.add_symbol(variable)
                continue
            if isinstance(variable, str):
                self.add_variable(variable)
                continue
            self.recursive_search(variable)

class Console(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        self.setReadOnly(True)

    def write(self, text):
        self.append(str(text))

    def flush(self):
        self.setText("")

# just in case anything gets weird, we will save a pointer to the regular console
backup = sys.stdout

app = MacleodApplication(sys.argv, backup)
window = MacleodWindow()
sys.stdout = window.console
window.setWindowTitle("Macleod")
window.show()

sys.exit(app.exec_())