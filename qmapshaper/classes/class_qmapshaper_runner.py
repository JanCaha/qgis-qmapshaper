from pathlib import Path
from typing import Union

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

    def __init__(self, path: Union[str, Path] = None) -> None:

        super().__init__()

        self.setProcessChannelMode(QProcess.MergedChannels)

        if path:

            path_ms = Path(path) / "bin" / "mapshaper"

            path = path_ms.absolute().as_posix()

        else:

            path = "mapshaper"

        self.setProgram(path)

        self.start()

        self.waitForStarted()

        self.waitForFinished()

        self.output_lines = bytes(self.readAllStandardOutput()).decode("utf8")

        if "Error: No commands to run" in self.output_lines:
            self.found = True
