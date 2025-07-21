import os
import signal
import subprocess
import sys
import time

from PyQt6.QtCore import QTimer, QRect, Qt
from PyQt6.QtGui import QIcon, QCloseEvent

import build_info
from UI.elements.AnimStackedWidget import FadeStackedWidget
from UI.elements.CardWidget import CardWidget, BuildCard
from UI.elements.ExpandablePanel import ExpandablePanel
from UI.elements.CompactWidgets import PanelButton
from UI.pages.cores import MinecraftVersionsPage
from UI.pages.profile import OfflineProfilePage
from UI.pages.settings import SettingsWidget
from UI.pages.versions import BuildsPage
from UI.pages.mods import ModsPage
from UI.translate import lang
from UI.windows import windowAbs
from UI.windows.windowAbs import WindowAbs, DialogAbs
from UI.icons import resources

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QDialog, \
    QApplication, QMessageBox

from func import settings, Console
from func.GitUpdater import get_latest_release_tag, download_updater_exe, get_latest_release_tag_for_launcher_version


class Window(WindowAbs):
    def __init__(self, mainWindow):
        super().__init__()
        self.main = mainWindow
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.setMinimumWidth(1000)

        self.cardWidget = BuildCard(self)
        self.cardWidget.hide()

        self.h = QHBoxLayout()
        self.v = QVBoxLayout(self.central)
        self.v.addLayout(self.h, 1)

        self.h.setContentsMargins(0, 0, 0, 0)
        self.v.setContentsMargins(2, 2, 2, 2)

        self.expPanel = ExpandablePanel(self, 37, 120)
        self.h.addWidget(self.expPanel)

        self.viewPages = FadeStackedWidget()
        self.h.addWidget(self.viewPages, 1)

        self.profilePage = OfflineProfilePage(self)
        self.profilePageIndex = self.viewPages.addWidget(self.profilePage)

        self.profile_page_btn = PanelButton(lang.Elements.profile)
        self.profile_page_btn.setObjectName("NavigationPanelButton")
        self.profile_page_btn.setIcon(QIcon(":Minecraft.png"))
        self.profile_page_btn.clicked.connect(lambda: self.viewPages.setCurrentIndex(self.profilePageIndex))
        self.expPanel.addWidget(self.profile_page_btn)

        self.builds_page_btn = PanelButton(lang.Elements.builds)
        self.builds_page_btn.setObjectName("NavigationPanelButton")
        self.builds_page_btn.setIcon(QIcon(":tools.ico"))
        self.builds_page_btn.clicked.connect(
            lambda: self.viewPages.setCurrentIndex(self.builds_page_index)
        )
        self.expPanel.addWidget(self.builds_page_btn)

        self.builds_page = BuildsPage(self)
        self.builds_page.detail_requested.connect(self.showBuildCard)
        self.builds_page_index = self.viewPages.addWidget(self.builds_page)

        self.cores_page_btn = PanelButton(lang.Elements.cores)
        self.cores_page_btn.setObjectName("NavigationPanelButton")
        self.cores_page_btn.setIcon(QIcon(":download.png"))
        self.cores_page_btn.clicked.connect(
            lambda: self.viewPages.setCurrentIndex(self.cores_page_index)
        )
        self.expPanel.addWidget(self.cores_page_btn)

        self.cores_page = MinecraftVersionsPage(self)
        self.cores_page_index = self.viewPages.addWidget(self.cores_page)

        self.mods_page_btn = PanelButton(lang.Elements.mods)
        self.mods_page_btn.setObjectName("NavigationPanelButton")
        self.mods_page_btn.setIcon(QIcon(":mods.png"))
        self.mods_page_btn.clicked.connect(
            lambda: self.viewPages.setCurrentIndex(self.mods_page_index)
        )
        self.expPanel.addWidget(self.mods_page_btn)

        self.mods_page = ModsPage()
        self.mods_page_index = self.viewPages.addWidget(self.mods_page)

        self.settings_page = SettingsWidget(self, main=self)
        self.settings_page_index = self.viewPages.addWidget(self.settings_page)

        self.settings_page_btn = PanelButton(lang.Elements.settings)
        self.settings_page_btn.setObjectName("NavigationPanelButton")
        self.settings_page_btn.setIcon(QIcon(":settings.png"))
        self.settings_page_btn.clicked.connect(
            lambda: self.viewPages.setCurrentIndex(self.settings_page_index)
        )
        self.expPanel.addWidget(self.settings_page_btn)

        self.expPanel.mask.layout.addStretch()
        self.updatePanelState(False)

    def updatePanelState(self, anim=True):
        if not settings.get('panelPositionBehavior', 0):
            self.expPanel.setOutWidget(True)
        else:
            self.expPanel.setOutWidget(False)

        if settings.get('panelEventBehavior', 0) == 0:
            self.expPanel.mask._isMouseTracking = True
            self.expPanel.collapse(anim)
        elif settings.get('panelEventBehavior', 0) == 1:
            self.expPanel.mask._isMouseTracking = False
            self.expPanel.expand(anim)
        else:
            self.expPanel.mask._isMouseTracking = False
            self.expPanel.collapse(anim)

        self.expPanel.update()
        self.update()

    def close_all_clients(self):
        dialog = DialogAbs(self)
        wid = QWidget()
        dialog.setCentralWidget(wid)
        dialog.setWindowTitle(lang.Dialogs.confirm_title)
        dialog.setFixedSize(300, 100)

        layout = QVBoxLayout(wid)

        label = QLabel(lang.Dialogs.confirm_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_close_all = QPushButton(lang.Dialogs.close_all)
        btn_hide = QPushButton(lang.Dialogs.hide_launcher)
        btn_cancel = QPushButton(lang.Dialogs.cancel)

        button_layout.addWidget(btn_close_all)
        button_layout.addWidget(btn_hide)
        button_layout.addWidget(btn_cancel)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self._close_action = None

        def choose_close_all():
            self._close_action = "close_all"
            dialog.accept()

        def choose_hide():
            self._close_action = "hide"
            dialog.accept()

        def choose_cancel():
            self._close_action = "cancel"
            dialog.reject()

        btn_close_all.clicked.connect(choose_close_all)
        btn_hide.clicked.connect(choose_hide)
        btn_cancel.clicked.connect(choose_cancel)

        result = dialog.exec()

        if self._close_action == "close_all":
            self.killAllClients()
            return True
        elif self._close_action == "hide":
            self.hide()
        return False

    def showUpdateSuccessfullInfo(self):
        print("Update installation is complete!")
        windowAbs.information(self, "", lang.Dialogs.update_successfully_info, btn_text=lang.Dialogs.ok,
                              width=250, height=130)

    def killAllClients(self):
        print("Executed all kills")
        for t in self.builds_page.allGameThreads:
            print(t)
            os.kill(self.builds_page.allGameThreads[t], signal.SIGILL)

    def close_with_update(self, event):
        if not self.settings_page._startLauncherAfterUpdate and not settings.get("silentUpdate", True):
            print("Silent installation is disabled.")
            super().closeEvent(event)
            return
        print("Check update:", self.settings_page._SilentNeedUpdate)
        needLauncher, needUpdater = self.settings_page._SilentNeedUpdate
        if not (needLauncher or needUpdater):
            print("Latest version installer -> Closing App...")
            super().closeEvent(event)
            return
        self.hide()
        ver, release = get_latest_release_tag_for_launcher_version(build_info.BUILD_VERSION)
        print("Installing", ver, release)
        if needUpdater:
            download_updater_exe(ver[1:])
        if not os.path.exists("updater.exe"):
            print("updater.exe not found")
            super().closeEvent(event)
            return
        if needLauncher:
            self.settings_page.download_update_zip_for_later_installation(ver, release)
            v = subprocess.CREATE_NEW_CONSOLE if Console.isVisible() else subprocess.CREATE_NO_WINDOW
            args = ["updater.exe"]
            args.append("--skip-download")
            args.append("--pid="+str(os.getpid()))
            args.append("--no-start") if self.settings_page._startLauncherAfterUpdate else None
            args.append(build_info.BUILD_VERSION)
            subprocess.Popen(
                args,
                creationflags=v
            )
            print("wait updater.exe...")
            time.sleep(10)
        super().closeEvent(event)

    def closeEvent(self, a0):
        if len(self.builds_page.allGameThreads) == 0:
            self.close_with_update(a0)
            return

        if self.close_all_clients():
            self.close_with_update(a0)
        else:
            a0.ignore()

    def showBuildCard(self, build: dict, path: str):
        self.cardWidget.set_build(build, path)
        self.cardWidget.show()
        self.cardWidget.raise_()