from qgis.core import (QgsVectorLayer, QgsMapLayerProxyModel)
from qgis.gui import (QgsMapCanvas, QgsMapLayerComboBox, QgisInterface)
from qgis.PyQt.QtWidgets import (QDialog, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QComboBox,
                                 QSpinBox, QDialogButtonBox, QCheckBox)
from qgis.PyQt.QtCore import (Qt, QThreadPool, pyqtSignal)

from ..processing.tool_simplify import SimplifyAlgorithm
from ..utils import log
from ..text_constants import TextConstants
from ..classes.classes_workers import WaitWorker
from .interactive_simplifier_process import InteractiveSimplifierProcess

TEXT_MODIFY_PART_OF_DATA = "Modify only part of data based on selection"
TEXT_NO_SELECTION = "No selection on the layer"


class InteractiveSimplifierTool(QDialog):

    percent_slider: QSlider
    percent_spin_box: QSpinBox
    canvas: QgsMapCanvas
    layer_selection: QgsMapLayerComboBox
    methods: QComboBox
    button_box: QDialogButtonBox

    threadpool: QThreadPool

    wait_worker: WaitWorker
    """
    Worker that waits for small amount of time (current 0.2 second). Helps avoid calling MapshaperProcess to often.
    Generally, the value of percent_spin_box needs to be stable while this run to trigger the data generalization.
    """

    process: InteractiveSimplifierProcess

    map_updated = pyqtSignal()
    data_generalized = pyqtSignal()

    def __init__(self, parent=None, iface: QgisInterface = None):

        super().__init__(parent)

        self.process = InteractiveSimplifierProcess(parent=self)

        self.process.generalized_layer_prepared.connect(self.load_generalized_data)

        self.iface = iface

        self.setWindowTitle(TextConstants.tool_name_interactive_simplifier)

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.threadpool = QThreadPool()

        self.layer_selection = QgsMapLayerComboBox(self)
        self.layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.layer_selection.layerChanged.connect(self.set_input_data)

        self.percent_slider = QSlider(Qt.Horizontal)
        self.percent_slider.setMinimum(1)
        self.percent_slider.setMaximum(99)
        self.percent_slider.setValue(50)
        self.percent_slider.sliderReleased.connect(self.slider_value_change)
        self.percent_slider.valueChanged.connect(self.slider_value_change)

        self.percent_spin_box = QSpinBox()
        self.percent_spin_box.setSuffix("%")
        self.percent_spin_box.setMinimum(1)
        self.percent_spin_box.setMaximum(99)
        self.percent_spin_box.setValue(50)
        self.percent_spin_box.setReadOnly(True)

        self.percent_spin_box.valueChanged.connect(self.spinner_value_change)

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

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.percent_slider)
        self.hlayout.addWidget(self.percent_spin_box)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(QLabel("Layer"))
        self.vlayout.addWidget(self.layer_selection)
        self.vlayout.addWidget(QLabel("Simplify to %"))
        self.vlayout.addLayout(self.hlayout)
        self.vlayout.addWidget(QLabel("Method"))
        self.vlayout.addWidget(self.methods)
        self.vlayout.addWidget(QLabel("Generalize part of layer"))
        self.vlayout.addWidget(self.modify_only_part)
        self.vlayout.addWidget(QLabel("Selection"))
        self.vlayout.addWidget(self.modify_selection)
        self.vlayout.addWidget(QLabel("Map"))
        self.vlayout.addWidget(self.canvas)
        self.vlayout.addWidget(self.button_box)
        self.setLayout(self.vlayout)

        self.setup_canvas()

        self.set_input_data()

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
                self.modify_only_part.setText(TEXT_MODIFY_PART_OF_DATA)
            else:
                self.modify_only_part.setEnabled(False)
                self.modify_only_part.setText(TEXT_NO_SELECTION)

            self.generalize_layer()

    def generalize_layer(self) -> None:

        self.process.generalize_layer(simplify_percent=self.percent_spin_box.value(),
                                      simplify_method=SimplifyAlgorithm.get_method(
                                          self.methods.currentIndex()))

        self.data_generalized.emit()

    def load_generalized_data(self) -> None:

        if self.process.generalized_data_only_geometry:

            self.process.apply_selection_to_generalized_data()

            self.canvas.setLayers([self.process.generalized_data_only_geometry])
            self.canvas.redrawAllLayers()

        self.map_updated.emit()

    def get_layer_for_project(self) -> QgsVectorLayer:

        return self.process.generalized_data_with_attributes

    def slider_value_change(self):

        self.percent_spin_box.setValue(self.percent_slider.value())

    def spinner_value_change(self):

        self.create_wait_worker()

    def run_update(self, percent: int):

        log(f"Prev: {percent} - curr: {self.percent_spin_box.value()}")

        if percent == self.percent_spin_box.value():
            self.trigger_input_parameters_change()

    def trigger_input_parameters_change(self) -> None:

        self.generalize_layer()

    def create_wait_worker(self) -> None:

        wait_worker = WaitWorker(self.percent_spin_box.value())
        wait_worker.signals.percent.connect(self.run_update)

        self.threadpool.start(wait_worker)

    def set_selection(self):

        self.modify_selection.setEnabled(self.modify_only_part.isChecked())

        self.process.generalize_select = self.modify_only_part.isChecked()

        self.set_input_data()
        self.generalize_layer()

    def set_generalization_type(self):

        self.process.generalize_select_features = self.modify_selection.currentData()

        self.set_input_data()
        self.generalize_layer()
