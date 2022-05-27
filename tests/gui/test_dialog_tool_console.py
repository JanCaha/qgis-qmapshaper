from pathlib import Path
import time
import pytest
import os

from pytestqt.qtbot import QtBot

from qgis.core import (QgsProject, QgsVectorLayer, QgsApplication)
from qgis.gui import (QgisInterface, QgsMapCanvas, QgsMapLayerComboBox, QgsFieldComboBox)
from qgis.PyQt.QtCore import (pyqtBoundSignal)
from qgis.PyQt.QtWidgets import (QDialogButtonBox, QLineEdit)

from qmapshaper.gui.dialog_tool_console import InteractiveConsoleTool


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") is not None, reason="Skip on Github Actions.")
def test_elements(data_layer: QgsVectorLayer, qgis_canvas: QgsMapCanvas, qgis_iface: QgisInterface,
                  qgis_parent):

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    dialog = InteractiveConsoleTool(qgis_parent, qgis_iface)

    assert isinstance(dialog.layer_selection, QgsMapLayerComboBox)
    assert isinstance(dialog.field, QgsFieldComboBox)
    assert isinstance(dialog.canvas, QgsMapCanvas)
    assert isinstance(dialog.button_box, QDialogButtonBox)
    assert isinstance(dialog.console_command, QLineEdit)

    assert isinstance(dialog.map_updated, pyqtBoundSignal)
    assert isinstance(dialog.data_processed, pyqtBoundSignal)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") is not None, reason="Skip on Github Actions.")
def test_usage(data_layer: QgsVectorLayer, qgis_iface: QgisInterface, qgis_parent,
               qgis_canvas: QgsMapCanvas, qgis_new_project, qtbot: QtBot,
               qgis_app: QgsApplication):

    assert isinstance(data_layer, QgsVectorLayer)

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    assert qgis_canvas.layerCount() == 1

    dialog = InteractiveConsoleTool(qgis_parent, qgis_iface)

    qtbot.addWidget(dialog)
    dialog.show()

    assert isinstance(dialog.layer_selection.currentLayer(), QgsVectorLayer)

    dialog.process.export_for_processing()

    def test_1():
        assert Path(dialog.process.input_data_filename).exists()

    qtbot.waitUntil(test_1)

    with qtbot.waitSignal(dialog.data_processed):
        dialog.set_input_data()

    with qtbot.waitSignal(dialog.data_processed):
        dialog.console_command.setText("-clean -simplify dp 1% -clean")

    assert dialog.canvas.layerCount() == 1

    assert isinstance(dialog.get_layer_for_project(), QgsVectorLayer)
    assert dialog.get_layer_for_project().featureCount() == 404

    dialog.hide()

    dialog.accept()

    dialog.destroy()
