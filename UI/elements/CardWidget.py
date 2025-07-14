import json
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QHBoxLayout, QGridLayout, QStackedLayout, QDialogButtonBox, QLineEdit, QMenu, QTextEdit,
    QDialog, QColorDialog, QFileDialog, QTextBrowser
)
from PyQt6.QtCore import Qt, QEvent, QPoint, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QPainter, QBrush, QColor, QPaintEvent, QFont, QLinearGradient, QIcon, QPalette, QPixmap

from func import memory


class CardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == event.Type.Resize:
            self.resize(event.size())
            self.move(3, 30)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
            self.move(1, 30)
        super().showEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 30, 200)))
        painter.drawRoundedRect(0, 0, self.width(), self.height()-30, 5, 5)


class BuildEditDialog(QDialog):
    def __init__(self, build: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать карточку")
        self.build = build.copy() if build else {}

        self.resize(600, 500)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название сборки:"))
        self.name_edit = QLineEdit(self.build.get("name", ""))
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Описание (HTML):"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setText(self.build.get("description", ""))
        layout.addWidget(self.desc_edit, 1)

        hl_bg = QHBoxLayout()
        hl_bg.addWidget(QLabel("Цвет фона:"))
        self.bgcolor_edit = QLineEdit(self.build.get("background_color", "#2f2f2f"))
        hl_bg.addWidget(self.bgcolor_edit)
        self.bgcolor_btn = QPushButton("Выбрать цвет")
        hl_bg.addWidget(self.bgcolor_btn)
        layout.addLayout(hl_bg)

        self.bgcolor_btn.clicked.connect(self.choose_color)

        hl_logo = QHBoxLayout()
        hl_logo.addWidget(QLabel("Путь к лого:"))
        self.logo_path_edit = QLineEdit(self.build.get("logo_path", ""))
        hl_logo.addWidget(self.logo_path_edit)
        self.logo_browse_btn = QPushButton("Обзор")
        hl_logo.addWidget(self.logo_browse_btn)
        layout.addLayout(hl_logo)

        self.logo_browse_btn.clicked.connect(self.browse_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(96, 96)
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        self.update_logo_preview()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def choose_color(self):
        current_color = QColor(self.bgcolor_edit.text())
        color = QColorDialog.getColor(current_color, self, "Выберите цвет фона")
        if color.isValid():
            self.bgcolor_edit.setText(color.name())

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл лого", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.logo_path_edit.setText(path)
            self.update_logo_preview()

    def update_logo_preview(self):
        path = self.logo_path_edit.text()
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_preview.setPixmap(scaled)
                return
        self.logo_preview.clear()

    def accept(self) -> None:
        self.build["name"] = self.name_edit.text()
        self.build["description"] = self.desc_edit.toPlainText()
        self.build["background_color"] = self.bgcolor_edit.text()
        self.build["logo_path"] = self.logo_path_edit.text()
        super().accept()


class BuildCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = None
        self.build = None
        self.edit_mode = False
        self._original_logo_pixmap = None
        self._original_bg_pixmap = None
        self.setMinimumHeight(500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        main_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)

        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("border-radius: 8px;")
        self.header_layout = QStackedLayout(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.bg_label = QLabel(self.header_frame)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bg_label.setStyleSheet("background: transparent;")

        self.logo = QLabel(self.header_frame)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.logo.setStyleSheet("background: transparent;")

        self.header_layout.addWidget(self.logo)
        self.header_layout.addWidget(self.bg_label)
        self.scroll_layout.addWidget(self.header_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.buttons_widget = QWidget(self)
        self.buttons_widget.setFixedWidth(300)
        buttons_layout = QHBoxLayout(self.buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        self.play_button = QPushButton("Играть", self.buttons_widget)
        self.play_button.setFixedSize(120, 40)
        self.play_button.setObjectName("PlayButton")

        self.more_button = QPushButton("…", self.buttons_widget)
        self.more_button.setFixedSize(40, 40)
        self.more_button.setObjectName("MoreButton")
        self.more_button.clicked.connect(self.show_more_menu)

        self.close_button = QPushButton("Закрыть", self.buttons_widget)
        self.close_button.setFixedSize(120, 40)
        self.close_button.setObjectName("CloseButton")
        self.close_button.clicked.connect(self.hide)

        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.more_button)
        buttons_layout.addWidget(self.close_button)
        self.buttons_widget.setFixedHeight(40)

        self.content_container = QWidget()
        content_layout = QHBoxLayout(self.content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)

        fill = QWidget()
        fill.setFixedHeight(self.play_button.height())
        content_layout.addWidget(fill, 3)

        self.desc = QTextBrowser()
        self.desc.setOpenExternalLinks(True)
        self.desc.setReadOnly(True)
        self.desc.setObjectName("DescLabel")
        self.desc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.desc.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_layout.addWidget(self.desc, 4)

        self.desc_edit = QTextEdit()
        self.desc_edit.setAcceptRichText(True)
        self.desc_edit.setVisible(False)
        content_layout.addWidget(self.desc_edit, 4)

        self.info_block = QWidget()
        info_layout = QVBoxLayout(self.info_block)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        self.info_labels = {
            "name": QLabel(),
            "minecraft": QLabel(),
            "core_type": QLabel(),
            "core_version": QLabel(),
            "created": QLabel()
        }
        for lbl in self.info_labels.values():
            lbl.setObjectName("InfoLabel")
            lbl.setWordWrap(True)
            info_layout.addWidget(lbl)
        info_layout.addStretch()
        content_layout.addWidget(self.info_block, 1)

        self.scroll_layout.addWidget(self.content_container)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._apply_styles()

        bottom_spacer = QWidget()
        bottom_spacer.setFixedSize(200, 200)
        self.scroll_layout.addWidget(bottom_spacer)

        QTimer.singleShot(100, lambda: self.resize(self.width()-1, self.height()))

    def show_more_menu(self):
        menu = QMenu()
        edit_action = menu.addAction("Редактировать карточку")
        edit_action.triggered.connect(self.open_edit_dialog)
        menu.exec(self.more_button.mapToGlobal(QPoint(0, self.more_button.height())))

    def open_edit_dialog(self):
        if not self.build:
            return
        dlg = BuildEditDialog(self.build, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.set_build(dlg.build, self.path)
            memory.get("build_manager").update_build(dlg.build)

    def set_build(self, build: dict, path):
        self.build = build
        self.path = path
        description = build.get("description", "")
        if re.search(r'<script[^>]*>.*?</script>', description, re.IGNORECASE | re.DOTALL):
            self.desc.setHtml("<p style='color: red;'>Выполнение скриптов запрещено.</p>")
        else:
            self.desc.setHtml(description)
        self._update_desc_height()
        name = build.get("name", "")
        self.info_labels["name"].setText(f"<b>Name:</b> {name}")
        self.info_labels["name"].setVisible(bool(name))
        for key in ("minecraft", "core_type", "core_version", "created"):
            text = build.get(key, "")
            lbl = self.info_labels.get(key)
            if lbl and text:
                lbl.setText(f"<b>{key.capitalize()}:</b> {text}")
                lbl.setVisible(True)
            elif lbl:
                lbl.setVisible(False)
        bg_color = build.get("background_color", "#2f2f2f")
        bg_path = self.path + "/bg.png"
        bg_pixmap = QPixmap(bg_path)
        if not bg_pixmap.isNull():
            self._original_bg_pixmap = bg_pixmap
            self.header_frame.setStyleSheet("border-radius: 8px; background: transparent;")
        else:
            self._original_bg_pixmap = None
            self.bg_label.clear()
            self.header_frame.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")
        logo_path = self.path + "/logo.png"
        if logo_path:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self._original_logo_pixmap = pixmap
            else:
                self._original_logo_pixmap = None
                self.logo.clear()
        else:
            self._original_logo_pixmap = None
            self.logo.clear()
        self._update_images_size()
        self._update_play_button_position()

    def _update_desc_height(self):
        doc_height = self.desc.document().size().height()
        margin = self.desc.contentsMargins().top() + self.desc.contentsMargins().bottom()
        new_height = int(doc_height) + margin + 5
        self.desc.setFixedHeight(new_height)
        self._update_play_button_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        window_width = self.parent().width() if self.parent() else self.width()
        window_height = self.parent().height() if self.parent() else self.height()
        margin = 40
        max_width = window_width - margin
        max_height = window_height * 0.5
        header_width = min(max_width, int(max_height * 2))
        header_height = header_width / 2
        self.header_frame.setFixedSize(int(header_width), int(header_height))
        self._update_images_size()
        self._update_play_button_position()
        self._update_desc_height()

    def _update_images_size(self):
        available_size = self.header_frame.size() - QSize(10, 10)
        if self._original_bg_pixmap:
            scaled_bg = self._original_bg_pixmap.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled_bg)
        else:
            self.bg_label.clear()
        if self._original_logo_pixmap:
            scaled_logo = self._original_logo_pixmap.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo.setPixmap(scaled_logo)
        else:
            self.logo.clear()

    def _on_scroll(self, value: int):
        self._update_play_button_position()

    def _update_play_button_position(self):
        scroll_y = self.scroll_area.verticalScrollBar().value()
        buttons_h = self.buttons_widget.height()
        margin = 20
        viewport_h = self.height()
        header_h = self.header_frame.height()
        header_x = (self.width() - self.header_frame.width()) // 2
        desc_global_pos = self.desc.mapTo(self, QPoint(0, 0))
        desc_left = desc_global_pos.x()
        buttons_width = self.play_button.width() + self.more_button.width() + 10
        ideal_x = header_x + 20
        max_x = desc_left - buttons_width - 20
        x_pos = min(ideal_x, max_x)
        x_pos = max(20, x_pos)
        if scroll_y < header_h - 80:
            target_y = header_h - scroll_y + margin
            if target_y + buttons_h > viewport_h:
                min_y = max(header_h - buttons_h - margin, margin)
                target_y = max(min_y, viewport_h - buttons_h - margin)
            self.buttons_widget.move(int(x_pos), int(target_y))
        else:
            self.buttons_widget.move(int(x_pos), margin)

    def _apply_styles(self):
        self.setStyleSheet("""
            QPushButton#PlayButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton#MoreButton {
                background-color: transparent;
                font-size: 20px;
                color: white;
                border: none;
            }
            QPushButton#MoreButton:hover {
                background-color: #444;
                border-radius: 5px;
            }
            QPushButton#CloseButton {
                background-color: transparent;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton#CloseButton:hover {
                background-color: #444;
                border-radius: 5px;
            }
            QLabel#DescLabel {
                font-size: 14px;
                color: white;
            }
            QLabel#InfoLabel {
                font-size: 13px;
                color: lightgray;
            }
            QTextBrowser#DescLabel {
                font-size: 14px;
                color: white;
                background: transparent;
                border: none;
            }
        """)