from processing.core.ProcessingConfig import ProcessingConfig, Setting

from qmapshaper.text_constants import TextConstants
from qmapshaper.classes.class_qmapshaper_paths import QMapshaperPaths
from qmapshaper.classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder


def test_guess_mapshaper_folder():

    assert QMapshaperPaths.guess_mapshaper_folder() == ""


def test_mapshaper_folder():

    assert QMapshaperPaths.mapshaper_folder() == ""


def test_mapshaper_bin_folder():

    assert QMapshaperPaths.mapshaper_bin_folder() == ""


def test_full_path_command():

    assert QMapshaperPaths.full_path_command(QMapshaperCommandBuilder.mapshaper_command_name()
                                            ) == QMapshaperCommandBuilder.mapshaper_command_name()


def test_mapshaper_builder_command():

    assert QMapshaperCommandBuilder.mapshaper_command(
    ) == QMapshaperCommandBuilder.mapshaper_command_name()


def test_with_folder_setting_set():

    ProcessingConfig.addSetting(
        Setting(TextConstants.plugin_name,
                TextConstants.MAPSHAPER_FOLDER,
                'Mapshaper folder',
                "/usr/local",
                valuetype=Setting.FOLDER))

    ProcessingConfig.readSettings()

    assert QMapshaperPaths.mapshaper_folder() == "/usr/local"
    assert QMapshaperPaths.mapshaper_bin_folder() == "/usr/local/bin"

    command = QMapshaperCommandBuilder.mapshaper_command_name()

    assert QMapshaperPaths.full_path_command(command) == f"/usr/local/bin/{command}"
