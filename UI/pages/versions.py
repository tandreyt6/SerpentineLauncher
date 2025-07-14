import signal

from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QDialog, QListWidget, QListWidgetItem,
    QGridLayout, QDialogButtonBox, QTextEdit, QFileDialog, QGroupBox, QStyle, QComboBox, QToolTip, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
import json
import os
import shutil

from UI.elements.CompactWidgets import PanelButton, NameInputWidget, CompactLabel

from UI.elements.ExpandablePanel import ExpandablePanel
from UI.pages.client_settings import ClientSettingsDialog
from UI.translate import lang
from UI.windows import windowAbs
from UI.windows.windowAbs import DialogAbs
from func import memory
from UI.Style import DARK_STYLESHEET
from func.BuildManager import slugify, BuildManager
from func.CreateShortcut import create_shortcut
from func.LaunchThread import LauncherThread
from func.runner import VanillaLauncher, FabricLauncher, ForgeLauncher, QuiltLauncher
from func.installer import MinecraftInstaller, FabricInstaller, ForgeInstaller, QuiltInstaller
from UI.install_dialog import InstallDialog
from func import settings

class VersionSelectionDialog(DialogAbs):
    def __init__(self, build_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.Dialogs.select_version_title)
        self.setStyleSheet(DARK_STYLESHEET)
        self.setMinimumSize(600, 400)
        self.build_manager = build_manager

        self.minecraft_version = ""
        self.core_type = ""
        self.core_version = ""
        self._central = QWidget()
        self.setCentralWidget(self._central)
        layout = QVBoxLayout(self._central)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(lang.Dialogs.search_versions)
        self.search_input.textChanged.connect(self.filter_versions)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        grid = QGridLayout()

        minecraft_label = QLabel(lang.Dialogs.minecraft_version)
        minecraft_label.setObjectName("section_title")
        grid.addWidget(minecraft_label, 0, 0)

        self.minecraft_list = QListWidget()
        self.minecraft_list.addItems(self.build_manager.get_minecraft_versions())
        self.minecraft_list.itemSelectionChanged.connect(self.minecraft_selected)
        grid.addWidget(self.minecraft_list, 1, 0)

        core_type_label = QLabel(lang.Dialogs.core_type)
        core_type_label.setObjectName("section_title")
        grid.addWidget(core_type_label, 0, 1)

        self.core_type_list = QListWidget()
        self.core_type_list.addItems(self.build_manager.get_core_types())
        self.core_type_list.itemSelectionChanged.connect(self.core_type_selected)
        grid.addWidget(self.core_type_list, 1, 1)

        core_version_label = QLabel(lang.Dialogs.core_version)
        core_version_label.setObjectName("section_title")
        grid.addWidget(core_version_label, 0, 2)

        self.core_version_list = QListWidget()
        grid.addWidget(self.core_version_list, 1, 2)

        layout.addLayout(grid)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.filter_versions()

    def filter_versions(self):
        search_text = self.search_input.text().lower()

        for i in range(self.minecraft_list.count()):
            item = self.minecraft_list.item(i)
            item.setHidden(search_text not in item.text().lower())

        for i in range(self.core_type_list.count()):
            item = self.core_type_list.item(i)
            item.setHidden(search_text not in item.text().lower())

        for i in range(self.core_version_list.count()):
            item = self.core_version_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def minecraft_selected(self):
        selected = self.minecraft_list.selectedItems()
        if selected:
            self.minecraft_version = selected[0].text()
            self.update_core_versions()

    def core_type_selected(self):
        selected = self.core_type_list.selectedItems()
        if selected:
            self.core_type = selected[0].text()
            self.update_core_versions()

    def update_core_versions(self):
        self.core_version_list.clear()

        if not self.minecraft_version or not self.core_type:
            return

        versions = self.build_manager.get_core_versions(self.core_type, self.minecraft_version)
        if self.core_type == "Vanilla":
            versions = [self.minecraft_version]
        elif self.core_type == "Forge":
            versions = [f"Forge {self.minecraft_version}-{v}" for v in versions]
        elif self.core_type == "Fabric":
            versions = [f"Fabric Loader {v}" for v in versions]
        elif self.core_type == "Quilt":
            versions = [f"Quilt Loader {v}" for v in versions]

        self.core_version_list.addItems(versions)

    def accept(self):
        selected_core = self.core_version_list.selectedItems()
        if selected_core:
            self.core_version = selected_core[0].text()

        if not self.minecraft_version:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.select_minecraft_version, btn_text=lang.Dialogs.ok)
            return

        if not self.core_type:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.select_core_type, btn_text=lang.Dialogs.ok)
            return

        if not self.core_version and self.core_type != "Vanilla":
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.select_core_version, btn_text=lang.Dialogs.ok)
            return

        super().accept()

