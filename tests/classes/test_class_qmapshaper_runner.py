from qmapshaper.classes.class_qmapshaper_runner import MapshaperProcessChecker, NpmPackageLocationCheckerProcess


def test_MapshaperProcessChecker():

    ms = MapshaperProcessChecker()

    assert "Error: No commands to run" in ms.output_lines
    assert "Run mapshaper -h to view help" in ms.output_lines

    assert ms.found

    ms = MapshaperProcessChecker("/bin")

    assert ms.output_lines == ""

    assert ms.found is False


def test_NpmPackageLocationCheckerProcess():

    npm = NpmPackageLocationCheckerProcess()

    assert npm.npm_exist()

    assert npm.npm_package_locations()
    assert npm.packages_location == "/workspaces/qgis-mapshaper/node_modules"

    assert npm.mapshaper_exists()

    assert npm.mapshaper_path() is None
