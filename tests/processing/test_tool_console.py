import pytest
from pathlib import Path

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterString,
                       QgsProcessingParameterVectorDestination, QgsProcessingParameterField,
                       QgsProcessingOutputVectorLayer, QgsProcessingFeedback, QgsProcessingContext,
                       QgsVectorLayer)

from qmapshaper.processing.tool_console import ConsoleAlgorithm

TEXT_QUOTE_1 = "-simplify dp variable percentage = 'TYPE == \"lines\" ? 0.1 : 1'"
TEXT_QUOTE_2 = "-simplify dp variable percentage = \"TYPE == 'lines' ? 0.1 : 1\""


def test_extract_parts():

    assert ConsoleAlgorithm.extract_parts(ConsoleAlgorithm.regex_quoted(),
                                          TEXT_QUOTE_1) == ['TYPE == "lines" ? 0.1 : 1']

    assert ConsoleAlgorithm.extract_parts(ConsoleAlgorithm.regex_quoted(),
                                          TEXT_QUOTE_2) == ["TYPE == 'lines' ? 0.1 : 1"]


def test_replace_parts():

    assert ConsoleAlgorithm.replace_parts(ConsoleAlgorithm.regex_quoted(),
                                          TEXT_QUOTE_1) == '-simplify dp variable percentage = ---'

    assert ConsoleAlgorithm.replace_parts(ConsoleAlgorithm.regex_quoted(),
                                          TEXT_QUOTE_2) == "-simplify dp variable percentage = ---"


def test_replace_parts_back():

    replacements = ConsoleAlgorithm.extract_parts(ConsoleAlgorithm.regex_quoted(), TEXT_QUOTE_1)

    text_replaced = ConsoleAlgorithm.replace_parts(ConsoleAlgorithm.regex_quoted(), TEXT_QUOTE_1)

    assert ConsoleAlgorithm.replace_parts_back(text_replaced, replacements) ==\
        ['-simplify', 'dp', 'variable', 'percentage', '=', 'TYPE == "lines" ? 0.1 : 1']


def test_split_text_into_parts():

    assert ConsoleAlgorithm.split_text_into_parts(TEXT_QUOTE_1) ==\
        ['-simplify', 'dp', 'variable', 'percentage', '=', 'TYPE == "lines" ? 0.1 : 1']

    assert ConsoleAlgorithm.split_text_into_parts(TEXT_QUOTE_2) ==\
        ['-simplify', 'dp', 'variable', 'percentage', '=', 'TYPE == \'lines\' ? 0.1 : 1']


def test_parameters():

    alg = ConsoleAlgorithm()

    alg.initAlgorithm()

    assert alg.countVisibleParameters() == 4

    parameter = alg.parameterDefinition("Input")

    assert isinstance(parameter, QgsProcessingParameterVectorLayer)

    parameter = alg.parameterDefinition("Console")

    assert isinstance(parameter, QgsProcessingParameterString)

    parameter = alg.parameterDefinition("Field")

    assert isinstance(parameter, QgsProcessingParameterField)

    parameter = alg.parameterDefinition("Output")

    assert isinstance(parameter, QgsProcessingParameterVectorDestination)


def test_outputs():

    alg = ConsoleAlgorithm()

    alg.initAlgorithm()

    assert len(alg.outputDefinitions()) == 1

    assert isinstance(alg.outputDefinitions()[0], QgsProcessingOutputVectorLayer)


@pytest.mark.parametrize("params,featureCount", [
    ({
        "Console": "-clean -simplify dp 1% -clean"
    }, 404),
    ({
        "Field": "generalized",
        "Console": '-simplify dp variable percentage = "generalize ? 0.1 : 1"'
    }, 404),
])
def test_parameter_combinations(data_layer, data_result_file, params, featureCount):

    params.update({"Input": data_layer})

    if "Output" not in params.keys():
        params.update({"Output": data_result_file})

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = ConsoleAlgorithm()

    alg.initAlgorithm()

    can_run, param_check_msg = alg.checkParameterValues(parameters=params, context=context)

    assert param_check_msg == ""
    assert can_run

    result = alg.run(parameters=params, context=context, feedback=feedback)

    assert isinstance(result, tuple)
    assert result[1]
    assert len(result[0]) == len(alg.outputDefinitions())
    assert "Output" in result[0].keys()

    layer = QgsVectorLayer(result[0]["Output"], "layer", "ogr")

    assert isinstance(layer, QgsVectorLayer)
    assert Path(layer.source()).exists()
    assert layer.featureCount() == featureCount
