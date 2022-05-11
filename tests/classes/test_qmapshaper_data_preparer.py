from pathlib import Path

from qgis.core import (QgsVectorLayer)

from qmapshaper.text_constants import TextConstants
from qmapshaper.classes.class_qmapshaper_data_preparer import QMapshaperDataPreparer


def test_copy_to_memory_layer(data_layer):

    assert isinstance(data_layer, QgsVectorLayer)

    copied_in_memory = QMapshaperDataPreparer.copy_to_memory_layer(data_layer)

    assert isinstance(copied_in_memory, QgsVectorLayer)

    assert copied_in_memory.crs().toWkt() == data_layer.crs().toWkt()
    assert copied_in_memory.fields().names() == data_layer.fields().names()
    assert copied_in_memory.featureCount() == data_layer.featureCount()
    assert copied_in_memory.name() == data_layer.name()


def test_write_layer_with_minimal_attributes(data_layer, data_result_path):

    file = Path(data_result_path) / "output.shp"
    file = file.as_posix()

    QMapshaperDataPreparer.write_layer_with_minimal_attributes(data_layer, file, 1)

    layer = QgsVectorLayer(file, "layer", "ogr")

    assert layer

    assert layer.crs().toWkt() == data_layer.crs().toWkt()
    assert len(layer.fields().names()) == 1
    assert layer.fields().names() == ["KOD_OBEC"]
    assert layer.featureCount() == data_layer.featureCount()
    assert layer.name() == data_layer.name()


def test_write_layer_with_as_geojson(data_layer, data_result_path):

    file = Path(data_result_path) / "output.geojson"
    file = file.as_posix()

    QMapshaperDataPreparer.write_layer_with_as_geojson(data_layer, file)

    layer = QgsVectorLayer(file, "layer", "ogr")

    assert layer

    assert layer.crs().toWkt() == data_layer.crs().toWkt()
    assert layer.fields().names() == data_layer.fields().names()
    assert layer.featureCount() == data_layer.featureCount()
    assert layer.name() == data_layer.name()


def test_write_output_file(data_layer, data_result_path):

    file = Path(data_result_path) / "output.gpkg"
    file = file.as_posix()

    QMapshaperDataPreparer.write_output_file(data_layer, file, layer_name="new name")

    layer = QgsVectorLayer(file, "layer", "ogr")

    assert layer

    assert layer.crs().toWkt() == data_layer.crs().toWkt()
    assert layer.fields().names() == data_layer.fields().names()
    assert layer.featureCount() == data_layer.featureCount()


def test_add_mapshaper_id_field(data_layer):

    assert isinstance(data_layer, QgsVectorLayer)

    copied_in_memory = QMapshaperDataPreparer.copy_to_memory_layer(data_layer)

    QMapshaperDataPreparer.add_mapshaper_id_field(copied_in_memory)

    assert TextConstants.JOIN_FIELD_NAME in copied_in_memory.fields().names()


def test_generalization_field(data_layer):

    assert isinstance(data_layer, QgsVectorLayer)

    copied_in_memory = QMapshaperDataPreparer.copy_to_memory_layer(data_layer)

    ids = copied_in_memory.allFeatureIds()[1:20]

    QMapshaperDataPreparer.add_mapshaper_generalization_field(copied_in_memory, ids)

    assert TextConstants.GENERALIZATION_FIELD_NAME in copied_in_memory.fields().names()

    index = copied_in_memory.fields().lookupField(TextConstants.GENERALIZATION_FIELD_NAME)

    assert sorted(copied_in_memory.uniqueValues(index)) == sorted([False, True])


def test_join_fields_back(data_layer):

    assert isinstance(data_layer, QgsVectorLayer)

    copied_in_memory = QMapshaperDataPreparer.copy_to_memory_layer(data_layer)

    field_index = QMapshaperDataPreparer.add_mapshaper_id_field(copied_in_memory)

    fields = [x for x in range(copied_in_memory.fields().count())]

    fields.remove(field_index)

    copied_in_memory.startEditing()
    copied_in_memory.deleteAttributes(fields)
    copied_in_memory.commitChanges()

    assert len(copied_in_memory.fields()) == 1

    QMapshaperDataPreparer.join_fields_back(copied_in_memory, data_layer)

    assert copied_in_memory.fields().count() == data_layer.fields().count() + 1
