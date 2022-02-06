from typing import List, Dict

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterField,
                       QgsProcessingFeedback, QgsProcessingParameterFileDestination, QgsField,
                       QgsProcessingParameterNumber, QgsProcessingException)

from .mapshaper_algorithm import MapshaperAlgorithm
from ..classes.class_qmapshaper_file import QMapshaperGeojsonFile, QMapshaperTopoJsonFile
from ..classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder


class ConvertToTopoJSONAlgorithm(MapshaperAlgorithm):

    INPUT_LAYER = "Input"
    OUTPUT_FILE = "OutputFile"
    DECIMAL_NUMBERS = "DecimalNumbers"
    FIELDS = "Fields"

    def __init__(self):
        super().__init__()

        self.mapshaper_output = QMapshaperTopoJsonFile.random_temp_filename()

        self.mapshaper_input = QMapshaperGeojsonFile.random_temp_filename()

        self.fields_to_retain = []

        self.output_layer = None

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_LAYER, "Input layer"))

        self.addParameter(
            QgsProcessingParameterField(self.FIELDS,
                                        "Select fields to retain",
                                        parentLayerParameterName=self.INPUT_LAYER,
                                        allowMultiple=True,
                                        optional=True))

        self.addParameter(
            QgsProcessingParameterNumber(self.DECIMAL_NUMBERS,
                                         "Number of decimal places for coordinates",
                                         defaultValue=3,
                                         minValue=0,
                                         maxValue=16,
                                         type=QgsProcessingParameterNumber.Integer))

        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_FILE,
                                                  "Output TopoJSON",
                                                  fileFilter="Topojson (*.topojson)"))

    def prepare_data(self, parameters, context, feedback: QgsProcessingFeedback) -> None:

        self.fields_to_retain = self.parameterAsFields(parameters, self.FIELDS, context)

        self.process_input_layer(self.INPUT_LAYER, parameters, context, feedback)

        self.result_layer_location = self.parameterAsFileOutput(parameters, self.OUTPUT_FILE,
                                                                context)

        self.mapshaper_output = self.result_layer_location

    def process_input_layer(self, parameter_name, parameters, context,
                            feedback: QgsProcessingFeedback) -> None:

        layer = self.parameterAsVectorLayer(parameters, parameter_name, context)

        decimal_numbers = self.parameterAsInt(parameters, self.DECIMAL_NUMBERS, context)

        if not layer:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))

        self.input_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(layer)

        self.input_layer_memory.startEditing()

        fields_existing = self.input_layer_memory.fields()
        fields_to_delete = []

        field: QgsField

        for field in fields_existing:

            if field.name() not in self.fields_to_retain:

                fields_to_delete.append(fields_existing.indexFromName(field.name()))

        if 0 < len(fields_to_delete):
            self.input_layer_memory.deleteAttributes(fields_to_delete)

        self.input_layer_memory.commitChanges()

        QMapshaperDataPreparer.write_layer_with_as_geojson(layer=self.input_layer_memory,
                                                           file=self.mapshaper_input,
                                                           decimal_precision=decimal_numbers)

    def get_arguments(self, parameters, context, feedback: QgsProcessingFeedback):

        arguments = self.prepare_arguments()

        return arguments

    def return_dict(self) -> Dict[str, str]:
        return {self.OUTPUT_FILE: self.result_layer_location}

    def process_output_layer(self, feedback: QgsProcessingFeedback):
        pass

    @staticmethod
    def command() -> str:
        return "clean"

    def name(self):
        return "totopojson"

    def displayName(self):
        return "Convert to TopoJSON"

    def createInstance(self):
        return ConvertToTopoJSONAlgorithm()

    @staticmethod
    def prepare_arguments() -> List[str]:

        arguments = ["allow-overlaps", "allow-empty"]

        return arguments

    def get_console_commands(self, parameters, context,
                             feedback: QgsProcessingFeedback) -> List[str]:

        arguments = self.get_arguments(parameters, context, feedback)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.mapshaper_input,
            output_data_path=self.mapshaper_output,
            command=ConvertToTopoJSONAlgorithm.command(),
            arguments=arguments)

        return commands
