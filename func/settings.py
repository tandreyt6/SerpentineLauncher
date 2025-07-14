import json
import os

data = {}

def load(path: str = "settings.json") -> bool:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data.clear()
            data.update(json.load(f))
    return os.path.exists(path)

def save(path: str = "settings.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def put(key: str, value):
    data[key] = value
    save()

def get(key: str, default=None):
    return data.get(key, default)

