import sys, os
import macleod.Filemgt as filemgt
from macleod.gui.gui_beta import gui_widgets, gui_settings, gui_highlighter, gui_threads
from PyQt5.Qt import QApplication, QMainWindow, QTabWidget, QAction, QShortcut, QKeySequence
from PyQt5.Qt import QSplitter, QFileDialog, QStyleFactory, Qt, QMessageBox

# Add the root project folder to the python Path
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../../")

class MacleodApplication(QApplication):
    def __init__(self, argv, output_backup):
        super(MacleodApplication, self).__init__(argv)

        # Save a reference to sys.stdout
        self.output_backup = output_backup

    def closingDown(self):
        """
        Override PyQt's method to deal w/ sys.stdout
        """

        # Reset sys.stdout to what it was before the application opened
        sys.stdout = self.output_backup
        super(MacleodApplication, self).closingDown()


class MacleodWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MacleodWindow, self).__init__(parent)

        # store the project path
        self.root_path = filemgt.read_config('system', 'path')

        # key: CodeEditor object, value: ontology object
        self.ontologies = dict()
        self.setup_widgets()
        self.setup_layout()

    def setup_widgets(self):
        # file editing and tabs
        self.editor_pane = gui_widgets.TabController(self, self.ontologies)
        self.editor_pane.currentChanged.connect(self.__on_tab_change)

        # project navigation
        self.explorer_tab = QTabWidget(self)
        self.project_explorer = gui_widgets.ProjectExplorer(self, self.root_path, self.editor_pane)
        self.explorer_tab.addTab(self.project_explorer, "Directory")
        self.import_explorer = gui_widgets.ImportSidebar(self, self.root_path, self.editor_pane)
        self.explorer_tab.addTab(self.import_explorer, "Imports")

        # informational sidebar
        self.info_bar = gui_widgets.InformationSidebar(self, self.root_path)

        # output
        self.console = gui_widgets.Console(self)

        main_menu = self.menuBar()

        # file menu and associated actions
        file_menu = main_menu.addMenu('File')

        # Create a new tab
        new_action = QAction("New File", self)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.new_command)

        # Open a file
        open_action = QAction("Open", self)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_command)
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_command)

        # Save file; if no file, open dialog
        save_action = QAction("Save", self)
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save_command)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_command)

        # Open Save dialog
        saveas_action = QAction("Save As..", self)
        file_menu.addAction(saveas_action)
        saveas_action.triggered.connect(self.saveas_command)

        # Open settings dialog
        settings_action = QAction("Settings..", self)
        file_menu.addAction(settings_action)
        settings_action.triggered.connect(self.settings_command)

        # Run menu and associated actions
        run_menu = main_menu.addMenu('Run')

        # Run the parse w/out resolving imports
        parse_action = QAction("Parse (No Imports)", self)
        run_menu.addAction(parse_action)
        parse_action.triggered.connect(self.parse_command)

        # Run the parse w/ imports
        parse_imports_action = QAction("Parse (w/ Imports)", self)
        run_menu.addAction(parse_imports_action)
        parse_imports_action.triggered.connect(self.parse_imports_command)

        # Threads
        self.parse_thread = gui_threads.ParseThread()
        self.parse_thread.finished.connect(self.__on_parse_done)

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
        horizontal_splitter.addWidget(self.explorer_tab)
        horizontal_splitter.addWidget(vertical_splitter)
        horizontal_splitter.addWidget(self.info_bar)
        horizontal_splitter.setStretchFactor(0, 1)
        horizontal_splitter.setStretchFactor(1, 4)
        horizontal_splitter.setStretchFactor(2, 1)
        self.setCentralWidget(horizontal_splitter)

    def __on_parse_done(self):
        """
        Update the UI when the parse thread completes
        """

        path = self.editor_pane.file_helper.get_path(self.editor_pane.currentWidget())
        ontology = self.parse_thread.ontology
        self.info_bar.flush()
        self.import_explorer.clear()

        # See if the parse thread caught any errors
        if self.parse_thread.error.contents != "":
            print(self.parse_thread.error.contents)
            self.parse_thread.error.flush()
        self.info_bar.build_model(ontology, path)

        # See if the info bar caught any errors
        if self.info_bar.error:
            print(self.info_bar.error)
        self.info_bar.build_tree()
        self.import_explorer.build_tree(ontology)
        self.add_ontology(ontology)
        gui_highlighter.CLIFSyntaxHighlighter(self.editor_pane.currentWidget(), self.info_bar.predicates,
                                              self.info_bar.functions)

    def add_ontology(self, ontology=None):
        """
        Stores ontology matching the current file
        """
        key = self.editor_pane.currentWidget()
        self.ontologies[key] = ontology

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
        if self.editor_pane.currentWidget() is None:
            return
        self.console.flush()
        self.parse_thread.resolve = False
        self.parse_thread.path = self.editor_pane.file_helper.get_path(self.editor_pane.currentWidget())
        self.parse_thread.text = self.editor_pane.currentWidget().toPlainText()
        if not self.parse_thread.isRunning():
            self.parse_thread.start()

    def settings_command(self):
        settings = gui_settings.MacleodSettings(self)
        settings.exec()

    def parse_imports_command(self):
        if self.editor_pane.currentWidget() is None:
            return

        self.console.flush()
        self.parse_thread.resolve = True
        self.parse_thread.path = self.editor_pane.file_helper.get_path(self.editor_pane.currentWidget())
        self.parse_thread.text = self.editor_pane.currentWidget().toPlainText()
        if not self.parse_thread.isRunning():
            self.parse_thread.start()

    def __on_tab_change(self):
        """
        Event handler for tab changes
        Tries to load a matching ontology for the tab
        """

        key = self.editor_pane.currentWidget()
        if key is None:
            return
        path = self.editor_pane.file_helper.get_path(self.editor_pane.currentWidget())
        self.info_bar.flush()
        self.import_explorer.clear()
        if self.editor_pane.file_helper.is_dirty(key, key.toPlainText()):
            self.parse_command()
        else:
            if key in self.ontologies:
                self.info_bar.build_model(self.ontologies[key], path)
                self.info_bar.build_tree()
                self.import_explorer.build_tree(self.ontologies[key])


# just in case anything gets weird, we will save a pointer to the regular console
backup = sys.stdout
app = MacleodApplication(sys.argv, backup)

# Set the style to "Fusion", which looks similar across all platforms
app.setStyle(QStyleFactory.create('Fusion'))
window = MacleodWindow()

# Capture all errors and print statements in our console
sys.stdout = window.console
window.setWindowTitle("Macleod")
window.show()

# Generic error capturing
while True:
    try:
        sys.exit(app.exec_())
    except Exception as e:
        error = QMessageBox()
        error_text = "An error has occurred:\n{0}".format(e)
        error.setText(error_text)
        error.exec()
