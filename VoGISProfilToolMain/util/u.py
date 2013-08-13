# -*- coding: iso-8859-15 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from qgis.core import QgsMessageLog
from qgis.core import QGis
from ..bo.node import Node
from ..bo.linkedList import LinkedList


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
        if fileName.isEmpty():
            return ''
        fileExt = str(selectedFilter[:3]).lower()
        if str(fileName).lower().endswith(fileExt) is False:
            fileName = fileName + '.' + fileExt
        return fileName

    def createQgLineFeature(self, vertices):
        line = QgsGeometry.fromPolyline(vertices)
        qgFeat = QgsFeature()
        qgFeat.setGeometry(line)
        return qgFeat

    #multipart explodieren
    #linien mit gleichen end und start vertices verinden
    def prepareFeatures(self, provider, origFeats):

        newFeats = self.__explodeMultiPartFeatures(provider, origFeats)
        newFeats = self.__mergeFeaturesAny(newFeats)
        newFeats = self.__mergeFeaturesSimple(newFeats)
        return newFeats

    def __mergeFeaturesAny(self, origFeats):
        ll = LinkedList()
        for idx, feat in enumerate(origFeats):
            n = Node(idx)
            featPnts = feat.geometry().asPolyline()
            for i, f in enumerate(origFeats):
                if idx == i:
                    continue
                fPnts = f.geometry().asPolyline()
                if featPnts[len(featPnts) - 1] == fPnts[0]:
                    n.setNext(i)
                if featPnts[0] == fPnts[len(fPnts) - 1]:
                    n.setPrev(i)
            ll.addNode(n)

        for n in ll.nodes:
            QgsMessageLog.logMessage('{0}'.format(n.toString()), 'VoGis')

        newFeats = []
        orderedIds = ll.getOrderedIds()
        QgsMessageLog.logMessage('{0}'.format(orderedIds), 'VoGis')
        for idx in orderedIds:
            newFeats.append(origFeats[idx])

        return newFeats

    def __mergeFeaturesSimple(self, origFeats):

        newFeats = []
        QgsMessageLog.logMessage('---- Merge Simple: {0} features'.format(len(origFeats)), 'VoGis')

        prevToPnt = None
        #newGeom = QgsGeometry()
        newGeom = QgsGeometry().fromPolyline([])
        #newGeom = QgsGeometry.fromPolyline([QgsPoint(1, 1), QgsPoint(2, 2)])
        QgsMessageLog.logMessage('newGeom WKB Type {0}'.format(newGeom.wkbType() == QGis.WKBLineString), 'VoGis')
        for feat in origFeats:
            currentGeom = feat.geometry()
            currentPnts = currentGeom.asPolyline()
            if prevToPnt is None:
                QgsMessageLog.logMessage('combining FIRST {0}'.format(currentGeom.asPolyline()), 'VoGis')
                newGeom = newGeom.combine(currentGeom)
            else:
                if currentPnts[0] == prevToPnt:
                    QgsMessageLog.logMessage('combining {0}'.format(currentGeom.asPolyline()), 'VoGis')
                    newGeom = newGeom.combine(currentGeom)
                else:
                    QgsMessageLog.logMessage('creating {0}'.format(newGeom.asPolyline()), 'VoGis')
                    newFeats.append(self.createQgLineFeature(newGeom.asPolyline()))
                    #newGeom = QgsGeometry()
                    newGeom = QgsGeometry().fromPolyline(currentPnts)
                    #newGeom = QgsGeometry.fromPolyline([QgsPoint(1, 1), QgsPoint(2, 2)])

            prevToPnt = currentPnts[len(currentPnts) - 1]

        newFeats.append(self.createQgLineFeature(newGeom.asPolyline()))

        QgsMessageLog.logMessage('---- {0} features after Merge Simple'.format(len(newFeats)), 'VoGis')

        #for idx, f in enumerate(newFeats):
        #    QgsMessageLog.logMessage('--------feature {0}---------'.format(idx), 'VoGis')
        #    geo = f.geometry()
        #    pnts = geo.asPolyline()
        #    for i, v in enumerate(pnts):
        #        QgsMessageLog.logMessage('   pnt {0}: {1}/{2}'.format(i, v.x(), v.y()), 'VoGis')

        return newFeats

    def __explodeMultiPartFeatures(self, provider, origFeats):

        newFeats = []
        QgsMessageLog.logMessage('exploding {0} features'.format(len(origFeats)), 'VoGis')

        for feat in origFeats:
            geom = feat.geometry()
            if geom.isMultipart():
                QgsMessageLog.logMessage('multipart feature!', 'VoGis')
                newFeats.extend(self.explodeMultiPartFeature(provider, feat))
            else:
                QgsMessageLog.logMessage('single part feature', 'VoGis')
                newFeats.append(feat)

        QgsMessageLog.logMessage('{0} features after exploding'.format(len(newFeats)), 'VoGis')
        return newFeats

    #https://github.com/SrNetoChan/MultipartSplit/blob/master/splitmultipart.py
    def explodeMultiPartFeature(self, provider, feat):

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

        parts = feat.geometry().asGeometryCollection()

        newFeats = []
        for i in range(len(parts)):
            tmpFeat.setGeometry(parts[i])
            newFeats.append(QgsFeature(tmpFeat))

        return newFeats
