from PyQt6.QtWidgets import QMessageBox
import json
import os
import shutil
import unicodedata
import re

def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '_', value)
    return value

class BuildManager:
    def __init__(self, minecraft_versions, core_types, core_versions, builds_dir='./builds/'):
        self.builds_dir = builds_dir
        self.builds = []
        self.minecraft_versions = minecraft_versions
        self.core_types = core_types
        self.core_versions = core_versions
        self.load_builds()

    def get_minecraft_versions(self):
        return self.minecraft_versions

    def get_core_types(self):
        return self.core_types

    def get_build_path(self, build: dict | str):
        if isinstance(build, dict):
            slug_name = slugify(build['name'])
        else:
            if build in [_['name'] for _ in self.builds]:
                slug_name = slugify(build)
            else: return None
        return os.path.abspath(os.path.join(self.builds_dir, slug_name))

    def get_core_versions(self, core_type, minecraft_version=None):
        core_versions = self.core_versions.get(core_type, {})
        if core_type == "Vanilla":
            return [minecraft_version] if minecraft_version else []
        elif core_type in ["Fabric", "Quilt"]:
            return core_versions.get('default', [])
        else:
            return core_versions.get(minecraft_version, [])

    def load_builds(self):
        if not os.path.exists(self.builds_dir):
            os.makedirs(self.builds_dir)

        self.builds = []
        for subdir in os.listdir(self.builds_dir):
            build_dir = os.path.join(self.builds_dir, subdir)
            if os.path.isdir(build_dir):
                build_file = os.path.join(build_dir, 'build.json')
                if os.path.exists(build_file):
                    try:
                        with open(build_file, 'r', encoding='utf-8') as f:
                            build = json.load(f)
                            self.builds.append(build)
                    except Exception as e:
                        print(f"Error loading build {subdir}: {e}")

    def get_build(self, name):
        for build in self.builds:
            if build['name'] == name:
                return build.copy()
        return None

    def get_all_builds(self):
        return [build.copy() for build in self.builds]

    def create_build(self, build_data):
        name = build_data['name'].strip()
        slug_name = slugify(name)

        build_dir = os.path.join(self.builds_dir, slug_name)
        if os.path.exists(build_dir):
            raise ValueError("An assembly with the same name already exists")

        build = {
            "name": name,
            "description": build_data.get('description', "<h2>A Minecraft build.</h2>"),
            "minecraft": build_data['minecraft'],
            "core_type": build_data['core_type'],
            "core_version": build_data['core_version'],
            "active": False,
        }

        os.makedirs(build_dir, exist_ok=True)
        build_file = os.path.join(build_dir, 'build.json')
        with open(build_file, 'w', encoding='utf-8') as f:
            json.dump(build, f, indent=2, ensure_ascii=False)

        self.builds.append(build)
        return build

    def update_build(self, updated_build):
        for i, build in enumerate(self.builds):
            if build['name'] == updated_build['name']:
                old_slug = slugify(build['name'])
                new_slug = slugify(updated_build['name'])
                if old_slug != new_slug:
                    old_dir = os.path.join(self.builds_dir, old_slug)
                    new_dir = os.path.join(self.builds_dir, new_slug)
                    if os.path.exists(old_dir):
                        os.rename(old_dir, new_dir)
                self.builds[i] = updated_build.copy()
                build_dir = os.path.join(self.builds_dir, new_slug)
                build_file = os.path.join(build_dir, 'build.json')
                with open(build_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_build, f, indent=2, ensure_ascii=False)
                return True
        return False

    def delete_build(self, name):
        build = self.get_build(name)
        if not build:
            return False

        build_dir = os.path.join(self.builds_dir, slugify(name))
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        self.builds = [b for b in self.builds if b['name'] != name]
        return True