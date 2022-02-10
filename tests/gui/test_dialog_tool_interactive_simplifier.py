from pathlib import Path
import pytest

from pytestqt.qtbot import QtBot

from qgis.core import (QgsProject, QgsVectorLayer)
from qgis.gui import (QgisInterface, QgsMapCanvas)
from qgis.PyQt.QtCore import QThread

from qmapshaper.gui.dialog_tool_interactive_simplifier import InteractiveSimplifierTool


@pytest.mark.qt_no_exception_capture
def test(data_layer: QgsVectorLayer, qgis_iface: QgisInterface, qgis_parent,
         qgis_canvas: QgsMapCanvas, qgis_new_project, qtbot: QtBot):

    assert isinstance(data_layer, QgsVectorLayer)

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    assert qgis_canvas.layerCount() == 1

    # dialog = InteractiveSimplifierTool(qgis_parent, qgis_iface)

    # assert isinstance(dialog.layer_selection.currentLayer(), QgsVectorLayer)

    # with qtbot.waitSignal(dialog.input_data_changed, timeout=3000, raising=True):
    #     dialog.update_input_layer()

    # def test_1():
    #     assert Path(dialog.process.input_data_filename).exists()

    # qtbot.wait_until(test_1)

    # assert isinstance(dialog.canvas, QgsMapCanvas)

    # assert dialog.canvas.extent().contains(data_layer.extent())

    # with qtbot.waitSignals(
    #     [dialog.process.generalized_layer_prepared, dialog.data_generalized, dialog.map_updated]):
    #     dialog.generalize_layer()

    # def check_data_1():
    #     assert dialog.process.generalized_data_only_geometry == "a"

    # qtbot.waitUntil(check_data_1)

    # def check_data_2():
    #     assert dialog.process.generalized_data_with_attributes.featureCount(
    #     ) == data_layer.featureCount()
    #     assert dialog.process.generalized_data_with_attributes.fields().count(
    #     ) == data_layer.fields().count()

    # qtbot.waitUntil(check_data_2)

    # assert isinstance(dialog.get_layer_for_project(), QgsVectorLayer)
    # assert dialog.get_layer_for_project().featureCount() == data_layer.featureCount()

    # layer = dialog.get_layer_for_project()

    # assert isinstance(layer, QgsVectorLayer)
    # assert layer.fields().names() == data_layer.fields().names()
    # assert layer.crs().toWkt() == data_layer.crs().toWkt()
    # assert layer.featureCount() == data_layer.featureCount()
    # assert layer.wkbType() == data_layer.wkbType()

    # dialog.accept()

    # def no_tasks_running():
    #     assert dialog.threadpool.activeThreadCount() == 0

    # qtbot.waitUntil(no_tasks_running)

    # dialog.reject()

    # QThread.sleep(5)
