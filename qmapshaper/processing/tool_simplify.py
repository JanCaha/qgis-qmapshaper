from typing import Dict, List, Union

from qgis.core import (
    QgsProcessingFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterVectorLayer,
)

from .mapshaper_algorithm import MapshaperAlgorithm


class SimplifyAlgorithm(MapshaperAlgorithm):
    INPUT_LAYER = "Input"
    SIMPLIFY = "Simplify"
    METHOD = "Method"
    FIELD = "Field"
    CLEAN_DATA = "CleanData"
    OUTPUT_LAYER = "Output"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_LAYER, "Input layer"))

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIMPLIFY,
                "Simplify %",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=50,
                minValue=1,
                maxValue=99,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD, "Simplification method", options=list(self.methods().keys()), defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                "Perform simplification based on feature field",
                parentLayerParameterName=self.INPUT_LAYER,
                optional=True,
                allowMultiple=False,
            )
        )

        self.addParameter(QgsProcessingParameterBoolean(self.CLEAN_DATA, "Clean data prior and after simplification"))

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_LAYER, "Output Layer"))

    def prepare_data(self, parameters, context, feedback: QgsProcessingFeedback) -> None:
        self.process_field(self.FIELD, parameters, context, feedback)

        self.process_input_layer(self.INPUT_LAYER, parameters, context, feedback)

        self.result_layer_location = self.parameterAsOutputLayer(parameters, self.OUTPUT_LAYER, context)

    def process_field(self, field_name: str, parameters, context, feedback: QgsProcessingFeedback) -> None:
        field = self.parameterAsFields(parameters, field_name, context)

        if field:
            field = field[0]

        self.simplify_field = field

    def get_arguments(self, parameters, context, feedback: QgsProcessingFeedback):
        clean_data = self.parameterAsBool(parameters, self.CLEAN_DATA, context)

        self.clean_data_before = clean_data
        self.clean_data_after = clean_data

        simplify_percent = self.parameterAsDouble(parameters, self.SIMPLIFY, context)

        method = self.parameterAsEnum(parameters, self.METHOD, context)

        method = self.get_method(method)

        planar = not self.input_layer_memory.crs().isGeographic()

        arguments = self.prepare_arguments(
            simplify_percent=simplify_percent, method=method, planar=planar, field=self.simplified_field_shortened
        )

        return arguments

    def return_dict(self) -> Dict[str, str]:
        return {self.OUTPUT_LAYER: self.result_layer_location}

    @staticmethod
    def command() -> str:
        return "simplify"

    def name(self):
        return SimplifyAlgorithm.command()

    def displayName(self):
        return "Simplify Vector"

    def createInstance(self):
        return SimplifyAlgorithm()

    @staticmethod
    def prepare_arguments(
        simplify_percent: Union[int, float, str] = 50, method: str = "dp", planar: bool = False, field: str = None
    ) -> List[str]:
        arguments = [method]

        if field:
            arguments.extend(
                ["variable", "percentage", "=", "{} ? {} : 1".format(field, float(simplify_percent) / 100)]
            )

        else:
            arguments.append("{}%".format(simplify_percent))

        arguments.append("keep-shapes")

        if planar:
            arguments.append("planar")

        return arguments

    @staticmethod
    def methods() -> Dict[str, str]:
        return {"Douglas-Peucker": "dp", "Visvalingam": "visvalingam"}

    @staticmethod
    def get_method(index: int) -> str:
        return list(SimplifyAlgorithm.methods().values())[index]
