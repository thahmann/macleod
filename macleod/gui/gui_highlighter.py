from PyQt5.Qt import Qt
from PyQt5.QtCore import QRegularExpression, QRegularExpressionMatchIterator
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat

COLOR_EQUALS = Qt.red
COLOR_PRED_FUNC = Qt.cyan
COLOR_CONNECTIVE = Qt.green
COLOR_NOT = Qt.gray
COLOR_QUANTIFIER = Qt.blue
COLOR_PARENTHESES = Qt.yellow


class CLIFSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super(CLIFSyntaxHighlighter, self).__init__(parent)

        # define formats and rules
        ignore_case = QRegularExpression.CaseInsensitiveOption
        self.rules = []

        format_pred_func = QTextCharFormat()
        format_pred_func.setForeground(COLOR_PRED_FUNC)
        self.rules.append((QRegularExpression("\(\w* "), 1, format_pred_func))

        format_equals = QTextCharFormat()
        format_equals.setForeground(COLOR_EQUALS)
        self.rules.append((QRegularExpression("="), 0, format_equals))

        format_connective = QTextCharFormat()
        format_connective.setForeground(COLOR_CONNECTIVE)
        connectives = ["AND", "OR", "IF", "IFF"]
        for c in connectives:
            self.rules.append((QRegularExpression("\(" + c, ignore_case), 1, format_connective))

        format_not = QTextCharFormat()
        format_not.setForeground(COLOR_NOT)
        self.rules.append((QRegularExpression("NOT", ignore_case), 0, format_not))

        format_quantifier = QTextCharFormat()
        format_quantifier.setForeground(COLOR_QUANTIFIER)
        quantifiers = ["EXISTS", "FORALL"]
        for q in quantifiers:
            self.rules.append((QRegularExpression("\(" + q, ignore_case), 1, format_quantifier))

        format_parentheses = QTextCharFormat()
        format_parentheses.setForeground(COLOR_PARENTHESES)
        parentheses = ["\(", "\)"]
        for p in parentheses:
            self.rules.append((QRegularExpression(p), 0, format_parentheses))

    def highlightBlock(self, p_str):
        for exp, index, format in self.rules:
            iterator = exp.globalMatch(p_str)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart() + index, match.capturedLength() - index, format)
