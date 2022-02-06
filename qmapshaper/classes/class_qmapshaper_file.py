from uuid import uuid4

from qgis.core import QgsProcessingUtils


class QMapshaperFile:

    @staticmethod
    def get_format(file_name: str) -> str:

        file_types = [QMapshaperFile, QMapshaperGeojsonFile, QMapshaperTopoJsonFile]

        for file_type in file_types:
            if file_name.endswith(file_type.extension()):
                return file_type.output_format()

        return QMapshaperFile.output_format()

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


class QMapshaperGeojsonFile:

    @staticmethod
    def random_temp_filename() -> str:

        filename = "{}.{}".format(uuid4(), QMapshaperGeojsonFile.extension())

        return QgsProcessingUtils.generateTempFilename(filename)

    @staticmethod
    def driver_name() -> str:
        return "GeoJSON"

    @staticmethod
    def output_format() -> str:
        return "geojson"

    @staticmethod
    def extension() -> str:
        return "geojson"


class QMapshaperTopoJsonFile:

    @staticmethod
    def random_temp_filename() -> str:

        filename = "{}.{}".format(uuid4(), QMapshaperTopoJsonFile.extension())

        return QgsProcessingUtils.generateTempFilename(filename)

    @staticmethod
    def output_format() -> str:
        return "topojson"

    @staticmethod
    def extension() -> str:
        return "topojson"
