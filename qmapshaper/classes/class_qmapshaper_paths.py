from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig

from ..text_constants import TextConstants
from .class_qmapshaper_runner import QMapshaperRunner


class QMapshaperPaths:

    @staticmethod
    def full_path_command(command: str) -> str:

        path = Path(QMapshaperPaths.mapshaper_bin_folder()) / command

        return path.absolute().as_posix()

    @staticmethod
    def mapshaper_bin_folder() -> str:

        folder = Path(QMapshaperPaths.mapshaper_folder()) / "bin"

        return folder.absolute().as_posix()

    @staticmethod
    def mapshaper_folder() -> str:

        folder = ProcessingConfig.getSetting(TextConstants.MAPSHAPER_FOLDER)

        if not folder:
            folder = QMapshaperPaths.guess_mapshaper_folder()

        return folder if folder else ''

    @staticmethod
    def guess_mapshaper_folder() -> str:

        # globally available
        if QMapshaperRunner.test_run(""):
            return ""

        folder = Path.home() / "node_modules" / "mapshaper"

        if QMapshaperRunner.test_run(folder):
            return folder.absolute().as_posix()

        return ""
