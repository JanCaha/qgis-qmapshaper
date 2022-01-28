from typing import List
from pathlib import Path
import subprocess

from qgis.core import (QgsProcessingFeedback)
from processing.core.ProcessingConfig import ProcessingConfig


class QMapshaperUtils:

    MAPSHAPER_FOLDER = "MAPSHAPER_FOLDER"

    @staticmethod
    def mapshaper_bin_folder() -> str:

        folder = ProcessingConfig.getSetting(QMapshaperUtils.MAPSHAPER_FOLDER)

        folder = Path(folder) / "bin"

        return folder.absolute().as_posix()

    @staticmethod
    def mapshaper_folder() -> str:
        folder = ProcessingConfig.getSetting(QMapshaperUtils.MAPSHAPER_FOLDER)

        if not folder:
            folder = QMapshaperUtils.guess_mapshaper_folder()

        return folder if folder else ''

    @staticmethod
    def guess_mapshaper_folder() -> str:

        folder = Path.home() / "node_modules" / "mapshaper"

        return folder.absolute().as_posix()

    @staticmethod
    def runMapshaper(commands: List[str], feedback: QgsProcessingFeedback):

        feedback.pushInfo("Running command: {}".format(" ".join(commands)))

        res = subprocess.Popen(commands,
                               stdout=subprocess.PIPE,
                               stdin=subprocess.DEVNULL,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)

        feedback.pushInfo("Result {}.".format(res.stdout.readlines()))
        feedback.pushInfo("Command runned.")
