import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from macleod.gui import gui_file_helper, gui_settings, gui_highlighter
import os
from macleod.logical import Symbol
from macleod.ClifModuleSet import ClifModuleSet
from macleod.parsing import Parser
import macleod.Filemgt as filemgt

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
        # store the project path
        self.root_path = filemgt.read_config('system', 'path')
        self.setup_widgets()
        self.setup_layout()

    def setup_widgets(self):
        # file editing and tabs
        self.editor_pane = TabController(self)

        # project navigation
        self.project_explorer = ProjectExplorer(self, self.root_path)

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
            self.info_bar.build_model(ontology)
            self.info_bar.build_tree()
        except Exception as e:
            print(e)

    def settings_command(self):
        settings = gui_settings.MacleodSettings(self)
        settings.exec()


class TabController(QTabWidget):
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
        new_highlighter = gui_highlighter.CLIFSyntaxHighlighter(new_tab)
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
    def __init__(self, parent=None, path=""):
        QTreeWidget.__init__(self, parent)
        model = QFileSystemModel(self)
        model.setRootPath(path)
        self.setModel(model)
        self.setRootIndex(model.index(path))

        # We don't need the columns other than the file names
        for i in range(1, model.columnCount()):
            self.hideColumn(i)
        self.setHeaderHidden(True)
        self.doubleClicked.connect(self.on_double_click)

    def on_double_click(self):
        index = self.selectedIndexes()[0]
        model = self.model()
        file_path = model.filePath(index)
        isdir = os.path.isdir(file_path)
        if isdir:
            return
        window.editor_pane.add_file(file_path)


class InformationSidebar(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Information", "Arity"])
        # set of strings
        self.variables = set()
        # set of ordered pairs of (string, arity)
        self.predicates = set()
        # set of ordered pairs of (string, arity)
        self.functions = set()

        self.build_tree()

    def build_tree(self):
        self.clear()
        variable_tree = QTreeWidgetItem()
        variable_tree.setText(0, "Variables")
        for v in self.variables:
            child = QTreeWidgetItem()
            child.setText(0, v)
            variable_tree.addChild(child)

        predicate_tree = QTreeWidgetItem()
        predicate_tree.setText(0, "Predicates")
        for p in self.predicates:
            child = QTreeWidgetItem()
            child.setText(0, p[0])
            child.setText(1, str(p[1]))
            predicate_tree.addChild(child)

        function_tree = QTreeWidgetItem()
        function_tree.setText(0, "Functions")
        for f in self.functions:
            child = QTreeWidgetItem()
            child.setText(0, f[0])
            child.setText(1, str(f[1]))
            function_tree.addChild(child)

        self.insertTopLevelItem(0, variable_tree)
        self.insertTopLevelItem(0, predicate_tree)
        self.insertTopLevelItem(0, function_tree)

    def __logical_search(self, logical):
        for term in logical.terms:
            if isinstance(term, Symbol.Predicate):
                self.predicates.add((term.name, len(term.variables)))
                self.__symbol_search(term)
                continue

            if isinstance(term, Symbol.Function):
                self.functions.add((term.name, len(term.variables)))
                self.__symbol_search(term)
                continue

            if isinstance(term, str):
                self.variables.add(term)
                continue
            self.__logical_search(term)

    def __symbol_search(self, symbol):
        for var in symbol.variables:
            if isinstance(var, Symbol.Predicate):
                self.predicates.add((var.name, len(var.variables)))
                self.__symbol_search(var)
                continue

            if isinstance(var, Symbol.Function):
                self.functions.add((var.name, len(var.variables)))
                self.__symbol_search(var)
                continue

            if isinstance(var, str):
                self.variables.add(var)
                continue

            self.__logical_search(var)

    def build_model(self, ontology):
        for axiom in ontology.axioms:
            self.__logical_search(axiom.sentence)


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
app.setStyle(QStyleFactory.create('Fusion'))
window = MacleodWindow()
sys.stdout = window.console
window.setWindowTitle("Macleod")
window.show()

sys.exit(app.exec_())