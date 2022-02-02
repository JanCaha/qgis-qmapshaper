from typing import List
import time

from qgis.PyQt.QtCore import (QRunnable, QObject, pyqtSignal, pyqtSlot)
from qgis.core import (QgsProcessingFeedback)

from .class_qmapshaper_runner import QMapshaperRunner


class WaitWorker(QRunnable):

    def __init__(self, percent: int):

        super(WaitWorker, self).__init__()

        self.signals = WorkerSignals()

        self.percent = percent

    @pyqtSlot()
    def run(self):

        time.sleep(0.2)

        self.signals.percent.emit(self.percent)


class ConvertWorker(QRunnable):

    commands: List[str]

    def __init__(self):

        super(ConvertWorker, self).__init__()

        self.signals = WorkerSignals()

        self.commands = []

    def set_commands(self, commands: List[str]) -> None:

        self.commands = commands

    @pyqtSlot()
    def run(self):

        QMapshaperRunner.run_mapshaper(self.commands, QgsProcessingFeedback())

        self.signals.result.emit()


class WorkerSignals(QObject):
    result = pyqtSignal()
    percent = pyqtSignal(int)
