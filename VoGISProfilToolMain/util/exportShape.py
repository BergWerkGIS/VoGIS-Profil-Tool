# -*- coding: utf-8 -*-

from os.path import basename
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QMessageBox
from qgis.core import QGis
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsField
from qgis.core import QgsPoint
#from qgis.core import QgsGeometry
#from qgis.core import QgsFeature
from u import Util


class ExportShape:

    def __init__(self, iface, settings, profiles):
        self.iface = iface
        self.settings = settings
        self.profiles = profiles

    def exportPoint(self):
        print 'NOT IMPLEMENTED'

    def exportLine(self, fileName):

        if QgsVectorFileWriter.deleteShapeFile(fileName) is False:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte vorhandenes Shapefile nicht löschen: {0}'.format(fileName)
                                )
            return

        flds = {}
        flds[0] = QgsField('DUMMY', QVariant.Int)
        shpWriter = QgsVectorFileWriter(fileName,
                                        "CP1250",
                                        flds,
                                        QGis.WKBLineString,
                                        self.settings.mapData.selectedLineLyr.line.crs()
                                        )
        if shpWriter.hasError() != QgsVectorFileWriter.NoError:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte Shapefile nicht erstellen: {0}'.format(fileName)
                                )
            return

        ut = Util(self.iface)

        for p in self.profiles:
            vertices = []
            for s in p.segments:
                for v in s.vertices:
                    vertices.append(QgsPoint(v.x,v.y))
            feat = ut.createQgLineFeature(vertices)
            shpWriter.addFeature(feat)

        del shpWriter
        self.__loadShp(fileName)

    def __loadShp(self, fileName):
        reply = QMessageBox.question(self.iface.mainWindow(),
                                     "VoGIS-Profiltool",
                                     'Shapefile gespeichert.\r\n\r\n\r\nLaden?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes
                                     )
        if reply == QMessageBox.Yes:
            self.iface.addVectorLayer(fileName,
                                      basename(str(fileName)),
                                      'ogr'
                                      )
