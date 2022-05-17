import pytest
from pathlib import Path

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination, QgsVectorLayer,
                       QgsProcessingFeedback, QgsProcessingContext, QgsProcessingOutputVectorLayer,
                       QgsProcessingParameterEnum)

from qmapshaper.processing.tool_simplify_lines import SimplifyPolygonLinesAlgorithm


def test_parameters():

    alg = SimplifyPolygonLinesAlgorithm()

    alg.initAlgorithm()

    assert alg.countVisibleParameters() == 6

    parameter = alg.parameterDefinition("Input")

    assert isinstance(parameter, QgsProcessingParameterVectorLayer)

    parameter = alg.parameterDefinition("Simplify")

    assert isinstance(parameter, QgsProcessingParameterNumber)

    parameter = alg.parameterDefinition("Method")

    assert isinstance(parameter, QgsProcessingParameterEnum)

    parameter = alg.parameterDefinition("Lines")

    assert isinstance(parameter, QgsProcessingParameterEnum)

    parameter = alg.parameterDefinition("Output")

    assert isinstance(parameter, QgsProcessingParameterVectorDestination)


def test_outputs():

    alg = SimplifyPolygonLinesAlgorithm()

    alg.initAlgorithm()

    assert len(alg.outputDefinitions()) == 1

    assert isinstance(alg.outputDefinitions()[0], QgsProcessingOutputVectorLayer)


@pytest.mark.parametrize("params", [{
    "Simplify": 50,
    "Method": 0,
    "Lines": 0,
    "CleanData": False,
    "Output": "TEMPORARY_OUTPUT"
}, {
    "Simplify": 50,
    "Method": 1,
    "CleanData": False,
    "Lines": 0
}, {
    "Simplify": 50,
    "Method": 0,
    "CleanData": True,
    "Lines": 1
}],
                         ids=["temporary_output", "lines_0", "lines_1"])
def test_parameter_combinations(data_layer, data_result_file, params):

    params.update({"Input": data_layer})

    if "Output" not in params.keys():
        params.update({"Output": data_result_file})

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = SimplifyPolygonLinesAlgorithm()

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

    assert layer.featureCount() > 0
    assert layer.featureCount() >= 404
