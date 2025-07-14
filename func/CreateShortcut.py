import os
import sys
import win32com.client

def create_shortcut(target_path, shortcut_path, icon_path=None, arguments=""):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    if icon_path:
        shortcut.IconLocation = icon_path.replace("/", "\\")
        print(shortcut.IconLocation)
    shortcut.Save()