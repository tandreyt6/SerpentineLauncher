print("import libs...")
import logging
import os
import json
import sys
import traceback
from datetime import datetime

from PyQt6.QtGui import QIcon

from UI.windows import windowAbs
from func import settings, ArgsParser
from UI import translate
import win32gui, win32con

from UI.elements import HtmlViewer

from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

print("Check settings...")
isSettingsExist = settings.load()
if not isSettingsExist:
    q = windowAbs.question(None, "", "Use Russian language in the launcher?\nИспользовать русский язык в лаунчере?", height=150,
                           yes_text="Yes/Да", no_text="No/Нет")
    settings.put("lang", "ru" if q else "en")
if settings.get('lang', 'ru') == "en":
    translate.lang = translate.EN
else:
    translate.lang = translate.RU

HtmlViewer.lang = translate.lang

from UI.Style import dark_style
from UI.windows.Launcher import Window
from func.installer import MinecraftInstaller, FabricInstaller, ForgeInstaller, QuiltInstaller
import minecraft_launcher_lib
from func import memory, ArgsActions
from localLauncher import SingleInstance

import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

print("Loading launcher...")

console_window = ctypes.windll.kernel32.GetConsoleWindow()

class ErrorOnlyFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        self.has_errors = False
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.has_errors = True
            super().emit(record)

    def close(self):
        if not self.has_errors:
            super().close()
            if os.path.exists(self.baseFilename) and os.path.getsize(self.baseFilename) == 0:
                os.remove(self.baseFilename)
        else:
            super().close()