class BuildsPage(QWidget):
    detail_requested = pyqtSignal(dict, str)

    def __init__(self, main, parent=None):
        super().__init__(parent)
        self.allCards = {}
        self.launcher = main
        self.setObjectName("container")
        self.setStyleSheet(DARK_STYLESHEET)
        self.build_manager = BuildManager(
            minecraft_versions=memory.get("minecraft_versions", []),
            core_types=memory.get("core_types", []),
            core_versions=memory.get("core_versions", {})
        )
        memory.put("build_manager", self.build_manager)
        self.active_build_name = None
        self.selected_build_name = None
        self.selected_minecraft = None
        self.canCloseLauncherWithBuild = True
        self.allGameThreads = {}
        self.running_threads = {}
        self.setup_ui()
        self.setup_connections()
        self.load_builds()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.layout1 = QVBoxLayout()
        main_layout.addLayout(self.layout1)
        self.layout1.setContentsMargins(12, 12, 12, 12)
        self.layout1.setSpacing(10)

        title = QLabel(lang.Dialogs.minecraft_builds)
        title.setObjectName("title")
        self.layout1.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(12)

        builds_frame = QFrame()
        builds_frame.setObjectName("container")
        builds_layout = QVBoxLayout(builds_frame)
        builds_layout.setContentsMargins(0, 0, 0, 0)
        builds_layout.setSpacing(8)

        area = QScrollArea()
        area.setObjectName("container")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)

        self.builds_container = QWidget()
        self.builds_container.setObjectName("container")
        self.builds_container_layout = QVBoxLayout(self.builds_container)
        self.builds_container_layout.setContentsMargins(0, 0, 0, 0)
        self.builds_container_layout.setSpacing(8)
        self.builds_container_layout.addStretch(1)
        area.setWidget(self.builds_container)
        builds_layout.addWidget(area, 1)

        self.launch_btn = QPushButton(lang.Elements.play)
        self.launch_btn.setObjectName("launch")
        self.delete_btn = QPushButton(lang.Elements.delete)
        self.delete_btn.setObjectName("secondary")
        self.detail_btn = QPushButton(lang.Elements.detailed_view)
        self.detail_btn.setObjectName("secondary")
        self.client_settings_btn = QPushButton(lang.Elements.client_settings_btn)
        self.client_settings_btn.setObjectName("secondary")
        self.create_shortcut_btn = QPushButton(lang.Elements.create_shortcut_btn)
        self.create_shortcut_btn.setObjectName("secondary")
        self.open_build_folder = QPushButton(lang.Elements.open_build_folder)
        self.open_build_folder.setObjectName("secondary")
        self.download_launcher = QPushButton(lang.Elements.download_launcher)
        self.download_launcher.setObjectName("secondary")

        self.toggleLaunchPanel(False)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.detail_btn)
        btn_layout.addWidget(self.client_settings_btn)
        btn_layout.addWidget(self.create_shortcut_btn)
        btn_layout.addWidget(self.open_build_folder)
        btn_layout.addWidget(self.download_launcher)
        builds_layout.addLayout(btn_layout)

        content.addWidget(builds_frame, 2)

        self.centralWidget = self
        self.create_panel = ExpandablePanel(self, min=5, max=230, direction="left")
        self.create_panel.animation.setDuration(270)
        self.create_panel.setOutWidget(False)
        self.create_panel.mask._isMouseTracking = False
        toggleBtn = QPushButton()
        toggleBtn.setIcon(QIcon(":plus.png"))
        toggleBtn.setIconSize(QSize(32, 32))
        toggleBtn.setStyleSheet("background: none;")

        def toggleFunc():
            self.create_panel.expand() if not self.create_panel.isExpanded() else self.create_panel.collapse()

        toggleBtn.clicked.connect(toggleFunc)
        main_layout.addWidget(toggleBtn)
        main_layout.addWidget(self.create_panel)

        self.name_input = NameInputWidget()
        self.name_warning = CompactLabel("")
        self.name_warning.setObjectName("warning")
        self.name_warning.setVisible(False)

        self.version_btn = PanelButton(lang.Elements.select_version)
        self.version_btn.setFixedHeight(32)
        self.version_info = QLabel(lang.Dialogs.no_version_selected)
        self.version_info.setStyleSheet("color: #A0A0A0; font-style: italic;")
        self.version_info.setWordWrap(True)

        self.create_btn = PanelButton(lang.Elements.create_build)
        self.create_btn.setFixedHeight(32)
        self.create_btn.setEnabled(False)

        self.create_panel.addWidget(self.name_input)
        self.create_panel.addWidget(self.name_warning)
        self.create_panel.addWidget(self.version_btn)
        self.create_panel.addWidget(self.create_btn)

        self.layout1.addLayout(content, 1)

        self.create_panel.mask.layout.addStretch()

    def toggleLaunchPanel(self, b: bool):
        self.launch_btn.setEnabled(b)
        self.delete_btn.setEnabled(b)
        self.detail_btn.setEnabled(b)
        self.client_settings_btn.setEnabled(b)
        self.create_shortcut_btn.setEnabled(b)
        self.open_build_folder.setEnabled(b)

    def setup_connections(self):
        self.name_input.input.textChanged.connect(self.validate_name)
        self.version_btn.clicked.connect(self.select_versions)
        self.create_btn.clicked.connect(self.create_build)
        self.launch_btn.clicked.connect(self.toggle_launch_stop)
        self.delete_btn.clicked.connect(lambda: self.delete_build(self.selected_build_name))
        self.detail_btn.clicked.connect(self.request_detail_view)
        self.client_settings_btn.clicked.connect(lambda: self.get_client_settings_dialog(self.selected_build_name))
        self.create_shortcut_btn.clicked.connect(self.createShotcut)
        self.open_build_folder.clicked.connect(self.openBuildFolder)
        self.download_launcher.clicked.connect(lambda: self.show_temp_message(">:)))))))))))))))))"))

    def createShotcut(self):
        create_shortcut(os.getcwd()+"/ViperLauncher.exe",
            self.build_manager.get_build_path(self.build_manager.get_build(self.selected_build_name))+"/"+self.selected_build_name+".lnk",
                        arguments=f"--start-with-build-name {self.selected_build_name} --nogui")
        os.startfile(self.build_manager.get_build_path(self.build_manager.get_build(self.selected_build_name)))

    def openBuildFolder(self):
        os.startfile(self.build_manager.get_build_path(self.build_manager.get_build(self.selected_build_name)))

    def get_client_settings_dialog(self, name=None):
        path = self.build_manager.get_build_path(self.build_manager.get_build(self.selected_build_name if name is None else name))
        print(path, self.build_manager.get_build(self.selected_build_name if name is None else name), name)
        dil = ClientSettingsDialog(path, self)
        dil.exec()

    def toggle_launch_stop(self):
        if not self.selected_build_name:
            self.show_temp_message(lang.Dialogs.select_build_first, "warning")
            return

        if self.selected_build_name in self.running_threads:
            self.stop_build(self.selected_build_name)
        else:
            self.launch_build()

    def select_build_by_name(self, name):
        self.selected_build_name = name
        self.toggleLaunchPanel(True)

        if name in self.running_threads:
            self.launch_btn.setText(lang.Elements.stop)
            self.launch_btn.setObjectName("stop")
        else:
            self.launch_btn.setText(lang.Elements.play)
            self.launch_btn.setObjectName("launch")
        self.launch_btn.style().polish(self.launch_btn)

        for name_ in self.allCards:
            card = self.allCards[name_]
            if card:
                if name_ == name:
                    card.setStyleSheet("QFrame#build_card {border: 2px solid #0078D7; border-radius: 4px;}")
                else:
                    card.setStyleSheet("QFrame#build_card {border: none;}")

    def stop_build(self, name, nogui=False):
        if name in self.running_threads:
            print(self.allGameThreads)
            os.kill(self.allGameThreads[name], signal.SIGILL)
            del self.allGameThreads[name]
            self.show_temp_message(lang.Dialogs.build_stopped.format(name=name), "info")
            self.launch_btn.setText(lang.Elements.play)
            self.launch_btn.setObjectName("launch")
            self.launch_btn.style().polish(self.launch_btn)
            self.launcher.show() if not nogui else print(f"Build {name} stopped!")
        else:
            self.show_temp_message(lang.Dialogs.build_not_running.format(name=name), "warning")
            print(f"Build {name} not running!")
        self.checkVisibleLauncher()

    def validate_name(self, text):
        self.name_warning.setVisible(False)
        self.name_input.input.setProperty("invalid", "false")
        self.name_input.style().polish(self.name_input.input)

        if len(text) < 3:
            self.name_warning.setText(lang.Dialogs.name_too_short)
            self.name_warning.setVisible(True)
            self.name_input.input.setProperty("invalid", "true")
            self.create_btn.setEnabled(False)
            return False

        if any(b['name'].lower() == text.lower() for b in self.build_manager.get_all_builds()):
            self.name_warning.setText(lang.Dialogs.build_exists)
            self.name_warning.setVisible(True)
            self.name_input.input.setProperty("invalid", "true")
            self.create_btn.setEnabled(False)
            return False

        self.create_btn.setEnabled(bool(self.selected_minecraft))
        return True

    def select_versions(self):
        dialog = VersionSelectionDialog(self.build_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_minecraft = dialog.minecraft_version
            self.selected_core_type = dialog.core_type
            self.selected_core_version = dialog.core_version

            version_info = f"{lang.Dialogs.minecraft_label} {self.selected_minecraft}<br>" \
                            "{lang.Dialogs.core_type_label} {self.selected_core_type}"
            if self.selected_core_version:
                version_info += f"<br>{lang.Dialogs.core_version_label} {self.selected_core_version}"

            self.version_info.setText(version_info)

            if self.name_input.input.text().strip():
                self.create_btn.setEnabled(True)

    def create_build(self):
        name = self.name_input.input.text().strip()
        try:
            build_data = {
                "name": name,
                "minecraft": self.selected_minecraft,
                "core_type": self.selected_core_type,
                "core_version": self.selected_core_version
            }
            build = self.build_manager.create_build(build_data)
            self.add_build_card(build)
            self.select_build_by_name(name)
            self.name_input.input.clear()
            self.selected_minecraft = ""
            self.selected_core_type = ""
            self.selected_core_version = ""
            self.version_info.setText(lang.Dialogs.no_version_selected)
            self.create_btn.setEnabled(False)
            self.show_temp_message(lang.Dialogs.build_created.format(name=name), "success")
            self.launcher.mods_page.buildsUpdate()
        except ValueError as e:
            self.show_temp_message(str(e), "warning")

    def add_build_card(self, build):
        if not self.build_manager.get_all_builds() and self.empty_label.isVisible():
            self.empty_label.setVisible(False)

        card = QFrame()
        card.setObjectName("build_card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(100)
        card.setStyleSheet("QFrame#build_card {border: none;}")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(4)

        name_layout = QHBoxLayout()

        name_label = QLabel(build['name'])
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        name_layout.addWidget(name_label)

        LoaderBtn = QPushButton()
        LoaderBtn.enterEvent = lambda event, btn=LoaderBtn, e=LoaderBtn.enterEvent: (
            QToolTip.showText(btn.mapToGlobal(btn.rect().center()), btn.toolTip(), btn),
            e(event) if e else None
        )[-1]
        if build['core_type'].lower() == "fabric":
            icon = QIcon(":fabric.png")
            LoaderBtn.setToolTip(lang.Dialogs.fabric_tooltip)
        elif build['core_type'].lower() == "forge":
            icon = QIcon(":forge.png")
            LoaderBtn.setToolTip(lang.Dialogs.forge_tooltip)
        elif build['core_type'].lower() == "quilt":
            icon = QIcon(":quilt.png")
            LoaderBtn.setToolTip(lang.Dialogs.quilt_tooltip)
        elif build['core_type'].lower() == "vanilla":
            icon = QIcon()
            LoaderBtn.setToolTip(lang.Dialogs.vanilla_tooltip)
        else:
            icon = QIcon()
            LoaderBtn.setToolTip(lang.Dialogs.vanilla_tooltip)
        LoaderBtn.setIcon(icon)
        LoaderBtn.setIconSize(QSize(32, 32))
        LoaderBtn.setFixedSize(32, 32)
        LoaderBtn.setStyleSheet("QPushButton {background: none;}")

        name_layout.addStretch()
        name_layout.addWidget(LoaderBtn)
        card_layout.addLayout(name_layout)

        version_info = QLabel(
            f"{lang.Dialogs.minecraft_version} {build['minecraft']} | "
            f"{lang.Dialogs.core_type} {build['core_type']}"
        )
        version_info.setStyleSheet("color: #A0A0A0; font-size: 8pt;")
        card_layout.addWidget(version_info)

        if build['core_version']:
            core_version = QLabel(f"{lang.Dialogs.core_version} {build['core_version']}")
            core_version.setStyleSheet("color: #A0A0A0; font-size: 8pt;")
            card_layout.addWidget(core_version)

        self.builds_container_layout.insertWidget(0, card)

        self.allCards[build['name']] = card

        def doubleClick(name):
            a = settings.get('doubleClickBehavior', 0)
            if a == 0:
                self.launch_build_by_name(name)
            elif a == 1:
                self.request_detail_view(name)
            else:
                self.get_client_settings_dialog(name)

        card.mousePressEvent = lambda event, name=build['name']: self.select_build_by_name(name)
        card.mouseDoubleClickEvent = lambda event, name=build['name']: doubleClick(name)

    def update_build_card(self, build):
        for i in range(self.builds_container_layout.count()):
            widget = self.builds_container_layout.itemAt(i).widget()
            if widget and widget == build['card']:
                self.builds_container_layout.removeWidget(widget)
                widget.deleteLater()
                break

        self.add_build_card(build)

    def is_core_installed(self, build):
        path = "./minecraft"
        if build['core_type'] == "Vanilla":
            return os.path.exists(os.path.join(path, "versions", build['minecraft'], f"{build['minecraft']}.json"))
        elif build['core_type'] == "Forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            return os.path.exists(os.path.join(path, "versions", f"{build['minecraft']}-forge-{forge_version}", f"{build['minecraft']}-forge-{forge_version}.json"))
        elif build['core_type'] == "Fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            return os.path.exists(os.path.join(path, "versions", f"fabric-loader-{fabric_version}-{build['minecraft']}", f"fabric-loader-{fabric_version}-{build['minecraft']}.json"))
        elif build['core_type'] == "Quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            return os.path.exists(os.path.join(path, "versions", f"quilt-loader-{quilt_version}-{build['minecraft']}", f"quilt-loader-{quilt_version}-{build['minecraft']}.json"))
        return False

    def remove_core_folder(self, build):
        path = "./minecraft/versions"
        folder_path = None

        if build['core_type'] == "Vanilla":
            folder_path = os.path.join(path, build['minecraft'])
        elif build['core_type'] == "Forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            folder_path = os.path.join(path, f"{build['minecraft']}-forge-{forge_version}")
        elif build['core_type'] == "Fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            folder_path = os.path.join(path, f"fabric-loader-{fabric_version}-{build['minecraft']}")
        elif build['core_type'] == "Quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            folder_path = os.path.join(path, f"quilt-loader-{quilt_version}-{build['minecraft']}")

        if folder_path and os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            return True
        return False

    def install_core(self, build, nogui=False, force=True):
        installer = None
        path = "./minecraft"
        os.makedirs(path, exist_ok=True)
        if build['core_type'].lower() == "vanilla":
            installer = MinecraftInstaller(path=path, version=build['minecraft'])
        elif build['core_type'].lower() == "forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            installer = ForgeInstaller(path=path, version=build['minecraft'], loaderVersion=forge_version)
        elif build['core_type'].lower() == "fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            installer = FabricInstaller(path=path, version=build['minecraft'], loaderVersion=fabric_version)
        elif build['core_type'].lower() == "quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            installer = QuiltInstaller(path=path, version=build['minecraft'], loaderVersion=quilt_version)

        if installer:
            if force and self.is_core_installed(build):
                self.remove_core_folder(build)
            dialog = InstallDialog(installer, parent=self)
            if not nogui:
                return dialog.exec() == QDialog.DialogCode.Accepted
            else:
                while not dialog.finished_installing:
                    pass
                return not dialog.canceled
        return False

    def checkVisibleLauncher(self):
        if len(self.allGameThreads) == 0 and not self.isVisible() and self.canCloseLauncherWithBuild:
            QApplication.quit()

    def launch_build(self, nogui=False):
        if not self.selected_build_name:
            self.show_temp_message(lang.Dialogs.select_build_to_launch, "warning")
            return

        build = self.build_manager.get_build(self.selected_build_name)
        if not build:
            self.show_temp_message(lang.Dialogs.build_not_exists, "warning")
            self.selected_build_name = None
            self.toggleLaunchPanel(False)
            return

        if settings.get('javaPath', "") == "" or not os.path.exists(settings.get('javaPath', "")):
            print("Check java...")
            if os.path.exists(settings.get('javaPath', 'java')):
                print(f"Check 'JAVA_HOME' - {os.getenv('JAVA_HOME')}")
                if not os.path.exists(os.getenv('JAVA_HOME') + "\\bin\\java.exe"):
                    self.show_temp_message(lang.Dialogs.no_java_selected, "warning")
                    print("Java is not selected!")
                    return

        if not self.is_core_installed(build):
            if nogui:
                print(f"Core '{build['core_version']}' is not installed")
                return
            if not self.install_core(build):
                self.show_temp_message(lang.Dialogs.core_install_canceled, "warning")
                return

        path = "./minecraft"
        username = self.launcher.main.getActivName()
        if username is None:
            self.show_temp_message(lang.Dialogs.username_not_specified, "warning")
            return

        launcher = None
        game_dir = self.build_manager.get_build_path(build)
        argv = [
            "-Xmx{memory}m".format(memory=settings.get('javaMemory', 1000)),
            "-Dminecraft.api.env=custom",
            "-Dminecraft.api.auth.host=https://invalid.invalid",
            "-Dminecraft.api.account.host=https://invalid.invalid",
            "-Dminecraft.api.session.host=https://invalid.invalid",
            "-Dminecraft.api.services.host=https://invalid.invalid"
        ]
        java = settings.get('javaPath', 'java')
        os.environ["JAVA_HOME"] = java if os.path.exists(java) else os.getenv('JAVA_HOME') + "\\bin\\java.exe"
        print(os.environ["JAVA_HOME"])

        if build['core_type'] == "Vanilla":
            launcher = VanillaLauncher(version=build['minecraft'], path=path, username=username, game_dir=game_dir,
                                       javaArgv=argv)
        elif build['core_type'] == "Forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            launcher = ForgeLauncher(version=build['minecraft'], forge_version=forge_version, path=path,
                                     username=username, game_dir=game_dir, javaArgv=argv)
        elif build['core_type'] == "Fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            launcher = FabricLauncher(version=build['minecraft'], fabric_version=fabric_version, path=path,
                                      username=username, game_dir=game_dir, javaArgv=argv)
        elif build['core_type'] == "Quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            launcher = QuiltLauncher(version=build['minecraft'], quilt_version=quilt_version, path=path,
                                     username=username, game_dir=game_dir, javaArgv=argv)

        if not launcher:
            self.show_temp_message(lang.Dialogs.unsupported_core_type, "warning")
            return

        if self.selected_build_name in self.running_threads:
            self.show_temp_message(lang.Dialogs.build_already_running.format(name=self.selected_build_name), "warning")
            print("Build already running!")
            return

        self.show_temp_message(lang.Dialogs.launching_build.format(minecraft=build['minecraft'], core_type=build['core_type']), "info")
        t = LauncherThread(launcher)

        def finish(thread, name):
            self.allGameThreads.pop(name) if name in self.allGameThreads else None,
            self.running_threads.pop(name, None),
            self.launch_btn.setText(lang.Elements.play),
            self.launch_btn.setObjectName("launch"),
            self.launch_btn.style().polish(self.launch_btn),
            self.launcher.show() if not nogui else print(f"Minecraft {name} is closed!"),
            self.checkVisibleLauncher()

        t.finished.connect(lambda x=t, name=self.selected_build_name: finish(x, name))
        self.running_threads[self.selected_build_name] = t
        t.start()
        while launcher.procces is None:
            pass
        self.allGameThreads[self.selected_build_name] = launcher.procces.pid

        self.launch_btn.setText(lang.Elements.stop)
        self.launch_btn.setObjectName("stop")
        self.launch_btn.style().polish(self.launch_btn)

        act = settings.get('launcherBehavior', 0)
        if act == 0:
            self.launcher.hide()
        elif act == 1:
            self.launcher.showMinimized()

    def launch_build_by_name(self, name, nogui=False):
        if not name:
            self.show_temp_message(lang.Dialogs.build_name_not_specified, "warning")
            return

        build = self.build_manager.get_build(name)
        if not build:
            self.show_temp_message(lang.Dialogs.build_not_found.format(name=name), "warning")
            return

        self.select_build_by_name(name)
        self.launch_build(nogui)

    def edit_build(self):
        if not self.selected_build_name:
            return

        build = self.build_manager.get_build(self.selected_build_name)
        if not build:
            self.show_temp_message(lang.Dialogs.build_not_found, "warning")
            self.selected_build_name = None
            self.toggleLaunchPanel(False)
            return

        self.request_detail_view(build['name'])
        self.launcher.mods_page.buildsUpdate()

    def request_detail_view(self, name=None):
        if not name:
            name = self.selected_build_name

        if not name:
            return

        build = self.build_manager.get_build(name)
        if not build:
            self.show_temp_message(lang.Dialogs.build_not_found, "warning")
            if self.selected_build_name == name:
                self.selected_build_name = None
                self.toggleLaunchPanel(False)
            return

        build_dir = os.path.join('./builds/', slugify(name))
        self.detail_requested.emit(build.copy(), build_dir)

    def update_build(self, updated_build):
        if self.build_manager.update_build(updated_build):
            self.update_build_card(updated_build)
            self.launcher.mods_page.buildsUpdate()
            self.show_temp_message(lang.Dialogs.build_updated.format(name=updated_build['name']), "success")
        else:
            self.show_temp_message(lang.Dialogs.build_update_failed, "warning")

    def delete_build(self, name=None):
        if not name:
            name = self.selected_build_name

        if not name:
            return

        build = self.build_manager.get_build(name)
        if not build:
            self.show_temp_message(lang.Dialogs.build_not_found, "warning")
            if self.selected_build_name == name:
                self.selected_build_name = None
                self.toggleLaunchPanel(False)
            return

        reply = windowAbs.question(self, lang.Dialogs.confirm_deletion,
                                     lang.Dialogs.confirm_delete_build.format(name=build['name']),
                                   yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no)

        if not reply:
            return

        if self.build_manager.delete_build(name):
            if 'card' in build and build['card']:
                build['card'].deleteLater()

            if name == self.selected_build_name:
                self.selected_build_name = None
                self.toggleLaunchPanel(False)

            self.build_manager.load_builds()
            self.load_builds()
            self.launcher.mods_page.buildsUpdate()

            if not self.build_manager.get_all_builds():
                self.empty_label.setVisible(True)

            self.show_temp_message(lang.Dialogs.build_deleted.format(name=build['name']), "info")

    def show_temp_message(self, text, style="info"):
        msg = QLabel(text)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if style == "success":
            msg.setObjectName("success_message")
        elif style == "warning":
            msg.setObjectName("warning_message")
        else:
            msg.setObjectName("info_message")

        self.builds_container_layout.insertWidget(0, msg)
        QTimer.singleShot(3000, msg.deleteLater)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def load_builds(self):
        self.clearLayout(self.builds_container_layout)
        for build in self.build_manager.get_all_builds():
            self.add_build_card(build)
            if build.get('active'):
                self.active_build_name = build['name']

        self.builds_container_layout.addStretch()

        self.empty_label = QLabel(lang.Dialogs.no_builds)
        self.empty_label.setObjectName("empty_label")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #7F7F7F; font-style: italic;")
        self.builds_container_layout.addWidget(self.empty_label)

        self.empty_label.setVisible(not self.build_manager.get_all_builds())