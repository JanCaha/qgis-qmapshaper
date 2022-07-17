from typing import List

from qgis.PyQt.QtCore import (QRunnable, QObject, pyqtSignal, pyqtSlot, QThread)


class WaitWorker(QRunnable):

    def __init__(self, percent: int, wait_time: int = 200):

        super(WaitWorker, self).__init__()

        self.signals = WorkerSignals()

        self.percent = percent

        self.wait_time = wait_time

    @pyqtSlot()
    def run(self):

        QThread.msleep(self.wait_time)

        self.signals.percent.emit(self.percent)


class WaitWorkerCommand(QRunnable):

    def __init__(self, command: str):

        super(WaitWorkerCommand, self).__init__()

        self.signals = WorkerSignals()

        self.command = command

    @pyqtSlot()
    def run(self):

        QThread.msleep(750)

        self.signals.command.emit(self.command)


class WorkerSignals(QObject):
    result = pyqtSignal()
    percent = pyqtSignal(int)
    command = pyqtSignal(str)
