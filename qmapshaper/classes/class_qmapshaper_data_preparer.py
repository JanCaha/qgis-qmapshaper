from typing import List, Union

from qgis.core import (QgsVectorLayer, QgsVectorLayerUtils, QgsMemoryProviderUtils,
                       QgsVectorFileWriter, QgsCoordinateTransformContext, QgsVectorLayerJoinInfo,
                       QgsField, QgsFeatureSink)
from qgis.PyQt.QtCore import QVariant

from processing.algs.gdal.GdalUtils import GdalUtils

from ..text_constants import TextConstants
from .class_qmapshaper_file import QMapshaperFile, QMapshaperGeojsonFile


class QMapshaperDataPreparer:

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
    def write_layer_with_minimal_attributes(layer: QgsVectorLayer, file: str,
                                            col_index: Union[int, List[int]]) -> None:

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = QMapshaperFile.driver_name()

        if isinstance(col_index, int):
            options.attributes = [col_index]
        else:
            options.attributes = col_index

        QgsVectorFileWriter.writeAsVectorFormatV3(layer=layer,
                                                  fileName=file,
                                                  transformContext=QgsCoordinateTransformContext(),
                                                  options=options)

    @staticmethod
    def write_layer_with_as_geojson(layer: QgsVectorLayer,
                                    file: str,
                                    decimal_precision: int = None) -> None:

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = QMapshaperGeojsonFile.driver_name()

        if decimal_precision:
            options.layerOptions = ["COORDINATE_PRECISION={}".format(decimal_precision)]

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
    def join_fields_back(layer_to_join_to: QgsVectorLayer,
                         layer_to_join_from: QgsVectorLayer,
                         prefix: str = "") -> None:

        join = QgsVectorLayerJoinInfo()
        join.setTargetFieldName(TextConstants.JOIN_FIELD_NAME)
        join.setJoinLayer(layer_to_join_from)
        join.setJoinFieldName(TextConstants.JOIN_FIELD_NAME)
        join.setUsingMemoryCache(True)
        join.setPrefix(prefix)

        layer_to_join_to.addJoin(join)

    @staticmethod
    def add_mapshaper_id_field(layer: QgsVectorLayer) -> int:

        layer.startEditing()

        field_index = layer.addExpressionField(
            "$id", QgsField(TextConstants.JOIN_FIELD_NAME, QVariant.Int))

        layer.commitChanges()

        return field_index
