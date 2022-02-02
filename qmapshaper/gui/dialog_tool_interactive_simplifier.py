from pathlib import Path

from qgis.core import (QgsProject, QgsVectorLayer, QgsMapLayerProxyModel)
from qgis.gui import (QgsMapCanvas, QgsMapLayerComboBox, QgisInterface)
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QComboBox, QSpinBox
from qgis.PyQt.QtCore import Qt, QThreadPool

from ..processing.tool_simplify import SimplifyAlgorithm
from ..utils import log, features_count_with_non_empty_geoms
from ..text_constants import TextConstants
from ..classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ..classes.class_qmapshaper_file import QMapshaperFile
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ..classes.classes_workers import ConvertWorker, WaitWorker


class InteractiveSimplifierTool(QDialog):

    label_text: QLabel
    percent_slider: QSlider
    percent_spin_box: QSpinBox
    canvas: QgsMapCanvas
    layer_selection: QgsMapLayerComboBox
    button_insert: QPushButton
    methods: QComboBox

    memory_layer: QgsVectorLayer = None

    base_data_filename: str = ""
    base_data_layer: QgsVectorLayer = None

    generalized_data_filename: str = ""
    generalized_data_layer: QgsVectorLayer = None

    threadpool: QThreadPool
    convert_worker: ConvertWorker
    """
    Worker that takes care of converting input layer into generalized version. Runs on solo thread to avoid blocking GUI.
    """
    wait_worker: WaitWorker
    """
    Worker that waits for small amount of time (current 0.2 second). Helps avoid calling ConvertWorker to often. 
    Generally, the value of percent_spin_box needs to be stable while this run to trigger the data generalization.
    """

    def __init__(self, parent=None, iface: QgisInterface = None):

        super().__init__(parent)

        self.iface = iface

        self.setWindowTitle(TextConstants.tool_name_interactive_simplifier)

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.threadpool = QThreadPool()

        self.create_convert_worker()

        self.layer_selection = QgsMapLayerComboBox()
        self.layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.layer_selection.layerChanged.connect(self.update_input_layer)

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

        self.methods.currentIndexChanged.connect(self.generalize_layer)

        self.canvas = QgsMapCanvas(self)

        self.button_insert = QPushButton(self)
        self.button_insert.setText("Export layer back to project")
        self.button_insert.clicked.connect(self.send_layer_to_project)

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
        self.vlayout.addWidget(QLabel("Map"))
        self.vlayout.addWidget(self.canvas)
        self.vlayout.addWidget(self.button_insert)
        self.setLayout(self.vlayout)

        self.update_input_layer()

    def update_input_layer(self) -> None:

        layer = self.layer_selection.currentLayer()

        self.memory_layer = QMapshaperDataPreparer.copy_to_memory_layer(layer)

        self.base_data_filename = QMapshaperFile.random_temp_filename()

        field_index = QMapshaperDataPreparer.add_mapshaper_id_field(self.memory_layer)

        QMapshaperDataPreparer.write_layer_with_single_attribute(layer=self.memory_layer,
                                                                 file=self.base_data_filename,
                                                                 col_index=field_index)

        log(f"Data stored at: {self.base_data_filename}")

        self.canvas.setDestinationCrs(self.iface.mapCanvas().project().crs())
        self.canvas.setExtent(self.iface.mapCanvas().extent())

        self.generalize_layer()

    def generalize_layer(self) -> None:

        if self.generalized_data_filename:
            path = Path(self.generalized_data_filename)
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)

        self.generalized_data_filename = QMapshaperFile.random_temp_filename()

        arguments = SimplifyAlgorithm.prepare_arguments(
            simplify_percent=self.percent_spin_box.value(),
            method=SimplifyAlgorithm.get_method(self.methods.currentIndex()))

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.base_data_filename,
            output_data_path=self.generalized_data_filename,
            command=SimplifyAlgorithm.command(),
            arguments=arguments)

        log(f"COMMAND TO RUN: {' '.join(commands)}")

        self.create_convert_worker()

        self.convert_worker.set_commands(commands)

        self.threadpool.start(self.convert_worker)

        log(f"Data to load: {self.generalized_data_filename}")

    def load_generalized_data(self) -> None:

        self.generalized_data_layer = QgsVectorLayer(self.generalized_data_filename, "geojson",
                                                     "ogr")

        if self.generalized_data_layer:

            log(f"Data source {self.generalized_data_layer.source()}")
            log(f"features {features_count_with_non_empty_geoms(self.generalized_data_layer)}")

            self.canvas.setLayers([self.generalized_data_layer])
            self.canvas.redrawAllLayers()

    def send_layer_to_project(self) -> None:

        generalized_layer = QMapshaperDataPreparer.copy_to_memory_layer(
            self.generalized_data_layer)

        QMapshaperDataPreparer.join_fields_back(generalized_layer, self.memory_layer)

        generalized_layer = QMapshaperDataPreparer.copy_to_memory_layer(generalized_layer)

        index = generalized_layer.fields().lookupField(TextConstants.JOIN_FIELD_NAME)

        generalized_layer.startEditing()
        generalized_layer.deleteAttribute(index)
        generalized_layer.commitChanges()

        generalized_layer.setName("{} generalized".format(self.memory_layer.name()))
        generalized_layer.setCrs(self.memory_layer.crs())

        QgsProject.instance().addMapLayer(generalized_layer)

    def slider_value_change(self):

        self.percent_spin_box.setValue(self.percent_slider.value())

    def spinner_value_change(self):

        self.create_wait_worker()

        self.threadpool.start(self.wait_worker)

    def run_update(self, percent: int):

        log(f"Prev: {percent} - curr: {self.percent_spin_box.value()}")

        if percent == self.percent_spin_box.value():
            self.generalize_layer()

    def create_convert_worker(self) -> None:
        self.convert_worker = ConvertWorker()
        self.convert_worker.signals.result.connect(self.load_generalized_data)

    def create_wait_worker(self) -> None:

        self.wait_worker = WaitWorker(self.percent_spin_box.value())
        self.wait_worker.signals.percent.connect(self.run_update)
