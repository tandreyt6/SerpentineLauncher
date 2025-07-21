from PyQt6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtSlot, QTimer
)



class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        self.fade_duration = 100
        self.is_animating = False
        self.animation = None

    def setCurrentIndex(self, index: int):
        if index == self.currentIndex() or self.is_animating:
            return

        self.is_animating = True

        self.opacity_effect.setOpacity(0.0)
        super().setCurrentIndex(index)

        QTimer.singleShot(100, self._fadeIn)

    def _fadeIn(self):
        if self.animation:
            self.animation.stop()

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(self.fade_duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation.finished.connect(self._onFadeFinished)
        self.animation.start()

    def _onFadeFinished(self):
        self.is_animating = False
