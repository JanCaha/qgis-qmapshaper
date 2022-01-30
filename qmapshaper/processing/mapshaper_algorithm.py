from pathlib import Path
from uuid import uuid4

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingUtils, QgsVectorFileWriter,
                       QgsCoordinateTransformContext, QgsVectorLayer, QgsField,
                       QgsVectorLayerJoinInfo, QgsProcessingFeedback, QgsMemoryProviderUtils,
                       QgsVectorLayerUtils, QgsProcessingException)
from processing.algs.gdal.GdalUtils import GdalUtils

from ..utils import QMapshaperUtils, log
from ..text_constants import TextConstants


class MapshaperAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

        self.input_layer_memory: QgsVectorLayer = None

        self.mapshaper_output = self.prepare_random_temp_filename()

        self.mapshaper_input = self.prepare_random_temp_filename()

        self.output_layer_location = ""

    def icon(self):

        location = Path(__file__).parent.parent / "icons" / "main_icon.png"

        return QIcon(location.absolute().as_posix())

    def run_command(self):

        bin_path = Path(QMapshaperUtils.mapshaper_bin_folder()) / self.commandName()

        return bin_path.absolute().as_posix()

    def commandName(self):
        return None

    def getConsoleCommands(self,
                           parameters,
                           context,
                           feedback: QgsProcessingFeedback,
                           executing=True):

        return [self.run_command()] + self.getConsoleArguments(
            parameters, context, feedback, executing=True)

    def getConsoleArguments(self, parameters, context, feedback, executing=True):
        return None

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):

        commands = self.getConsoleCommands(parameters, context, feedback, executing=True)

        QMapshaperUtils.runMapshaper(commands, feedback)

        self.process_output_layer(feedback)

        return {}

    def process_input_layer(self, parameter_name, parameters, context,
                            feedback: QgsProcessingFeedback) -> None:

        layer = self.parameterAsVectorLayer(parameters, parameter_name, context)

        if not layer:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))

        self.input_layer_memory = self.copy_to_memory_layer(layer)

        self.input_layer_memory.startEditing()

        join_field_index = self.input_layer_memory.addExpressionField(
            "$id", QgsField(TextConstants.JOIN_FIELD_NAME, QVariant.Int))

        self.input_layer_memory.commitChanges()

        self.write_layer_with_single_attribute(layer=self.input_layer_memory,
                                               file=self.mapshaper_input,
                                               col_index=join_field_index)

        return self.mapshaper_input

    def process_output_layer(self, feedback: QgsProcessingFeedback):

        layer_generalized = QgsVectorLayer(self.mapshaper_output, "data", "ogr")

        memory_layer = self.copy_to_memory_layer(layer_generalized)

        memory_layer.setCrs(self.input_layer_memory.crs())

        self.join_fields_back(memory_layer, self.input_layer_memory)

        self.write_output_file(layer=memory_layer,
                               file=self.output_layer_location,
                               layer_name=self.input_layer_memory.name())

    @staticmethod
    def join_fields_back(layer_to_join_to: QgsVectorLayer,
                         layer_to_join_from: QgsVectorLayer) -> None:

        join = QgsVectorLayerJoinInfo()
        join.setTargetFieldName(TextConstants.JOIN_FIELD_NAME)
        join.setJoinLayer(layer_to_join_from)
        join.setJoinFieldName(TextConstants.JOIN_FIELD_NAME)
        join.setUsingMemoryCache(True)

        layer_to_join_to.addJoin(join)

    @staticmethod
    def copy_to_memory_layer(layer: QgsVectorLayer) -> QgsVectorLayer:

        memory_layer = QgsMemoryProviderUtils.createMemoryLayer(layer.name(), layer.fields(),
                                                                layer.wkbType(), layer.crs())

        memory_layer.startEditing()

        for feature in layer.getFeatures():
            features = QgsVectorLayerUtils.makeFeatureCompatible(feature, memory_layer)
            memory_layer.addFeatures(features)

        memory_layer.commitChanges()

        return memory_layer

    @staticmethod
    def write_layer_with_single_attribute(layer: QgsVectorLayer, file: str,
                                          col_index: int) -> None:

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.attributes = [col_index]

        QgsVectorFileWriter.writeAsVectorFormatV3(layer=layer,
                                                  fileName=file,
                                                  transformContext=QgsCoordinateTransformContext(),
                                                  options=options)

    @staticmethod
    def write_output_file(layer: QgsVectorLayer, file: str, layer_name: str) -> None:

        fields = layer.fields()

        fields_indexes = [x for x in range(0, fields.count())]

        field_join_index = fields.lookupField(TextConstants.JOIN_FIELD_NAME)

        if field_join_index in fields_indexes:
            fields_indexes.remove(field_join_index)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = GdalUtils.getVectorDriverFromFileName(file)
        options.layerName = layer_name
        options.attributes = fields_indexes
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        QgsVectorFileWriter.writeAsVectorFormatV3(layer=layer,
                                                  fileName=file,
                                                  transformContext=QgsCoordinateTransformContext(),
                                                  options=options)

    @staticmethod
    def prepare_random_temp_filename() -> str:
        return QgsProcessingUtils.generateTempFilename("{}.shp".format(uuid4()))

    @staticmethod
    def add_mapshaper_id_field(layer: QgsVectorLayer) -> int:

        layer.startEditing()

        field_index = layer.addExpressionField(
            "$id", QgsField(TextConstants.JOIN_FIELD_NAME, QVariant.Int))

        layer.commitChanges()

        return field_index

    @staticmethod
    def output_format() -> str:
        return "shapefile"
