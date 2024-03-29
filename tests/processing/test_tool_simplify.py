from pathlib import Path
import pytest

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum, QgsProcessingParameterVectorDestination,
                       QgsProcessingFeedback, QgsProcessingContext, QgsProcessingOutputVectorLayer,
                       QgsVectorLayer, QgsProcessingParameterField, QgsProcessingParameterBoolean)

from qmapshaper.processing.tool_simplify import SimplifyAlgorithm


def test_parameters():

    alg = SimplifyAlgorithm()

    alg.initAlgorithm()

    assert alg.countVisibleParameters() == 6

    parameter = alg.parameterDefinition("Input")

    assert isinstance(parameter, QgsProcessingParameterVectorLayer)

    parameter = alg.parameterDefinition("Simplify")

    assert isinstance(parameter, QgsProcessingParameterNumber)

    parameter = alg.parameterDefinition("Method")

    assert isinstance(parameter, QgsProcessingParameterEnum)

    parameter = alg.parameterDefinition("Output")

    assert isinstance(parameter, QgsProcessingParameterVectorDestination)

    parameter = alg.parameterDefinition("Field")

    assert isinstance(parameter, QgsProcessingParameterField)

    parameter = alg.parameterDefinition("CleanData")

    assert isinstance(parameter, QgsProcessingParameterBoolean)


def test_outputs():

    alg = SimplifyAlgorithm()

    alg.initAlgorithm()

    assert len(alg.outputDefinitions()) == 1

    assert isinstance(alg.outputDefinitions()[0], QgsProcessingOutputVectorLayer)


@pytest.mark.parametrize("params", [{
    "Simplify": 12,
    "Method": 0,
    "Output": "TEMPORARY_OUTPUT",
    "CleanData": False
}, {
    "Simplify": 12,
    "Method": 0,
    "Field": "generalized",
    "CleanData": True
}, {
    "Simplify": 12,
    "Method": 0,
    "CleanData": True
}, {
    "Simplify": 12,
    "Method": 0,
    "CleanData": False
}],
                         ids=["temporary_output", "with_field", "clean_data", "dont_clean_data"])
def test_parameter_combinations(data_layer, data_result_file, params):

    params.update({"Input": data_layer})

    if "Output" not in params.keys():
        params.update({"Output": data_result_file})

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = SimplifyAlgorithm()

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
    assert layer.featureCount() == 404
    assert layer.crs().isValid()
