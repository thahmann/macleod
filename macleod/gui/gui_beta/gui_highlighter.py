from PyQt5.Qt import Qt
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
import macleod.Filemgt as filemgt
import configparser

COLOR_HIGHLIGHT_SYMBOL = Qt.yellow


class CLIFSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, predicates=None, functions=None):
        super(CLIFSyntaxHighlighter, self).__init__(parent)

        self.predicates = predicates if predicates is not None else []
        self.functions = functions if functions is not None else []

        # define formats and rules
        ignore_case = QRegularExpression.CaseInsensitiveOption
        self.rules = []

        # placeholder for comparison
        self.format_pred_func = QTextCharFormat()
        self.rules.append((QRegularExpression("\(\w* [\w ]*\)"), 0, self.format_pred_func))

        # real colors for functions and predicates
        self.format_predicate = QTextCharFormat()
        self.format_predicate.setForeground(get_color("color_predicate"))
        self.format_function = QTextCharFormat()
        self.format_function.setForeground(get_color("color_function"))

        format_equals = QTextCharFormat()
        format_equals.setForeground(get_color("color_equals"))
        self.rules.append((QRegularExpression("="), 0, format_equals))

        format_connective = QTextCharFormat()
        format_connective.setForeground(get_color("color_connective"))
        connectives = ["AND", "OR", "IF", "IFF"]
        for c in connectives:
            self.rules.append((QRegularExpression("\(" + c, ignore_case), 1, format_connective))

        format_not = QTextCharFormat()
        format_not.setForeground(get_color("color_not"))
        self.rules.append((QRegularExpression("NOT", ignore_case), 0, format_not))

        format_quantifier = QTextCharFormat()
        format_quantifier.setForeground(get_color("color_quantifier"))
        quantifiers = ["EXISTS", "FORALL"]
        for q in quantifiers:
            self.rules.append((QRegularExpression("\(" + q, ignore_case), 1, format_quantifier))

        format_parentheses = QTextCharFormat()
        format_parentheses.setForeground(get_color("color_parentheses"))
        parentheses = ["\(", "\)"]
        for p in parentheses:
            self.rules.append((QRegularExpression(p), 0, format_parentheses))

    def highlightBlock(self, p_str):
        for exp, index, format in self.rules:
            iterator = exp.globalMatch(p_str)
            while iterator.hasNext():
                match = iterator.next()
                # format_pred_func is a placeholder object,
                # as the regular expressions for predicates and functions are the same
                if format == self.format_pred_func:
                    line = match.captured()
                    name = line.lstrip("(").split(" ")[0]
                    offset = line.index(name)
                    for f in self.functions:
                        if f[0] == name:
                            self.setFormat(match.capturedStart() + offset, len(name), self.format_function)
                            break
                    for p in self.predicates:
                        if p[0] == name:
                            self.setFormat(match.capturedStart() + offset, len(name), self.format_predicate)
                            break
                else:
                    self.setFormat(match.capturedStart() + index, match.capturedLength() - index, format)

    def highlightSymbol(self, symbolName):
        exp = QRegularExpression(symbolName)
        highlightFormat = QTextCharFormat()
        highlightFormat.setBackground(COLOR_HIGHLIGHT_SYMBOL)
        while self.currentBlock().isValid():
            iterator = exp.globalMatch(self.currentBlock().text())
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength, highlightFormat)
            self.currentBlock().next()


def get_color(setting_name):
    try:
        return QColor(filemgt.read_config("gui", setting_name, filemgt.config_file))
    except configparser.NoOptionError:
        return QColor()