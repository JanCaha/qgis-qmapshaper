from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig

from ..text_constants import TextConstants
from ..utils import log


class QMapshaperPaths:

    @staticmethod
    def mapshaper_executable_path() -> str:

        mapshaper_folder = QMapshaperPaths.mapshaper_folder()

        if mapshaper_folder:
            path = QMapshaperPaths.subfolder_bin(
                mapshaper_folder) / QMapshaperPaths.mapshaper_command_name()
            return path.as_posix()

        return ""

    @staticmethod
    def subfolder_bin(folder) -> Path:

        command = "mapshaper"

        exec_path = Path(folder) / command
        exec_path_bin = exec_path.parent / "bin" / command

        if exec_path_bin.exists():
            return exec_path_bin.parent

        if exec_path.exists():
            return exec_path.parent

        return exec_path.parent

    @staticmethod
    def mapshaper_folder() -> str:

        folder = ProcessingConfig.getSetting(TextConstants.MAPSHAPER_FOLDER)

        if not folder:
            folder = QMapshaperPaths.guess_mapshaper_folder()

        return folder if folder else ''

    @staticmethod
    def guess_mapshaper_folder() -> str:

        from .class_qmapshaper_runner import MapshaperProcessChecker, NpmPackageLocationCheckerProcess

        # globally available
        mp = MapshaperProcessChecker("")
        if mp.found:
            return ""

        npm_checker = NpmPackageLocationCheckerProcess()

        folder = npm_checker.mapshaper_path()

        mp = MapshaperProcessChecker(folder)
        if mp.found:
            return mp.path

        return ""

    @staticmethod
    def mapshaper_command_name() -> str:

        tool = ProcessingConfig.getSetting(TextConstants.MAPSHAPER_TOOL_NAME)

        if not tool:
            return QMapshaperPaths.guess_mapshaper_command_name()

        return tool

    @staticmethod
    def guess_mapshaper_command_name() -> str:
        return "mapshaper-xl"

    @staticmethod
    def mapshaper_command_call() -> str:

        mapshaper_bin_folder = QMapshaperPaths.mapshaper_executable_path()

        if mapshaper_bin_folder:

            return mapshaper_bin_folder

        else:

            return QMapshaperPaths.mapshaper_command_name()
