from pathlib import Path
from typing import List, Union
import subprocess

from qgis.core import QgsProcessingFeedback


class QMapshaperRunner:

    @staticmethod
    def run_mapshaper(commands: List[str], feedback: QgsProcessingFeedback = None):

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

    @staticmethod
    def test_run(path: Union[str, Path]):

        path_command = Path(path) / "bin" / "mapshaper"

        res = subprocess.Popen([path_command],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.DEVNULL,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)

        lines = res.stdout.readlines()

        if lines[0] == "Error: No commands to run":
            return True

        return False
