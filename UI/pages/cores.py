import os
import re

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QSizePolicy, QFrame, QVBoxLayout, QScrollArea, \
    QToolButton, QMenu, QLineEdit

from UI.Style import TEMPLATE_STYLE
from UI.translate import lang
from UI.windows import windowAbs


def find_installed_cores():
    path = "./minecraft/versions"
    if not os.path.exists(path):
        return []

    builds = []
    for folder in os.listdir(path):
        full_path = os.path.join(path, folder)
        if not os.path.isdir(full_path):
            continue

        # Vanilla
        if re.fullmatch(r"\d+\.\d+(\.\d+)?", folder):
            builds.append({
                "core_type": "Vanilla",
                "core_version": folder,
                "minecraft": folder
            })

        # Forge: 1.16.5-forge-47.1.1
        elif match := re.fullmatch(r"(\d+\.\d+(\.\d+)?)-forge-(.+)", folder):
            mc_version = match.group(1)
            forge_version = match.group(3)
            builds.append({
                "core_type": "Forge",
                "core_version": f"Forge {mc_version}-{forge_version}",
                "minecraft": mc_version
            })

        # Fabric: fabric-loader-0.15.9-1.20.4
        elif match := re.fullmatch(r"fabric-loader-(.+)-(\d+\.\d+(\.\d+)?)", folder):
            loader_version = match.group(1)
            mc_version = match.group(2)
            builds.append({
                "core_type": "Fabric",
                "core_version": f"Fabric Loader {loader_version}",
                "minecraft": mc_version
            })

        # Quilt: quilt-loader-0.20.2-1.20.1
        elif match := re.fullmatch(r"quilt-loader-(.+)-(\d+\.\d+(\.\d+)?)", folder):
            loader_version = match.group(1)
            mc_version = match.group(2)
            builds.append({
                "core_type": "Quilt",
                "core_version": f"Quilt Loader {loader_version}",
                "minecraft": mc_version
            })

    return builds


