from qmapshaper.classes.class_qmapshaper_runner import MapshaperProcessChecker, MapshaperProcess


def test_MapshaperProcessChecker():

    ms = MapshaperProcessChecker()

    assert "Error: No commands to run" in ms.output_lines
    assert "Run mapshaper -h to view help" in ms.output_lines

    assert ms.found

    ms = MapshaperProcessChecker("/bin")

    assert ms.output_lines == ""

    assert ms.found is False
