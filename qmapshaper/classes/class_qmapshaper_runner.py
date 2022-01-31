from typing import List
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
