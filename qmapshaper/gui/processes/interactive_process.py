from pathlib import Path
from typing import Optional, List
import random
import shutil
import platform

from qgis.core import (QgsVectorLayer, QgsSingleSymbolRenderer, QgsFillSymbol)
from qgis.PyQt.QtCore import (QObject, pyqtSignal)
from qgis.PyQt.QtWidgets import (QDialog)

from ...classes.class_qmapshaper_file import QMapshaperFile
from ...classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer
from ...classes.class_qmapshaper_runner import MapshaperProcess
from ...text_constants import TextConstants
from ...utils import log


class InteractiveProcess(QObject):

    memory_layer: QgsVectorLayer = None
    stored_ids: List[int] = []

    process_selection: bool = False
    process_selected_features: bool = True

    clean_data: bool = False

    input_data_filename: str = ""

    field: str = None

    processed_data_filename: str = None
    _processed_data_layer: QgsVectorLayer = None

    _processed_data_layer_memory: QgsVectorLayer = None

    input_layer_changed = pyqtSignal()
    processed_layer_changed = pyqtSignal()
    processed_layer_prepared = pyqtSignal()

    parent_gui: QDialog

    result_layer_name: str = ""

    def __init__(self, parent: QDialog = None) -> None:

        super().__init__()

        self.parent_gui = parent

        self.input_layer_changed.connect(self.export_for_processing)
        self.processed_layer_changed.connect(self.load_processed_layer)

    def set_input_data(self, layer: QgsVectorLayer) -> None:

        if self.process_selection:

            self.stored_ids = layer.selectedFeatureIds()

        generalize_field_index = QMapshaperDataPreparer.add_mapshaper_generalization_field(
            layer, self.stored_ids, self.process_selected_features)

        self.memory_layer = QMapshaperDataPreparer.copy_to_memory_layer(layer)

        layer.removeExpressionField(generalize_field_index)

        self.input_layer_changed.emit()

    def export_for_processing(self) -> None:

        self.input_data_filename = QMapshaperFile.random_temp_filename()

        field_index_id = QMapshaperDataPreparer.add_mapshaper_id_field(self.memory_layer)

        fields = [field_index_id]

        if self.process_selection and self.stored_ids:

            field_index_generalization = self.memory_layer.fields().lookupField(
                TextConstants.GENERALIZATION_FIELD_NAME)
            fields.append(field_index_generalization)

        if self.field:
            required_field = self.memory_layer.fields().lookupField(self.field)
            fields.append(required_field)

        QMapshaperDataPreparer.write_layer_with_minimal_attributes(layer=self.memory_layer,
                                                                   file=self.input_data_filename,
                                                                   col_index=fields)
        log(f"Data stored at: {self.input_data_filename}")

    def remove_previous_data(self) -> None:

        self._processed_data_layer = None

        if self.processed_data_filename and platform.system() != "Windows":
            path = Path(self.processed_data_filename)
            if path.exists() and path.is_file():
                shutil.rmtree(path.parent)

    def load_processed_layer(self) -> None:

        self._processed_data_layer = QgsVectorLayer(self.processed_data_filename,
                                                    "{} data".format(self.result_layer_name),
                                                    "ogr")

        self._processed_data_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(
            self._processed_data_layer)

        QMapshaperDataPreparer.join_fields_back(self._processed_data_layer_memory,
                                                self.memory_layer)

        self._processed_data_layer_memory = QMapshaperDataPreparer.copy_to_memory_layer(
            self._processed_data_layer_memory)

        fields_to_delete = []

        index = self._processed_data_layer_memory.fields().lookupField(
            TextConstants.JOIN_FIELD_NAME)

        fields_to_delete.append(index)

        self._processed_data_layer_memory.startEditing()
        self._processed_data_layer_memory.deleteAttributes(fields_to_delete)
        self._processed_data_layer_memory.commitChanges()

        self._processed_data_layer_memory.setName("{} {}".format(self.memory_layer.name(),
                                                                 self.result_layer_name))
        self._processed_data_layer_memory.setCrs(self.memory_layer.crs())

        if self._processed_data_layer.renderer() is None:

            random_number = random.randint(0, 16777215)
            hex_number = str(hex(random_number))
            hex_number = '#' + hex_number[2:]

            sym1 = QgsFillSymbol.createSimple({'color': hex_number})
            renderer = QgsSingleSymbolRenderer(sym1)

            self._processed_data_layer_memory.setRenderer(renderer)

        else:

            self._processed_data_layer_memory.setRenderer(
                self._processed_data_layer.renderer().clone())

        self.processed_layer_prepared.emit()

    @property
    def processed_data_with_attributes(self) -> QgsVectorLayer:
        return self._processed_data_layer_memory

    @property
    def processed_data_only_geometry(self) -> Optional[QgsVectorLayer]:

        if self._processed_data_layer:
            return self._processed_data_layer
        else:
            return None

    def processed_layer_updated(self) -> None:

        self.processed_layer_changed.emit()

    def run_mapshaper_process(self, commands: List[str]) -> None:

        process = MapshaperProcess()

        process.finished.connect(self.processed_layer_updated)

        process.setArguments(commands)

        process.run()

    def apply_selection_to_generalized_data(self) -> None:

        index = self.processed_data_only_geometry.fields().indexOf(
            TextConstants.GENERALIZATION_FIELD_NAME)

        value = 1

        if not self.process_selected_features:
            value = 0

        if -1 < index:

            expr = "{} = {}".format(TextConstants.GENERALIZATION_FIELD_NAME, value)

            self.processed_data_only_geometry.selectByExpression(expr)
