import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QTextEdit, QMainWindow, \
    QFileSystemModel, QTreeWidget, QSplitter, QLabel, QFileDialog, QAction, QTreeView
from PyQt5.QtCore import Qt
import os

class MacleodWindow(QMainWindow):
    def __init__(self, parent=None):
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
        open_action = QAction("Open", self)
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_command)
        file_menu.addAction("Save")

        # edit menu and associated actions
        editMenu = main_menu.addMenu('Edit')

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

class EditorPane(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.setTabsClosable(True)

        self.untitled_file_counter = 1

        self.add_file()

        self.tabCloseRequested.connect(self.remove_tab)

    def add_file(self, path=None):
        file_title = "Untitled " + str(self.untitled_file_counter) if path is None else os.path.basename(path)
        new_tab = QTextEdit()
        self.addTab(new_tab, file_title)
        if path is not None:
            f = open(path, 'r')
            with f:
                new_tab.setText((f.read()))
        self.setCurrentWidget(new_tab)

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
        try:
            window.editor_pane.add_file(path)
        except Exception as e:
            print(e)

class InformationSidebar(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)

class Console(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

app = QApplication(sys.argv)
window = MacleodWindow()
window.setWindowTitle("Macleod")
window.show()

sys.exit(app.exec_())