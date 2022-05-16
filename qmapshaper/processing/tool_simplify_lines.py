from typing import List, Union, Dict

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum, QgsProcessingFeedback,
                       QgsProcessingParameterVectorDestination, QgsProcessingParameterField,
                       QgsProcessingParameterBoolean, QgsProcessing)

from .mapshaper_algorithm import MapshaperAlgorithm
from ..text_constants import TextConstants


class SimplifyPolygonLinesAlgorithm(MapshaperAlgorithm):

    INPUT_LAYER = "Input"
    SIMPLIFY = "Simplify"
    METHOD = "Method"
    LINES = "Lines"
    CLEAN_DATA = "CleanData"
    OUTPUT_LAYER = "Output"

    def __init__(self):
        super().__init__()

        self.needs_join = True
        self.join_fid_field_back = False

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(self.INPUT_LAYER, "Input layer",
                                              [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(
            QgsProcessingParameterNumber(self.SIMPLIFY,
                                         "Simplify %",
                                         type=QgsProcessingParameterNumber.Integer,
                                         defaultValue=50,
                                         minValue=1,
                                         maxValue=99))

        self.addParameter(
            QgsProcessingParameterEnum(self.METHOD,
                                       "Simplification method",
                                       options=list(self.methods().keys()),
                                       defaultValue=0))

        self.addParameter(
            QgsProcessingParameterEnum(self.LINES,
                                       "Generalize polygon's lines",
                                       options=list(self.lines().keys()),
                                       defaultValue=0))

        self.addParameter(
            QgsProcessingParameterBoolean(self.CLEAN_DATA,
                                          "Clean data prior and after simplification"))

        self.addParameter(
            QgsProcessingParameterVectorDestination(self.OUTPUT_LAYER, "Output Layer"))

    def prepare_data(self, parameters, context, feedback: QgsProcessingFeedback) -> None:

        self.process_input_layer(self.INPUT_LAYER, parameters, context, feedback)

        self.result_layer_location = self.parameterAsOutputLayer(parameters, self.OUTPUT_LAYER,
                                                                 context)

    def get_arguments(self, parameters, context, feedback: QgsProcessingFeedback):

        clean_data = self.parameterAsBool(parameters, self.CLEAN_DATA, context)

        self.clean_data_before = clean_data
        self.clean_data_after = clean_data

        simplify_percent = self.parameterAsDouble(parameters, self.SIMPLIFY, context)

        method = self.parameterAsEnum(parameters, self.METHOD, context)

        method = self.get_method(method)

        lines_type = self.parameterAsEnum(parameters, self.LINES, context)

        lines_type = self.get_lines(lines_type)

        planar = not self.input_layer_memory.crs().isGeographic()

        arguments = self.prepare_arguments(simplify_percent=simplify_percent,
                                           method=method,
                                           lines=lines_type,
                                           planar=planar,
                                           join_file=self.mapshaper_join)

        return arguments

    def return_dict(self) -> Dict[str, str]:
        return {self.OUTPUT_LAYER: self.result_layer_location}

    @staticmethod
    def command() -> str:
        return "lines"

    def name(self):
        return SimplifyPolygonLinesAlgorithm.command()

    def displayName(self):
        return "Simplify Polygon Lines"

    def createInstance(self):
        return SimplifyPolygonLinesAlgorithm()

    @staticmethod
    def prepare_arguments(simplify_percent: Union[int, float, str] = 50,
                          lines: str = "inner",
                          method: str = "dp",
                          planar: bool = False,
                          join_file: str = None) -> List[str]:

        arguments = [
            '-simplify',
            method,
            'variable',
            'percentage',
            '=',
            'TYPE == "{}" ? {} : 1'.format(lines,
                                           float(simplify_percent) / 100),
        ]

        arguments.append('keep-shapes')

        if planar:
            arguments.append('planar')

        arguments.append('-polygons')

        if join_file:
            arguments.extend(['-join', 'largest-overlap', join_file])

        arguments.extend(['-filter-fields', TextConstants.JOIN_FIELD_NAME])

        arguments.extend(['-dissolve2', TextConstants.JOIN_FIELD_NAME])

        return arguments

    @staticmethod
    def methods() -> Dict[str, str]:
        return {"Douglas-Peucker": "dp", "Visvalingam": "visvalingam"}

    @staticmethod
    def get_method(index: int) -> str:
        return list(SimplifyPolygonLinesAlgorithm.methods().values())[index]

    @staticmethod
    def lines() -> Dict[str, str]:
        return {"Inner lines": "inner", "Outer lines": "outer"}

    @staticmethod
    def get_lines(index: int) -> str:
        return list(SimplifyPolygonLinesAlgorithm.lines().values())[index]
