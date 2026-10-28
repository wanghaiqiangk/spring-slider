import sys

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class SpringSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._value = 0.0
        self._dragging = False

        # 外观参数
        self._track_width = 8
        self._handle_radius = 12
        self._margin = 20

        self._track_color = QColor("#d0d0d0")
        self._fill_color = QColor("#5058a5")
        self._handle_color = QColor("#ffffff")
        self._handle_border_color = QColor("#bbbbbb")

        self.setMinimumSize(50, 120)
        self.setMouseTracking(True)

    def sizeHint(self):
        return QSize(70, 300)

    def value(self):
        return self._value

    def setValue(self, value):
        value = max(-1.0, min(1.0, float(value)))

        if abs(value - self._value) < 1e-9:
            return

        self._value = value
        self.valueChanged.emit(value)
        self.update()

    def reset(self):
        self._dragging = False
        self.setValue(0.0)

    def _geometry(self):
        cx = self.width() / 2
        top = self._margin
        bottom = self.height() - self._margin
        center = (top + bottom) / 2
        return cx, top, bottom, center

    def _value_to_y(self, value):
        _, top, bottom, center = self._geometry()
        half_height = (bottom - top) / 2
        return center - value * half_height

    def _y_to_value(self, y):
        _, top, bottom, center = self._geometry()
        half_height = (bottom - top) / 2

        if half_height <= 0:
            return 0.0

        return max(
            -1.0,
            min(1.0, (center - y) / half_height)
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        cx, top, bottom, center = self._geometry()
        current_y = self._value_to_y(self._value)
        radius = self._track_width / 2

        painter.setPen(Qt.PenStyle.NoPen)

        # 1. 灰色轨道
        painter.setBrush(self._track_color)
        painter.drawRoundedRect(
            QRectF(
                cx - radius,
                top,
                self._track_width,
                bottom - top,
            ),
            radius,
            radius,
        )

        # 2. 从中心开始的填充
        if self._value != 0:
            fill_top = min(center, current_y)
            fill_height = abs(current_y - center)

            painter.setBrush(self._fill_color)
            painter.drawRoundedRect(
                QRectF(
                    cx - radius,
                    fill_top,
                    self._track_width,
                    fill_height,
                ),
                radius,
                radius,
            )

        # 3. 刻度线（-1.0 到 1.0，每 0.25 一格）
        tick_pen = QPen(QColor("#aaaaaa"))
        tick_pen.setWidthF(1)
        painter.setPen(tick_pen)

        for i in range(-4, 5):
            tick_value = i / 4.0
            y = self._value_to_y(tick_value)

            length = 12 if i == 0 else 6

            painter.drawLine(
                int(cx - 24),
                int(y),
                int(cx - 24 + length),
                int(y),
            )

        # 4. 滑块手柄
        painter.setPen(
            QPen(self._handle_border_color, 1)
        )
        painter.setBrush(self._handle_color)
        painter.drawEllipse(
            QRectF(
                cx - self._handle_radius,
                current_y - self._handle_radius,
                self._handle_radius * 2,
                self._handle_radius * 2,
            )
        )

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self.setValue(self._y_to_value(event.position().y()))
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.setValue(self._y_to_value(event.position().y()))
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset()
            event.accept()
        else:
            event.ignore()

    def event(self, event):
        if event.type() in (
            QEvent.Type.WindowDeactivate,
            QEvent.Type.UngrabMouse,
        ):
            self.reset()

        return super().event(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Spring-centered Slider")

    layout = QVBoxLayout(window)

    slider = SpringSlider()

    label = QLabel("0.000")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    slider.valueChanged.connect(
        lambda value: label.setText(f"{value:+.3f}")
    )

    layout.addWidget(slider)
    layout.addWidget(label)

    window.resize(160, 400)
    window.show()

    sys.exit(app.exec())
