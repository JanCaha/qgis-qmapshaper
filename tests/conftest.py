import pytest
from pathlib import Path

from qgis.core import QgsProject, QgsLayout, QgsVectorLayer
from processing.core.ProcessingConfig import ProcessingConfig

from qmapshaper.qmapshaper_plugin import QMapshaperPlugin
from qmapshaper.text_constants import TextConstants
from qmapshaper.classes.class_qmapshaper_paths import QMapshaperPaths


@pytest.fixture
def qgs_project() -> QgsProject:
    return QgsProject.instance()


@pytest.fixture
def qgs_layout(qgs_project) -> QgsLayout:
    return QgsLayout(qgs_project)


@pytest.fixture
def data_layer_path() -> str:

    path = Path(__file__).parent / "_data" / "villages.gpkg"

    return f"{path.as_posix()}|layername=obce"


@pytest.fixture
def data_layer(data_layer_path) -> QgsVectorLayer:

    return QgsVectorLayer(data_layer_path, "layer", "ogr")


@pytest.fixture
def data_result_path() -> str:

    path = Path(__file__).parent / "_data" / "results"

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path.absolute().as_posix()


@pytest.fixture()
def data_result_file(data_result_path) -> str:

    path = Path(data_result_path) / "result.gpkg"

    return path.absolute().as_posix()


@pytest.fixture(autouse=True, scope="session")
def plugin_load(qgis_iface) -> QMapshaperPlugin:

    plugin = QMapshaperPlugin(qgis_iface)

    plugin.initProcessing()

    return plugin


@pytest.fixture(autouse=True, scope="function")
def resetSettings() -> None:

    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_FOLDER, "")
    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_TOOL_NAME, "mapshaper-xl")
