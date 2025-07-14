from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QTextEdit, QDialogButtonBox, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import logging

from UI.Style import DARK_STYLESHEET
from UI.translate import lang
from UI.windows.windowAbs import DialogAbs


class InstallerThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    max_updated = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, installer):
        super().__init__()
        self.installer = installer
        self.canceled = False

    def run(self):
        callback_dict = {
            'setStatus': lambda status: self.status_updated.emit(status) if not self.canceled else None,
            'setProgress': lambda progress: self.progress_updated.emit(progress) if not self.canceled else None,
            'setMax': lambda max_val: self.max_updated.emit(max_val) if not self.canceled else None
        }

        try:
            self.installer.callback = callback_dict
            self.installer.install_version()
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))

class InstallDialog(DialogAbs):
    def __init__(self, installer, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.Dialogs.install_core_title)
        self.setStyleSheet(DARK_STYLESHEET)
        self.setMinimumSize(400, 300)
        self.installer = installer
        self.installTryCount = 0
        self.finished_installing = False
        self.canceled = False
        self.setup_ui()
        self.start_installation()

    def setup_ui(self):
        self._central = QWidget()
        self.setCentralWidget(self._central)
        layout = QVBoxLayout(self._central)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_btn.clicked.connect(self.cancel_installation)
        layout.addWidget(button_box)

    def start_installation(self):
        self.installTryCount += 1
        self.log_text.append(lang.Dialogs.start_installation)
        self.thread = InstallerThread(self.installer)
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.status_updated.connect(self.update_status)
        self.thread.max_updated.connect(self.update_max)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.log_text.append(status)
        print(status, str(self.progress_bar.value()) + "%")

    def update_max(self, max_val):
        self.progress_bar.setMaximum(max_val)

    def on_finished(self, success, error_msg):
        if self.canceled:
            self.reject()
            return
        if success:
            self.log_text.append(lang.Dialogs.installation_success)
            self.finished_installing = True
            self.accept()
        else:
            self.log_text.append(lang.Dialogs.installation_error.format(error_msg=error_msg))
            if not self.installTryCount > 2:
                QTimer.singleShot(1000, lambda: self.start_installation())
            else:
                self.finished_installing = True
            self.cancel_btn.setText(lang.Dialogs.close)

    def cancel_installation(self):
        if not self.canceled:
            self.canceled = True
            self.log_text.append(lang.Dialogs.cancel_installation)
            self.thread.terminate()
            self.thread.wait()
            self.reject()