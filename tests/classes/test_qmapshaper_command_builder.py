from qmapshaper.classes.class_qmapshaper_command_builder import QMapshaperCommandBuilder


def test_prepare_console_commands():

    commands = QMapshaperCommandBuilder.prepare_console_commands("in.geojson", "out.geojson",
                                                                 "simplify", ["dp", "20%"])

    assert commands == [
        'in.geojson', '-simplify', 'dp', '20%', '-o', "format=geojson", "out.geojson"
    ]

    commands = QMapshaperCommandBuilder.prepare_console_commands("in.shp", "out.shp", "simplify",
                                                                 ["dp", "50%"])

    assert commands == ['in.shp', '-simplify', 'dp', '50%', '-o', "format=shapefile", "out.shp"]

    commands = QMapshaperCommandBuilder.prepare_console_commands("in.shp", "out.topojson",
                                                                 "simplify", ["dp", "50%"])

    assert commands == [
        'in.shp', '-simplify', 'dp', '50%', '-o', "format=topojson", "out.topojson"
    ]


def test_prepare_console_output_data():

    assert QMapshaperCommandBuilder.prepare_console_output_data("out.topojson") == [
        '-o', "format=topojson", "out.topojson"
    ]

    assert QMapshaperCommandBuilder.prepare_console_output_data("out.shp") == [
        '-o', "format=shapefile", "out.shp"
    ]

    assert QMapshaperCommandBuilder.prepare_console_output_data("out.geojson") == [
        '-o', "format=geojson", "out.geojson"
    ]


def test_prepare_console_tool_command():

    assert QMapshaperCommandBuilder.prepare_console_tool_command("simplify") == "-simplify"

    assert QMapshaperCommandBuilder.prepare_console_tool_command("clean") == "-clean"
