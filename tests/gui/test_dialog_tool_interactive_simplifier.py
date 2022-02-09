import pytest

from pytestqt.qtbot import QtBot

from qgis.core import (QgsProject, QgsVectorLayer, QgsApplication)
from qgis.gui import (QgisInterface, QgsMapCanvas)

from qmapshaper.gui.dialog_tool_interactive_simplifier import InteractiveSimplifierTool


@pytest.mark.qt_no_exception_capture
def test(data_layer: QgsVectorLayer, qgis_iface: QgisInterface, qgis_parent,
         qgis_canvas: QgsMapCanvas, qgis_new_project, qtbot: QtBot, qgis_app: QgsApplication):

    assert isinstance(data_layer, QgsVectorLayer)

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    assert qgis_canvas.layerCount() == 1

    dialog = InteractiveSimplifierTool(qgis_parent, qgis_iface)

    qtbot.addWidget(dialog)

    assert isinstance(dialog.layer_selection.currentLayer(), QgsVectorLayer)

    with qtbot.waitSignal(dialog.input_data_changed, timeout=3000, raising=True):
        dialog.update_input_layer()

    assert isinstance(dialog.canvas, QgsMapCanvas)

    assert dialog.canvas.extent().contains(data_layer.extent())

    with qtbot.waitSignal(dialog.process.generalized_layer_changed, timeout=5000):
        dialog.process.generalize_layer(50, "dp")

    with qtbot.waitSignal(dialog.process.generalized_layer_prepared, timeout=5000):
        dialog.process.load_generalized_layer()

    with qtbot.waitSignal(dialog.map_updated, timeout=5000):
        dialog.load_generalized_data()

    def check_data_1():
        assert dialog.process.generalized_data_only_geometry.featureCount(
        ) == data_layer.featureCount()

    qtbot.waitUntil(check_data_1)

    with qtbot.waitSignal(dialog.map_updated, timeout=5000):
        dialog.load_generalized_data()

    def check_data_2():
        assert dialog.process.generalized_data_with_attributes.featureCount(
        ) == data_layer.featureCount()
        assert dialog.process.generalized_data_with_attributes.fields().count(
        ) == data_layer.fields().count()

    qtbot.waitUntil(check_data_2)

    assert isinstance(dialog.get_layer_for_project(), QgsVectorLayer)
    assert dialog.get_layer_for_project().featureCount() == data_layer.featureCount()

    layer = dialog.get_layer_for_project()

    assert isinstance(layer, QgsVectorLayer)
    assert layer.fields().names() == data_layer.fields().names()
    assert layer.crs().toWkt() == data_layer.crs().toWkt()
    assert layer.featureCount() == data_layer.featureCount()
    assert layer.wkbType() == data_layer.wkbType()

    dialog.accept()

    def no_tasks_running():
        assert dialog.threadpool.activeThreadCount() == 0

    qtbot.waitUntil(no_tasks_running)

    dialog.reject()
