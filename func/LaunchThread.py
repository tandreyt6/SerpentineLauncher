from PyQt6.QtCore import QThread, pyqtSignal


class LauncherThread(QThread):
    started_launch = pyqtSignal()
    finished_launch = pyqtSignal(bool, str)  # успех, сообщение

    def __init__(self, launcher):
        super().__init__()
        self.launcher = launcher
        self._success = False
        self._error = ""

    def run(self):
        self.started_launch.emit()
        try:
            self.launcher.run(False)
            self._success = True
        except Exception as e:
            self._error = str(e)
        self.finished_launch.emit(self._success, self._error)