def get_log_filename(base_name="viper_errors"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("./logs/", exist_ok=True)
    log_file = f"./logs/{base_name}.log"

    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        log_file = f"./logs/{base_name}_{timestamp}.log"

    return log_file

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

handler = ErrorOnlyFileHandler(get_log_filename())
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def log_exception(exc_type, exc_value, exc_traceback):
    logger.error(
        "Exception Error:\n%s",
        ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )

sys.excepthook = log_exception

def bring_window_foreground(hwnd):
    SW_RESTORE = 9
    if user32.IsIconic(hwnd): user32.ShowWindow(hwnd, SW_RESTORE)
    fg = user32.GetForegroundWindow()
    if fg == hwnd: return True
    tid_fg = user32.GetWindowThreadProcessId(fg, None)
    tid_target = user32.GetWindowThreadProcessId(hwnd, None)
    attached = user32.AttachThreadInput(tid_fg, tid_target, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    if attached: user32.AttachThreadInput(tid_fg, tid_target, False)
    timeout = ctypes.c_int()
    SPI_GET = 0x2000
    SPI_SET = 0x2001
    SPIF = 2
    user32.SystemParametersInfoW(SPI_GET, 0, ctypes.byref(timeout), 0)
    user32.SystemParametersInfoW(SPI_SET, 0, ctypes.byref(ctypes.c_int(0)), SPIF)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.SystemParametersInfoW(SPI_SET, 0, ctypes.byref(timeout), SPIF)
    return user32.GetForegroundWindow() == hwnd

class Main:
    def __init__(self):
        self._nickname = None
        core_versions = {
            "Vanilla": {},
            "Forge": {},
            "Fabric": {"default": []},
            "Quilt": {"default": []}
        }

        try:
            minecraft_versions = [v['id'] for v in MinecraftInstaller.list_versions(onlyRelease=True)]

            forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
            for version in forge_versions:
                parts = version.split("-")
                if len(parts) >= 2:
                    mc_version = parts[0]
                    forge_version = "-".join(parts[1:]).replace("forge-", "")
                    if mc_version not in core_versions["Forge"]:
                        core_versions["Forge"][mc_version] = []
                    core_versions["Forge"][mc_version].append(forge_version)
                else:
                    print(f"Forge version skipped: {version} (incorrect format)")

            fabric_loaders = []
            for v in FabricInstaller.list_versions(onlyStable=True):
                if isinstance(v, dict):
                    if 'loader' in v and 'version' in v['loader']:
                        fabric_loaders.append(v['loader']['version'])
                    elif 'version' in v:
                        fabric_loaders.append(v['version'])
                    else:
                        print(f"Fabric version skipped: {v} (incorrect format)")
                else:
                    print(f"Skipped the Fabric version: {v} (not a dictionary)")
            core_versions["Fabric"]["default"] = fabric_loaders

            quilt_loaders = []
            for v in QuiltInstaller.list_versions():
                if isinstance(v, dict) and 'version' in v:
                    quilt_loaders.append(v['version'])
                else:
                    print(f"Quilt version skipped: {v} (incorrect format)")
            core_versions["Quilt"]["default"] = quilt_loaders

        except Exception as e:
            print(f"Error getting versions: {e}")
            installed_versions = minecraft_launcher_lib.utils.get_installed_versions("./minecraft/")
            minecraft_versions = [v['id'] for v in installed_versions]
            for version in installed_versions:
                version_id = version['id']
                if "forge" in version_id:
                    parts = version_id.split("-forge-")
                    if len(parts) == 2:
                        mc_version, forge_version = parts
                        if mc_version not in core_versions["Forge"]:
                            core_versions["Forge"][mc_version] = []
                        core_versions["Forge"][mc_version].append(forge_version)
                    else:
                        print(f"The installed Forge version is missing: {version_id} (invalid format)")
                elif "fabric-loader" in version_id:
                    parts = version_id.split("-")
                    if len(parts) == 3:
                        _, loader_version, mc_version = parts
                        core_versions["Fabric"]["default"].append(loader_version)
                    else:
                        print(f"Skipped Fabric version: {version_id} (invalid format)")
                elif "quilt-loader" in version_id:
                    parts = version_id.split("-")
                    if len(parts) == 3:
                        _, loader_version, mc_version = parts
                        core_versions["Quilt"]["default"].append(loader_version)
                    else:
                        print(f"Skipped Quilt version: {version_id} (invalid format)")

        core_types = ["Vanilla", "Forge", "Fabric", "Quilt"]

        memory.put("minecraft_versions", minecraft_versions)
        memory.put("core_types", core_types)
        memory.put("core_versions", core_versions)

        self.launcherWindow = Window(self)
        self.launcherWindow.setWindowTitle("Serpentine Launcher")

    def getActivName(self) -> str:
        return self._nickname

    def setActiveName(self, name: str) -> None:
        self._nickname = name


app.setApplicationName("SerpentineLauncher")

instance = SingleInstance("minecraft_launcher_v2_key_server", json.dumps(ArgsParser.msg))

if instance.is_running() or ArgsParser.msg.get('nostart'):
    print("App is running...\nexecute window...")
    sys.exit(0)

if sys.platform == "win32" and getattr(sys, 'frozen', False) and not ArgsParser.msg['debug']:
    if console_window:
        win32gui.ShowWindow(console_window, win32con.SW_HIDE)

ArgsActions.check()

def handle_message(msg):
    data = json.loads(msg)
    if not ArgsParser.msg.get('nogui') and win.launcherWindow.builds_page.canCloseLauncherWithBuild:
        win.launcherWindow.builds_page.canCloseLauncherWithBuild = False
    if not data.get('nogui'):
        win.launcherWindow.showNormal()
        win.launcherWindow.raise_()
        win.launcherWindow.activateWindow()
        hwnd = int(win.launcherWindow.winId())
        bring_window_foreground(hwnd)
    if data.get('swbn'):
        win.launcherWindow.builds_page.launch_build_by_name(data['swbn'], data.get('nogui'))
    if data.get('MCClose'):
        win.launcherWindow.builds_page.stop_build(data.get('MCClose'), nogui=data.get('nogui'))
    if data.get('instcore') and not data.get('nogui'):
        build = {'core_version': data.get('instcore')[1], 'core_type': data.get('instcore')[0], 'minecraft': data.get('instcore')[2]}
        win.launcherWindow.builds_page.install_core(build, nogui=data.get('nogui'))


instance.message_received.connect(handle_message)

print("Init UI...")
win = Main()

app.setWindowIcon(QIcon(":Minecraft.png"))
app.setStyleSheet(dark_style)

win.launcherWindow.builds_page.canCloseLauncherWithBuild = ArgsParser.msg.get('nogui')

handle_message(json.dumps(ArgsParser.msg))

if not isSettingsExist:
    q = windowAbs.question(win.launcherWindow, "", translate.lang.Dialogs.about_changes_question, height=150,
                           yes_text=translate.lang.Dialogs.yes, no_text=translate.lang.Dialogs.no)
    if q:
        dil = HtmlViewer.AboutDialog(win.launcherWindow)
        dil.exec()

app.exec()
