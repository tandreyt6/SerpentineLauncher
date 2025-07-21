from PyQt6.QtCore import QObject, Qt, QEvent


class TabBlocker(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                return True
        return super().eventFilter(obj, event)