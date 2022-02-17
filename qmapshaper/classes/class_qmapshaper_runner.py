from pathlib import Path
from typing import Union, Optional

from qgis.PyQt.QtCore import QProcess

from .class_qmapshaper_paths import QMapshaperPaths


class MapshaperProcess(QProcess):

    output_lines: str = ""

    error_lines: str = ""

    finished_correctly = False

    def __init__(self) -> None:

        super().__init__()

        self.setProcessChannelMode(QProcess.MergedChannels)

        self.setProgram(QMapshaperPaths.mapshaper_command_call())

        self.finished.connect(self.read_output)
        self.error.connect(self.read_output)

    def command_to_run(self) -> str:
        commands = [self.program()] + self.arguments()
        return " ".join(commands)

    def run(self):

        self.start()

        self.waitForStarted()

        self.waitForFinished()

    def read_output(self):

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")
        self.error_lines = bytes(self.readAllStandardError()).decode("utf8")

        if "Wrote" in self.output_lines:
            self.finished_correctly = True


class MapshaperProcessChecker(QProcess):

    output_lines: str

    found = False

    path: str

    def __init__(self, path: Optional[Union[str, Path]] = None) -> None:

        super().__init__()

        self.path = path

        self.setProcessChannelMode(QProcess.MergedChannels)

        if self.path:

            path_ms = Path(self.path) / "bin" / "mapshaper"

            self.path = path_ms.absolute().as_posix()

        else:

            self.path = "mapshaper"

        self.setProgram(self.path)

        self.start()

        self.waitForStarted()

        self.waitForFinished()

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")

        if "Error: No commands to run" in self.output_lines:
            self.found = True


class NpmPackageLocationCheckerProcess(QProcess):

    output_lines: str

    packages_location: str = None

    mapshaper_present: bool = False

    _mapshaper_location: str = None

    def __init__(self) -> None:

        super().__init__()

    def npm_exist(self) -> bool:

        self.setProgram("npm")

        self.start()

        self.waitForStarted()

        self.waitForFinished()

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")

        if "Usage: npm <command>" in self.output_lines:
            return True

        return False

    def npm_package_locations(self) -> bool:

        self.setProgram("npm")
        self.setArguments(["root"])

        self.start()

        self.waitForStarted()

        self.waitForFinished()

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")

        if 0 < len(self.output_lines):

            self.packages_location = self.output_lines.strip()

            return True

        return False

    def mapshaper_exists(self) -> bool:

        self.setProgram("npm")
        self.setArguments(["list"])

        self.start()

        self.waitForStarted()

        self.waitForFinished()

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")

        if "mapshaper" in self.output_lines:

            self.mapshaper_present = True

            path = Path(self.packages_location) / "mapshaper"

            self._mapshaper_location = path.absolute().as_posix()

            return True

        return False

    def mapshaper_path(self) -> Optional[str]:

        if self.npm_exist():

            if self.npm_package_locations():

                if self.mapshaper_exists():

                    return self._mapshaper_location

        return None
