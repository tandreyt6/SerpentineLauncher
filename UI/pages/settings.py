import ctypes
import os
import psutil
import win32con
import win32gui
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys

from UI.elements.HtmlViewer import AboutDialog
from UI.elements.TextSlider import SliderTicksLables
from UI.elements.buttons import AnimatedToggle
from UI.windows import windowAbs
from func import settings, memory
from UI.translate import lang

CONSOLE_WINDOW = ctypes.windll.kernel32.GetConsoleWindow()

class SettingsWidget(QWidget):
    def __init__(self, parent=None, css="", settings={}, main=None):
        super().__init__(parent)
        self.java_input: QLineEdit = None
        self.setStyleSheet(css)
        self.css = css
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

    def create_tab_button(self, name, layout):
        button = QPushButton(name)
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

        h0 = QHBoxLayout()
        self.show_console = QPushButton(lang.Elements.show_console)
        self.show_console.clicked.connect(self.showConsole)
        h0.addWidget(self.show_console)
        self.hide_console = QPushButton(lang.Elements.hide_console)
        self.hide_console.clicked.connect(self.hideConsole)
        h0.addWidget(self.hide_console)
        layout.addRow(h0)

        self.open_launcher_folder = QPushButton(lang.Elements.open_launcher_folder)
        self.open_launcher_folder.clicked.connect(self.openLauncherFolder)
        layout.addRow(self.open_launcher_folder)

        self.about_changes_btn = QPushButton(lang.Elements.about_changes_title)
        self.about_changes_btn.clicked.connect(self.openAboutChanges)
        layout.addRow(self.about_changes_btn)

        self.settings_stack.addWidget(widget)

    def showConsole(self):
        if CONSOLE_WINDOW:
            win32gui.ShowWindow(CONSOLE_WINDOW, win32con.SW_SHOW)

    def hideConsole(self):
        if not getattr(sys, 'frozen', False):
            windowAbs.critical(None, lang.Dialogs.impossible, lang.Dialogs.error_debug_hide_console,
                               btn_text=lang.Dialogs.ok, height=140)
            return
        if CONSOLE_WINDOW:
            win32gui.ShowWindow(CONSOLE_WINDOW, win32con.SW_HIDE)

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
        btn_on_top.setCheckable(True)
        self.position_button_group.addButton(btn_on_top, 0)
        position_layout.addWidget(btn_on_top)

        btn_shift = QPushButton(lang.Dialogs.panel_position_shift)
        btn_shift.setCheckable(True)
        self.position_button_group.addButton(btn_shift, 1)
        position_layout.addWidget(btn_shift)

        state_layout = QHBoxLayout()
        self.state_button_group = QButtonGroup()
        self.state_button_group.setExclusive(True)

        btn_standard = QPushButton(lang.Dialogs.panel_state_standard)
        btn_standard.setCheckable(True)
        self.state_button_group.addButton(btn_standard, 0)
        state_layout.addWidget(btn_standard)

        btn_always_expanded = QPushButton(lang.Dialogs.panel_state_always_expanded)
        btn_always_expanded.setCheckable(True)
        self.state_button_group.addButton(btn_always_expanded, 1)
        state_layout.addWidget(btn_always_expanded)

        btn_always_collapsed = QPushButton(lang.Dialogs.panel_state_always_collapsed)
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
        btn_launch.setCheckable(True)
        self.double_click_button_group.addButton(btn_launch, 0)
        double_click_layout.addWidget(btn_launch)

        btn_info = QPushButton(lang.Dialogs.double_click_info)
        btn_info.setCheckable(True)
        self.double_click_button_group.addButton(btn_info, 1)
        double_click_layout.addWidget(btn_info)

        btn_settings = QPushButton(lang.Dialogs.double_click_settings)
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
        self.MemorySlider.slider.setStyleSheet(self.css)
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
        btn_hide.setCheckable(True)
        self.launcher_button_group.addButton(btn_hide, 0)
        launcher_layout.addWidget(btn_hide)

        btn_minimize = QPushButton(lang.Dialogs.launcher_minimize_to_taskbar)
        btn_minimize.setCheckable(True)
        self.launcher_button_group.addButton(btn_minimize, 1)
        launcher_layout.addWidget(btn_minimize)

        btn_nothing = QPushButton(lang.Dialogs.launcher_do_nothing)
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

    def add_about_info(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.about_text = QTextBrowser()
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet(self.css)
        about_info = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 8pt;
            color: #E0E0E0;
            background-color: #1E1E1E;
            margin: 0;
            padding: 10px;
        }}
        .container {{
            max-width: 300px;
            margin: 0 auto;
            background-color: #252526;
            border: 1px solid #3F3F46;
            border-radius: 6px;
            padding: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            padding-bottom: 8px;
            border-bottom: 1px solid #3F3F46;
        }}
        h1 {{
            font-size: 14px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 0;
        }}
        .version {{
            font-size: 9pt;
            color: #A0A0A0;
            margin: 4px 0;
        }}
        .author {{
            font-size: 10pt;
            font-weight: bold;
            color: #0078D7;
            transition: color 0.3s ease;
        }}
        .author:hover {{
            color: #1C97EA;
        }}
        .content {{
            margin-top: 8px;
        }}
        .info-block {{
            background-color: #3F3F46;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 8px;
            transition: transform 0.2s ease;
        }}
        .info-block:hover {{
            transform: translateY(-1px);
        }}
        .info-block p {{
            margin: 0;
            line-height: 1.4;
            font-size: 8pt;
            color: #E0E0E0;
        }}
        .highlight {{
            background-color: #0078D7;
            color: #FFFFFF;
            padding: 6px;
            border-radius: 4px;
            font-weight: bold;
            margin: 8px 0;
            transition: background-color 0.3s ease;
        }}
        .highlight:hover {{
            background-color: #1C97EA;
        }}
        .footer {{
            text-align: center;
            font-size: 7pt;
            color: #A0A0A0;
            padding-top: 8px;
            border-top: 1px solid #3F3F46;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{lang.Dialogs.about_title}</h1>
            <div class="version">{lang.Dialogs.about_version}</div>
            <div class="author">{lang.Dialogs.about_author}</div>
        </div>
        <div class="content">
            <div class="info-block">
                <p>{lang.Dialogs.about_description}</p>
            </div>
            <div class="info-block">
                <p class="highlight">{lang.Dialogs.about_new_in_version}</p>
                <p>{lang.Dialogs.about_new_features}</p>
            </div>
        </div>
        <div class="footer">{lang.Dialogs.about_copyright}</div>
    </div>
</body>
</html>"""

        self.about_text.setHtml(about_info)
        layout.addWidget(self.about_text)
        self.settings_stack.addWidget(widget)