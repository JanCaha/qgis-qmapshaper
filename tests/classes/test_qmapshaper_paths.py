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

    ProcessingConfig.addSetting(
        Setting(TextConstants.plugin_name,
                TextConstants.MAPSHAPER_FOLDER,
                'Mapshaper folder',
                "/usr/local/test",
                valuetype=Setting.FOLDER))

    ProcessingConfig.readSettings()

    assert QMapshaperPaths.mapshaper_executable_path(use_defined=True) ==\
        "/usr/local/test/mapshaper-xl"


def test_mapshaper_builder_command():

    assert QMapshaperPaths.mapshaper_command_call() == QMapshaperPaths.mapshaper_command_name()


def test_with_folder_setting_set():

    ProcessingConfig.addSetting(
        Setting(TextConstants.plugin_name,
                TextConstants.MAPSHAPER_FOLDER,
                'Mapshaper folder',
                "/usr/local/test",
                valuetype=Setting.FOLDER))

    ProcessingConfig.readSettings()

    assert QMapshaperPaths.mapshaper_folder() == "/usr/local/test"


def test_mapshaper_command_name():

    assert QMapshaperPaths.mapshaper_command_name() == "mapshaper-xl"


def test_mapshaper_command():

    assert QMapshaperPaths.mapshaper_command_call() == "mapshaper-xl"

    ProcessingConfig.addSetting(
        Setting(TextConstants.plugin_name,
                TextConstants.MAPSHAPER_FOLDER,
                'Mapshaper folder',
                "/usr/local/test",
                valuetype=Setting.FOLDER))

    ProcessingConfig.readSettings()

    assert QMapshaperPaths.mapshaper_command_call(use_settings_path=True) ==\
        "/usr/local/test/mapshaper-xl"
