import sys
import psutil
import random

from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QSpinBox,
    QStackedWidget, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QIcon, QPainter, QColor
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QTimer
)

from UI.Style import TEMPLATE_STYLE
from UI.elements.TextSlider import SliderTicksLables
from UI.translate import lang, RU, EN
from func import settings
from UI.windows.windowAbs import DialogAbs, question


class NoisePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0.035)
        w, h = self.width(), self.height()
        for _ in range(1200):
            x = random.randint(0, w)
            y = random.randint(0, h)
            g = random.randint(180, 255)
            painter.setPen(QColor(g, g, g))
            painter.drawPoint(x, y)
        painter.end()
        super().paintEvent(event)

class FirstRunDialog(DialogAbs):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.finished_settings = False
        self.lang = RU
        self.setWindowTitle(self.lang.Dialogs.hello_dialog_title)
        self.setModal(True)
        wid = QWidget()
        self.setCentralWidget(wid)
        self.setFixedSize(600, 200)
        self.current = 0
        self.page_items = []

        self.setStyleSheet(TEMPLATE_STYLE)

        main_layout = QVBoxLayout(wid)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton()
        self.next_btn = QPushButton()
        nav.addWidget(self.prev_btn)
        nav.addStretch()
        nav.addWidget(self.next_btn)
        main_layout.addLayout(nav)

        self.prev_btn.clicked.connect(self.go_prev)
        self.next_btn.clicked.connect(self.go_next)

        self._add_pages()
        for group in self.page_items:
            for w in group:
                eff = QGraphicsOpacityEffect(w)
                eff.setOpacity(0)
                w.setGraphicsEffect(eff)

        self.update_translations(self.lang)
        self._fade_in_items(self.current)

    def _add_pages(self):
        p0 = NoisePage()
        v0 = QVBoxLayout(p0)
        self.greet1 = QLabel()
        self.greet2 = QLabel()
        self.greet2.setWordWrap(True)
        v0.addStretch()
        v0.addWidget(self.greet1)
        v0.addWidget(self.greet2)
        v0.addStretch()
        self.stacked.addWidget(p0)
        self.page_items.append([self.greet1, self.greet2])

        p1 = NoisePage()
        v1 = QVBoxLayout(p1)
        self.lang_info = QLabel()
        self.lang_row = QWidget()
        hl = QHBoxLayout(self.lang_row)
        self.lbl_lang = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        self.lang_combo.setCurrentIndex(0 if settings.get("language", "ru") == "ru" else 1)
        self.lang_combo.currentIndexChanged.connect(
            lambda idx: self.update_translations(RU if idx == 0 else EN)
        )
        hl.addWidget(self.lbl_lang)
        hl.addWidget(self.lang_combo)
        hl.setContentsMargins(0, 0, 0, 0)
        v1.addWidget(self.lang_info)
        v1.addWidget(self.lang_row)
        self.stacked.addWidget(p1)
        self.page_items.append([self.lang_info, self.lang_row])

        p2 = NoisePage()
        v2 = QVBoxLayout(p2)
        self.behavior_lbl = QLabel()
        self.behavior_row = QWidget()
        hl2 = QHBoxLayout(self.behavior_row)
        self.combo_behavior = QComboBox()
        hl2.addWidget(self.combo_behavior)
        hl2.setContentsMargins(0, 0, 0, 0)
        v2.addWidget(self.behavior_lbl)
        v2.addWidget(self.behavior_row)
        self.stacked.addWidget(p2)
        self.page_items.append([self.behavior_lbl, self.behavior_row])

        p3 = NoisePage()
        v3 = QVBoxLayout(p3)
        self.mem_lbl = QLabel()
        self.mem_ctrl = QWidget()
        hl3 = QHBoxLayout(self.mem_ctrl)
        total = psutil.virtual_memory().total // (2**20)
        self.slider = SliderTicksLables()
        self.slider.setRange(1000, total, 5)
        self.slider.slider.setValue(settings.get("javaMemory", 2048))
        self.spin = QSpinBox()
        self.spin.setRange(1000, total)
        self.spin.setValue(settings.get("javaMemory", 2048))
        self.spin.setFixedWidth(60)
        self.slider.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.slider.setValue)
        hl3.addWidget(self.slider)
        hl3.addWidget(self.spin)
        v3.addWidget(self.mem_lbl)
        v3.addWidget(self.mem_ctrl)
        self.stacked.addWidget(p3)
        self.page_items.append([self.mem_lbl, self.mem_ctrl])

        p4 = NoisePage()
        v4 = QVBoxLayout(p4)
        self.fin = QLabel()
        v4.addStretch()
        v4.addWidget(self.fin)
        v4.addStretch()
        self.stacked.addWidget(p4)
        self.page_items.append([self.fin])

    def update_translations(self, lang_obj):
        self.lang = lang_obj

        self.setWindowTitle(self.lang.Dialogs.hello_dialog_title)

        self.greet1.setText(f"<h2 align='center'>{self.lang.Dialogs.hello_header}</h2>")
        self.greet2.setText(f"<p align='center'>{self.lang.Dialogs.hello_description}</p>")

        self.lang_info.setText(f"<b>{self.lang.Dialogs.language_title}</b>")
        self.lbl_lang.setText(self.lang.Dialogs.language_label)

        self.behavior_lbl.setText(f"<b>{self.lang.Dialogs.behavior_title}</b>")
        self.combo_behavior.blockSignals(True)
        self.combo_behavior.clear()
        self.combo_behavior.addItems([
            self.lang.Dialogs.launcher_hide_completely,
            self.lang.Dialogs.launcher_minimize_to_taskbar,
            self.lang.Dialogs.launcher_do_nothing
        ])
        self.combo_behavior.setCurrentIndex(settings.get("gameLaunchBehavior", 0))
        self.combo_behavior.blockSignals(False)

        self.mem_lbl.setText(f"<b>{self.lang.Dialogs.java_memory_title}</b>")
        self.slider.dlsText = self.lang.Dialogs.memory_suffix

        self.fin.setText(
            f"<h3 align='center'>{self.lang.Dialogs.finish_title}</h3>"
            f"<p align='center'>{self.lang.Dialogs.finish_message}</p>"
        )

        self.prev_btn.setText(self.lang.Dialogs.back)
        self._update_nav()

    def _fade_in_items(self, idx):
        for w in self.page_items[idx]:
            w.graphicsEffect().setOpacity(0)
        seq = QSequentialAnimationGroup(self)
        for w in self.page_items[idx]:
            anim = QPropertyAnimation(w.graphicsEffect(), b"opacity", self)
            anim.setDuration(250)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            seq.addAnimation(anim)
            seq.addPause(100)
        seq.start()
        self._current_anim = seq

    def go_next(self):
        old = self.current
        if old == self.stacked.count() - 1:
            self._save()
            self.accept()
            return
        self.current += 1
        self._update_nav()
        self.stacked.setCurrentIndex(self.current)
        for w in self.page_items[old]:
            w.graphicsEffect().setOpacity(1)
        self._fade_in_items(self.current)

    def go_prev(self):
        old = self.current
        if old == 0:
            return
        self.current -= 1
        self._update_nav()
        self.stacked.setCurrentIndex(self.current)
        for w in self.page_items[old]:
            w.graphicsEffect().setOpacity(1)
        self._fade_in_items(self.current)

    def _update_nav(self):
        self.prev_btn.setEnabled(self.current > 0)
        self.next_btn.setText(
            self.lang.Dialogs.done if self.current == self.stacked.count() - 1 else self.lang.Dialogs.next
        )

    def _save(self):
        settings.put("lang", "ru" if self.lang is RU else "en")
        settings.put("launcherBehavior", self.combo_behavior.currentIndex())
        settings.put("javaMemory", self.spin.value())
        self.finished_settings = True

    def closeEvent(self, event):
        if not self.finished_settings:
            q = question(None, "", self.lang.Dialogs.need_ckip_settings,
                         yes_text=self.lang.Dialogs.yes, no_text=self.lang.Dialogs.no, height=130)
            if not q:
                event.ignore()
                return
            self._save()
        super().closeEvent(event)
