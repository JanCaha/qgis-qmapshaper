from uuid import uuid4

from qgis.core import QgsProcessingUtils


class QMapshaperFile:

    @staticmethod
    def random_temp_filename() -> str:

        filename = "{}.{}".format(uuid4(), QMapshaperFile.extension())

        return QgsProcessingUtils.generateTempFilename(filename)

    @staticmethod
    def driver_name() -> str:
        return "ESRI Shapefile"

    @staticmethod
    def output_format() -> str:
        return "shapefile"

    @staticmethod
    def extension() -> str:
        return "shp"
