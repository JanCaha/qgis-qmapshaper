from typing import Union, Optional

from qgis.PyQt.QtWidgets import (QWidget, QSlider, QSpinBox, QHBoxLayout)
from qgis.PyQt.QtCore import (Qt, pyqtSignal, QThreadPool)

from ..classes.classes_workers import WaitWorker


class PercentSliderSpinBox(QWidget):

    valueChanged = pyqtSignal()
    valueChangedInteractionStopped = pyqtSignal()

    def __init__(self,
                 defaultValue: int = 50,
                 minimum: int = 1,
                 maximum: int = 99,
                 parent: Optional['QWidget'] = None,
                 flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(defaultValue)
        self.slider.valueChanged.connect(self.slider_value_change)

        self.spin_box = QSpinBox()
        self.spin_box.setSuffix("%")
        self.spin_box.setMinimum(minimum)
        self.spin_box.setMaximum(maximum)
        self.spin_box.setValue(defaultValue)
        self.spin_box.valueChanged.connect(self.spin_box_value_change)

        layout.addWidget(self.slider)
        layout.addWidget(self.spin_box)

        self._value: int = defaultValue

        self.threadpool = QThreadPool()
        self.wait_worker: WaitWorker = None

    def _set_value(self, widget: Union[QSpinBox, QSlider], value: int) -> None:
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)
        if self._value != value:
            self._value = value
            self.valueChanged.emit()
            self.create_wait_worker()

    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        self._set_value(self.spin_box, value)
        self._set_value(self.slider, value)

    def slider_value_change(self):
        self._set_value(self.spin_box, self.slider.value())

    def spin_box_value_change(self):
        self._set_value(self.slider, self.spin_box.value())

    def run_update(self, percent: int):

        if percent == self.spin_box.value():
            self.valueChangedInteractionStopped.emit()

    def create_wait_worker(self) -> None:

        wait_worker = WaitWorker(self.spin_box.value())
        wait_worker.signals.percent.connect(self.run_update)

        self.threadpool.start(wait_worker)
