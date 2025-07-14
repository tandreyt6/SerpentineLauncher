from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from UI.translate import lang
from UI.windows.windowAbs import DialogAbs


class AboutDialog(DialogAbs):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.Elements.about_changes_title)
        self.resize(600, 400)
        self._central = QWidget()
        self.setCentralWidget(self._central)
        layout = QVBoxLayout(self._central)

        web_view = QWebEngineView()
        web_view.setHtml(lang.Html.about_changes)

        layout.addWidget(web_view)
