import ctypes
import time
from ctypes import wintypes

import win32gui

buf = ctypes.create_unicode_buffer(1024)
ctypes.windll.kernel32.GetConsoleTitleW(buf, 1024)
old_title = buf.value

unique = f"SERPENTINE_LAUNCHER_CONSOLE_{time.time()}"
ctypes.windll.kernel32.SetConsoleTitleW(ctypes.c_wchar_p(unique))
time.sleep(0.1)

HWND_CONSOLE = ctypes.windll.user32.FindWindowW(None, ctypes.c_wchar_p(unique))

user32 = ctypes.windll.user32

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL

def isVisible() -> bool:
    return bool(IsWindowVisible(HWND_CONSOLE))

def hide():
    ctypes.windll.user32.ShowWindow(HWND_CONSOLE, 0)

def show():
    ctypes.windll.user32.ShowWindow(HWND_CONSOLE, 5)
    ctypes.windll.user32.ShowWindow(HWND_CONSOLE, 9)

def minimize():
    ctypes.windll.user32.ShowWindow(HWND_CONSOLE, 2)