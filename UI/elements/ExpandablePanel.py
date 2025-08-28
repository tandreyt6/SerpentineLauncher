from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint


class ExpandableMask(QWidget):
    def __init__(self, parent, panel):
        super().__init__(parent)
        self.panel = panel
        self.layout = QVBoxLayout(self) if panel.direction in ["right", "left"] else QHBoxLayout(self)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(3)
        self._isMouseTracking = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(Qt.PenStyle.NoPen)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(30, 30, 30, 230)))
        painter.drawRoundedRect(self.rect(), 5, 5)

    def enterEvent(self, event):
        if self._isMouseTracking and self.panel.event_behavior == 0:
            self.panel.expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._isMouseTracking and self.panel.event_behavior == 0:
            self.panel.collapse()
        super().leaveEvent(event)

class ExpandablePanel(QWidget):
    def __init__(self, parent, min, max, direction="right"):
        super().__init__(parent)
        self.direction = direction.lower()
        if self.direction not in ["right", "left", "up", "down"]:
            raise ValueError("direction must be 'right', 'left', 'up' or 'down'")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._isExpanded = False
        self._isOutWidget = True
        self.min_size = min
        self.max_size = max
        self.position_behavior = 0
        self.event_behavior = 0
        self.widgets = []

        if direction in ["left", "right"]:
            self.setFixedWidth(min)
        else:
            self.setFixedHeight(min)
        if hasattr(parent, 'centralWidget') and callable(parent.centralWidget):
            self.mask = ExpandableMask(parent.centralWidget(), self)
        elif hasattr(parent, 'centralWidget'):
            self.mask = ExpandableMask(parent.centralWidget, self)
        else:
            self.mask = ExpandableMask(parent, self)

        self._update_mask_geometry()


        self.animation = QPropertyAnimation(self.mask, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self._update_panel_geometry)

        self.mask.setGeometry(self.geometry())

    def _update_mask_geometry(self):
        rect = self.geometry()
        rect.setY(rect.y() + 30)
        if self._isOutWidget:
            rect.setHeight(self.mask.height())
            rect.setWidth(self.mask.width())
        self.mask.setGeometry(rect)

    def _update_panel_geometry(self, rect):
        if not self._isOutWidget:
            if self.direction in ["left", "right"]:
                self.setFixedWidth(rect.width())
            else:
                self.setFixedHeight(rect.height())
        for widget in self.widgets:
            widget.setSizeMode(rect, self.direction)

    def resizeEvent(self, event):
        self._update_mask_geometry()
        if self.direction in ["left", "right"]:
            self.mask.setFixedHeight(self.height())
        else:
            self.mask.setFixedWidth(self.width())
        super().resizeEvent(event)

    def moveEvent(self, event):
        if self._isExpanded:
            self._update_mask_geometry()
        else:
            self._update_mask_geometry()
        super().moveEvent(event)

    def addWidget(self, wid):
        wid.setSizeMode(self.size(), self.direction)
        self.widgets.append(wid)
        self.mask.layout.addWidget(wid)

    def expand(self, animate=True):
        if self._isExpanded or self.event_behavior == 2:
            return

        self._isExpanded = True

        panel_geo = self.geometry()
        panel_geo.setY(panel_geo.y() + 30)
        if self.direction == "right":
            end_geo = QRect(panel_geo.x(), panel_geo.y(),
                            self.max_size, panel_geo.height())
        elif self.direction == "left":
            end_geo = QRect(panel_geo.x() + panel_geo.width() - self.max_size,
                            panel_geo.y(), self.max_size, panel_geo.height())
        elif self.direction == "down":
            end_geo = QRect(panel_geo.x(), panel_geo.y(),
                            panel_geo.width(), self.max_size)
        elif self.direction == "up":
            end_geo = QRect(panel_geo.x(),
                            panel_geo.y() + panel_geo.height() - self.max_size,
                            panel_geo.width(), self.max_size)

        if self.position_behavior == 1:
            self._shift_sibling_widgets(end_geo)

        if animate:
            r = self.mask.geometry()
            self.animation.stop()
            self.animation.setStartValue(r)
            self.animation.setEndValue(end_geo)
            self.animation.start()
        else:
            self.mask.setGeometry(end_geo)
            if not self._isOutWidget:
                if self.direction in ["left", "right"]:
                    self.setFixedWidth(end_geo.width())
                else:
                    self.setFixedHeight(end_geo.height())

        if self.position_behavior == 0:
            self.raise_()

    def collapse(self, animate=True):
        if not self._isExpanded or self.event_behavior == 1:
            return

        self._isExpanded = False

        panel_geo = self.geometry()
        panel_geo.setY(panel_geo.y() + 30)
        if self.direction == "right":
            end_geo = QRect(panel_geo.x(), panel_geo.y(),
                            self.min_size, panel_geo.height())
        elif self.direction == "left":
            end_geo = QRect(panel_geo.x() + panel_geo.width() - self.min_size,
                            panel_geo.y(), self.min_size, panel_geo.height())
        elif self.direction == "down":
            end_geo = QRect(panel_geo.x(), panel_geo.y(),
                            panel_geo.width(), self.min_size)
        elif self.direction == "up":
            end_geo = QRect(panel_geo.x(),
                            panel_geo.y() + panel_geo.height() - self.min_size,
                            panel_geo.width(), self.min_size)

        if self.position_behavior == 1:
            self._shift_sibling_widgets(end_geo)

        if animate:
            self.animation.stop()
            self.animation.setStartValue(self.mask.geometry())
            self.animation.setEndValue(end_geo)
            self.animation.start()
        else:
            self.mask.setGeometry(end_geo)
            if not self._isOutWidget:
                if self.direction in ["left", "right"]:
                    self.setFixedWidth(end_geo.width())
                else:
                    self.setFixedHeight(end_geo.height())

    def _shift_sibling_widgets(self, end_geo):
        parent = self.parent()
        if not parent:
            return
        for sibling in parent.findChildren(QWidget):
            if sibling != self and sibling != self.mask:
                sib_geo = sibling.geometry()
                if self.direction == "right" and sib_geo.x() >= end_geo.x():
                    sibling.move(sib_geo.x() + (end_geo.width() - self.geometry().width()), sib_geo.y())
                elif self.direction == "left" and sib_geo.x() <= end_geo.x():
                    sibling.move(sib_geo.x() - (end_geo.width() - self.geometry().width()), sib_geo.y())
                elif self.direction == "down" and sib_geo.y() >= end_geo.y():
                    sibling.move(sib_geo.x(), sib_geo.y() + (end_geo.height() - self.geometry().height()))
                elif self.direction == "up" and sib_geo.y() <= end_geo.y():
                    sibling.move(sib_geo.x(), sib_geo.y() - (end_geo.height() - self.geometry().height()))

    def isExpanded(self):
        return self._isExpanded

    def setOutWidget(self, is_out: bool):
        self._isOutWidget = is_out
        if is_out:
            if self.direction in ["left", "right"]:
                self.setFixedWidth(self.min_size)
            else:
                self.setFixedHeight(self.min_size)
        else:
            if self.direction in ["left", "right"]:
                self.setFixedWidth(self.mask.width())
            else:
                self.setFixedHeight(self.mask.height())