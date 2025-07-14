import os
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QComboBox, QProgressBar, QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QRunnable, QThreadPool, QVariantAnimation, \
    QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap
from pyrinth.projects import Project
from pyrinth.teams import Team
import pyrinth.exceptions as exceptions
import func.memory as memory
from UI.Style import DARK_STYLESHEET
from UI.elements.ModElements import ModWidget
from UI.translate import lang
from UI.windows import windowAbs


class IconLoaderSignals(QObject):
    finished = pyqtSignal(QListWidgetItem, QIcon)

class IconLoader(QRunnable):
    def __init__(self, item, url):
        super().__init__()
        self.item = item
        self.url = url
        self.signals = IconLoaderSignals()

    def run(self):
        import requests
        try:
            data = requests.get(self.url, timeout=5).content
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            icon = QIcon(pixmap.scaled(32, 32))
            self.signals.finished.emit(self.item, icon)
        except Exception:
            self.signals.finished.emit(self.item, QIcon())

class SearchWorker(QObject):
    finished = pyqtSignal(list, str)  # (hits, error_message)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        import requests
        try:
            url = "https://api.modrinth.com/v2/search"
            params = {"query": self.query, "index": "downloads", "limit": 30}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            self.finished.emit(hits, "")
        except Exception as e:
            self.finished.emit([], str(e))

