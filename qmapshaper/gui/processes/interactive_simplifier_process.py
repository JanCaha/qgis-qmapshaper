from qgis.PyQt.QtWidgets import (QDialog)

from ...classes.class_qmapshaper_file import QMapshaperFile
from ...classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ...processing.tool_simplify import SimplifyAlgorithm
from ...text_constants import TextConstants
from ...utils import log
from .interactive_process import InteractiveProcess


class InteractiveSimplifierProcess(InteractiveProcess):

    def __init__(self, parent: QDialog = None) -> None:

        super(InteractiveSimplifierProcess, self).__init__(parent=parent)

        self.result_layer_name = "generalized"

    def process_layer(self, simplify_percent: float, simplify_method: str) -> None:

        self.remove_previous_data()

        self.processed_data_filename = QMapshaperFile.random_temp_filename()

        planar = not self.memory_layer.crs().isGeographic()

        if self.process_selection:
            field_name = TextConstants.GENERALIZATION_FIELD_NAME
        else:
            field_name = None

        arguments = SimplifyAlgorithm.prepare_arguments(simplify_percent=simplify_percent,
                                                        method=simplify_method,
                                                        planar=planar,
                                                        field=field_name)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.input_data_filename,
            output_data_path=self.processed_data_filename,
            command=SimplifyAlgorithm.command(),
            arguments=arguments,
            clean_before=self.clean_data,
            clean_after=self.clean_data)

        log(f"COMMAND TO RUN: {' '.join(commands)}")

        self.run_mapshaper_process(commands)

        log(f"Data to load: {self.processed_data_filename}")
