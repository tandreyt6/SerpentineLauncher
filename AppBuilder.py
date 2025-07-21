import os
import subprocess
from datetime import datetime

script_dir = os.path.abspath(os.path.dirname(__file__))

os.chdir(script_dir)


build_date = datetime.now().strftime("%Y-%m-%d")
with open("build_info.py", "w", encoding="utf-8") as f:
    f.write(f'BUILD_DATE = "{build_date}"\nBUILD_NAME = "SerpentineLauncher"\nBUILD_VERSION = "2"')

print(f"[INFO] Build data: {build_date} -> build_info.py")

pyinstaller_path = rf"{os.getcwd()}\.venv\Scripts\pyinstaller.exe"
pyinstaller_cmd = [
    pyinstaller_path,
    "main.py",
    "-i", "icon.ico",
    "--name=\"SerpentineLauncher\"",
    "--noconfirm"
]

updater_cmd = [
    pyinstaller_path,
    "func/GitUpdater.py",
    "--icon=\"icon.ico\"",
    "--name=\"updater\"",
    "-F",
]

print("[INFO] Start PyInstaller...")
result = os.system(" ".join(pyinstaller_cmd))
result2 = os.system(" ".join(updater_cmd))