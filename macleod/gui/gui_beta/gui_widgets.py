import os
from PyQt5.QtWidgets import *
from PyQt5.Qt import QSize, QColor, Qt, QTextFormat, QRect, QPainter

from gui_beta import gui_highlighter, gui_file_helper
from macleod.logical import Symbol


class TabController(QTabWidget):
    def __init__(self, parent=None, ontologies=None):
        QTabWidget.__init__(self, parent)
        self.ontologies = ontologies
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

        new_tab = CodeEditor(self)
        gui_highlighter.CLIFSyntaxHighlighter(new_tab, None, None)
        new_tab.setLineWrapMode(QPlainTextEdit.NoWrap)
        new_tab.setPlainText(file_data)
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
        self.file_helper.remove_key(widget)
        if widget in self.ontologies.keys():
            self.ontologies.pop(widget, None)

    # Returns the index if successful, none if failed
    def focus_tab_from_path(self, path):
        for tab in self.file_helper.paths:
            if self.file_helper.paths[tab] == os.path.normpath(path):
                index = self.indexOf(tab)
                self.setCurrentIndex(index)
                return index
        return None


class ProjectExplorer(QTreeView):
    def __init__(self, parent=None, root_path="", editor=None):
        QTreeWidget.__init__(self, parent)
        self.editor = editor
        model = QFileSystemModel(self)
        model.setRootPath(root_path)
        self.setModel(model)
        self.setRootIndex(model.index(root_path))

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
        if self.editor.focus_tab_from_path(file_path) is None:
            self.editor.add_file(file_path)


class InformationSidebar(QTreeWidget):
    def __init__(self, parent=None, root_path=None):
        QTreeWidget.__init__(self, parent)
        self.root_path = root_path
        self.setColumnCount(3)
        self.setHeaderLabels(["Information", "Arity", "File"])
        # set of strings
        self.variables = set()
        # set of ordered pairs of (string, arity, file)
        self.predicates = set()
        # set of ordered pairs of (string, arity, file)
        self.functions = set()

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
            child.setText(2, p[2])
            predicate_tree.addChild(child)

        function_tree = QTreeWidgetItem()
        function_tree.setText(0, "Functions")
        for f in self.functions:
            child = QTreeWidgetItem()
            child.setText(0, f[0])
            child.setText(1, str(f[1]))
            child.setText(2, f[2])
            function_tree.addChild(child)

        self.insertTopLevelItem(0, variable_tree)
        self.insertTopLevelItem(0, predicate_tree)
        self.insertTopLevelItem(0, function_tree)

    def __logical_search(self, logical, file_path):
        for term in logical.terms:
            if isinstance(term, Symbol.Predicate):
                self.predicates.add((term.name, len(term.variables), file_path))
                self.__symbol_search(term, file_path)
                continue

            if isinstance(term, Symbol.Function):
                self.functions.add((term.name, len(term.variables), file_path))
                self.__symbol_search(term, file_path)
                continue

            if isinstance(term, str):
                self.variables.add(term)
                continue
            self.__logical_search(term, file_path)

    def __symbol_search(self, symbol, file_path):
        for var in symbol.variables:
            if isinstance(var, Symbol.Predicate):
                self.predicates.add((var.name, len(var.variables), file_path))
                self.__symbol_search(var, file_path)
                continue

            if isinstance(var, Symbol.Function):
                self.functions.add((var.name, len(var.variables), file_path))
                self.__symbol_search(var, file_path)
                continue

            if isinstance(var, str):
                self.variables.add(var)
                continue

            self.__logical_search(var, file_path)

    def build_model(self, ontology):
        for axiom in ontology.axioms:
            self.__logical_search(axiom.sentence,
                                  os.path.relpath(ontology.name, self.root_path))
        for import_ontology in ontology.imports.values():
            if import_ontology is None:
                continue

            self.build_model(import_ontology)

    def flush(self):
        self.variables = set()
        self.functions = set()
        self.predicates = set()
        self.clear()

    # True: display symbols from imports, False: just symbols for open file
    # show is a boolean value
    def show_imported_symbols(self, show):
        pass


class ImportSidebar(QTreeWidget):
    def __init__(self, parent=None, root_path=None, editor=None,):
        QTreeWidget.__init__(self, parent)
        self.editor = editor
        self.root_path = root_path
        self.setHeaderHidden(True)
        self.doubleClicked.connect(self.on_double_click)

    def build_tree(self, ontology, parent_item=None):
        new_item = QTreeWidgetItem(self if parent_item is None else parent_item)
        new_item.setText(0, os.path.relpath(ontology.name, self.root_path))
        for imported_ontology in ontology.imports.values():
            if imported_ontology is None:
                continue

            self.build_tree(imported_ontology, new_item)

    def on_double_click(self):
        item = self.selectedItems()[0]
        file_path = os.path.join(self.root_path, item.text(0))
        file_path = os.path.normpath(file_path)
        if self.editor.focus_tab_from_path(file_path) is None:
            self.editor.add_file(file_path)


class Console(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        self.setReadOnly(True)

    def write(self, text):
        self.append(str(text))

    def flush(self):
        self.setText("")


# The two classes come from http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
class LineNumberArea(QWidget):
    def __init__(self, editor=None):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaPaintEvent(self, event):
        #TODO: CHANGE THIS COLOR
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        top = int(top)
        bottom = top + self.blockBoundingRect(block).height()
        bottom = int(bottom)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.line_number_area.width()-2, self.fontMetrics().height(),Qt.AlignRight, number);

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            bottom = int(bottom)
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 4 + self.fontMetrics().width('9') * digits
        return space

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def highlightCurrentLine(self):
        extra_selections = []
        if not self.isReadOnly():
            line_color = QColor(Qt.yellow).lighter(160)
            selection = QTextEdit.ExtraSelection()

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

