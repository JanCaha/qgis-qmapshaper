from qgis.core import (QgsVectorLayer, QgsMapLayerProxyModel)
from qgis.gui import (QgsMapCanvas, QgsMapLayerComboBox, QgisInterface)
from qgis.PyQt.QtWidgets import (QDialog, QLabel, QVBoxLayout, QComboBox, QDialogButtonBox,
                                 QCheckBox)
from qgis.PyQt.QtCore import (QThreadPool, pyqtSignal)

from ..processing.tool_simplify import SimplifyAlgorithm
from ..utils import log
from ..text_constants import TextConstants
from ..classes.classes_workers import WaitWorker
from .processes.interactive_simplifier_process import InteractiveSimplifierProcess
from .percentsliderspinbox import PercentSliderSpinBox


class InteractiveSimplifierTool(QDialog):

    map_updated = pyqtSignal()
    data_generalized = pyqtSignal()

    def __init__(self, parent=None, iface: QgisInterface = None):

        super().__init__(parent)

        self.process = InteractiveSimplifierProcess(parent=self)

        self.process.processed_layer_prepared.connect(self.load_generalized_data)

        self.iface = iface

        self.setWindowTitle(TextConstants.tool_name_interactive_simplifier)

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.threadpool = QThreadPool()
        self.wait_worker: WaitWorker = None

        self.set_up_ui()

        self.setup_canvas()

        self.set_input_data()

    def set_up_ui(self) -> None:

        self.layer_selection = QgsMapLayerComboBox(self)
        self.layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.layer_selection.layerChanged.connect(self.set_input_data)

        self.percent_widget = PercentSliderSpinBox(parent=self)
        self.percent_widget.valueChangedInteractionStopped.connect(self.generalize_layer)

        self.methods = QComboBox(self)
        self.methods.addItems(SimplifyAlgorithm.methods().keys())

        self.methods.currentIndexChanged.connect(self.trigger_input_parameters_change)

        self.canvas = QgsMapCanvas(self)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok, self)

        self.modify_only_part = QCheckBox("Generalize only part of layer (based on selection)",
                                          self)
        self.modify_only_part.stateChanged.connect(self.set_selection)

        self.modify_selection = QComboBox(self)
        self.modify_selection.addItem("Generalize only selected features", True)
        self.modify_selection.addItem("Generalize all not selected features", False)
        self.modify_selection.setEnabled(False)
        self.modify_selection.currentIndexChanged.connect(self.set_generalization_type)

        self.clean_data = QCheckBox("Clean data prior and after simplification", self)
        self.clean_data.stateChanged.connect(self.set_clean_data)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Layer"))
        layout.addWidget(self.layer_selection)
        layout.addWidget(QLabel("Simplify to %"))
        layout.addWidget(self.percent_widget)
        layout.addWidget(QLabel("Method"))
        layout.addWidget(self.methods)
        layout.addWidget(QLabel("Generalize part of layer"))
        layout.addWidget(self.modify_only_part)
        layout.addWidget(QLabel("Selection"))
        layout.addWidget(self.modify_selection)
        layout.addWidget(QLabel("Topologically clean data"))
        layout.addWidget(self.clean_data)
        layout.addWidget(QLabel("Map"))
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_box)

    def setup_canvas(self):
        self.canvas.setDestinationCrs(self.iface.mapCanvas().project().crs())
        self.canvas.setExtent(self.iface.mapCanvas().extent())
        self.canvas.setLayers([self.layer_selection.currentLayer()])

    def set_input_data(self):

        log(f"Modify only part: {self.modify_only_part.isChecked()}")

        if self.layer_selection.currentLayer():

            self.process.generalize_select = self.modify_only_part.isChecked()

            self.process.set_input_data(self.layer_selection.currentLayer())

            if self.layer_selection.currentLayer().selectedFeatureIds():
                self.modify_only_part.setEnabled(True)
                self.modify_only_part.setText(TextConstants.TEXT_MODIFY_PART_OF_DATA)
            else:
                self.modify_only_part.setEnabled(False)
                self.modify_only_part.setText(TextConstants.TEXT_NO_SELECTION)

            self.generalize_layer()

    def generalize_layer(self) -> None:

        self.process.process_layer(simplify_percent=self.percent_widget.value(),
                                   simplify_method=SimplifyAlgorithm.get_method(
                                       self.methods.currentIndex()))

        self.data_generalized.emit()

    def load_generalized_data(self) -> None:

        if self.process.processed_data_only_geometry:

            self.process.apply_selection_to_generalized_data()

            self.canvas.setLayers([self.process.processed_data_only_geometry])
            self.canvas.redrawAllLayers()

        self.map_updated.emit()

    def get_layer_for_project(self) -> QgsVectorLayer:

        return self.process.processed_data_with_attributes

    def trigger_input_parameters_change(self) -> None:

        self.generalize_layer()

    def set_selection(self):

        self.modify_selection.setEnabled(self.modify_only_part.isChecked())

        self.process.process_selection = self.modify_only_part.isChecked()

        self.set_input_data()
        self.generalize_layer()

    def set_generalization_type(self):

        self.process.process_selected_features = self.modify_selection.currentData()

        self.set_input_data()
        self.generalize_layer()

    def set_clean_data(self):

        self.process.clean_data = self.clean_data.isChecked()

        self.generalize_layer()
