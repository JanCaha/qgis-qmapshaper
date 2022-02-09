from typing import List

from qgis.PyQt.QtCore import (QRunnable, QObject, pyqtSignal, pyqtSlot, QThread)

from .class_qmapshaper_runner import QMapshaperRunner


class WaitWorker(QRunnable):

    def __init__(self, percent: int):

        super(WaitWorker, self).__init__()

        self.signals = WorkerSignals()

        self.percent = percent

    @pyqtSlot()
    def run(self):

        QThread.msleep(200)

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

        QMapshaperRunner.run_mapshaper(self.commands)

        self.signals.result.emit()


class WorkerSignals(QObject):
    result = pyqtSignal()
    percent = pyqtSignal(int)
