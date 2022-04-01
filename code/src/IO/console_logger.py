import sys
from PyQt5.QtCore import QObject, pyqtSignal


class ConsoleLogger(QObject):
    _stdout = None
    _stderr = None

    messageWritten = pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if not ConsoleLogger._stdout:
            ConsoleLogger._stdout = ConsoleLogger()
            sys.stdout = ConsoleLogger._stdout
        return ConsoleLogger._stdout

    @staticmethod
    def stderr():
        if not ConsoleLogger._stderr:
            ConsoleLogger._stderr = ConsoleLogger()
            sys.stderr = ConsoleLogger._stderr
        return ConsoleLogger._stderr