import argparse
import ctypes
import os
import signal
import sys
import time
import zipfile
import shutil
from argparse import ArgumentError
from ctypes import wintypes

import requests
import subprocess

REPO = "tandreyt6/SerpentineLauncher"
UPDATER_VERSION = "1"


def get_latest_release_tag(timeout=5) -> str | None:
    url = f"https://api.github.com/repos/{REPO}/releases"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        releases = response.json()
        for release in releases:
            if release.get("draft"):
                continue
            tag = release.get("tag_name", "")
            if tag.startswith("v"):
                return tag
        return None
    except Exception:
        return None


def get_latest_release_notes() -> str | None:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        release = response.json()
        if release.get("draft"):
            return None
        return release.get("body", "").strip() or None
    except Exception:
        return None


def print_progress_bar(iteration, total, length=40):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f"\rDownloading: |{bar}| {percent}% ", end='\r')
    if iteration >= total:
        print()


def download_with_progress(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('Content-Length', 0))
        with open(path, 'wb') as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print_progress_bar(downloaded, total)


def download_updater_exe(version: str, path: str = "updater.exe"):
    url = f"https://github.com/{REPO}/releases/download/v{version}/updater.exe"
    download_with_progress(url, path)


def get_latest_release_tag_for_launcher_version(launcher_version):
    url = f"https://api.github.com/repos/{REPO}/releases"
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()
    print(url, releases)
    filtered = []
    for release in releases:
        if release.get("draft"):
            continue
        tag = release.get("tag_name", "")
        print(tag, launcher_version)
        if not tag.startswith("v"):
            continue
        try:
            x_str, y_str = tag[1:].split(".")
            y = int(y_str)
            filtered.append((y, tag, release))
        except Exception:
            continue

    if not filtered:
        return None, None

    filtered.sort(key=lambda t: t[0], reverse=True)
    return filtered[0][1], filtered[0][2]


def get_zip_root_items(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        items = set()
        for name in zipf.namelist():
            parts = name.strip("/").split("/", 1)
            if parts:
                items.add(parts[0])
        return list(items)


def extract_zip(zip_path, to_path="."):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(to_path)


def restart_launcher():
    launcher_exe = "SerpentineLauncher.exe"
    subprocess.Popen([launcher_exe, "--with-update"], creationflags=subprocess.CREATE_NEW_CONSOLE )

def parse_args():
    parser = argparse.ArgumentParser(description="Updater for Serpentine Launcher")
    parser.add_argument("launcher_version", type=int, help="Current launcher major version")
    parser.add_argument("--pid", type=int, default=-1, help="Current launcher major version")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading update.zip")
    parser.add_argument("--no-start", action="store_true", help="No start launcher")
    parser.add_argument("-v", "--version", action="store_true", help="Print updater version and exit")
    return parser.parse_args()


def isProcessAlive(pid: int) -> bool:
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if handle:
        exit_code = wintypes.DWORD()
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return exit_code.value == 259
    return False


def main():
    args = parse_args()
    if args.version:
        print(UPDATER_VERSION, end="")
        sys.exit(0)
    print(args.pid)

    if not isProcessAlive(args.pid):
        raise ArgumentError("To install the update, you must transfer the PID of the Active launcher process.")
    os.kill(args.pid, signal.SIGILL)

    if args.skip_download:
        zip_path = "update.zip"
        if not os.path.exists(zip_path):
            print("update.zip not found, skipping")
            sys.exit(0)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if zipf.testzip() is not None:
                    raise zipfile.BadZipFile
        except Exception:
            print("update.zip is not valid")
            sys.exit(1)

        print("Applying existing update.zip...")
        roots = get_zip_root_items(zip_path)
        extract_zip(zip_path)
        os.remove(zip_path)

        print("Update applied. Restarting launcher...")
        if not args.no_start:
            restart_launcher()
        return

    print(f"Looking for updates for launcher version {args.launcher_version}...")

    tag, release = get_latest_release_tag_for_launcher_version(args.launcher_version)
    if tag is None:
        print(f"No releases found for launcher version {args.launcher_version}")
        sys.exit(0)

    print(f"Latest release for launcher version {args.launcher_version}: {tag}")

    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
    if "update.zip" not in assets:
        print("update.zip not found in release assets")
        sys.exit(1)

    zip_url = assets["update.zip"]
    zip_path = "update.zip"

    print(f"Downloading update.zip from {zip_url}...")
    download_with_progress(zip_url, zip_path)

    print("Applying update...")
    extract_zip(zip_path)
    os.remove(zip_path)

    print("Update applied. Restarting launcher...")
    if not args.no_start:
        restart_launcher()


if __name__ == "__main__":
    main()
