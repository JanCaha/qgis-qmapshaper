from pathlib import Path

from qgis.core import (QgsVectorLayer)

from qmapshaper.gui.processes.interactive_console_process import InteractiveConsoleProcess


def test_steps(data_layer, qtbot):

    process = InteractiveConsoleProcess()

    assert process.memory_layer is None
    assert process.input_data_filename == ""

    process.set_input_data(data_layer)

    assert isinstance(process.memory_layer, QgsVectorLayer)
    assert process.memory_layer.featureCount() == data_layer.featureCount()

    assert isinstance(process.input_data_filename, str)
    assert Path(process.input_data_filename).exists()

    with qtbot.waitSignal(process.processed_layer_changed, timeout=10000):
        process.process_layer(console_call="-clean -simplify dp 1% -clean")

    assert isinstance(process.processed_data_filename, str)
    assert Path(process.processed_data_filename).exists()

    assert isinstance(process.processed_data_only_geometry, QgsVectorLayer)

    assert process.processed_data_only_geometry.fields().count() == 1
    assert process.processed_data_only_geometry.featureCount() == data_layer.featureCount()

    assert isinstance(process.processed_data_only_geometry, QgsVectorLayer)

    assert process.processed_data_with_attributes.fields().count() == data_layer.fields().count()

    assert "processed" in process.processed_data_with_attributes.name()
    assert process.processed_data_with_attributes.crs().toWkt() == data_layer.crs().toWkt()
    assert process.processed_data_with_attributes.featureCount() == data_layer.featureCount()
