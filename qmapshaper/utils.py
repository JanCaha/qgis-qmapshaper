import os
from typing import Any
from pathlib import Path

from qgis.core import (QgsMessageLog, QgsVectorLayer, Qgis)

from .text_constants import TextConstants

LOG_DEV = False

if os.environ.get("QMAPSHAPER_DEV"):
    if os.environ.get("QMAPSHAPER_DEV").lower() == "true":
        LOG_DEV = True


def get_icons_folder() -> Path:
    return Path(__file__).parent / "icons"


def get_icon_path(file_name: str) -> str:

    file: Path = get_icons_folder() / file_name

    return file.absolute().as_posix()


def log(text: Any) -> None:
    if LOG_DEV:
        QgsMessageLog.logMessage(str(text), TextConstants.plugin_name, Qgis.Info)


def features_count_with_non_empty_geoms(layer: QgsVectorLayer) -> int:

    count = 0

    for feature in layer.getFeatures():
        if not feature.geometry().isEmpty():
            count += 1

    return count
