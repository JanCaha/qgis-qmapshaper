from pathlib import Path
from typing import Optional, List
import random

from qgis.core import (QgsVectorLayer, QgsSingleSymbolRenderer, QgsFillSymbol)
from qgis.PyQt.QtCore import (QObject, pyqtSignal)
from qgis.PyQt.QtWidgets import (QDialog)

from ..classes.class_qmapshaper_file import QMapshaperFile
from ..classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ..classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder
from ..classes.class_qmapshaper_runner import MapshaperProcess
from ..processing.tool_simplify import SimplifyAlgorithm
from ..text_constants import TextConstants
from ..utils import log


class InteractiveSimplifierProcess(QObject):

    memory_layer: QgsVectorLayer = None

    input_data_filename: str = ""

    generalized_data_filename: str = ""
    _generalized_data_layer: QgsVectorLayer = None

    _generalized_data_layer_memory: QgsVectorLayer = None

    input_layer_changed = pyqtSignal()
    generalized_layer_changed = pyqtSignal()
    generalized_layer_prepared = pyqtSignal()

    parent_gui: QDialog

    def __init__(self, parent: QDialog = None) -> None:

        super().__init__()

        self.parent_gui = parent

        self.input_layer_changed.connect(self.export_for_generalization)
        self.generalized_layer_changed.connect(self.load_generalized_layer)

    def set_input_data(self, layer: QgsVectorLayer) -> None:

        self.memory_layer = QMapshaperDataPreparer.copy_to_memory_layer(layer)

        self.input_layer_changed.emit()

    def export_for_generalization(self) -> None:

        self.input_data_filename = QMapshaperFile.random_temp_filename()

        field_index = QMapshaperDataPreparer.add_mapshaper_id_field(self.memory_layer)

        QMapshaperDataPreparer.write_layer_with_single_attribute(layer=self.memory_layer,
                                                                 file=self.input_data_filename,
                                                                 col_index=field_index)
        log(f"Data stored at: {self.input_data_filename}")

    def generalize_layer(self, simplify_percent: float, simplify_method: str) -> None:

        if self.generalized_data_filename:
            path = Path(self.generalized_data_filename)
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)

        self.generalized_data_filename = QMapshaperFile.random_temp_filename()

        arguments = SimplifyAlgorithm.prepare_arguments(simplify_percent=simplify_percent,
                                                        method=simplify_method)

        commands = QMapshaperCommandBuilder.prepare_console_commands(
            input_data_path=self.input_data_filename,
            output_data_path=self.generalized_data_filename,
            command=SimplifyAlgorithm.command(),
            arguments=arguments)

        log(f"COMMAND TO RUN: {' '.join(commands)}")

        self.run_mapshaper_process(commands)

        log(f"Data to load: {self.generalized_data_filename}")

    def load_generalized_layer(self) -> None:

        self._generalized_data_layer = QgsVectorLayer(self.generalized_data_filename,
                                                      "generalized data", "ogr")

        self._generalized_data_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(
            self._generalized_data_layer)

        QMapshaperDataPreparer.join_fields_back(self._generalized_data_layer_memory,
                                                self.memory_layer)

        self._generalized_data_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(
            self._generalized_data_layer_memory)

        index = self._generalized_data_layer_memory.fields().lookupField(
            TextConstants.JOIN_FIELD_NAME)

        self._generalized_data_layer_memory.startEditing()
        self._generalized_data_layer_memory.deleteAttribute(index)
        self._generalized_data_layer_memory.commitChanges()

        self._generalized_data_layer_memory.setName("{} generalized".format(
            self.memory_layer.name()))
        self._generalized_data_layer_memory.setCrs(self.memory_layer.crs())

        if self._generalized_data_layer.renderer() is None:

            random_number = random.randint(0, 16777215)
            hex_number = str(hex(random_number))
            hex_number = '#' + hex_number[2:]

            sym1 = QgsFillSymbol.createSimple({'color': hex_number})
            renderer = QgsSingleSymbolRenderer(sym1)

            self._generalized_data_layer_memory.setRenderer(renderer)

        else:

            self._generalized_data_layer_memory.setRenderer(
                self._generalized_data_layer.renderer().clone())

        self.generalized_layer_prepared.emit()

    @property
    def generalized_data_with_attributes(self) -> QgsVectorLayer:
        return self._generalized_data_layer_memory

    @property
    def generalized_data_only_geometry(self) -> Optional[QgsVectorLayer]:

        if self._generalized_data_layer:
            return self._generalized_data_layer
        else:
            return None

    def generalized_layer_updated(self) -> None:

        self.generalized_layer_changed.emit()

    def run_mapshaper_process(self, commands: List[str]) -> None:

        process = MapshaperProcess()

        process.finished.connect(self.generalized_layer_updated)

        process.setArguments(commands)

        process.run()