class ModsDownloaderThread(QThread):
    progress_changed = pyqtSignal(str, int)
    mod_downloaded = pyqtSignal(str)
    all_finished = pyqtSignal()

    def __init__(self, mods_list, build_manager, build):
        super().__init__()
        self.mods_list = mods_list
        self.build_manager = build_manager
        self.build = build
        self._is_interrupted = False

    def run(self):
        build_dir = self.build_manager.get_build_path(self.build)
        mods_dir = os.path.join(build_dir, "mods")
        os.makedirs(mods_dir, exist_ok=True)

        for project in self.mods_list:
            if self._is_interrupted:
                break
            try:
                minecraft_version = self.build['minecraft']
                versions = project.get_versions(game_versions=[minecraft_version])
                if not versions:
                    continue
                version = versions[0]
                files = version.get_files()
                if not files:
                    continue
                file = files[0]

                download_url = file.url
                filename = file.name
                mod_path = os.path.join(mods_dir, filename)

                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    total_length = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    with open(mod_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if self._is_interrupted:
                                break
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                percent = int(downloaded * 100 / total_length) if total_length > 0 else 0
                                self.progress_changed.emit(project.id, percent)
                self.mod_downloaded.emit(project.id)
            except Exception as e:
                pass

        self.all_finished.emit()

    def interrupt(self):
        self._is_interrupted = True

class ProjectCheckWorker(QObject):
    finished = pyqtSignal(QListWidgetItem, bool, str)  # (item, supported, reason)

    def __init__(self, project_id, mc_version, loader, item):
        super().__init__()
        self.project_id = project_id
        self.mc_version = mc_version
        self.loader = loader
        self.item = item

    def run(self):
        supported = False
        reason = ""
        try:
            project = Project.get(self.project_id)
            versions = project.get_versions()
            supports_version = any(self.mc_version in v.model.game_versions for v in versions)
            supports_loader = any(self.loader in v.model.loaders for v in versions)
            if supports_version and supports_loader:
                supported = True
            else:
                reasons = []
                if not supports_version:
                    reasons.append(f"Minecraft {self.mc_version}")
                if not supports_loader:
                    reasons.append(f"{lang.Dialogs.loader} {self.loader.capitalize()}")
                reason = ", ".join(reasons)
        except Exception as e:
            reason = f"{lang.Dialogs.error}: {str(e)}"

        self.finished.emit(self.item, supported, reason)

class ModDetailsWorker(QObject):
    finished = pyqtSignal(object, str)  # (project_or_None, error_msg)

    def __init__(self, project_id):
        super().__init__()
        self.project_id = project_id

    def run(self):
        try:
            project = Project.get(self.project_id)
            self.finished.emit(project, "")
        except Exception as e:
            self.finished.emit(None, str(e))

class ModsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("container")
        self.setStyleSheet(DARK_STYLESHEET)
        self.thread_pool = QThreadPool()
        self.mods_queue = []
        self.active_threads = []
        self.build_manager = memory.get("build_manager")
        self.selected_search_result = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.search_mods)
        self.current_build = None
        self.expanded_widget = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        build_selection_layout = QHBoxLayout()
        build_selection_layout.addWidget(QLabel(lang.Dialogs.select_build))
        self.build_combo = QComboBox()
        self.build_combo.setStyleSheet("border: 2px solid #0078D7; border-radius: 5px; background-color: #434343;")
        self.buildsUpdate()
        build_selection_layout.addWidget(self.build_combo)
        build_selection_layout.addStretch()
        main_layout.addLayout(build_selection_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        filter_layout = QHBoxLayout()
        self.loader_filter = QComboBox()
        self.loader_filter.addItem(lang.Dialogs.all_loaders, None)
        self.loader_filter.addItem("Fabric", "fabric")
        self.loader_filter.addItem("Forge", "forge")
        self.loader_filter.addItem("Quilt", "quilt")
        self.loader_filter.addItem("Vanilla", "minecraft")
        filter_layout.addWidget(QLabel(lang.Dialogs.filter_by_loader))
        filter_layout.addWidget(self.loader_filter)
        filter_layout.addStretch()
        search_layout.addLayout(filter_layout)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(lang.Dialogs.enter_mod_name)
        search_layout.addWidget(self.search_input)
        self.search_results_list = QListWidget()
        search_layout.addWidget(self.search_results_list, 1)
        self.mod_details_label = QTextEdit()
        self.mod_details_label.setReadOnly(True)
        self.mod_details_label.setMinimumHeight(150)
        search_layout.addWidget(self.mod_details_label)
        self.add_btn = QPushButton(lang.Dialogs.add_to_queue)
        self.add_btn.setEnabled(False)
        search_layout.addWidget(self.add_btn)
        self.tabs.addTab(search_widget, lang.Dialogs.search_mods)

        queue_widget = QWidget()
        queue_layout = QVBoxLayout(queue_widget)
        queue_layout.addWidget(QLabel(lang.Dialogs.download_queue))
        self.queue_list = QListWidget()
        queue_layout.addWidget(self.queue_list, 1)

        btns_layout = QHBoxLayout()
        self.up_btn = QPushButton(lang.Dialogs.move_up)
        self.down_btn = QPushButton(lang.Dialogs.move_down)
        self.remove_queue_btn = QPushButton(lang.Dialogs.remove)
        self.install_all_btn = QPushButton(lang.Dialogs.install_all)
        btns_layout.addWidget(self.up_btn)
        btns_layout.addWidget(self.down_btn)
        btns_layout.addWidget(self.remove_queue_btn)
        btns_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        btns_layout.addWidget(self.install_all_btn)
        queue_layout.addLayout(btns_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        queue_layout.addWidget(self.progress_bar)
        self.tabs.addTab(queue_widget, lang.Dialogs.download_queue_tab)

        build_widget = QWidget()
        build_layout = QVBoxLayout(build_widget)
        build_layout.addWidget(QLabel(lang.Dialogs.installed_mods))

        self.installed_mods_scroll = QScrollArea()
        self.installed_mods_scroll.setWidgetResizable(True)
        self.installed_mods_widget = QWidget()
        self.installed_mods_layout = QVBoxLayout(self.installed_mods_widget)
        self.installed_mods_scroll.setWidget(self.installed_mods_widget)
        build_layout.addWidget(self.installed_mods_scroll, 1)

        build_layout.addWidget(QLabel(lang.Dialogs.build_structure))
        self.build_tree = QTreeWidget()
        self.build_tree.setHeaderLabels([lang.Dialogs.file_folder, lang.Dialogs.path])
        build_layout.addWidget(self.build_tree, 1)
        self.tabs.addTab(build_widget, lang.Dialogs.build_management)

    def setup_connections(self):
        self.build_combo.currentIndexChanged.connect(self.on_build_selected)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.loader_filter.currentIndexChanged.connect(self.on_search_text_changed)
        self.search_results_list.itemClicked.connect(self.select_search_mod)
        self.add_btn.clicked.connect(self.add_to_queue)
        self.queue_list.itemClicked.connect(self.on_queue_item_selected)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        self.remove_queue_btn.clicked.connect(self.remove_from_queue)
        self.install_all_btn.clicked.connect(self.install_all_from_queue)

    def install_all_from_queue(self):
        if not self.mods_queue:
            windowAbs.information(self, lang.Dialogs.queue_empty_title, lang.Dialogs.queue_empty_message,
                                  btn_text=lang.Dialogs.ok)
            return

        errors = []
        for project in list(self.mods_queue):
            print(project.model.title)
            try:
                minecraft_version = self.current_build['minecraft']
                selected_loader = self.current_build.get("core_type", "").lower()

                versions = project.get_versions()
                compatible_versions = [
                    v for v in versions
                    if minecraft_version in v.model.game_versions and
                       selected_loader in v.model.loaders
                ]
                if not compatible_versions:
                    errors.append(f"{project.model.title}: {lang.Dialogs.no_compatible_versions}")
                    continue

                file = compatible_versions[0].get_files()[0]
                download_url = file.url
                filename = file.name

                build_dir = self.build_manager.get_build_path(self.current_build)
                mods_dir = os.path.join(build_dir, "mods")
                os.makedirs(mods_dir, exist_ok=True)

                mod_path = os.path.join(mods_dir, filename)
                if os.path.exists(mod_path):
                    continue

                response = requests.get(download_url)
                response.raise_for_status()
                with open(mod_path, "wb") as f:
                    f.write(response.content)

            except Exception as e:
                errors.append(f"{project.model.title}: {str(e)}")

        self.refresh_installed_mods()
        self.refresh_build_tree()

        if errors:
            windowAbs.critical(self, lang.Dialogs.completed_with_errors, "\n".join(errors), btn_text=lang.Dialogs.ok)
        else:
            windowAbs.information(self, lang.Dialogs.success, lang.Dialogs.all_mods_installed_successfully, btn_text=lang.Dialogs.ok)
            self.queue_list.clear()

    def buildsUpdate(self):
        self.build_combo.clear()
        self.build_combo.addItem(lang.Dialogs.select_build, None)
        for build in self.build_manager.get_all_builds():
            if build.get('core_type', '').lower() != 'vanilla':
                self.build_combo.addItem(build['name'], build)

    def on_build_selected(self, index):
        self.current_build = self.build_combo.itemData(index)
        self.search_input.clear()
        self.search_results_list.clear()
        self.mod_details_label.clear()
        self.add_btn.setEnabled(False)
        self.refresh_installed_mods()
        self.refresh_build_tree()

    def on_search_text_changed(self):
        self.search_timer.stop()
        self.search_timer.start(1000)

    def search_mods(self):
        query = self.search_input.text().strip()
        if not query or not self.current_build:
            self.search_results_list.clear()
            return

        self.search_input.setEnabled(False)
        self.loader_filter.setEnabled(False)
        self.search_results_list.clear()
        item = QListWidgetItem(lang.Dialogs.loading)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.search_results_list.addItem(item)

        self.thread = QThread(self)
        self.worker = SearchWorker(query)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_project_check_finished(self, item, supported, reason):
        if not supported:
            text = item.text()
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            item.setText(f"{text} – ({lang.Dialogs.not_supported}: {reason})")
            item.setToolTip(f"{lang.Dialogs.mod_not_supported}: {reason}")

    def on_search_finished(self, hits, error):
        self.search_input.setEnabled(True)
        self.loader_filter.setEnabled(True)

        if error:
            windowAbs.critical(self, lang.Dialogs.search_error, error, btn_text=lang.Dialogs.ok)
            return

        if not hits:
            item = QListWidgetItem(lang.Dialogs.no_mods_found)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.search_results_list.addItem(item)
            return

        mc_version = self.current_build.get("minecraft")
        loader = self.current_build.get("core_type", "").lower()

        for mod_data in hits:
            title = mod_data.get("title", lang.Dialogs.untitled)
            desc = mod_data.get("description", "")
            icon_url = mod_data.get("icon_url")
            project_id = mod_data.get("project_id") or mod_data.get("id")

            item_text = f"{title} – {desc[:100]}{'...' if len(desc) > 100 else ''}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, project_id)

            self.search_results_list.addItem(item)

            if icon_url:
                loader_icon = IconLoader(item, icon_url)
                loader_icon.signals.finished.connect(self.on_icon_loaded)
                self.thread_pool.start(loader_icon)

            self.start_project_check_worker(project_id, mc_version, loader, item)

    def start_project_check_worker(self, project_id, mc_version, loader, item):
        thread = QThread()
        worker = ProjectCheckWorker(project_id, mc_version, loader, item)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        def cleanup():
            worker.deleteLater()
            thread.quit()
            thread.wait()
            self.active_threads.remove(thread)

        worker.finished.connect(lambda *args: cleanup())
        worker.finished.connect(self.on_project_check_finished)

        thread.finished.connect(thread.deleteLater)

        self.active_threads.append(thread)
        thread.start()

    def on_icon_loaded(self, item, icon):
        if not icon.isNull():
            item.setIcon(icon)

    def select_search_mod(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole)
        if not project_id:
            self.selected_search_result = None
            self.mod_details_label.clear()
            self.add_btn.setEnabled(False)
            return

        self.mod_details_label.setText(lang.Dialogs.loading_mod_info)
        self.add_btn.setEnabled(False)

        self.details_thread = QThread(self)
        self.details_worker = ModDetailsWorker(project_id)
        self.details_worker.moveToThread(self.details_thread)
        self.details_thread.started.connect(self.details_worker.run)
        self.details_worker.finished.connect(self.on_mod_details_loaded)
        self.details_worker.finished.connect(self.details_thread.quit)
        self.details_worker.finished.connect(self.details_worker.deleteLater)
        self.details_thread.finished.connect(self.details_thread.deleteLater)
        self.details_thread.start()

    def on_mod_details_loaded(self, project, error):
        if error or not project:
            windowAbs.critical(self, lang.Dialogs.error, f"{lang.Dialogs.failed_to_get_mod_data}: {error}", btn_text=lang.Dialogs.ok)
            self.mod_details_label.clear()
            self.add_btn.setEnabled(False)
            self.selected_search_result = None
            return

        try:
            mod = project.model
            try:
                team = project.get_team()
                authors = ", ".join(
                    [member.get_user().model.username for member in team.get_members()]) if team else lang.Dialogs.unknown
            except Exception:
                authors = lang.Dialogs.unknown

            details = (
                f"<b>{lang.Dialogs.name}:</b> {mod.title}<br>"
                f"<b>{lang.Dialogs.authors}:</b> {authors}<br>"
                f"<b>{lang.Dialogs.description}:</b> {mod.description}<br>"
                f"<b>{lang.Dialogs.game_versions}:</b> {', '.join(project.model.game_versions)}<br>"
                f"<b>{lang.Dialogs.categories}:</b> {', '.join(project.model.categories)}<br>"
                f"<b>{lang.Dialogs.project_type}:</b> {mod.project_type}<br>"
                f"<b>{lang.Dialogs.downloads}:</b> {mod.downloads}"
            )
            self.mod_details_label.setText(details)
            self.selected_search_result = project
            self.add_btn.setEnabled(self.current_build is not None and project is not None)
        except Exception as e:
            windowAbs.critical(self, lang.Dialogs.error, f"{lang.Dialogs.mod_data_processing_error}: {e}", btn_text=lang.Dialogs.ok)
            self.mod_details_label.clear()
            self.add_btn.setEnabled(False)
            self.selected_search_result = None

    def add_to_queue(self):
        if not self.selected_search_result or not self.current_build:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.select_build_and_mod, btn_text=lang.Dialogs.ok)
            return
        project = self.selected_search_result
        if project.model.id in [p.model.id for p in self.mods_queue]:
            windowAbs.information(self, lang.Dialogs.information, lang.Dialogs.mod_already_in_queue, btn_text=lang.Dialogs.ok)
            return
        self.mods_queue.append(project)
        item = QListWidgetItem(project.model.title)
        item.setData(Qt.ItemDataRole.UserRole, project)
        self.queue_list.addItem(item)
        windowAbs.information(self, lang.Dialogs.added, lang.Dialogs.mod_added_to_queue.format(title=project.model.title), btn_text=lang.Dialogs.ok)

    def on_queue_item_selected(self, item):
        self.remove_queue_btn.setEnabled(True)
        self.up_btn.setEnabled(True)
        self.down_btn.setEnabled(True)

    def move_up(self):
        row = self.queue_list.currentRow()
        if row > 0:
            self.mods_queue[row], self.mods_queue[row - 1] = self.mods_queue[row - 1], self.mods_queue[row]
            item = self.queue_list.takeItem(row)
            self.queue_list.insertItem(row - 1, item)
            self.queue_list.setCurrentRow(row - 1)

    def move_down(self):
        row = self.queue_list.currentRow()
        if row < self.queue_list.count() - 1:
            self.mods_queue[row], self.mods_queue[row + 1] = self.mods_queue[row + 1], self.mods_queue[row]
            item = self.queue_list.takeItem(row)
            self.queue_list.insertItem(row + 1, item)
            self.queue_list.setCurrentRow(row + 1)

    def remove_from_queue(self):
        row = self.queue_list.currentRow()
        if row >= 0:
            self.mods_queue.pop(row)
            self.queue_list.takeItem(row)
            self.remove_queue_btn.setEnabled(False)

    def on_queue_progress(self, project_id, percent):
        self.progress_bar.setValue(percent)

    def on_mod_downloaded(self, project_id):
        pass

    def on_all_finished(self):
        windowAbs.information(self, lang.Dialogs.done, lang.Dialogs.all_mods_downloaded, btn_text=lang.Dialogs.ok)
        self.mods_queue.clear()
        self.queue_list.clear()
        self.progress_bar.setValue(0)

    def install_mod(self):
        if not self.selected_search_result or not self.current_build:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.select_build_and_mod, btn_text=lang.Dialogs.ok)
            return

        try:
            project = Project.get(self.selected_search_result.id)
            minecraft_version = self.current_build['minecraft']
            selected_loader = self.loader_filter.currentData()

            versions = project.get_versions(game_versions=[minecraft_version])
            compatible_versions = [v for v in versions if not selected_loader or selected_loader in v.model.loaders]
            if not compatible_versions:
                windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.no_compatible_versions, btn_text=lang.Dialogs.ok)
                return

            file = compatible_versions[0].get_files()[0]
            download_url = file.url
            filename = file.name

            build_dir = self.build_manager.get_build_path(self.current_build)
            mods_dir = os.path.join(build_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            mod_path = os.path.join(mods_dir, filename)
            if os.path.exists(mod_path):
                reply = windowAbs.question(
                    self, lang.Dialogs.confirmation,
                    lang.Dialogs.mod_exists.format(filename=filename),
                    yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no
                )
                if not reply:
                    return

            response = requests.get(download_url)
            if response.status_code == 200:
                with open(mod_path, "wb") as f:
                    f.write(response.content)
                windowAbs.information(self, lang.Dialogs.success, lang.Dialogs.mod_installed.format(title=project.model.title), btn_text=lang.Dialogs.ok)
                self.refresh_installed_mods()
                self.refresh_build_tree()
            else:
                windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.download_failed.format(status=response.status_code), btn_text=lang.Dialogs.ok)
        except Exception as e:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.installation_error.format(error=e), btn_text=lang.Dialogs.ok)

    def select_installed_mod(self, item):
        self.selected_installed_mod_path = item.data(Qt.ItemDataRole.UserRole)

    def remove_mod(self):
        if not self.selected_installed_mod_path or not self.current_build:
            return

        reply = windowAbs.question(
            self, lang.Dialogs.confirmation,
            lang.Dialogs.confirm_remove.format(mod=os.path.basename(self.selected_installed_mod_path)),
            yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no
        )
        if reply:
            try:
                os.remove(self.selected_installed_mod_path)
                windowAbs.information(self, lang.Dialogs.success, lang.Dialogs.mod_removed, btn_text=lang.Dialogs.ok)
                self.refresh_installed_mods()
                self.refresh_build_tree()
            except Exception as e:
                windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.remove_error.format(error=e), btn_text=lang.Dialogs.ok)

    def refresh_installed_mods(self):
        for i in reversed(range(self.installed_mods_layout.count())):
            item = self.installed_mods_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        if not self.current_build:
            label = QLabel(lang.Dialogs.no_build_selected)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.installed_mods_layout.addWidget(label)
            self.installed_mods_layout.addStretch()
            return

        mods_dir = os.path.join(self.build_manager.get_build_path(self.current_build), "mods")

        if not os.path.exists(mods_dir):
            label = QLabel(lang.Dialogs.mods_dir_not_found)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.installed_mods_layout.addWidget(label)
            self.installed_mods_layout.addStretch()
            return

        mods = [f for f in os.listdir(mods_dir) if f.endswith((".jar", ".jar.disabled"))]

        if not mods:
            label = QLabel(lang.Dialogs.no_mods_installed)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.installed_mods_layout.addWidget(label)
            self.installed_mods_layout.addStretch()
            return

        for mod_file in mods:
            mod_path = os.path.join(mods_dir, mod_file)
            mod_name = os.path.basename(mod_path)
            try:
                mod_widget = ModWidget(
                    mod_name,
                    mod_path,
                    self.toggle_mod,
                    self.delete_mod,
                    self.expand_or_collapse,
                    parent=self
                )
                self.installed_mods_layout.addWidget(mod_widget)
            except Exception as e:
                print(f"Error loading mod {mod_name}: {e}")  # Оставлено на английском для отладки
                error_label = QLabel(lang.Dialogs.mod_load_error.format(mod=mod_name))
                error_label.setStyleSheet("color: red;")
                self.installed_mods_layout.addWidget(error_label)

        self.installed_mods_layout.addStretch()

    def toggle_mod(self, is_checked, mod_path, item: ModWidget = None):
        new_mod_path = mod_path
        print(new_mod_path, is_checked)  # Оставлено на английском для отладки
        if is_checked:
            if mod_path.endswith(".disabled"):
                new_mod_path = mod_path.rsplit(".disabled", 1)[0]
        else:
            if not mod_path.endswith(".disabled"):
                new_mod_path = mod_path + ".disabled"
        item.mod_path = new_mod_path
        try:
            os.rename(mod_path, new_mod_path)
        except Exception as e:
            windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.toggle_mod_error.format(error=e), btn_text=lang.Dialogs.ok)

    def delete_mod(self, mod_path, item: ModWidget):
        confirm = windowAbs.question(self, lang.Dialogs.confirmation,
                                       lang.Dialogs.confirm_remove.format(mod=os.path.basename(mod_path)),
                                       yes_text=lang.Dialogs.yes, no_text=lang.Dialogs.no)
        if confirm:
            try:
                os.remove(mod_path)
                self.refresh_installed_mods()
            except Exception as e:
                windowAbs.critical(self, lang.Dialogs.error, lang.Dialogs.delete_mod_error.format(error=e), btn_text=lang.Dialogs.ok)

    def expand_or_collapse(self, widget: ModWidget):
        if self.expanded_widget and self.expanded_widget != widget:
            self.animate_height(self.expanded_widget, self.expanded_widget.height(), 90)
            self.expanded_widget = None

        if self.expanded_widget == widget:
            self.expanded_widget = None
            self.animate_height(widget, widget.height(), 90)
        else:
            self.expanded_widget = widget
            self.animate_height(widget, widget.height(), 250)

    def animate_height(self, widget, start_height, end_height):
        def ch(value):
            widget.setFixedHeight(value)

        def ch2(value):
            widget.descript_label.setFixedHeight(value)

        animation = QVariantAnimation(widget)
        animation.setDuration(300)
        animation.setStartValue(start_height)
        animation.setEndValue(end_height)
        animation.valueChanged.connect(ch)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.start()

        if isinstance(widget, ModWidget):
            animation2 = QVariantAnimation(widget.descript_label)
            animation2.setDuration(300)
            animation2.setStartValue(widget.descript_label.height())
            animation2.setEndValue(end_height - 90)
            animation2.valueChanged.connect(ch2)
            animation2.setEasingCurve(QEasingCurve.Type.InOutCubic)
            animation2.start()

    def refresh_build_tree(self):
        self.build_tree.clear()
        if self.current_build:
            build_dir = self.build_manager.get_build_path(self.current_build)
            root_item = QTreeWidgetItem(self.build_tree, [lang.Dialogs.build, build_dir])
            self._populate_tree(build_dir, root_item)
            root_item.setExpanded(True)
        else:
            self.build_tree.addTopLevelItem(QTreeWidgetItem([lang.Dialogs.no_build_selected, ""]))

    def _populate_tree(self, path, parent_item):
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            item = QTreeWidgetItem(parent_item, [name, full_path])
            if os.path.isdir(full_path):
                self._populate_tree(full_path, item)

    def showEvent(self, event):
        self.refresh_installed_mods()
        self.refresh_build_tree()
        super().showEvent(event)