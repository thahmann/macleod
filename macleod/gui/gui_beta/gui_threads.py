from PyQt5.QtCore import QThread
from macleod.parsing import Parser
import os
import macleod.Filemgt as filemgt
import tempfile
import sys


class ParseThread(QThread):
    """
    Runs the parser and returns an ontology object
    """

    def __init__(self):
        QThread.__init__(self)

        # input
        self.resolve = False
        self.text = None
        self.path = None

        # output
        self.error = ErrorBuffer()
        self.ontology = None

    def __del__(self):
        self.wait()

    def run(self):
        # We need to capture the print statements from the parser
        backup = sys.stdout
        sys.stdout = self.error

        # Create a place to read the text from
        buffer = tempfile.mkstemp(".macleod")
        with open(buffer[1], 'w') as f:
            f.write(self.text)

        try:
            self.ontology = Parser.parse_file(buffer[1],
                                              filemgt.read_config('cl', 'prefix'),
                                              os.path.abspath(filemgt.read_config('system', 'path')),
                                              self.resolve,
                                              self.path)

        except Exception as e:
            self.error.write(str(e))
            self.ontology = None

        # return to the previous output
        sys.stdout = backup

        # leave no trace of the buffer
        os.close(buffer[0])
        os.remove(buffer[1])


class ErrorBuffer:
    """
    A place to capture errors
    """

    def __init__(self):
        self.contents = ""

    def write(self, text):
        self.contents += text

    def flush(self):
        self.contents = ""
