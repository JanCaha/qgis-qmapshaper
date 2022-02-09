import pytest
from pathlib import Path

from pytest_qgis import clean_qgis_layer

from qgis.core import QgsProject, QgsLayout, QgsVectorLayer


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
@clean_qgis_layer
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
