from pathlib import Path
import configparser

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from .classes.class_qmapshaper_paths import QMapshaperPaths
from .processing.tool_simplify import SimplifyAlgorithm
from .text_constants import TextConstants


class QMapshaperProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()

        path = Path(__file__).parent / 'metadata.txt'

        config = configparser.ConfigParser()
        config.read(path)

        self.version = config['general']['version']

    def load(self) -> bool:

        ProcessingConfig.settingIcons[self.name()] = self.icon()

        ProcessingConfig.addSetting(
            Setting(self.name(),
                    TextConstants.MAPSHAPER_FOLDER,
                    self.tr('Mapshaper folder'),
                    QMapshaperPaths.mapshaper_folder(),
                    valuetype=Setting.FOLDER))

        ProcessingConfig.readSettings()

        self.refreshAlgorithms()

        return True

    def versionInfo(self):
        return self.version

    def loadAlgorithms(self):
        self.addAlgorithm(SimplifyAlgorithm())

    def id(self):
        return TextConstants.plugin_id

    def name(self):
        return TextConstants.plugin_name

    def icon(self):
        path = Path(__file__).parent / "icons" / "qmapshaper.png"
        return QIcon(str(path))

    def longName(self):
        return self.name()
