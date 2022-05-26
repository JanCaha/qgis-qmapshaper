from typing import List, Union, Dict
import re

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingFeedback,
                       QgsProcessingParameterVectorDestination, QgsProcessingParameterString,
                       QgsProcessingParameterField)

from .mapshaper_algorithm import MapshaperAlgorithm
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder


class ConsoleAlgorithm(MapshaperAlgorithm):

    INPUT_LAYER = "Input"
    CONSOLE = "Console"
    OUTPUT_LAYER = "Output"
    FIELD = "Field"

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_LAYER, "Input layer"))

        self.addParameter(QgsProcessingParameterString(self.CONSOLE, "Console Command"))

        self.addParameter(
            QgsProcessingParameterField(self.FIELD,
                                        "Select field that is needed for command",
                                        parentLayerParameterName=self.INPUT_LAYER,
                                        optional=True,
                                        allowMultiple=False))

        self.addParameter(
            QgsProcessingParameterVectorDestination(self.OUTPUT_LAYER, "Output Layer"))

    def prepare_data(self, parameters, context, feedback: QgsProcessingFeedback) -> None:

        self.process_field(self.FIELD, parameters, context, feedback)

        self.process_input_layer(self.INPUT_LAYER, parameters, context, feedback)

        self.result_layer_location = self.parameterAsOutputLayer(parameters, self.OUTPUT_LAYER,
                                                                 context)

    def process_field(self, field_name: str, parameters, context,
                      feedback: QgsProcessingFeedback) -> None:

        field = self.parameterAsFields(parameters, field_name, context)

        if field:
            field = field[0]

        self.simplify_field = field

    def get_console_commands(self, parameters, context,
                             feedback: QgsProcessingFeedback) -> List[str]:

        console_command = self.parameterAsString(parameters, self.CONSOLE, context)

        list_of_commands = self.split_text_into_parts(console_command)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.mapshaper_input,
            output_data_path=self.mapshaper_output,
            command=list_of_commands[0],
            arguments=list_of_commands[1:],
            clean_before=self.clean_data_before,
            clean_after=self.clean_data_after)

        return commands

    def return_dict(self) -> Dict[str, str]:
        return {self.OUTPUT_LAYER: self.result_layer_location}

    def name(self):
        return "console"

    def displayName(self):
        return "Mapshaper Console"

    def createInstance(self):
        return ConsoleAlgorithm()

    @staticmethod
    def prepare_arguments(simplify_percent: Union[int, float, str] = 50,
                          method: str = "dp",
                          planar: bool = False,
                          field: str = None) -> List[str]:

        arguments = [method]

        if field:

            arguments.extend([
                "variable", "percentage", "=", "{} ? {} : 1".format(field,
                                                                    float(simplify_percent) / 100)
            ])

        else:

            arguments.append('{}%'.format(simplify_percent))

        arguments.append('keep-shapes')

        if planar:
            arguments.append("planar")

        return arguments

    @staticmethod
    def regex_quoted() -> re.Pattern:
        return re.compile("['|\"](.+)['|\"]")

    @staticmethod
    def split_text_into_parts(text: str) -> List[str]:

        replace_constant = "---"

        quoted_regex = ConsoleAlgorithm.regex_quoted()

        quoted_parts = ConsoleAlgorithm.extract_parts(quoted_regex, text)

        text_replaced = ConsoleAlgorithm.replace_parts(quoted_regex, text, replace_constant)

        return ConsoleAlgorithm.replace_parts_back(text_replaced,
                                                   quoted_parts,
                                                   replacement=replace_constant)

    @staticmethod
    def extract_parts(quoted_regex: re.Pattern, text: str) -> List[str]:

        quoted_parts = quoted_regex.findall(text)

        return quoted_parts

    @staticmethod
    def replace_parts(quoted_regex: re.Pattern, text: str, replacement: str = "---") -> List[str]:

        text_replaced = quoted_regex.sub(replacement, text)

        return text_replaced

    @staticmethod
    def replace_parts_back(base_text: str,
                           replacements: List[str],
                           split_by: str = " ",
                           replacement: str = "---") -> List[str]:

        text_splitted = base_text.split(" ")

        for quoted_part in replacements:
            for i, text in enumerate(text_splitted):
                if text == replacement:
                    text_splitted[i] = quoted_part

        return text_splitted
