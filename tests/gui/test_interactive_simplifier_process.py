from pathlib import Path

from qgis.core import (QgsVectorLayer)

from qmapshaper.gui.interactive_simplifier_process import InteractiveSimplifierProcess


def test_steps(data_layer, qtbot):

    process = InteractiveSimplifierProcess()

    assert process.memory_layer is None
    assert process.input_data_filename == ""

    process.set_input_data(data_layer)

    assert isinstance(process.memory_layer, QgsVectorLayer)
    assert process.memory_layer.featureCount() == data_layer.featureCount()

    assert isinstance(process.input_data_filename, str)
    assert Path(process.input_data_filename).exists()

    with qtbot.waitSignal(process.generalized_layer_changed, timeout=10000):
        process.generalize_layer(50, "dp")

    assert isinstance(process.generalized_data_filename, str)
    assert Path(process.generalized_data_filename).exists()

    assert isinstance(process.generalized_data_only_geometry, QgsVectorLayer)

    assert process.generalized_data_only_geometry.fields().count() == 1
    assert process.generalized_data_only_geometry.featureCount() == data_layer.featureCount()

    assert isinstance(process.generalized_data_only_geometry, QgsVectorLayer)

    assert process.generalized_data_with_attributes.fields().count() == data_layer.fields().count()

    assert "generalized" in process.generalized_data_with_attributes.name()
    assert process.generalized_data_with_attributes.crs().toWkt() == data_layer.crs().toWkt()
    assert process.generalized_data_with_attributes.featureCount() == data_layer.featureCount()
