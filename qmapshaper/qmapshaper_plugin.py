import os
import sys
import inspect

from qgis.core import (QgsApplication)
from qgis.gui import (QgisInterface)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .qmapshaper_provider import QMapshaperProvider
from .utils import get_icon_path
from .gui.dialog_tool_interactive_simplifier import DialogTool
from .text_constants import TextConstants

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class QMapshaperPlugin():

    def __init__(self, iface):

        self.iface: QgisInterface = iface

        self.provider = QMapshaperProvider()

        self.tool = None

        self.actions = []
        self.menu = TextConstants.plugin_name

    def initProcessing(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

        self.add_action(icon_path=get_icon_path("main_icon.png"),
                        text=TextConstants.tool_name_interactive_simplifier,
                        callback=self.run_tool_interactive_simplifier,
                        add_to_toolbar=True)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

        for action in self.actions:
            self.iface.removePluginMenu(TextConstants.plugin_name, action)
            self.iface.removeToolBarIcon(action)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None,
                   add_to_specific_toolbar=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        if add_to_specific_toolbar:
            add_to_specific_toolbar.addAction(action)

        self.actions.append(action)

        return action

    def run_tool_interactive_simplifier(self):

        dlg = DialogTool(parent=self.iface.mainWindow(), iface=self.iface)

        dlg.show()
        dlg.exec_()

        dlg = None
