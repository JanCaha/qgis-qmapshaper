from typing import List

from .class_qmapshaper_file import QMapshaperFile

CLEAN_COMMAND = "-clean"


class QMapshaperCommandBuilder:

    @staticmethod
    def prepare_console_commands(input_data_path: str,
                                 output_data_path: str,
                                 command: str,
                                 arguments: List[str],
                                 clean_before: bool = False,
                                 clean_after: bool = False) -> List[str]:

        commands = []

        commands.append(input_data_path)

        if clean_before:
            commands.append(CLEAN_COMMAND)

        if not command.startswith("-"):
            command = QMapshaperCommandBuilder.prepare_console_tool_command(command)

        commands.append(command)

        commands += arguments

        if clean_after:
            commands.append(CLEAN_COMMAND)

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
