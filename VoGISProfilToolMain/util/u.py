# -*- coding: iso-8859-15 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from qgis.core import QgsMessageLog
from qgis.core import QGis


class Util:

    def __init__(self, iface):
        self.iface = iface

    def isFloat(self, val, valName):
        try:
            f = float(val)
            f += 0.01
            return True
        except:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "'" + valName + "' ist keine gültige Zahl!")
            return False

    def getFileName(self, text, filter):
        selectedFilter = QString()
        fileDlg = QFileDialog(self.iface.mainWindow())
        fileName = fileDlg.getSaveFileName(self.iface.mainWindow(),
                                           text,
                                           "",
                                           filter,
                                           selectedFilter,
                                           )
        return fileName

    def createQgLineFeature(self, vertices):
        line = QgsGeometry.fromPolyline(vertices)
        qgFeat = QgsFeature()
        qgFeat.setGeometry(line)
        return qgFeat

    #multipart explodieren
    #linien mit gleichen end und start vertices verinden
    def prepareFeatures(self, provider, origFeats):

        newFeats = []

        for feat in origFeats:

            geom = feat.geometry()
            if geom.isMultipart():
                QgsMessageLog.logMessage('MULTIPART!', 'VoGis')
                newFeats.extend(self.__explodeMultiPart(provider, feat))
            else:
                QgsMessageLog.logMessage('single part', 'VoGis')
                newFeats.append(feat)

        return newFeats

    #https://github.com/SrNetoChan/MultipartSplit/blob/master/splitmultipart.py
    def __explodeMultiPart(self, provider, feat):

        tmpFeat = QgsFeature()

        # Get attributes from original feature
        # Because of changes in the way the 1.9 api handle attributes
        if QGis.QGIS_VERSION_INT < 10900:
            newAttribs = feat.attributeMap()
            for j in range(newAttribs.__len__()):
                if not provider.defaultValue(j).isNull():
                    newAttribs[j] = provider.defaultValue(j)
            tmpFeat.setAttributeMap(newAttribs)
        else:
            newAttribs = feature.attributes()
            for j in range(newAttribs.__len__()):
                if not provider.defaultValue(j).isNull():
                    newAttribs[j] = provider.defaultValue(j)
            tmpFeat.setAttributes(newAttribs)

        # Get parts geometries from original feature
        parts = feat.geometry().asGeometryCollection()

        # from 2nd to last part create a new features using their
        # single geometry and the attributes of the original feature
        newFeats = []
        for i in range(len(parts)):
            tmpFeat.setGeometry(parts[i])
            newFeats.append(QgsFeature(tmpFeat))

        return newFeats
