from pathlib import Path
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from qmapshaper.text_constants import TextConstants
from qmapshaper.classes.class_qmapshaper_paths import QMapshaperPaths
from qmapshaper.classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder


def test_guess_mapshaper_folder():

    assert QMapshaperPaths.guess_mapshaper_folder() == ""


def test_mapshaper_folder():

    assert QMapshaperPaths.mapshaper_folder() == ""


def test_mapshaper_executable_path():

    assert QMapshaperPaths.mapshaper_executable_path() == ""

    test_path = Path("/usr/bin")

    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_FOLDER, test_path.as_posix())

    assert QMapshaperPaths.mapshaper_executable_path() ==\
        "/usr/bin/mapshaper-xl"


def test_mapshaper_builder_command():

    test_path = Path("")

    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_FOLDER, test_path.as_posix())

    assert QMapshaperPaths.mapshaper_command_call() == QMapshaperPaths.mapshaper_command_name()


def test_mapshaper_command_name():

    assert QMapshaperPaths.mapshaper_command_name() == "mapshaper-xl"


def test_mapshaper_command():

    test_path = Path("/usr/bin")

    test_path_mapshaper_xl = test_path / "mapshaper-xl"
    test_path_mapshaper = test_path / "mapshaper"

    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_FOLDER, test_path.as_posix())

    assert QMapshaperPaths.mapshaper_command_name() == test_path_mapshaper_xl.stem
    assert QMapshaperPaths.mapshaper_command_call() == test_path_mapshaper_xl.as_posix()
    assert QMapshaperPaths.mapshaper_executable_path() ==\
        test_path_mapshaper_xl.as_posix()

    ProcessingConfig.setSettingValue(TextConstants.MAPSHAPER_TOOL_NAME, "mapshaper")

    assert QMapshaperPaths.mapshaper_command_name() == test_path_mapshaper.stem
    assert QMapshaperPaths.mapshaper_command_call() == test_path_mapshaper.as_posix()
