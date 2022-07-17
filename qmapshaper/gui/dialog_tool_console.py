from qgis.core import (QgsVectorLayer, QgsMapLayerProxyModel)
from qgis.gui import (QgsMapCanvas, QgsMapLayerComboBox, QgisInterface, QgsFieldComboBox)
from qgis.PyQt.QtWidgets import (QDialog, QLabel, QVBoxLayout, QDialogButtonBox, QLineEdit)
from qgis.PyQt.QtGui import QPalette
from qgis.PyQt.QtCore import (Qt, QThreadPool, pyqtSignal)

from ..utils import log
from ..text_constants import TextConstants
from ..classes.classes_workers import WaitWorkerCommand
from .processes.interactive_console_process import InteractiveConsoleProcess


class InteractiveConsoleTool(QDialog):

    map_updated = pyqtSignal()
    data_processed = pyqtSignal()

    def __init__(self, parent=None, iface: QgisInterface = None):

        super().__init__(parent)

        self.process = InteractiveConsoleProcess(self)

        self.process.processed_layer_changed.connect(self.load_processed_data)

        self.iface = iface

        self.setWindowTitle(TextConstants.tool_name_interactive_console)

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.threadpool = QThreadPool()
        self.wait_worker: WaitWorkerCommand = None

        self.layer_selection = QgsMapLayerComboBox(self)
        self.layer_selection.setFilters(QgsMapLayerProxyModel.VectorLayer)

        self.layer_selection.layerChanged.connect(self.set_input_data)

        self.field = QgsFieldComboBox()
        self.field.setAllowEmptyFieldName(True)
        self.field.fieldChanged.connect(self.set_required_field)

        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.black)
        palette.setColor(QPalette.Text, Qt.white)

        self.console_command = QLineEdit()
        self.console_command.textChanged.connect(self.create_wait_worker)
        self.console_command.setPalette(palette)

        self.canvas = QgsMapCanvas(self)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok, self)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(QLabel("Layer"))
        self.vlayout.addWidget(self.layer_selection)
        self.vlayout.addWidget(QLabel("Field needed to perform the command"))
        self.vlayout.addWidget(self.field)
        self.vlayout.addWidget(QLabel("Console command to run in mapshaper"))
        self.vlayout.addWidget(self.console_command)
        self.vlayout.addWidget(QLabel("Map"))
        self.vlayout.addWidget(self.canvas)
        self.vlayout.addWidget(self.button_box)
        self.setLayout(self.vlayout)

        self.setup_canvas()

        self.set_input_data()

    def setup_canvas(self):
        self.canvas.setDestinationCrs(self.iface.mapCanvas().project().crs())
        self.canvas.setExtent(self.iface.mapCanvas().extent())
        self.canvas.setLayers([self.layer_selection.currentLayer()])

    def set_required_field(self):

        self.process.field = self.field.currentField()

    def set_input_data(self):

        if self.layer_selection.currentLayer():

            self.field.setLayer(self.layer_selection.currentLayer())

            self.process.set_input_data(self.layer_selection.currentLayer())

            self.process_layer()

    def process_layer(self) -> None:

        self.process.process_layer(self.console_command.text())

        self.data_processed.emit()

    def load_processed_data(self) -> None:

        if self.process.processed_data_only_geometry:

            self.canvas.setLayers([self.process.processed_data_only_geometry])
            self.canvas.redrawAllLayers()

        self.map_updated.emit()

    def get_layer_for_project(self) -> QgsVectorLayer:

        return self.process.processed_data_with_attributes

    def create_wait_worker(self) -> None:

        wait_worker = WaitWorkerCommand(self.console_command.text())
        wait_worker.signals.command.connect(self.run_update)

        self.threadpool.start(wait_worker)

    def run_update(self, command: str):

        log(f"Prev: {command} - curr: {self.console_command.text()}")

        if command == self.console_command.text():
            self.process_layer()
