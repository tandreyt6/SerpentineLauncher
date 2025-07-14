import os
import sys
import time
import zipfile
import shutil
import requests
import subprocess

REPO = "tandreyt6/SerpentineLauncher"


def get_latest_release_tag() -> str | None:
    url = f"https://api.github.com/repos/{REPO}/releases"
    try:
        response = requests.get(url, timeout=5)
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

def get_latest_release_tag_for_launcher_version(launcher_version):
    url = f"https://api.github.com/repos/{REPO}/releases"
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()

    filtered = []
    for release in releases:
        if release.get("draft"):
            continue
        tag = release.get("tag_name", "")
        if not tag.startswith("v"):
            continue
        try:
            x_str, y_str = tag[1:].split(".")
            x = int(x_str)
            y = int(y_str)
            if x == launcher_version:
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

def remove_existing(items):
    for item in items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
            else:
                os.remove(item)

def extract_zip(zip_path, to_path="."):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(to_path)

def restart_launcher():
    launcher_exe = "main.exe"
    if not os.path.exists(launcher_exe):
        launcher_exe = "main.py"
    if launcher_exe.endswith(".exe"):
        subprocess.Popen([launcher_exe, "--with-update"])
    else:
        subprocess.Popen([sys.executable, launcher_exe, "--with-update"])

def main():
    if len(sys.argv) < 2:
        print("Missing launcher version argument")
        sys.exit(1)

    try:
        launcher_version = int(sys.argv[1])
    except ValueError:
        print("Launcher version must be an integer")
        sys.exit(1)

    print(f"Looking for updates for launcher version {launcher_version}...")

    tag, release = get_latest_release_tag_for_launcher_version(launcher_version)
    if tag is None:
        print(f"No releases found for launcher version {launcher_version}")
        sys.exit(0)

    print(f"Latest release for launcher version {launcher_version}: {tag}")

    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
    if "update.zip" not in assets:
        print("update.zip not found in release assets")
        sys.exit(1)

    zip_url = assets["update.zip"]
    zip_path = "update.zip"

    print(f"Downloading update.zip from {zip_url}...")
    download_with_progress(zip_url, zip_path)

    print("Applying update...")
    roots = get_zip_root_items(zip_path)
    remove_existing(roots)
    extract_zip(zip_path)
    os.remove(zip_path)

    print("Update applied. Restarting launcher...")
    restart_launcher()

if __name__ == "__main__":
    main()
