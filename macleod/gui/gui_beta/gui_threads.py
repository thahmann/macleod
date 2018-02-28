from PyQt5.QtCore import QThread, pyqtSignal
from macleod.parsing import Parser
import os
import macleod.Filemgt as filemgt
import tempfile



class ParseThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.resolve = False
        self.ontology = None
        self.text = None
        self.path = None

    def __del__(self):
        self.wait()

    def run(self):
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
            print(e)
            self.ontology = None

        os.close(buffer[0])
        os.remove(buffer[1])