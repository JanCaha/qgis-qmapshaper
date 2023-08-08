from qgis.PyQt.QtWidgets import QDialog

from ...classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ...classes.class_qmapshaper_file import QMapshaperFile
from ...processing.tool_console import ConsoleAlgorithm
from ...utils import log
from .interactive_process import InteractiveProcess


class InteractiveConsoleProcess(InteractiveProcess):
    def __init__(self, parent: QDialog = None) -> None:
        super(InteractiveConsoleProcess, self).__init__(parent=parent)

        self.result_layer_name = "processed"

    def process_layer(self, console_call: str) -> None:
        self.remove_previous_data()

        self.processed_data_filename = QMapshaperFile.random_temp_filename()

        commands = ConsoleAlgorithm.split_text_into_parts(console_call)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.input_data_filename,
            output_data_path=self.processed_data_filename,
            command=commands[0],
            arguments=commands[1:],
            clean_before=self.clean_data,
            clean_after=self.clean_data,
        )

        log(f"COMMAND TO RUN: {' '.join(commands)}")

        self.run_mapshaper_process(commands)

        log(f"Data to load: {self.processed_data_filename}")
