from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig

from ..text_constants import TextConstants
from ..utils import log


class QMapshaperPaths:

    @staticmethod
    def mapshaper_executable_path(use_defined: bool = False) -> str:

        mapshaper_folder = QMapshaperPaths.mapshaper_folder()

        if mapshaper_folder:

            exec_path = Path(mapshaper_folder) / QMapshaperPaths.mapshaper_command_name()

            if exec_path.exists() or use_defined:
                return exec_path.as_posix()

            exec_path = Path(mapshaper_folder) / "bin" / QMapshaperPaths.mapshaper_command_name()

            if exec_path.exists() or use_defined:
                return exec_path.as_posix()

        return ""

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
    def mapshaper_command_name():
        return "mapshaper-xl"

    @staticmethod
    def mapshaper_command_call(use_settings_path: bool = False) -> str:

        mapshaper_bin_folder = QMapshaperPaths.mapshaper_executable_path(
            use_defined=use_settings_path)

        if mapshaper_bin_folder:

            return mapshaper_bin_folder

        else:

            return QMapshaperPaths.mapshaper_command_name()
