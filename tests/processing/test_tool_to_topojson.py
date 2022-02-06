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


def test_input_data_temp_file(data_layer_path):

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = ConvertToTopoJSONAlgorithm()

    alg.initAlgorithm()

    parameters = {
        "Input": data_layer_path,
        "Fields": [],
        "DecimalNumbers": 3,
        "OutputFile": "TEMPORARY_OUTPUT"
    }

    can_run, param_check_msg = alg.checkParameterValues(parameters=parameters, context=context)

    assert param_check_msg == ""
    assert can_run

    result = alg.run(parameters=parameters, context=context, feedback=feedback)

    assert isinstance(result, tuple)
    assert result[1]
    assert len(result[0]) == len(alg.outputDefinitions())
    assert "OutputFile" in result[0].keys()

    layer = QgsVectorLayer(result[0]["OutputFile"], "layer", "ogr")

    assert isinstance(layer, QgsVectorLayer)
    assert layer.featureCount() == 404


def test_input_data_specified_file(data_layer_path, data_result_path):

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = ConvertToTopoJSONAlgorithm()

    alg.initAlgorithm()

    data_result_file = Path(data_result_path) / "test.topojson"

    parameters = {
        "Input": data_layer_path,
        "Fields": [],
        "DecimalNumbers": 3,
        "OutputFile": data_result_file.as_posix()
    }

    can_run, param_check_msg = alg.checkParameterValues(parameters=parameters, context=context)

    assert param_check_msg == ""
    assert can_run

    result = alg.run(parameters=parameters,
                     context=context,
                     feedback=feedback,
                     catchExceptions=False)

    assert isinstance(result, tuple)
    assert result[1]
    assert len(result[0]) == len(alg.outputDefinitions())
    assert "OutputFile" in result[0].keys()

    layer = QgsVectorLayer(result[0]["OutputFile"], "layer", "ogr")

    assert isinstance(layer, QgsVectorLayer)
    assert layer.featureCount() == 404
