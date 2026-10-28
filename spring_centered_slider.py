import sys

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)


class SpringSlider(QSlider):
    valueChangedFloat = Signal(float)

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)

        self.setRange(-1000, 1000)
        self.setValue(0)
        self.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.setTickInterval(250)

        self.track_width = 8
        self.track_color = QColor("#d0d0d0")
        self.fill_color = QColor("#5058a5")
        self.center_color = QColor("#888888")

        self.valueChanged.connect(self._on_value_changed)
        self.sliderReleased.connect(self.reset)

        # 避免滚轮意外改变运动速度
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _on_value_changed(self, value):
        self.valueChangedFloat.emit(value / 1000.0)

    def reset(self):
        self.setValue(0)

    def wheelEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        style = self.style()
        option = QStyleOptionSlider()
        self.initStyleOption(option)

        groove = style.subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderGroove,
            self,
        )

        handle = style.subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderHandle,
            self,
        )

        # 手柄中心可以移动的有效范围
        half_handle = handle.height() / 2
        y_min = groove.top() + half_handle
        y_max = groove.bottom() - half_handle
        travel = max(0.0, y_max - y_min)

        def value_to_y(value):
            position = QStyle.sliderPositionFromValue(
                self.minimum(),
                self.maximum(),
                value,
                round(travel),
                option.upsideDown,
            )
            return y_min + position

        center_y = value_to_y(0)
        current_y = value_to_y(self.value())
        track_x = groove.center().x()

        # 1. 绘制完整的灰色轨道
        track_rect = QRectF(
            track_x - self.track_width / 2,
            y_min,
            self.track_width,
            travel,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.track_color)
        painter.drawRoundedRect(
            track_rect,
            self.track_width / 2,
            self.track_width / 2,
        )

        # 2. 绘制从中心延伸到当前位置的填充
        if self.value() != 0:
            top = min(center_y, current_y)
            bottom = max(center_y, current_y)

            fill_rect = QRectF(
                track_x - self.track_width / 2,
                top,
                self.track_width,
                bottom - top,
            )

            painter.setBrush(self.fill_color)
            painter.drawRoundedRect(
                fill_rect,
                self.track_width / 2,
                self.track_width / 2,
            )

        # 3. 绘制中心刻度
        painter.setPen(self.center_color)
        painter.drawLine(
            int(track_x - 13),
            int(center_y),
            int(track_x + 13),
            int(center_y),
        )

        # 4. 绘制原生刻度
        tick_option = QStyleOptionSlider(option)
        tick_option.subControls = (
            QStyle.SubControl.SC_SliderTickmarks
        )
        style.drawComplexControl(
            QStyle.ComplexControl.CC_Slider,
            tick_option,
            painter,
            self,
        )

        # 5. 绘制原生手柄
        handle_option = QStyleOptionSlider(option)
        handle_option.subControls = (
            QStyle.SubControl.SC_SliderHandle
        )
        style.drawComplexControl(
            QStyle.ComplexControl.CC_Slider,
            handle_option,
            painter,
            self,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Spring-centered Slider")

    layout = QVBoxLayout(window)

    slider = SpringSlider()
    label = QLabel("0.000")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    slider.valueChangedFloat.connect(
        lambda value: label.setText(f"{value:+.3f}")
    )

    layout.addWidget(slider)
    layout.addWidget(label)

    window.resize(160, 400)
    window.show()

    sys.exit(app.exec())
