import os
from typing import List, Any
from pathlib import Path
import subprocess
from pytest_qgis import QgsVectorLayer

from qgis.core import (QgsProcessingFeedback, QgsMessageLog, Qgis)
from processing.core.ProcessingConfig import ProcessingConfig

from .text_constants import TextConstants

LOG_DEV = False

if os.environ.get("QMAPSHAPER_DEV"):
    if os.environ.get("QMAPSHAPER_DEV").lower() == "true":
        LOG_DEV = True


class QMapshaperCommandsUtils:

    @staticmethod
    def full_path_command(command: str) -> str:

        path = Path(QMapshaperCommandsUtils.mapshaper_bin_folder()) / command

        return path.absolute().as_posix()

    @staticmethod
    def mapshaper_bin_folder() -> str:

        folder = Path(QMapshaperCommandsUtils.mapshaper_folder()) / "bin"

        return folder.absolute().as_posix()

    @staticmethod
    def mapshaper_folder() -> str:

        folder = ProcessingConfig.getSetting(TextConstants.MAPSHAPER_FOLDER)

        if not folder:
            folder = QMapshaperCommandsUtils.guess_mapshaper_folder()

        return folder if folder else ''

    @staticmethod
    def guess_mapshaper_folder() -> str:

        folder = Path.home() / "node_modules" / "mapshaper"

        return folder.absolute().as_posix()

    @staticmethod
    def runMapshaper(commands: List[str], feedback: QgsProcessingFeedback = None):

        if feedback:
            feedback.pushInfo("Running command: {}".format(" ".join(commands)))

        res = subprocess.Popen(commands,
                               stdout=subprocess.PIPE,
                               stdin=subprocess.DEVNULL,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)

        if feedback:
            feedback.pushInfo("Result: ")

            lines = res.stdout.readlines()

            for line in lines:
                feedback.pushInfo("{}.".format(line))

            feedback.pushInfo("Command runned.")


def get_icons_folder() -> Path:
    return Path(__file__).parent / "icons"


def get_icon_path(file_name: str) -> str:

    file: Path = get_icons_folder() / file_name

    return file.absolute().as_posix()


def log(text: Any) -> None:
    if LOG_DEV:
        QgsMessageLog.logMessage(str(text), TextConstants.plugin_name, Qgis.Info)


def features_count_with_non_empty_geoms(layer: QgsVectorLayer) -> int:

    count = 0

    for feature in layer.getFeatures():
        if not feature.geometry().isEmpty():
            count += 1

    return count
