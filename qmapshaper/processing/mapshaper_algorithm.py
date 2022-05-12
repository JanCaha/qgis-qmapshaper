import abc
from pathlib import Path
from typing import List, Dict

from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessingAlgorithm, QgsVectorLayer, QgsProcessingFeedback,
                       QgsProcessingException)

from ..classes.class_qmapshaper_runner import MapshaperProcess
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ..classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ..classes.class_qmapshaper_file import QMapshaperFile


class MapshaperAlgorithm(QgsProcessingAlgorithm):

    __metaclass__ = abc.ABCMeta

    input_layer_memory: QgsVectorLayer
    """
    Copy of input layer hold in memory. With added field for identification and joins.
    """

    mapshaper_input: str
    """
    Path to the file that will be used as input to mapshaper command.
    """

    mapshaper_output: str
    """
    Path to the file that will be used as output from mapshaper command.
    """

    simplify_field = None
    clean_data_before = False
    clean_data_after = False

    def __init__(self):
        super().__init__()

        self.input_layer_memory: QgsVectorLayer = None

        self.mapshaper_output = QMapshaperFile.random_temp_filename()

        self.mapshaper_input = QMapshaperFile.random_temp_filename()

        self.result_layer_location = ""

    @abc.abstractmethod
    def prepare_data(self, parameters, context, feedback: QgsProcessingFeedback) -> None:
        return None

    @abc.abstractmethod
    def get_arguments(self, parameters, context, feedback: QgsProcessingFeedback) -> List[str]:
        return None

    @abc.abstractmethod
    def process_field(self, parameter_name, parameters, context,
                      feedback: QgsProcessingFeedback) -> None:
        return None

    @staticmethod
    @abc.abstractmethod
    def command() -> str:
        return None

    @abc.abstractmethod
    def return_dict(self) -> Dict[str, str]:
        return None

    @staticmethod
    def prepare_arguments() -> List[str]:
        return None

    def get_console_commands(self, parameters, context,
                             feedback: QgsProcessingFeedback) -> List[str]:

        arguments = self.get_arguments(parameters, context, feedback)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.mapshaper_input,
            output_data_path=self.mapshaper_output,
            command=self.name(),
            arguments=arguments,
            clean_before=self.clean_data_before,
            clean_after=self.clean_data_after)

        return commands

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):

        self.prepare_data(parameters, context, feedback)

        commands = self.get_console_commands(parameters, context, feedback)

        ms = MapshaperProcess()
        ms.setArguments(commands)
        ms.run()

        feedback.pushInfo("COMMAND TO RUN:")
        feedback.pushInfo(ms.command_to_run())
        feedback.pushInfo("RESULT:")

        if ms.output_lines:
            feedback.pushInfo(ms.output_lines)

        if ms.error_lines:
            feedback.pushWarning(ms.output_lines)

        self.process_output_layer(feedback)

        return self.return_dict()

    @property
    def simplified_field_full_name(self) -> str:
        if self.simplify_field:
            return self.simplify_field
        return None

    @property
    def simplified_field_shortened(self) -> str:
        if self.simplify_field:
            return self.simplify_field[0:10]
        return None

    def process_input_layer(self, parameter_name, parameters, context,
                            feedback: QgsProcessingFeedback) -> None:

        layer = self.parameterAsVectorLayer(parameters, parameter_name, context)

        if not layer:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))

        self.input_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(layer)

        fields = []

        join_field_index = QMapshaperDataPreparer.add_mapshaper_id_field(self.input_layer_memory)

        fields.append(join_field_index)

        if self.simplify_field:
            index = self.input_layer_memory.fields().lookupField(self.simplified_field_full_name)
            fields.append(index)

        QMapshaperDataPreparer.write_layer_with_minimal_attributes(layer=self.input_layer_memory,
                                                                   file=self.mapshaper_input,
                                                                   col_index=fields)

    def process_output_layer(self, feedback: QgsProcessingFeedback):

        layer_generalized = QgsVectorLayer(self.mapshaper_output, "data", "ogr")

        memory_layer = QMapshaperDataPreparer.copy_to_memory_layer(layer_generalized)

        memory_layer.setCrs(self.input_layer_memory.crs())

        QMapshaperDataPreparer.join_fields_back(memory_layer, self.input_layer_memory)

        QMapshaperDataPreparer.write_output_file(layer=memory_layer,
                                                 file=self.result_layer_location,
                                                 layer_name=self.input_layer_memory.name())

    def icon(self):

        location = Path(__file__).parent.parent / "icons" / "main_icon.png"

        return QIcon(location.absolute().as_posix())
