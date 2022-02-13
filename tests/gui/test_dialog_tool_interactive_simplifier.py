from pathlib import Path
import time

from pytestqt.qtbot import QtBot

from qgis.core import (QgsProject, QgsVectorLayer, QgsApplication)
from qgis.gui import (QgisInterface, QgsMapCanvas, QgsMapLayerComboBox)
from qgis.PyQt.QtCore import (pyqtBoundSignal)
from qgis.PyQt.QtWidgets import (QSlider, QSpinBox, QDialogButtonBox, QComboBox)

from qmapshaper.gui.dialog_tool_interactive_simplifier import InteractiveSimplifierTool


def test_elements(data_layer: QgsVectorLayer, qgis_canvas: QgsMapCanvas, qgis_iface: QgisInterface,
                  qgis_parent):

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    dialog = InteractiveSimplifierTool(qgis_parent, qgis_iface)

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


def test_usage(data_layer: QgsVectorLayer, qgis_iface: QgisInterface, qgis_parent,
               qgis_canvas: QgsMapCanvas, qgis_new_project, qtbot: QtBot,
               qgis_app: QgsApplication):

    assert isinstance(data_layer, QgsVectorLayer)

    qgs_project = QgsProject.instance()

    qgs_project.addMapLayer(data_layer)

    qgis_canvas.setProject(qgs_project)
    qgis_canvas.zoomToFullExtent()

    assert qgis_canvas.layerCount() == 1

    dialog = InteractiveSimplifierTool(qgis_parent, qgis_iface)

    qtbot.addWidget(dialog)
    dialog.show()

    assert isinstance(dialog.layer_selection.currentLayer(), QgsVectorLayer)

    dialog.process.export_for_generalization()

    def test_1():
        assert Path(dialog.process.input_data_filename).exists()

    qtbot.waitUntil(test_1)

    with qtbot.waitSignal(dialog.input_data_changed):
        dialog.update_input_layer()

    with qtbot.waitSignal(dialog.map_updated):
        dialog.percent_slider.setValue(10)

    assert dialog.canvas.layerCount() == 1

    assert isinstance(dialog.get_layer_for_project(), QgsVectorLayer)
    assert dialog.get_layer_for_project().featureCount() == 404

    dialog.hide()

    dialog.accept()
