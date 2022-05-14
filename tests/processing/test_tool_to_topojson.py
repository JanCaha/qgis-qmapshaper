import pytest
from pathlib import Path

from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterField,
                       QgsProcessingParameterNumber, QgsProcessingParameterFileDestination,
                       QgsVectorLayer, QgsProcessingFeedback, QgsProcessingContext,
                       QgsProcessingOutputFile)

from qmapshaper.processing.tool_to_topojson import ConvertToTopoJSONAlgorithm


def test_parameters():

    alg = ConvertToTopoJSONAlgorithm()

    alg.initAlgorithm()

    assert alg.countVisibleParameters() == 4

    parameter = alg.parameterDefinition("Input")

    assert isinstance(parameter, QgsProcessingParameterVectorLayer)

    parameter = alg.parameterDefinition("Fields")

    assert isinstance(parameter, QgsProcessingParameterField)

    parameter = alg.parameterDefinition("DecimalNumbers")

    assert isinstance(parameter, QgsProcessingParameterNumber)

    parameter = alg.parameterDefinition("OutputFile")

    assert isinstance(parameter, QgsProcessingParameterFileDestination)


def test_outputs():

    alg = ConvertToTopoJSONAlgorithm()

    alg.initAlgorithm()

    assert len(alg.outputDefinitions()) == 1

    assert isinstance(alg.outputDefinitions()[0], QgsProcessingOutputFile)


@pytest.mark.parametrize("params", [{
    "Fields": [],
    "DecimalNumbers": 3,
    "OutputFile": "TEMPORARY_OUTPUT"
}, {
    "Fields": [],
    "DecimalNumbers": 3,
}, {
    "Fields": ["generalized"],
    "DecimalNumbers": 3,
}],
                         ids=["temporary_output", "without_field", "with_field"])
def test_parameter_combinations(data_layer, data_result_path, params):

    output_filename = None

    params.update({"Input": data_layer})

    if "OutputFile" not in params.keys():
        output_filename = "test.topojson"
        data_result_file = Path(data_result_path) / output_filename
        params.update({"OutputFile": data_result_file.as_posix()})

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = ConvertToTopoJSONAlgorithm()

    alg.initAlgorithm()

    can_run, param_check_msg = alg.checkParameterValues(parameters=params, context=context)

    assert param_check_msg == ""
    assert can_run

    result = alg.run(parameters=params, context=context, feedback=feedback)

    assert isinstance(result, tuple)
    assert result[1]
    assert len(result[0]) == len(alg.outputDefinitions())
    assert "OutputFile" in result[0].keys()

    layer = QgsVectorLayer(result[0]["OutputFile"], "layer", "ogr")

    assert isinstance(layer, QgsVectorLayer)

    if output_filename:
        assert output_filename in layer.source()
    else:
        assert "OutputFile.topojson" in layer.source()

    assert Path(layer.source()).exists()
    assert layer.featureCount() == 404
