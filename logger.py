from qgis.core import (
    Qgis,
    QgsMessageLog
)

class Logger():
    def log(self, msg, level):
        QgsMessageLog.logMessage(msg, level=level)
