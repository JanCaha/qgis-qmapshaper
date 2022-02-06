from typing import List
from pathlib import Path

from .class_qmapshaper_paths import QMapshaperPaths
from .class_qmapshaper_file import QMapshaperFile


class QMapshaperCommandBuilder:

    @staticmethod
    def mapshaper_command_name():
        return "mapshaper-xl"

    @staticmethod
    def mapshaper_command() -> str:

        mapshaper_bin_folder = QMapshaperPaths.mapshaper_bin_folder()

        if mapshaper_bin_folder:

            bin_path = Path(mapshaper_bin_folder)

            bin_path = bin_path / QMapshaperCommandBuilder.mapshaper_command_name()

            return bin_path.absolute().as_posix()

        else:

            return QMapshaperCommandBuilder.mapshaper_command_name()

    @staticmethod
    def prepare_console_commands(input_data_path: str, output_data_path: str, command: str,
                                 arguments: List[str]) -> List[str]:

        commands = [QMapshaperCommandBuilder.mapshaper_command()]

        commands.append(input_data_path)

        if not command.startswith("-"):
            command = QMapshaperCommandBuilder.prepare_console_tool_command(command)

        commands.append(command)

        commands += arguments

        commands += QMapshaperCommandBuilder.prepare_console_output_data(output_data_path)

        return commands

    @staticmethod
    def prepare_console_output_data(output_data_path: str) -> List[str]:

        command = ["-o"]
        command.append('format={}'.format(QMapshaperFile.get_format(output_data_path)))
        command.append(output_data_path)

        return command

    @staticmethod
    def prepare_console_tool_command(tool: str) -> str:
        return "-{}".format(tool)
