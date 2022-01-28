__author__ = 'Jan Caha'
__date__ = '2022-01-28'
__copyright__ = '(C) 2022 by Jan Caha'

from .qmapshaper_plugin import QMapshaperPlugin


# noinspection PyPep8Naming
def classFactory(iface):

    return QMapshaperPlugin()
