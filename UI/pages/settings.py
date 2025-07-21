import ctypes
import os
import subprocess
import traceback

import psutil
import win32con
import win32console
import win32gui
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys

from UI.elements.HtmlViewer import AboutDialog
from UI.elements.TextSlider import SliderTicksLables
from UI.elements.buttons import AnimatedToggle
from UI.windows import windowAbs
from func import settings, memory, Console
from UI.translate import lang
import build_info
from func.GitUpdater import get_latest_release_tag, download_updater_exe, get_latest_release_tag_for_launcher_version, download_with_progress

THIS_VERSION = build_info.BUILD_VERSION

if os.path.exists(os.getcwd() + "/updater.exe"):
    process = subprocess.Popen(
                [os.getcwd() + "/updater.exe", "-v", THIS_VERSION],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
    process.wait()
    stdout, stderr = process.communicate()
    print(stdout)
    UPDATER_VERSION = stdout.split("\n")[0]
else: UPDATER_VERSION = "X"

class SettingsWidget(QWidget):
    def __init__(self, parent=None, main=None):
        super().__init__(parent)
        self._startLauncherAfterUpdate = False
        self._SilentNeedUpdate = (False, False)
        self.java_input: QLineEdit = None
        self.main = main
        main_layout = QHBoxLayout(self)

        self.settings = settings

        tabs_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget(self)
        scroll_widget.setObjectName("settingsArea")
        scroll_widget.setLayout(tabs_layout)
        self.scroll_area.setWidget(scroll_widget)

        self.tab_buttons = []
        self.create_tab_button(lang.Dialogs.general_tab, tabs_layout)
        self.create_tab_button(lang.Dialogs.game_settings_tab, tabs_layout)
        self.create_tab_button(lang.Dialogs.advanced_tab, tabs_layout)
        self.create_tab_button(lang.Dialogs.about_tab, tabs_layout)
        tabs_layout.addStretch()

        main_layout.addWidget(self.scroll_area, 1)

        self.settings_stack = QStackedWidget()
        main_layout.addWidget(self.settings_stack, 3)

        self.add_general_settings()
        self.add_game_settings()
        self.add_advanced_settings()
        self.add_about_info()

        self.tab_buttons[0].click()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

    def updateTime(self):
        if settings.get("javaMemory", 8000) != self.MemorySpin.value():
            settings.put("javaMemory", self.MemorySpin.value())

    def checkUpdateForApp(self, silent: bool = False):
        ver = get_latest_release_tag()
        if ver is None:
            if not silent:
                print("Ошибка получения версии с сервера")
            return

        LauncherVersion = THIS_VERSION if THIS_VERSION != "X" else "-1"
        UpdaterVersion = UPDATER_VERSION

        try:
            latestLauncher = int(ver[1:].split(".")[0])
            latestUpdater = int(ver[1:].split(".")[1])
        except Exception as e:
            if not silent:
                print("Ошибка разбора версии:", e)
            return

        currentLauncher = int(LauncherVersion) if LauncherVersion.isdigit() else -1
        currentUpdater = int(UpdaterVersion) if UpdaterVersion.isdigit() else -1

        launcher_update_needed = latestLauncher > currentLauncher
        updater_update_needed = latestUpdater > currentUpdater

        if not launcher_update_needed:
            if not silent:
                windowAbs.information(
                    self, "", lang.Dialogs.this_latest_version,
                    height=140, width=350, btn_text=lang.Dialogs.ok
                )
            return

        if settings.get("silentUpdate", True) and silent:
            self._SilentNeedUpdate = (launcher_update_needed, updater_update_needed)
            return

        if not silent:
            d = windowAbs.question(
                self, "", lang.Dialogs.need_update_for_app.format(version=ver),
                height=140, width=350,
                yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no
            )
            if not d:
                return

            if len(self.main.builds_page.allGameThreads) != 0:
                q = windowAbs.question(
                    self, "", lang.Dialogs.need_close_all_for_update,
                    height=140, width=350,
                    yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no
                )
                if not q:
                    return
                self.main.killAllClients()
            self._startLauncherAfterUpdate = True
            self.showConsole()
            self.main.close()

    def download_update_zip_for_later_installation(self, tag, release):
        if tag is None:
            return

        assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
        if "update.zip" not in assets:
            return

        zip_url = assets["update.zip"]
        zip_path = os.path.join(os.getcwd(), "update.zip")

        try:
            download_with_progress(zip_url, zip_path)
        except Exception:
            if os.path.exists(zip_path):
                os.remove(zip_path)

    def create_tab_button(self, name, layout):
        button = QPushButton(name)
        button.setObjectName("SettingsTabButton")
        button.setCheckable(True)
        button.clicked.connect(lambda: self.display_settings(name))
        layout.addWidget(button)
        self.tab_buttons.append(button)

    def display_settings(self, name):
        for button in self.tab_buttons:
            button.setChecked(False)

        button = next(b for b in self.tab_buttons if b.text() == name)
        button.setChecked(True)

        index = self.tab_buttons.index(button)
        self.settings_stack.setCurrentIndex(index)

    def showConsoleToggle(self, checked):
        settings.put("showConsole", checked)

    def langChange(self):
        lang_code = "ru" if self.language_combo.currentIndex() == 0 else "en"
        settings.put("lang", lang_code)
        self.langTitle.setText(lang.Dialogs.restart_required)
        self.langTitle.setFixedHeight(20)

    def setAutoUpdate(self, checked):
        settings.put("autoUpdate", self.autoupdate_chechbox.isChecked())
        self.silentUpdate_chechbox.setChecked(self.silentUpdate_chechbox.isChecked() and self.autoupdate_chechbox.isChecked())
        self.silentUpdate_chechbox.setEnabled(self.autoupdate_chechbox.isChecked())
        settings.put("silentUpdate", self.silentUpdate_chechbox.isChecked() and self.autoupdate_chechbox.isChecked())

    def add_general_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.langTitle = QLabel()
        self.langTitle.setFixedHeight(0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English"])
        self.language_combo.setItemIcon(0, QIcon(self.settings.get("russianIcon")))
        self.language_combo.setItemIcon(1, QIcon(self.settings.get("englishIcon")))
        if settings.get("lang", "ru") == "ru":
            self.language_combo.setCurrentIndex(0)
        else:
            self.language_combo.setCurrentIndex(1)
        layout.addRow(self.langTitle)
        layout.addRow(QLabel(lang.Dialogs.language_label), self.language_combo)
        self.language_combo.currentTextChanged.connect(self.langChange)

        self.autoupdate_chechbox = AnimatedToggle()
        self.autoupdate_chechbox.setChecked(settings.get("checkUpdates", True))
        self.autoupdate_chechbox.toggled.connect(self.setAutoUpdate)
        layout.addRow(self.autoupdate_chechbox, QLabel(lang.Dialogs.check_auto_update))

        self.silentUpdate_chechbox = AnimatedToggle()
        self.silentUpdate_chechbox.setChecked(settings.get("silentUpdate", True))
        self.silentUpdate_chechbox.toggled.connect(self.setAutoUpdate)
        layout.addRow(self.silentUpdate_chechbox, QLabel(lang.Dialogs.allow_silent_update))

        self.check_updates_btn = QPushButton(lang.Elements.check_updates)
        self.check_updates_btn.setObjectName("SettingsButton")
        self.check_updates_btn.clicked.connect(self.checkUpdateForApp)
        layout.addRow(self.check_updates_btn)

        h0 = QHBoxLayout()
        self.show_console = QPushButton(lang.Elements.show_console)
        self.show_console.setObjectName("SettingsButton")
        self.show_console.clicked.connect(self.showConsole)
        h0.addWidget(self.show_console)
        self.hide_console = QPushButton(lang.Elements.hide_console)
        self.hide_console.setObjectName("SettingsButton")
        self.hide_console.clicked.connect(self.hideConsole)
        h0.addWidget(self.hide_console)
        layout.addRow(h0)

        self.open_launcher_folder = QPushButton(lang.Elements.open_launcher_folder)
        self.open_launcher_folder.setObjectName("SettingsButton")
        self.open_launcher_folder.clicked.connect(self.openLauncherFolder)
        layout.addRow(self.open_launcher_folder)

        self.about_changes_btn = QPushButton(lang.Elements.about_changes_title)
        self.about_changes_btn.setObjectName("SettingsButton")
        self.about_changes_btn.clicked.connect(self.openAboutChanges)
        layout.addRow(self.about_changes_btn)

        self.settings_stack.addWidget(widget)

    def showConsole(self):
        Console.show()

    def hideConsole(self):
        if not getattr(sys, 'frozen', False):
            windowAbs.critical(None, lang.Dialogs.impossible, lang.Dialogs.error_debug_hide_console,
                               btn_text=lang.Dialogs.ok, height=140)
            return
        Console.hide()

    def openLauncherFolder(self):
        os.startfile(os.getcwd())

    def openAboutChanges(self):
        dil = AboutDialog(QApplication.activeWindow())
        dil.exec()

    def selectJavaDil(self):
        dil, _ = QFileDialog.getOpenFileName(self, lang.Dialogs.select_java_path, "C:/Program Files/Java/", "exe files (*.exe)")
        if dil:
            settings.put("javaPath", dil)
            self.java_input.setText(dil)
            if self.main:
                self.main.javaPath = dil

    def add_advanced_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.console_checkbox = AnimatedToggle()
        self.console_checkbox.setChecked(settings.get("showConsole", False))
        self.console_checkbox.toggled.connect(self.showConsoleToggle)

        self.javaHelp = QLabel(lang.Dialogs.select_java_path)
        self.java_input = QLineEdit()
        self.java_input.setReadOnly(True)
        self.java_input.setText(str(settings.get("javaPath", "java")))
        self.java_input.setFixedHeight(30)
        self.select_java = QPushButton(lang.Dialogs.select)
        self.select_java.setObjectName("SettingsButton")
        self.select_java.clicked.connect(self.selectJavaDil)
        self.select_java.setFixedHeight(30)
        layout.addRow(self.javaHelp)
        layout.addRow(self.select_java, self.java_input)
        layout.addRow(self.console_checkbox, QLabel(lang.Dialogs.show_console))

        panel_behavior_group = QGroupBox(lang.Dialogs.panel_behavior_group)
        main_layout = QVBoxLayout()

        position_layout = QHBoxLayout()
        self.position_button_group = QButtonGroup()
        self.position_button_group.setExclusive(True)

        btn_on_top = QPushButton(lang.Dialogs.panel_position_on_top)
        btn_on_top.setObjectName("SelectionButton")
        btn_on_top.setCheckable(True)
        self.position_button_group.addButton(btn_on_top, 0)
        position_layout.addWidget(btn_on_top)

        btn_shift = QPushButton(lang.Dialogs.panel_position_shift)
        btn_shift.setObjectName("SelectionButton")
        btn_shift.setCheckable(True)
        self.position_button_group.addButton(btn_shift, 1)
        position_layout.addWidget(btn_shift)

        state_layout = QHBoxLayout()
        self.state_button_group = QButtonGroup()
        self.state_button_group.setExclusive(True)

        btn_standard = QPushButton(lang.Dialogs.panel_state_standard)
        btn_standard.setCheckable(True)
        btn_standard.setObjectName("SelectionButton")
        self.state_button_group.addButton(btn_standard, 0)
        state_layout.addWidget(btn_standard)

        btn_always_expanded = QPushButton(lang.Dialogs.panel_state_always_expanded)
        btn_always_expanded.setObjectName("SelectionButton")
        btn_always_expanded.setCheckable(True)
        self.state_button_group.addButton(btn_always_expanded, 1)
        state_layout.addWidget(btn_always_expanded)

        btn_always_collapsed = QPushButton(lang.Dialogs.panel_state_always_collapsed)
        btn_always_collapsed.setObjectName("SelectionButton")
        btn_always_collapsed.setCheckable(True)
        self.state_button_group.addButton(btn_always_collapsed, 2)
        state_layout.addWidget(btn_always_collapsed)

        self.position_button_group.buttonClicked.connect(self.set_position_behavior)
        self.state_button_group.buttonClicked.connect(self.set_state_behavior)

        main_layout.addLayout(position_layout)
        main_layout.addLayout(state_layout)
        panel_behavior_group.setLayout(main_layout)

        double_click_group = QGroupBox(lang.Dialogs.double_click_behavior_group)
        double_click_layout = QHBoxLayout()
        self.double_click_button_group = QButtonGroup()
        self.double_click_button_group.setExclusive(True)

        btn_launch = QPushButton(lang.Dialogs.double_click_launch)
        btn_launch.setObjectName("SelectionButton")
        btn_launch.setCheckable(True)
        self.double_click_button_group.addButton(btn_launch, 0)
        double_click_layout.addWidget(btn_launch)

        btn_info = QPushButton(lang.Dialogs.double_click_info)
        btn_info.setObjectName("SelectionButton")
        btn_info.setCheckable(True)
        self.double_click_button_group.addButton(btn_info, 1)
        double_click_layout.addWidget(btn_info)

        btn_settings = QPushButton(lang.Dialogs.double_click_settings)
        btn_settings.setObjectName("SelectionButton")
        btn_settings.setCheckable(True)
        self.double_click_button_group.addButton(btn_settings, 2)
        double_click_layout.addWidget(btn_settings)

        self.double_click_button_group.buttonClicked.connect(self.set_double_click_behavior)
        double_click_group.setLayout(double_click_layout)

        double_click_id = settings.get("doubleClickBehavior", 0)
        self.double_click_button_group.button(double_click_id).setChecked(True)

        layout.addRow(double_click_group)

        layout.addRow(panel_behavior_group)

        self.load_button_states()

        self.settings_stack.addWidget(widget)

    def set_double_click_behavior(self, button):
        button_id = self.double_click_button_group.id(button)
        settings.put("doubleClickBehavior", button_id)

    def set_position_behavior(self, button):
        button_id = self.position_button_group.id(button)
        settings.put("panelPositionBehavior", button_id)
        self.main.updatePanelState()

    def set_state_behavior(self, button):
        button_id = self.state_button_group.id(button)
        settings.put("panelEventBehavior", button_id)
        self.main.updatePanelState()

    def load_button_states(self):
        position_id = settings.get("panelPositionBehavior", 0)
        self.position_button_group.button(position_id).setChecked(True)

        state_id = settings.get("panelEventBehavior", 0)
        self.state_button_group.button(state_id).setChecked(True)

    def set_launcher_behavior(self, button):
        button_id = self.launcher_button_group.id(button)
        settings.put("launcherBehavior", button_id)

    def changeValueMemory(self, value):
        self.MemorySlider.blockSignals(True)
        self.MemorySpin.blockSignals(True)
        self.MemorySlider.slider.setValue(value)
        self.MemorySpin.setValue(value)
        self.MemorySlider.blockSignals(False)
        self.MemorySpin.blockSignals(False)

    def add_game_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        memoryS = psutil.virtual_memory()
        memoryV = (memoryS.total / (2 ** 20))
        self.MemorySlider = SliderTicksLables()
        self.MemorySlider.dlsText = lang.Dialogs.memory_suffix
        self.MemorySlider.isLeftOffset = True
        self.MemorySlider.setRange(1000, int(memoryV), 5)
        self.MemorySlider.slider.setValue(settings.get('javaMemory', 1000))
        self.MemorySlider.slider.valueChanged.connect(self.changeValueMemory)

        self.MemorySpin = QSpinBox()
        self.MemorySpin.setRange(1000, int(memoryV))
        self.MemorySpin.setValue(settings.get('javaMemory', 1000))
        self.MemorySpin.valueChanged.connect(self.changeValueMemory)
        self.MemorySpin.setFixedWidth(100)

        launcher_behavior_group = QGroupBox(lang.Dialogs.launcher_behavior_group)
        launcher_layout = QHBoxLayout()
        self.launcher_button_group = QButtonGroup()
        self.launcher_button_group.setExclusive(True)

        btn_hide = QPushButton(lang.Dialogs.launcher_hide_completely)
        btn_hide.setObjectName("SelectionButton")
        btn_hide.setCheckable(True)
        self.launcher_button_group.addButton(btn_hide, 0)
        launcher_layout.addWidget(btn_hide)

        btn_minimize = QPushButton(lang.Dialogs.launcher_minimize_to_taskbar)
        btn_minimize.setObjectName("SelectionButton")
        btn_minimize.setCheckable(True)
        self.launcher_button_group.addButton(btn_minimize, 1)
        launcher_layout.addWidget(btn_minimize)

        btn_nothing = QPushButton(lang.Dialogs.launcher_do_nothing)
        btn_nothing.setObjectName("SelectionButton")
        btn_nothing.setCheckable(True)
        self.launcher_button_group.addButton(btn_nothing, 2)
        launcher_layout.addWidget(btn_nothing)

        self.launcher_button_group.buttonClicked.connect(self.set_launcher_behavior)
        launcher_behavior_group.setLayout(launcher_layout)

        launcher_id = settings.get("launcherBehavior", 0)
        self.launcher_button_group.button(launcher_id).setChecked(True)

        memoryHelp = QLabel(lang.Dialogs.set_java_memory)
        memoryHelp.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        stretch = QLabel()
        stretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        h1 = QHBoxLayout()
        h1.addWidget(self.MemorySlider)
        h1.addWidget(self.MemorySpin)
        layout.addRow(memoryHelp)
        layout.addRow(h1)
        layout.addRow(launcher_behavior_group)
        layout.addRow(stretch)

        self.settings_stack.addWidget(widget)

    def setAboutHtml(self):
        about_info_template = """<!DOCTYPE html>
                <html lang="ru">
                <head>
                  <meta charset="UTF-8" />
                  <meta name="viewport" content="width=device-width, initial-scale=1" />
                  <title>{about_title}</title>
                  <style>
                    body {{
                      margin: 0;
                      background-color: #0f0f0f;
                      color: #ffffff;
                      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                      display: flex;
                      flex-direction: column;
                      align-items: center;
                      padding: 24px;
                      min-height: 100vh;
                    }}
                    .container {{
                      max-width: 768px;
                      width: 100%;
                      padding: 32px 0;
                    }}
                    h1 {{
                      font-size: 1.75rem;
                      font-weight: 600;
                      margin-bottom: 12px;
                      text-align: center;
                      color: #ffffff;
                    }}
                    p.description {{
                      color: #ffffff;
                      text-align: center;
                      margin-bottom: 24px;
                      font-size: 0.9rem;
                    }}
                    h2 {{
                      font-size: 1.125rem;
                      font-weight: 500;
                      margin-bottom: 8px;
                      color: #ffffff;
                    }}
                    ul {{
                      list-style: none;
                      padding-left: 0;
                      margin-top: 0;
                      margin-bottom: 24px;
                      color: #ffffff;
                      font-size: 0.9rem;
                      line-height: 1.5;
                    }}
                    ul li {{
                      margin-bottom: 8px;
                      display: flex;
                      align-items: flex-start;
                      gap: 8px;
                    }}
                    ul li span.key {{
                      min-width: 140px;
                      display: inline-block;
                      font-weight: 600;
                      color: #ffffff;
                    }}
                    .grid {{
                      display: grid;
                      grid-template-columns: 1fr;
                      gap: 24px;
                    }}
                    @media (min-width: 640px) {{
                      .grid {{
                        grid-template-columns: repeat(2, 1fr);
                      }}
                    }}
                    .footer {{
                      padding-top: 12px;
                      margin-top: 24px;
                      font-size: 0.75rem;
                      color: #ffffff;
                      text-align: center;
                    }}
                  </style>
                </head>
                <body>
                  <div class="container">
                    <h1>{about_title}</h1>
                    <p class="description">{description}</p>
                    <div class="grid">
                      <section>
                        <h2>{section_main}</h2>
                        <ul>
                          <li><span class="key">{lang_impl}</span> Python</li>
                          <li><span class="key">{version}</span> v{slv}.{updv}</li>
                          <li><span class="key">{auto_update}</span> {update_value}</li>
                        </ul>
                      </section>
                      <section>
                        <h2>{section_platforms}</h2>
                        <ul>
                          {platforms_html}
                        </ul>
                      </section>
                      <footer class="footer">
                        {build_date}<br />
                        {bug_report}
                      </footer>
                    </div>
                  </div>
                </body>
                </html>"""
        platforms_html = '\n'.join(f'<li>{p}</li>' for p in lang.Elements.platforms)
        about_info = about_info_template.format(
            about_title=lang.Elements.about_title,
            header=lang.Elements.header,
            description=lang.Elements.description,
            section_main=lang.Elements.section_main,
            lang_impl=lang.Elements.lang_impl,
            version=lang.Elements.version,
            auto_update=lang.Elements.auto_update if settings.get("autoUpdate", True) else lang.Elements.off_auto_update,
            update_value=lang.Elements.update_value,
            platforms_html=platforms_html,
            section_platforms=lang.Elements.section_platforms,
            section_interface=lang.Elements.section_interface,
            build_date=lang.Elements.build_date.format(build_date=build_info.BUILD_DATE),
            bug_report=lang.Elements.bug_report,
            updv=UPDATER_VERSION,
            slv=THIS_VERSION
        )
        self.about_text.setHtml(about_info)

    def add_about_info(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.about_text = QTextBrowser()
        self.about_text.setReadOnly(True)
        self.setAboutHtml()
        layout.addWidget(self.about_text)
        self.settings_stack.addWidget(widget)