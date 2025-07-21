from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QMessageBox, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter
import json
import os
import uuid
import secrets

from UI.Style import TEMPLATE_STYLE
from UI.windows import windowAbs
from func import memory
from UI.translate import lang

PROFILES_FILE = "profiles.json"

class OfflineProfilePage(QWidget):
    def __init__(self, main, parent=None):
        super().__init__(parent)
        self.launcher = main
        self.setObjectName("container")
        self.setStyleSheet(TEMPLATE_STYLE)
        self.profiles = []
        self.active_profile_id = None
        self.selected_profile_id = None
        self.setup_ui()
        self.setup_connections()
        self.load_profiles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        title = QLabel(lang.Dialogs.profiles_title)
        title.setObjectName("title")
        main_layout.addWidget(title)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        create_panel = QFrame()
        create_panel.setObjectName("container")
        create_layout = QVBoxLayout(create_panel)
        create_layout.setContentsMargins(0, 0, 0, 0)
        create_layout.setSpacing(8)

        nickname_layout = QVBoxLayout()
        nickname_label = QLabel(lang.Dialogs.nickname_label)
        nickname_label.setObjectName("section_title")
        nickname_layout.addWidget(nickname_label)

        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText(lang.Dialogs.nickname_placeholder)
        nickname_layout.addWidget(self.nickname_input)

        info_layout = QHBoxLayout()
        self.char_counter = QLabel(lang.Dialogs.char_counter)
        self.char_counter.setStyleSheet("color: #A0A0A0; font-size: 8pt;")

        self.warning_label = QLabel("")
        self.warning_label.setObjectName("warning")
        self.warning_label.setVisible(False)

        info_layout.addWidget(self.char_counter)
        info_layout.addWidget(self.warning_label)
        nickname_layout.addLayout(info_layout)
        create_layout.addLayout(nickname_layout)

        self.create_btn = QPushButton(lang.Dialogs.create_profile)
        self.create_btn.setFixedHeight(32)
        self.create_btn.setEnabled(False)
        create_layout.addWidget(self.create_btn)

        self.toggle_tech_btn = QPushButton(lang.Dialogs.toggle_tech_params)
        self.toggle_tech_btn.setObjectName("secondary")
        self.toggle_tech_btn.setFixedHeight(24)
        create_layout.addWidget(self.toggle_tech_btn)

        self.tech_group = QFrame()
        self.tech_group.setObjectName("tech_group")
        self.tech_group.setVisible(False)
        tech_layout = QVBoxLayout(self.tech_group)
        tech_layout.setSpacing(8)

        token_label = QLabel(lang.Dialogs.token_label)
        token_label.setObjectName("section_title")
        tech_layout.addWidget(token_label)

        self.token_input = QLineEdit()
        tech_layout.addWidget(self.token_input)

        uuid_label = QLabel(lang.Dialogs.uuid_label)
        uuid_label.setObjectName("section_title")
        tech_layout.addWidget(uuid_label)

        self.uuid_input = QLineEdit()
        tech_layout.addWidget(self.uuid_input)

        create_layout.addWidget(self.tech_group)
        create_layout.addStretch(1)

        profiles_panel = QFrame()
        profiles_panel.setObjectName("container")
        profiles_layout = QVBoxLayout(profiles_panel)
        profiles_layout.setContentsMargins(0, 0, 0, 0)
        profiles_layout.setSpacing(8)

        profiles_label = QLabel(lang.Dialogs.your_profiles)
        profiles_label.setObjectName("title")
        profiles_layout.addWidget(profiles_label)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("container")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.profiles_container = QWidget()
        self.profiles_container.setObjectName("container")
        self.profiles_container_layout = QVBoxLayout(self.profiles_container)
        self.profiles_container_layout.setContentsMargins(0, 0, 0, 0)
        self.profiles_container_layout.setSpacing(8)
        self.profiles_container_layout.addStretch()

        scroll_area.setWidget(self.profiles_container)
        profiles_layout.addWidget(scroll_area, 1)

        self.select_btn = QPushButton(lang.Dialogs.select_profile)
        self.select_btn.setObjectName("select")
        self.select_btn.setFixedHeight(36)
        self.select_btn.setEnabled(False)
        profiles_layout.addWidget(self.select_btn)

        content_layout.addWidget(create_panel, 1)
        content_layout.addWidget(profiles_panel, 2)
        main_layout.addLayout(content_layout, 1)

        self.empty_label = QLabel(lang.Dialogs.no_profiles)
        self.empty_label.setObjectName("empty_label")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #7F7F7F; font-style: italic;")
        self.profiles_container_layout.addWidget(self.empty_label)
        self.empty_label.setVisible(False)

        self.generate_tech_params()

    def setup_connections(self):
        self.nickname_input.textChanged.connect(self.validate_nickname)
        self.toggle_tech_btn.clicked.connect(self.toggle_tech_params)
        self.create_btn.clicked.connect(self.create_profile)
        self.select_btn.clicked.connect(self.select_profile)

    def toggle_tech_params(self):
        visible = not self.tech_group.isVisible()
        self.tech_group.setVisible(visible)
        self.toggle_tech_btn.setText(
            lang.Dialogs.toggle_tech_params_expanded if visible
            else lang.Dialogs.toggle_tech_params
        )

    def validate_nickname(self, text):
        self.char_counter.setText(f"{len(text)}/16")
        self.warning_label.setVisible(False)
        self.nickname_input.setProperty("invalid", "false")
        self.nickname_input.style().polish(self.nickname_input)

        if len(text) < 3 or len(text) > 16:
            self.warning_label.setText(lang.Dialogs.nickname_length_warning)
            self.warning_label.setVisible(True)
            self.nickname_input.setProperty("invalid", "true")
            self.create_btn.setEnabled(False)
            return

        if not all(c.isalnum() or c == '_' for c in text):
            self.warning_label.setText(lang.Dialogs.nickname_chars_warning)
            self.warning_label.setVisible(True)
            self.nickname_input.setProperty("invalid", "true")
            self.create_btn.setEnabled(False)
            return

        if any(p['nickname'].lower() == text.lower() for p in self.profiles):
            self.warning_label.setText(lang.Dialogs.nickname_exists_warning)
            self.warning_label.setVisible(True)
            self.nickname_input.setProperty("invalid", "true")
            self.create_btn.setEnabled(False)
            return

        self.create_btn.setEnabled(True)

    def generate_tech_params(self):
        self.uuid_input.setText("3f69c852b89645ca81e05f5952d9d8e9")
        self.token_input.setText("null")

    def create_profile(self):
        nickname = self.nickname_input.text()
        profile = {
            "id": str(uuid.uuid4()),
            "nickname": nickname,
            "uuid": self.uuid_input.text(),
            "token": self.token_input.text(),
            "active": False
        }

        self.profiles.append(profile)
        self.add_profile_card(profile)
        self.select_profile_by_id(profile['id'])

        self.nickname_input.clear()
        self.generate_tech_params()
        self.create_btn.setEnabled(False)
        self.save_profiles()

        self.show_temp_message(lang.Dialogs.profile_created.format(nickname=nickname), "success")

    def add_profile_card(self, profile):
        if not self.profiles and self.empty_label.isVisible():
            self.empty_label.setVisible(False)

        card = QFrame()
        card.setObjectName("profile_card")
        card.setProperty("active", "false")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(52)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(12)

        avatar_label = QLabel()
        avatar_label.setPixmap(self.generate_avatar(profile['nickname']).scaled(
            36, 36, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        card_layout.addWidget(avatar_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(profile['nickname'])
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        info_layout.addWidget(name_label)

        status_text = lang.Dialogs.offline_status
        if profile.get('active'):
            self.launcher.main.setActiveName(profile['nickname'])
            status_text = lang.Dialogs.active_status
        status_label = QLabel(status_text)
        status_label.setStyleSheet("color: #A0A0A0; font-size: 8pt;")
        info_layout.addWidget(status_label)

        card_layout.addLayout(info_layout, 1)

        self.delete_btn = QPushButton(lang.Dialogs.delete)
        self.delete_btn.setObjectName("secondary")
        self.delete_btn.setFixedSize(64, 26)
        card_layout.addWidget(self.delete_btn)

        self.delete_btn.setVisible(not profile.get('active'))
        self.delete_btn.clicked.connect(
            lambda _, id=profile['id']: self.delete_profile(id)
        )

        self.profiles_container_layout.insertWidget(0, card)
        profile['card'] = card
        profile['status_label'] = status_label
        profile['delete_btn'] = self.delete_btn

        card.mousePressEvent = lambda event, id=profile['id']: self.select_profile_by_id(id)

        if len(self.profiles) == 1:
            self.empty_label.setVisible(False)

    def select_profile_by_id(self, profile_id):
        self.selected_profile_id = profile_id
        self.select_btn.setEnabled(self.active_profile_id != profile_id)

        for profile in self.profiles:
            card = profile['card']
            if profile['id'] == profile_id:
                card.setProperty("selected", "true")
                card.setStyleSheet("""QFrame#profile_card {border: 2px solid #0078D7; border-radius: 4px;}""")
            else:
                card.setStyleSheet("""QFrame#profile_card {border: none;}""")
                card.setProperty("selected", "false")
            card.style().polish(card)

    def set_active_profile(self, profile_id):
        for profile in self.profiles:
            active = profile['id'] == profile_id
            profile['active'] = active
            card = profile['card']
            card.setProperty("active", "true" if active else "false")
            card.style().polish(card)

            if active:
                profile['status_label'].setText(lang.Dialogs.active_status)
                profile['delete_btn'].setVisible(False)
                self.launcher.main.setActiveName(profile['nickname'])
            else:
                profile['status_label'].setText(lang.Dialogs.offline_status)
                profile['delete_btn'].setVisible(True)
        self.active_profile_id = profile_id
        self.save_profiles()

    def select_profile(self):
        if self.selected_profile_id is None:
            self.show_temp_message(lang.Dialogs.select_profile_first, "warning")
            return

        self.set_active_profile(self.selected_profile_id)
        profile = next(p for p in self.profiles if p['id'] == self.selected_profile_id)

    def delete_profile(self, profile_id):
        print(profile_id)
        profile = next((p for p in self.profiles if p['id'] == profile_id), None)
        print(profile, not profile)
        if not profile:
            return
        print("Delete profile...")
        reply = windowAbs.question(
            self,
            lang.Dialogs.confirm_deletion_title,
            lang.Dialogs.confirm_deletion_text.format(nickname=profile['nickname']),
            yes_text=lang.Dialogs.yes,
            no_text=lang.Dialogs.no,
        )

        if not reply:
            return

        self.profiles = [p for p in self.profiles if p['id'] != profile_id]
        profile['card'].deleteLater()

        if profile_id == self.selected_profile_id:
            self.selected_profile_id = None
            self.select_btn.setEnabled(False)

        if profile_id == self.active_profile_id:
            self.active_profile_id = None
            if self.profiles:
                self.set_active_profile(self.profiles[0]['id'])

        if not self.profiles:
            self.empty_label.setVisible(True)
            self.selected_profile_id = None
            self.select_btn.setEnabled(False)

        self.save_profiles()
        self.show_temp_message(lang.Dialogs.profile_deleted.format(nickname=profile['nickname']), "info")

    def show_temp_message(self, text, style="info"):
        msg = QLabel(text)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if style == "success":
            msg.setObjectName("success_message")
        elif style == "warning":
            msg.setObjectName("warning_message")
        else:
            msg.setObjectName("info_message")

        self.layout().insertWidget(1, msg)
        QTimer.singleShot(3000, msg.deleteLater)

    def generate_avatar(self, nickname):
        colors = [
            "#4E7AB5", "#B54E7A", "#7AB54E", "#B57A4E", "#7A4EB5",
            "#5E8C87", "#8C5E87", "#5E878C", "#8C875E", "#6A5E8C"
        ]

        total = sum(ord(char) for char in nickname)
        color_index = total % len(colors)
        color = colors[color_index]

        initials = nickname[:2].upper() if nickname else "MC"

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 64, 64, 12, 12)

        painter.setPen(QColor(Qt.GlobalColor.white))
        font = QFont("Arial", 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials)

        painter.end()

        return pixmap

    def load_profiles(self):
        try:
            if os.path.exists(PROFILES_FILE):
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)

                    for profile in self.profiles:
                        if profile.get('active'):
                            self.launcher.main.setActiveName(profile['nickname'])
                            self.active_profile_id = profile['id']
                            break

                    for profile in self.profiles:
                        self.add_profile_card(profile)

                    if not self.profiles:
                        self.empty_label.setVisible(True)
        except:
            self.profiles = []
            self.empty_label.setVisible(True)

    def save_profiles(self):
        try:
            profiles_to_save = [
                {k: v for k, v in p.items() if k != 'card' and k != 'status_label' and k != 'delete_btn'}
                for p in self.profiles
            ]

            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump(profiles_to_save, f, indent=2, ensure_ascii=False)
        except:
            pass