import os
from PyQt5.QtWidgets import *
from PyQt5.Qt import QSize, QColor, Qt, QTextFormat, QRect, QPainter, QFontDatabase, QMessageBox

from macleod.gui.gui_beta import gui_highlighter, gui_file_helper
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
        self.file_helper.add_path(new_tab, path)
        self.addTab(new_tab, file_title)
        self.setCurrentWidget(new_tab)
        self.file_helper.add_clean_hash(new_tab, new_tab.toPlainText())
        self.untitled_file_counter += 1

    def remove_tab(self, index):
        widget = self.widget(index)
        if self.file_helper.is_dirty(widget, widget.toPlainText()):
            box = QMessageBox()
            box.setIcon(QMessageBox.Question)
            box.setText("If you continue you will lose your changes\n" +
                        "Would you like to continue?")
            box.setWindowTitle("Unsaved Changes")
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            val = box.exec()
            if val == QMessageBox.No:
                return

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
        QTreeView.__init__(self, parent)
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


class InformationSidebar(QWidget):
    def __init__(self, parent=None, root_path=None):
        QWidget.__init__(self, parent)
        self.tree = QTreeWidget(parent)         # the widget for displaying
        self.root_path = root_path              # the root path of the project
        self.current_file = None                # the path to the currently open file
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Information", "Arity", "File"])
        self.variables = set()                  # set of ordered pairs of (name, path to file)
        self.predicates = set()                 # set of ordered pairs of (name, arity, path to file)
        self.functions = set()                  # set of ordered pairs of (name, arity, path to file)

        self.error = ""                         # A place to store error messages

        self.hide_imports = QCheckBox(parent)   # The Widget for determining visibility
        self.hide_imports.setText("Hide Import Info")
        self.hide_imports.stateChanged.connect(self.__show_imported_symbols)
        self.hide_imports.setChecked(True)

        # layout our two widgets
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.hide_imports)
        self.setLayout(layout)

        # shrink the left and right margins to 1
        old_margin = layout.getContentsMargins()
        new_margin = (1, old_margin[1], 1, old_margin[3])
        layout.setContentsMargins(*new_margin)

        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def build_tree(self):
        self.tree.clear()

        # top level items to group symbols by predicate, function, or variable
        predicate_tree = QTreeWidgetItem()
        function_tree = QTreeWidgetItem()
        variable_tree = QTreeWidgetItem()

        self.tree.addTopLevelItem(function_tree)
        self.tree.addTopLevelItem(predicate_tree)
        self.tree.addTopLevelItem(variable_tree)

        variable_tree.setText(0, "Variables")
        for v in self.variables:
            child = QTreeWidgetItem()
            child.setText(0, v[0])
            child.setText(2, v[1])
            variable_tree.addChild(child)
            self.__format_item(child)

        # Set up groupings for predicates
        predicate_tree.setText(0, "Predicates")
        predicate_unary = QTreeWidgetItem()
        predicate_unary.setText(0, "Unary")
        predicate_tree.addChild(predicate_unary)
        predicate_binary = QTreeWidgetItem()
        predicate_binary.setText(0, "Binary")
        predicate_tree.addChild(predicate_binary)
        predicate_nary = QTreeWidgetItem()
        predicate_nary.setText(0, "N-ary")
        predicate_tree.addChild(predicate_nary)

        for p in self.predicates:
            arity = p[1]
            child = QTreeWidgetItem()
            child.setText(0, p[0])
            child.setText(1, str(arity))
            child.setText(2, p[2])

            if arity == 1:
                predicate_unary.addChild(child)
            elif arity == 2:
                predicate_binary.addChild(child)
            else:
                predicate_nary.addChild(child)

            self.__format_item(child)

        # Hide empty groupings for predicates
        predicate_unary.setHidden(predicate_unary.childCount() == 0)
        predicate_binary.setHidden(predicate_binary.childCount() == 0)
        predicate_nary.setHidden(predicate_nary.childCount() == 0)

        # Set up groupings for functions
        function_tree.setText(0, "Functions")
        function_unary = QTreeWidgetItem()
        function_unary.setText(0, "Unary")
        function_tree.addChild(function_unary)
        function_binary = QTreeWidgetItem()
        function_binary.setText(0, "Binary")
        function_tree.addChild(function_binary)
        function_nary = QTreeWidgetItem()
        function_nary.setText(0, "N-ary")
        function_tree.addChild(function_nary)

        for f in self.functions:
            arity = f[1]
            child = QTreeWidgetItem()
            child.setText(0, f[0])
            child.setText(1, str(arity))
            child.setText(2, f[2])

            if arity == 1:
                function_unary.addChild(child)
            elif arity == 2:
                function_binary.addChild(child)
            else:
                function_nary.addChild(child)

            self.__format_item(child)

        # Hide empty groupings for functions
        function_unary.setHidden(function_unary.childCount() == 0)
        function_binary.setHidden(function_binary.childCount() == 0)
        function_nary.setHidden(function_nary.childCount() == 0)


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
                self.variables.add((term, file_path))
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
                self.variables.add((var, file_path))
                continue

            self.__logical_search(var, file_path)

    def build_model(self, ontology, current_file=None):
        self.current_file = current_file
        if ontology is None:
            return

        for axiom in ontology.axioms:
            try:
                path = os.path.relpath(ontology.name, self.root_path)
            except ValueError:
                path = ontology.name

            self.__logical_search(axiom.sentence, path)
        for import_ontology in ontology.imports.values():
            self.build_model(import_ontology, current_file)

        functions_copy = self.functions.copy()
        predicates_copy = self.predicates.copy()

        for f in self.functions:
            functions_copy.remove(f)
            matches = filter(lambda x: x[0] == f[0], functions_copy)
            for match in matches:
                # Same name and different arity??
                if f[1] != match[1]:
                    self.error += "Function \"{}\" has inconsistent arity\n".format(f[0])

        for p in self.predicates:
            predicates_copy.remove(p)
            matches = filter(lambda x: x[0] == p[0], predicates_copy)
            for match in matches:
                # Same name and different arity??
                if p[1] != match[1]:
                    self.error += "Predicate \"{}\" has inconsistent arity\n".format(p[0])

        # Check for functions and predicates with the same name
        for f in self.functions:
            for p in self.predicates:
                if f[0] == p[0]:
                    self.error += "\"{}\" is treated as both a predicate and a function\n".format(f[0])

    def flush(self):
        self.variables = set()
        self.functions = set()
        self.predicates = set()
        self.error = ""
        self.tree.clear()

    # True: display symbols from imports, False: just symbols for open file
    def __show_imported_symbols(self):
        if self.current_file is None:
            return

        # Here we get the three top level items
        for i in range(self.tree.invisibleRootItem().childCount()):
            top_level_item = self.tree.invisibleRootItem().child(i)
            # Here we get the "arity" groupings
            for j in range(top_level_item.childCount()):
                mid_level_item = top_level_item.child(j)
                count = mid_level_item.childCount()

                # Variables don't have arity groupings, so this is the item we want
                if count == 0:
                    self.__format_item(mid_level_item)
                else:
                    # Here we get all the children of the arity grouping and show or hide them
                    for k in range(count):
                        child = mid_level_item.child(k)
                        self.__format_item(child)

    # Determines whether or not to hide an item
    def __format_item(self, item):
        # first, we hide if necessary
        item_path = item.text(2)
        current_path = os.path.relpath(self.current_file, self.root_path)
        is_hidden = self.hide_imports.isChecked() and item_path != current_path
        item.setHidden(is_hidden)

        # next, we bold if necessary
        item_font = item.font(0)
        make_bold = (not self.hide_imports.isChecked()) and item_path == current_path
        item_font.setBold(make_bold)
        item.setFont(0, item_font)
        item.setFont(1, item_font)
        item.setFont(2, item_font)


class ImportSidebar(QTreeWidget):
    def __init__(self, parent=None, root_path=None, editor=None,):
        QTreeWidget.__init__(self, parent)
        self.editor = editor
        self.root_path = root_path
        self.setHeaderHidden(True)
        self.doubleClicked.connect(self.on_double_click)

    def build_tree(self, ontology, parent_item=None):
        if ontology is None:
            return

        new_item = QTreeWidgetItem(self if parent_item is None else parent_item)
        try:
            path = os.path.relpath(ontology.name, self.root_path)
        except ValueError:
            path = ontology.name

        new_item.setText(0, path)
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
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.setReadOnly(True)

    def write(self, text):
        self.insertPlainText(text)

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
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
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

