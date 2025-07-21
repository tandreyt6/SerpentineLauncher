from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit

from UI.translate import lang


class PanelButton(QPushButton):
    def __init__(self, *args, **kwargs):
        if kwargs.get('icon', None) is None:
            kwargs['icon'] = QIcon()
        super().__init__(*args, **kwargs)

        self._full_text = self.text()
        self.setObjectName("expandedPanelButton")
        self.setMinimumHeight(30)
        self.setIconSize(QSize(24, 24))

        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 2px;
            }
        """)

    def setSizeMode(self, size: QSize, direction: str):
        pass

class CompactLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = self.text()

    def setSizeMode(self, size: QSize, direction: str):
        # self._text = self.text() if b else self._text
        # self.setText("-" if b else self._text)
        pass

class NameInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = CompactLabel(lang.Elements.build_new_minecraft)
        self.input = QLineEdit()
        self.input.setPlaceholderText(lang.Elements.enter_build_name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.input)

    def setSizeMode(self, size: QSize, direction: str):
        # self.label.setCompactMode(b)
        # self.input.setVisible(not b)
        pass


class WarningWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = PanelButton("")
        self.label.setObjectName("warning")
        self.message = QLabel("")
        self.message.setStyleSheet("color: red")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.message)
        self.setVisible(False)

    def setSizeMode(self, size: QSize, direction: str):
        return
        # self.label.setCompactMode(b)
        # self.message.setVisible(not b)