class MinecraftVersionsPage(QWidget):
    def __init__(self, launcher, parent=None):
        super().__init__(parent)
        self.launcher = launcher
        self.setObjectName("container")
        self.setStyleSheet(TEMPLATE_STYLE)
        self.cores = []
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel(lang.Elements.installed_cores_title)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(lang.Elements.search_placeholder)
        self.search_input.textChanged.connect(self.apply_search_filter)
        self.search_input.setFixedWidth(200)
        header.addWidget(self.search_input)

        header.addStretch()
        refresh_btn = QPushButton(lang.Elements.update_cores_elements)
        refresh_btn.setFixedHeight(28)
        refresh_btn.clicked.connect(self.populate_versions)
        header.addWidget(refresh_btn)
        self.main_layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll, 1)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        self.layout_scroll = QVBoxLayout(self.container)
        self.layout_scroll.setContentsMargins(0, 0, 0, 0)
        self.layout_scroll.setSpacing(8)

        self.populate_versions()

    def is_core_installed(self, build):
        path = "./minecraft"
        if build['core_type'] == "Vanilla":
            return os.path.exists(os.path.join(path, "versions", build['minecraft'], f"{build['minecraft']}.json"))
        elif build['core_type'] == "Forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            return os.path.exists(os.path.join(path, "versions", f"{build['minecraft']}-forge-{forge_version}",
                                               f"{build['minecraft']}-forge-{forge_version}.json"))
        elif build['core_type'] == "Fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            return os.path.exists(os.path.join(path, "versions", f"fabric-loader-{fabric_version}-{build['minecraft']}",
                                               f"fabric-loader-{fabric_version}-{build['minecraft']}.json"))
        elif build['core_type'] == "Quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            return os.path.exists(os.path.join(path, "versions", f"quilt-loader-{quilt_version}-{build['minecraft']}",
                                               f"quilt-loader-{quilt_version}-{build['minecraft']}.json"))
        return False

    def populate_versions(self):
        while self.layout_scroll.count():
            item = self.layout_scroll.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cores = find_installed_cores()
        if not self.cores:
            empty = QLabel(lang.Elements.no_available_installed_cores)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #777; font-style: italic;")
            self.layout_scroll.addWidget(empty)
            return

        for build in self.cores:
            self.add_version_card(build)

        self.layout_scroll.addStretch()

    def apply_search_filter(self):
        query = self.search_input.text().lower()
        filtered_builds = [build for build in self.cores if
                           query in build['core_type'].lower() or query in build['core_version'].lower() or query in
                           build['minecraft'].lower()]
        self.populate_filtered_versions(filtered_builds)

    def populate_filtered_versions(self, builds):
        while self.layout_scroll.count():
            item = self.layout_scroll.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not builds:
            empty = QLabel(lang.Elements.no_available_installed_cores)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #777; font-style: italic;")
            self.layout_scroll.addWidget(empty)
            return

        for build in builds:
            self.add_version_card(build)

        self.layout_scroll.addStretch()

    def add_version_card(self, build):
        card = QFrame()
        card.setObjectName("version_card")
        card.setStyleSheet("""
            QFrame#version_card {
                border: 1px solid #444;
                border-radius: 6px;
                background-color: #1e1e1e;
            }
        """)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(56)

        hl = QHBoxLayout(card)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.setSpacing(12)

        label = QLabel(
            f"{build['core_type'] if build['core_type'].lower() == 'vanilla' else ''} {build['core_version']} ({build['minecraft']})")
        label.setFont(QFont("Segoe UI", 10))
        label.setStyleSheet("color: white;")
        hl.addWidget(label)

        hl.addStretch()

        installed = self.is_core_installed(build)
        status = QLabel(lang.Elements.installed if installed else lang.Elements.not_installed)
        status.setStyleSheet("color: #aaa; font-size: 9pt;")
        hl.addWidget(status)

        btn = QPushButton(lang.Elements.reinstall if installed else lang.Elements.install)
        btn.setFixedHeight(28)
        btn.clicked.connect(lambda _, b=build, s=status, button=btn: self.install_core(b, s, button))
        hl.addWidget(btn)

        menu_btn = QPushButton()
        menu_btn.setFixedSize(28, 28)
        menu_btn.setText("⋮")
        menu_btn.setStyleSheet("""
            QToolButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ccc;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
        """)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                border: 1px solid #444;
                color: #ccc;
            }
            QMenu::item {
                padding: 5px 20px 5px 10px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)

        about_action = QAction(lang.Elements.about_core, self)
        about_action.triggered.connect(lambda: self.show_core_info(build))
        menu.addAction(about_action)

        delete_action = QAction(lang.Elements.delete, self)
        delete_action.triggered.connect(lambda: self.remove_core(build))
        menu.addAction(delete_action)

        menu_btn.clicked.connect(lambda: menu.exec(menu_btn.parent().mapToGlobal(menu_btn.pos())))
        hl.addWidget(menu_btn)

        self.layout_scroll.addWidget(card)

    def show_core_info(self, build):
        info = f"""
        <b>{lang.Elements.core_type}</b> {build['core_type']}<br>
        <b>{lang.Elements.core_version}</b> {build['core_version']}<br>
        <b>{lang.Elements.minecraft_version}</b> {build['minecraft']}<br>
        """
        self.show_temp_message(info, "info")

    def remove_core(self, build):
        r = windowAbs.question(self, lang.Dialogs.delete_title, lang.Dialogs.delete_core,
                               yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no)
        if not r: return
        success = self.launcher.builds_page.remove_core_folder(build)
        if success:
            self.show_temp_message(lang.Elements.core_deleted.format(type=build['core_type'], version=build['core_version']), "success")
            QTimer.singleShot(1000, self.populate_versions)
        else:
            self.show_temp_message(lang.Dialogs.error_delete_core.format(type=build['core_type'], version=build['core_version']), "warning")

    def install_core(self, build, status_label, button):
        if self.is_core_installed(build):
            r = windowAbs.question(self, lang.Dialogs.confirm_title,
                                   lang.Dialogs.reinstall_core,
                                   yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no)
            if not r:
                return
            success = self.launcher.builds_page.remove_core_folder(build)
            if not success:
                self.show_temp_message(lang.Dialogs.error_delete_core.format(type=build['core_type'], version=build['core_version']), "warning")
                return
        success = self.launcher.builds_page.install_core(build, nogui=False, force=True)
        if success:
            status_label.setText(lang.Elements.installed)
            button.setText(lang.Elements.reinstall)
            self.show_temp_message(lang.Elements.core_installed.format(type=build['core_type'], version=build['core_version']), "success")
        else:
            self.show_temp_message(lang.Dialogs.error_delete_core.format(type=build['core_type'], version=build['core_version']), "warning")

    def show_temp_message(self, text, style="info"):
        msg = QLabel(text)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if style == "success":
            msg.setStyleSheet("color: #4caf50;")
        elif style == "warning":
            msg.setStyleSheet("color: #f44336;")
        else:
            msg.setStyleSheet("color: #fff;")
        self.main_layout.insertWidget(1, msg)
        QTimer.singleShot(3000, msg.deleteLater)