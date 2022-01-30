from typing import List, Union

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
                       QgsProcessingFeedback, QgsProcessingParameterVectorDestination)

from .mapshaper_algorithm import MapshaperAlgorithm


class SimplifyAlgorithm(MapshaperAlgorithm):

    INPUT_LAYER = "INPUT"
    SIMPLIFY = "SIMPLIFY"
    OUTPUT_LAYER = "OUTPUT"

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_LAYER, "Input layer"))

        self.addParameter(
            QgsProcessingParameterNumber(self.SIMPLIFY,
                                         "Simplify %",
                                         type=QgsProcessingParameterNumber.Integer,
                                         defaultValue=50,
                                         minValue=1,
                                         maxValue=99))

        self.addParameter(
            QgsProcessingParameterVectorDestination(self.OUTPUT_LAYER, "Output Layer"))

    def getConsoleArguments(self,
                            parameters,
                            context,
                            feedback: QgsProcessingFeedback,
                            executing=True):

        input_layer = self.process_input_layer(self.INPUT_LAYER, parameters, context, feedback)

        self.output_layer_location = self.parameterAsOutputLayer(parameters, self.OUTPUT_LAYER,
                                                                 context)

        simplify_percent = self.parameterAsDouble(parameters, self.SIMPLIFY, context)

        arguments = self.prepare_arguments(input_file_name=input_layer,
                                           output_file_name=self.mapshaper_output,
                                           simplify_percent=simplify_percent)

        return arguments

    def commandName(self):
        return self.get_command()

    def name(self):
        return "simplify"

    def displayName(self):
        return "Simplify vector"

    def createInstance(self):
        return SimplifyAlgorithm()

    @staticmethod
    def get_command() -> str:
        return "mapshaper-xl"

    @staticmethod
    def prepare_arguments(input_file_name: str,
                          output_file_name: str,
                          simplify_percent: Union[int, float, str] = 50,
                          method: str = "dp") -> List[str]:

        arguments = [
            input_file_name,
            '-simplify',
            method,
            '{}%'.format(simplify_percent),
            'keep-shapes',
            '-o',
            'format={}'.format(MapshaperAlgorithm.output_format()),
            output_file_name,
        ]

        return arguments
