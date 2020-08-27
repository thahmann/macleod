from PyQt5.Qt import Qt
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from macleod.Filemgt import MacleodConfigParser
import configparser

COLOR_HIGHLIGHT_SYMBOL = Qt.yellow


class CLIFSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, predicates=None, functions=None):
        super(CLIFSyntaxHighlighter, self).__init__(parent)
        self.setDocument(parent.document())

        self.predicates = [] if predicates is None else predicates
        self.functions = [] if functions is None else functions

        # define formats and rules
        ignore_case = QRegularExpression.CaseInsensitiveOption
        self.rules = []

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
        # Skip comments!
        if "cl-comment" in p_str:
            return

        for exp, index, format in self.rules:
            iterator = exp.globalMatch(p_str)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart() + index, match.capturedLength() - index, format)

        for pred in self.predicates:
            expression = QRegularExpression(pred[0] + " ")
            iterator = expression.globalMatch(p_str)
            while iterator.hasNext():
                match = iterator.next()
                line = match.captured()
                self.setFormat(match.capturedStart(), len(line), self.format_predicate)

        for func in self.functions:
            expression = QRegularExpression(func[0] + " ")
            iterator = expression.globalMatch(p_str)
            while iterator.hasNext():
                match = iterator.next()
                line = match.captured()
                self.setFormat(match.capturedStart(), len(line), self.format_function)

    def rehighlight(self, predicates=None, functions=None):
        if predicates is not None:
            self.predicates = predicates

        if functions is not None:
            self.functions = functions

        super(CLIFSyntaxHighlighter, self).rehighlight()


def get_color(setting_name):
    try:
        return QColor(MacleodConfigParser().get("gui", setting_name))
    except configparser.NoOptionError:
        return QColor()