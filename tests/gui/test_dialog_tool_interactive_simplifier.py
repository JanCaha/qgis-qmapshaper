from pathlib import Path
import pytest
import time

from pytestqt.qtbot import QtBot

from qgis.core import (QgsProject, QgsVectorLayer, QgsApplication)
from qgis.gui import (QgisInterface, QgsMapCanvas, QgsMapLayerComboBox)
from qgis.PyQt.QtCore import (QThread, QCoreApplication, Qt, pyqtSignal, pyqtBoundSignal)
from qgis.PyQt.QtWidgets import (QSlider, QLabel, QSpinBox, QDialogButtonBox, QComboBox)

from qmapshaper.gui.dialog_tool_interactive_simplifier import InteractiveSimplifierTool


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
    dialog.show()

    assert isinstance(dialog.percent_slider, QSlider)
    assert isinstance(dialog.percent_spin_box, QSpinBox)
    assert isinstance(dialog.layer_selection, QgsMapLayerComboBox)
    assert isinstance(dialog.methods, QComboBox)
    assert isinstance(dialog.canvas, QgsMapCanvas)
    assert isinstance(dialog.button_box, QDialogButtonBox)

    assert isinstance(dialog.map_updated, pyqtBoundSignal)
    assert isinstance(dialog.data_generalized, pyqtBoundSignal)
    assert isinstance(dialog.input_data_changed, pyqtBoundSignal)
    assert isinstance(dialog.input_parameters_changed, pyqtBoundSignal)

    assert isinstance(dialog.layer_selection.currentLayer(), QgsVectorLayer)

    dialog.process.export_for_generalization()

    def test_1():
        assert Path(dialog.process.input_data_filename).exists()

    qtbot.waitUntil(test_1)

    qgis_app.processEvents()
    time.sleep(5)

    dialog.hide()

    dialog.accept()
