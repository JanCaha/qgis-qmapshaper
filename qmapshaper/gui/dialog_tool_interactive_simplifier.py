from pathlib import Path

from qgis.core import (QgsProject, QgsVectorLayer, QgsMapLayerProxyModel, QgsProcessingFeedback)
from qgis.gui import (QgsMapCanvas, QgsMapLayerComboBox, QgisInterface)
from qgis.PyQt.QtWidgets import QDialog, QLabel, QVBoxLayout, QSlider, QPushButton, QComboBox
from qgis.PyQt.QtCore import Qt

from ..processing.tool_simplify import SimplifyAlgorithm
from ..utils import log, features_count_with_non_empty_geoms
from ..text_constants import TextConstants
from ..classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ..classes.class_qmapshaper_file import QMapshaperFile
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ..classes.class_qmapshaper_runner import QMapshaperRunner


class InteractiveSimplifierTool(QDialog):

    label_text: QLabel
    percent_slider: QSlider
    canvas: QgsMapCanvas
    layer_selection: QgsMapLayerComboBox
    button_insert: QPushButton
    methods: QComboBox

    memory_layer: QgsVectorLayer = None

    base_data_filename: str = ""
    base_data_layer: QgsVectorLayer = None

    generalized_data_filename: str = ""
    generalized_data_layer: QgsVectorLayer = None

    def __init__(self, parent=None, iface: QgisInterface = None):

        super().__init__(parent)

        self.iface = iface

        self.setWindowTitle(TextConstants.tool_name_interactive_simplifier)

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.layer_selection = QgsMapLayerComboBox()
        self.layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.layer_selection.layerChanged.connect(self.update_layer)

        self.percent_slider = QSlider(Qt.Horizontal)
        self.percent_slider.setMinimum(1)
        self.percent_slider.setMaximum(99)
        self.percent_slider.setValue(50)
        self.percent_slider.sliderReleased.connect(self.update_generalized_layer)

        self.methods = QComboBox(self)
        self.methods.addItems(SimplifyAlgorithm.methods().keys())

        self.methods.currentIndexChanged.connect(self.update_generalized_layer)

        self.canvas = QgsMapCanvas(self)

        self.button_insert = QPushButton(self)
        self.button_insert.setText("Export layer back to project")
        self.button_insert.clicked.connect(self.send_layer_to_project)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(QLabel("Layer"))
        self.vlayout.addWidget(self.layer_selection)
        self.vlayout.addWidget(QLabel("Simplify to %"))
        self.vlayout.addWidget(self.percent_slider)
        self.vlayout.addWidget(QLabel("Method"))
        self.vlayout.addWidget(self.methods)
        self.vlayout.addWidget(QLabel("Map"))
        self.vlayout.addWidget(self.canvas)
        self.vlayout.addWidget(self.button_insert)
        self.setLayout(self.vlayout)

        self.update_layer()

    def update_layer(self) -> None:

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

        self.update_generalized_layer()

    def update_generalized_layer(self) -> None:

        if self.generalized_data_filename:
            path = Path(self.generalized_data_filename)
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)

        self.generalized_data_filename = QMapshaperFile.random_temp_filename()

        arguments = SimplifyAlgorithm.prepare_arguments(
            simplify_percent=self.percent_slider.value(),
            method=SimplifyAlgorithm.get_method(self.methods.currentIndex()))

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.base_data_filename,
            output_data_path=self.generalized_data_filename,
            command=SimplifyAlgorithm.command(),
            arguments=arguments)

        log(f"COMMAND TO RUN: {' '.join(commands)}")

        QMapshaperRunner.run_mapshaper(commands, QgsProcessingFeedback())

        log(f"Data to load: {self.generalized_data_filename}")

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
