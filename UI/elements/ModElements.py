import json
import os
import shutil
import zipfile
from io import BytesIO

import toml
from PIL import Image
from PyQt6.QtCore import Qt, QByteArray, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QPlainTextEdit, QSizePolicy, QLabel, QPushButton, \
    QScrollArea, QMessageBox

from UI.elements.buttons import AnimatedToggle


class ModWidget(QFrame):
    def __init__(self, mod_name, mod_path, toggle_callback, delete_callback, expand_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("mod_frame")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(90)

        self.mod_path = mod_path
        self.toggle_callback = toggle_callback
        self.delete_callback = delete_callback
        self.expand_callback = expand_callback

        v = QVBoxLayout(self)

        panel = QWidget()
        panel.setFixedHeight(70)
        layout = QHBoxLayout(panel)
        v.addWidget(panel)
        v.addStretch()

        self.descript_label = QPlainTextEdit()
        self.descript_label.setObjectName("TextPlain")
        self.descript_label.setReadOnly(True)
        self.descript_label.setFixedHeight(0)
        self.descript_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v.addWidget(self.descript_label)

        self.icon_label = QLabel(self)
        layout.addWidget(self.icon_label)

        self.mod_label = QLabel(mod_name)
        self.mod_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.mod_label)

        layout.addStretch()

        self.toggle_checkbox = AnimatedToggle()
        self.toggle_checkbox.setChecked(not mod_path.endswith(".disabled"))
        self.toggle_checkbox.toggled.connect(self.on_toggle)
        layout.addWidget(self.toggle_checkbox)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setFixedWidth(55)
        layout.addWidget(self.delete_button)

        self.openBtn = QPushButton("...")
        self.openBtn.setFixedWidth(30)
        self.openBtn.clicked.connect(self.on_click)
        layout.addWidget(self.openBtn)
        try:
            mod_info = get_mod_info(mod_path)
            # print(mod_info)
            self.mod_label.setText(mod_info.get("name", mod_name))
            self.descript_label.setPlainText(mod_info.get("description", "No description"))
            if 'icon_data' in mod_info and mod_info['icon_data']:
                icon_data = mod_info['icon_data']
                icon_image = Image.open(BytesIO(icon_data))
                buffer = BytesIO()
                icon_image.save(buffer, format="PNG")
                buffer.seek(0)
                byte_array = QByteArray(buffer.read())
                icon_pixmap = QPixmap()
                icon_pixmap.loadFromData(byte_array)
                max_size = 64
                original_width = icon_pixmap.width()
                original_height = icon_pixmap.height()
                if original_width > original_height:
                    scale_factor = max_size / original_width
                    scaled_width = max_size
                    scaled_height = int(original_height * scale_factor)
                else:
                    scale_factor = max_size / original_height
                    scaled_height = max_size
                    scaled_width = int(original_width * scale_factor)
                print(scaled_height, scaled_width)
                assert icon_pixmap is not None, "icon_pixmap is None"
                assert not icon_pixmap.isNull(), "icon_pixmap is null"
                assert scaled_width > 0 and scaled_height > 0, "Width and height must be positive"
                icon_pixmap = icon_pixmap.scaled(
                    scaled_width, scaled_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                print(1)
                self.icon_label.setPixmap(icon_pixmap)
            else:
                self.icon_label.setFixedWidth(64)
        except:
            pass

    def on_toggle(self, checked):
        self.toggle_callback(checked, self.mod_path, self)

    def on_delete(self):
        self.delete_callback(self.mod_path, self)

    def on_click(self):
        self.expand_callback(self)

    def mousePressEvent(self, a0):
        self.on_click()
        return super().mousePressEvent(a0)


def get_mod_info(jar_file_path):
    with zipfile.ZipFile(jar_file_path, 'r') as jar:
        if 'fabric.mod.json' in jar.namelist():
            core = 'Fabric'
            info_file = 'fabric.mod.json'
        elif 'quilt.mod.json' in jar.namelist():
            core = 'Quilt'
            info_file = 'quilt.mod.json'
        elif 'META-INF/mods.toml' in jar.namelist():
            core = 'Forge'
            info_file = 'META-INF/mods.toml'
        else:
            return {"error": "Unknown mod type"}

        with jar.open(info_file) as file:
            if core in ['Fabric', 'Quilt']:
                mod_info = json.load(file)
                name = mod_info.get('name', 'Unknown')
                description = mod_info.get('description', 'No description')
                authors = mod_info.get('authors', 'Unknown')
                contact = mod_info.get('contact', {})
                icon_path = mod_info.get('icon')
            elif core == 'Forge':
                content = file.read().decode('utf-8')
                mod_info = toml.loads(content)
                mod = mod_info['mods'][0]
                name = mod.get('displayName', 'Unknown')
                description = mod.get('description', 'No description')
                authors = mod.get('authors', 'Unknown')
                contact = {}
                if 'issueTrackerURL' in mod:
                    contact['issueTrackerURL'] = mod['issueTrackerURL']
                icon_path = mod.get('logoFile')

        icon_data = None
        if icon_path and icon_path in jar.namelist():
            with jar.open(icon_path) as icon_file:
                icon_data = icon_file.read()

        return {
            "core": core,
            "name": name,
            "description": description,
            "authors": authors,
            "contact": contact,
            "icon_data": icon_data,
        }


