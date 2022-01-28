from pathlib import Path
import configparser

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from .utils import QMapshaperUtils
from .processing.tool_simplify import SimplifyAlgorithm


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
                    QMapshaperUtils.MAPSHAPER_FOLDER,
                    self.tr('Mapshaper folder'),
                    QMapshaperUtils.mapshaper_folder(),
                    valuetype=Setting.FOLDER))

        ProcessingConfig.readSettings()

        self.refreshAlgorithms()

        return True

    def versionInfo(self):
        return self.version

    def loadAlgorithms(self):
        self.addAlgorithm(SimplifyAlgorithm())

    def id(self):
        return 'qmapshaper'

    def name(self):
        return "QMapshaper"

    def icon(self):
        path = Path(__file__).parent / "icons" / "main_icon.png"
        return QIcon(str(path))

    def longName(self):
        return self.name()
