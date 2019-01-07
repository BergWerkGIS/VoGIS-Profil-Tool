# -*- coding: iso-8859-15 -*-

import os
import pdb

from osgeo import ogr
from osgeo import osr

from qgis.PyQt.QtWidgets import QApplication, QFileDialog, QMessageBox

from qgis.core import Qgis, QgsVectorFileWriter, QgsPointXY, QgsGeometry, QgsFeature, QgsMessageLog, QgsWkbTypes

from VoGisProfilTool.bo.node import Node
from VoGisProfilTool.bo.linkedList import LinkedList


class Util:

    @staticmethod
    def t(txt):
        return QApplication.translate("code", txt)

    def __init__(self, iface):
        self.iface = iface

    def get_geometry_wkbType_as_string(self, geom):
        if QgsWkbTypes.Unknown == geom.wkbType(): return "WKBUnknown"
        if QgsWkbTypes.Point == geom.wkbType(): return "WKBPoint"
        if QgsWkbTypes.LineString == geom.wkbType(): return "WKBLineString"
        if QgsWkbTypes.Polygon == geom.wkbType(): return "WKBPolygon"
        if QgsWkbTypes.MultiPoint == geom.wkbType(): return "WKBMultiPoint"
        if QgsWkbTypes.MultiLineString == geom.wkbType(): return "WKBMultiLineString"
        if QgsWkbTypes.MultiPolygon == geom.wkbType(): return "WKBMultiPolygon"
        if QgsWkbTypes.NoGeometry == geom.wkbType(): return "WKBNoGeometry"
        if QgsWkbTypes.Point25D == geom.wkbType(): return "WKBPoint25D"
        if QgsWkbTypes.LineString25D == geom.wkbType(): return "WKBLineString25D"
        if QgsWkbTypes.Polygon25D == geom.wkbType(): return "WKBPolygon25D"
        if QgsWkbTypes.MultiPoint25D == geom.wkbType(): return "WKBMultiPoint25D"
        if QgsWkbTypes.MultiLineString25D == geom.wkbType(): return "WKBMultiLineString25D"
        if QgsWkbTypes.MultiPolygon25D == geom.wkbType(): return "WKBMultiPolygon25D"

        return "no valid WKB Type"

    def isFloat(self, val, valName):
        try:
            val = val.replace(",", ".")
            f = float(val)
            f += 0.01
            return True
        except:
            #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", unicode(valName) + u" " + unicode(QApplication.translate("code", u"ist keine gültige Zahl!")))
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "'" + valName + "' " + QApplication.translate("code", "ist keine gültige Zahl!"))
            #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", tr(u"ist keine gültige Zahl!"))
            return False

    def isInt(self, val, valName):
        try:
            i = int(val)
            i += 1
            return True
        except:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "'" + valName + "' " + QApplication.translate("code", "ist keine gültige Zahl!"))
            return False

    def getFileName(self, text, filter, filePath):
        """filter: [["Shapefile", "shp"], ["Keyhole Markup Language", "kml"]]"""
        filters = []
        for item in filter:
            filters.append("%s (*.%s)" % (item[0], item[1]))
        fileDlg = QFileDialog(self.iface.mainWindow())
        fileDlg.setNameFilters(filters)
        fileName, selectedFilter = fileDlg.getSaveFileName(self.iface.mainWindow(),
                                           text,
                                           filePath,
                                           ";;".join(filters)
                                           )
        QgsMessageLog.logMessage("selectedFilter: {0}".format(selectedFilter), "VoGis", Qgis.Info)

        #QgsMessageLog.logMessage("{0}".format(fileName), "VoGis", Qgis.Info)
        if fileName is None or fileName == "":
            return "", ""

        QgsMessageLog.logMessage("fileDlg.filters(): {0}".format(fileDlg.nameFilters()), "VoGis", Qgis.Info)
        selectedFilter = fileDlg.nameFilters().index(selectedFilter)
        fileExt = filter[selectedFilter][1]

        QgsMessageLog.logMessage("selectedFilter: {0}".format(selectedFilter), "VoGis", Qgis.Info)
        QgsMessageLog.logMessage("fileExt: {0}".format(fileExt), "VoGis", Qgis.Info)

        if fileName.lower().endswith(fileExt) is False:
            fileName = fileName + "." + fileExt
        return fileName, fileExt

    def get_features(self, lyr):
        feats = []
        if lyr.selectedFeatureCount() > 0:
            feats = lyr.selectedFeatures()
        else:
            #processing.getfeatures: This will iterate over all the features in the layer, in case there is no selection, or over the selected features otherwise.
            #obviously not available with windows standalone installer
            #features = processing.getfeatures(self.settings.mapData.selectedLineLyr.line)
            features = lyr.getFeatures()
            for feat in features:
                feats.append(feat)
        return feats

    def createQgLineFeature(self, vertices):
        line = QgsGeometry.fromPolylineXY(vertices)
        qgFeat = QgsFeature()
        qgFeat.setGeometry(line)
        return qgFeat

    def createQgPointFeature(self, vertex):
        pnt = QgsGeometry.fromPointXY(QgsPointXY(vertex.x, vertex.y))
        qgPnt = QgsFeature()
        qgPnt.setGeometry(pnt)
        return qgPnt

    def prepareFeatures(self, settings, provider, feats):
        """explode multipart features"""
        """merge lines with same direction and same start and end vertices"""

        err_msg = "Vector input not valid!\nPlease check message log and\n'Check Geometry Validity Tool'."

        if self.valid(feats) is False:
            return None, "Original features:\n" + err_msg

        if settings.linesExplode is True:
            feats = self.__explodeMultiPartFeatures(provider, feats)
            #self.__printAttribs(feats[0].attributeMap())
            if self.valid(feats) is False:
                return None, "Explode features:\n" + err_msg

        if settings.linesMerge is True:
            if len(feats) > 500:
                QgsMessageLog.logMessage("+500 features: merging not possible", "VoGis", Qgis.Critical)
            else:
                feats = self.__mergeFeaturesAny(feats)
                #self.__printAttribs(feats[0].attributeMap())
                if self.valid(feats) is False:
                    return None, "Merge features (any):\n" + err_msg
                feats = self.__mergeFeaturesSimple(provider, feats)
                #self.__printAttribs(feats[0].attributeMap())
                if self.valid(feats) is False:
                    return None, "Merge features (simple):\n" + err_msg

        return feats, None

    def valid(self, feats):
        #QgsMessageLog.logMessage("check feat valid", "VoGis", Qgis.Info)
        err_cnt = 0
        for feat in feats:
            #QgsMessageLog.logMessage("feat", "VoGis", Qgis.Info)
            #if feat.isValid() is False:
            #    return [], "Vector input not valid!\nPlease check using the check validity tool."
            #geom = QgsGeometry(feat.geometry())
            geom = feat.geometry()
            if geom.isEmpty():
                err_cnt +=1
                QgsMessageLog.logMessage("$id [{0}] Empty geometry".format(feat.id()), "VoGis", Qgis.Warning)
            else:
                errors = geom.validateGeometry()
                if len(errors) > 0:
                    if len(errors) < 1:
                        continue
                    for err in errors:
                        err_cnt += 1
                        QgsMessageLog.logMessage("$id [{0}] {1}".format(feat.id(), err.what()), "VoGis", Qgis.Critical)
        return (1 > err_cnt)

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

        #for n in ll.nodes:
        #    QgsMessageLog.logMessage("{0}".format(n.toString()), "VoGis", Qgis.Info)

        newFeats = []
        orderedIds = ll.getOrderedIds()
        #QgsMessageLog.logMessage("{0}".format(orderedIds), "VoGis", Qgis.Info)
        for idx in orderedIds:
            newFeats.append(origFeats[idx])

        tmpFeats = []
        for feat in newFeats:
            if feat.geometry().isEmpty() is True:
                QgsMessageLog.logMessage("dropping empty geometry", "VoGis", Qgis.Warning)
                continue
            else:
                tmpFeats.append(feat)
        newFeats = tmpFeats

        return newFeats

    def __mergeFeaturesSimple(self, provider, origFeats):
        newFeats = []
        QgsMessageLog.logMessage("---- Merge Simple: {0} features".format(len(origFeats)), "VoGis", Qgis.Info)

        if len(origFeats) < 1:
            return []

        prevToPnt = None
        #newGeom = QgsGeometry()
        newGeom = QgsGeometry().fromPolylineXY([])
        attrMap = None
        #newGeom = QgsGeometry.fromPolyline([QgsPoint(1, 1), QgsPoint(2, 2)])
        #QgsMessageLog.logMessage("newGeom WKB Type {0}".format(newGeom.wkbType() == QGis.WKBLineString), "VoGis", Qgis.Info)
        for feat in origFeats:
            #QgsMessageLog.logMessage("{0}:{1}".format("ORIG FEAT AttributeMap", self.__printAttribs(feat.attributeMap())), "VoGis", Qgis.Info)
            #self.__printAttribs(feat.attributeMap())
            currentGeom = feat.geometry()
            currentPnts = currentGeom.asPolyline()
            if prevToPnt is None:
                #QgsMessageLog.logMessage("combining FIRST {0}".format(currentGeom.asPolyline()), "VoGis", Qgis.Info)
                newGeom = newGeom.combine(currentGeom)
                attrMap = feat.attributes()
            else:
                if currentPnts[0] == prevToPnt:
                    #QgsMessageLog.logMessage("combining {0}".format(currentGeom.asPolyline()), "VoGis", Qgis.Info)
                    newGeom = newGeom.combine(currentGeom)
                    attrMap = feat.attributes();
                else:
                    #QgsMessageLog.logMessage("creating {0}".format(newGeom.asPolyline()), "VoGis", Qgis.Info)
                    featNew = self.createQgLineFeature(newGeom.asPolyline())
                    featNew = self.__transferAttributes(provider, attrMap, featNew)
                    newFeats.append(featNew)
                    #feat = QgsFeature()
                    #newGeom = QgsGeometry()
                    newGeom = QgsGeometry().fromPolylineXY(currentPnts)
                    attrMap = feat.attributes()
                #newGeom = QgsGeometry.fromPolyline([QgsPoint(1, 1), QgsPoint(2, 2)])

            prevToPnt = currentPnts[len(currentPnts) - 1]

        featNew = self.createQgLineFeature(newGeom.asPolyline())
        self.__transferAttributes(provider, attrMap, featNew)
        #newFeats.append(self.createQgLineFeature(newGeom.asPolyline()))
        newFeats.append(featNew)

        tmpFeats = []
        for feat in newFeats:
            if feat.geometry().isEmpty() is True:
                QgsMessageLog.logMessage("dropping empty geometry", "VoGis", Qgis.Warning)
                continue
            else:
                tmpFeats.append(feat)
        newFeats = tmpFeats

        QgsMessageLog.logMessage("---- {0} features after Merge Simple".format(len(newFeats)), "VoGis", Qgis.Info)

        #for idx, f in enumerate(newFeats):
        #    QgsMessageLog.logMessage("--------feature {0}---------".format(idx), "VoGis", Qgis.Info)
        #    geo = f.geometry()
        #    pnts = geo.asPolyline()
        #    for i, v in enumerate(pnts):
        #        QgsMessageLog.logMessage("   pnt {0}: {1}/{2}".format(i, v.x(), v.y()), "VoGis", Qgis.Info)

        return newFeats

    # def __printAttribs(self, attributeMap):
    #     txt = ""
    #     for (k, attr) in attributeMap.items():
    #         txt += "({0}: {1}) ".format(k, attr.toString())
    #     return txt

    def __explodeMultiPartFeatures(self, provider, origFeats):
        newFeats = []
        QgsMessageLog.logMessage("exploding {0} features".format(len(origFeats)), "VoGis", Qgis.Info)

        for feat in origFeats:
            geom = feat.geometry()
            if geom.isMultipart():
                #QgsMessageLog.logMessage("FId[{0}]: {1}".format(feat.id(), "multipart feature!"), "VoGis", Qgis.Info)
                newFeats.extend(self.explodeMultiPartFeature(provider, feat))
            else:
                #QgsMessageLog.logMessage("FId[{0}]: {1}".format(feat.id(), "single part feature"), "VoGis", Qgis.Info)
                newFeats.append(feat)

        QgsMessageLog.logMessage("{0} features after exploding".format(len(newFeats)), "VoGis", Qgis.Info)
        return newFeats

    #https://github.com/SrNetoChan/MultipartSplit/blob/master/splitmultipart.py
    def explodeMultiPartFeature(self, provider, feat):
        tmpFeat = QgsFeature()

        # Get attributes from original feature
        # Because of changes in the way the 1.9 api handle attributes
        #pyqtRemoveInputHook()
        #pdb.set_trace()
        newAttribs = feat.attributes()
        for j in range(newAttribs.__len__()):
            #if not provider.defaultValue(j).isNull():
            #    newAttribs[j] = provider.defaultValue(j)
            newAttribs[j] = provider.defaultValue(j)
        tmpFeat.setAttributes(newAttribs)

        parts = feat.geometry().asGeometryCollection()

        newFeats = []
        for part in parts:
            if part.isEmpty() is False:
                tmpFeat.setGeometry(part)
                newFeat = QgsFeature(tmpFeat)
                #if newFeat.isValid() is True:
                newFeats.append(newFeat)

        return newFeats

    def __transferAttributes(self, provider, attrMap, featNew):
        #QgsMessageLog.logMessage("{0}: {1}".format("__transferAttributes OLD", self.__printAttribs(attrMap)), "VoGis", Qgis.Info)
        #QgsMessageLog.logMessage("{0}: {1}".format("__transferAttributes NEW", self.__printAttribs(featNew.attributeMap())), "VoGis", Qgis.Info)

        newAttribs = attrMap
        for j in range(newAttribs.__len__()):
            if not provider.defaultValue(j) is None:
                newAttribs[j] = provider.defaultValue(j)
        featNew.setAttributes(newAttribs)

        #QgsMessageLog.logMessage("{0}: {1}".format("__transferAttributes NEW2", self.__printAttribs(featNew.attributeMap())), "VoGis", Qgis.Info)
        return featNew

    def deleteVectorFile(self, fileName):
        if QgsVectorFileWriter.deleteShapeFile(fileName) is False:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                QApplication.translate("code", "Konnte vorhandene Datei nicht löschen") + ": " + fileName
                                )
            return False
        else:
            return True

    def loadVectorFile(self, fileName):
        fileSaved = QApplication.translate("code", "Datei gespeichert.")
        load =QApplication.translate("code", "Laden?")
        reply = QMessageBox.question(self.iface.mainWindow(),
                                     "VoGIS-Profiltool",
                                     #fileSaved + os.linesep + os.linesep + os.linesep + load,
                                     fileSaved + "\n\n\n" + load,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes
                                     )
        if reply == QMessageBox.Yes:
            self.iface.addVectorLayer(fileName,
                                      os.path.basename(fileName),
                                      "ogr"
                                      )


    #def createOgrDataSrcAndLyr(self, driverName, fileName, epsg, geomType):
    def createOgrDataSrcAndLyr(self, driverName, fileName, wkt, geomType):
        drv = ogr.GetDriverByName(driverName)
        if drv is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                driverName + " " + QApplication.translate("code", "Treiber nicht verfügbar")
                                )
            return None, None

        ds = drv.CreateDataSource(fileName)
        if ds is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                QApplication.translate("code", "Konnte Datei nicht erstellen") + ": " + driverName + ", " + fileName
                                )
            return None, None

        #if epsg is None:
        if wkt is None:
            spatialReference = None
        else:
            spatialReference = osr.SpatialReference()
            #if spatialReference.ImportFromEPSG(epsg) != 0:
            if spatialReference.ImportFromWkt(wkt) != 0:
                QMessageBox.warning(self.iface.mainWindow(),
                                    "VoGIS-Profiltool",
                                    QApplication.translate("code", "Konnte Koordinatensystem nicht initialisieren!") + " EPSG: {0}".format(epsg)
                                    )
                return None, None
        #http://www.digital-geography.com/create-and-edit-shapefiles-with-python-only/
        lyr = ds.CreateLayer("ogrlyr", spatialReference, geomType)
        if lyr is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                QApplication.translate("code", "Konnte Layer nicht erstellen") + ": {0}, {1}".format(driverName, fileName)
                                )
            return None, None

        return ds, lyr

    def createOgrPointFeature(self, lyr, v):
        #QgsMessageLog.logMessage("zVal: {0}".format(v.zvals[0]), "VoGis", Qgis.Info)
        feat = ogr.Feature(lyr.GetLayerDefn())
        pt = ogr.Geometry(ogr.wkbPoint25D)
        z = 0
        if len(v.zvals) > 0:
            z = v.zvals[0]
        if z is None:
            pt.SetPoint(0, v.x, v.y)
        else:
            pt.SetPoint(0, v.x, v.y, z)
        feat.SetGeometry(pt)
        return feat
