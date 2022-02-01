from qgis.core import (QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum, QgsProcessingParameterVectorDestination,
                       QgsProcessingFeedback, QgsProcessingContext, QgsProcessingOutputVectorLayer)

from qmapshaper.processing.tool_simplify import SimplifyAlgorithm


def test_parameters():

    alg = SimplifyAlgorithm()

    alg.initAlgorithm()

    assert alg.countVisibleParameters() == 4

    parameter = alg.parameterDefinition("INPUT")

    assert isinstance(parameter, QgsProcessingParameterVectorLayer)

    parameter = alg.parameterDefinition("SIMPLIFY")

    assert isinstance(parameter, QgsProcessingParameterNumber)

    parameter = alg.parameterDefinition("METHOD")

    assert isinstance(parameter, QgsProcessingParameterEnum)

    parameter = alg.parameterDefinition("OUTPUT")

    assert isinstance(parameter, QgsProcessingParameterVectorDestination)


def test_outputs():

    alg = SimplifyAlgorithm()

    alg.initAlgorithm()

    assert len(alg.outputDefinitions()) == 1

    assert isinstance(alg.outputDefinitions()[0], QgsProcessingOutputVectorLayer)


def test_input_data(data_layer, data_result_file):

    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()

    alg = SimplifyAlgorithm()

    alg.initAlgorithm()

    parameters = {"INPUT": data_layer, "SIMPLIFY": 12, "METHOD": 0, "OUTPUT": "TEMPORARY_OUTPUT"}

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
    assert "OUTPUT" in result[0].keys()

    parameters = {"INPUT": data_layer, "SIMPLIFY": 12, "METHOD": 0, "OUTPUT": data_result_file}

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
    assert "OUTPUT" in result[0].keys()
