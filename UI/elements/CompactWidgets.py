from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit

from UI.translate import lang


class PanelButton(QPushButton):
    def __init__(self, *args, **kwargs):
        if kwargs.get('icon', None) is None: kwargs['icon'] = QIcon()
        super().__init__(*args, **kwargs)
        self._text = self.text()
        self.setObjectName("expandedPanelButton")
        self.setMinimumHeight(30)

    def setCompactMode(self, b: bool):
        self._text = self.text() if b else self._text
        self.setText("" if b else self._text)


class CompactLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = self.text()

    def setCompactMode(self, b: bool):
        self._text = self.text() if b else self._text
        self.setText("-" if b else self._text)

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

    def setCompactMode(self, b: bool):
        self.label.setCompactMode(b)
        # self.input.setVisible(not b)


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

    def setCompactMode(self, b: bool):
        self.label.setCompactMode(b)
        self.message.setVisible(not b)