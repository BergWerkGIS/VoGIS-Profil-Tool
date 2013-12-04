# -*- coding: utf-8 -*-

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QMessageBox
from qgis.core import QGis
if QGis.QGIS_VERSION_INT < 10900:
    import ogr
else:
    from osgeo import ogr
from qgis.core import QgsMessageLog
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsField
from qgis.core import QgsPoint
#from qgis.core import QgsGeometry
#from qgis.core import QgsFeature
from u import Util
from ..bo.settings import enumModeLine


class ExportShape:

    def __init__(self, iface, hekto, attribs, delimiter, decimalDelimiter, fileName, settings, profiles):
        self.iface = iface
        self.hekto = hekto
        self.attribs = attribs
        self.delimiter = delimiter
        self.decimalDelimiter = decimalDelimiter
        self.fileName = fileName
        self.settings = settings
        self.profiles = profiles
        self.u = Util(self.iface)

    def exportPoint(self):

        if self.u.deleteVectorFile(self.fileName) is False:
            return

        #self.settings.mapData.selectedLineLyr.line.crs().epsg()
        if QGis.QGIS_VERSION_INT < 10900:
            #epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().epsg()
            wkt = self.iface.mapCanvas().mapRenderer().destinationCrs().toWkt()
        else:
            #u'EPSG:31254'
            #authid = self.iface.mapCanvas().mapRenderer().destinationCrs().authid().split(":")[1]
            #epsg = int(authid)
            wkt = self.iface.mapCanvas().mapRenderer().destinationCrs().toWkt()
        #ds, lyr = self.u.createOgrDataSrcAndLyr('ESRI Shapefile', self.fileName, epsg, ogr.wkbPoint25D)
        ds, lyr = self.u.createOgrDataSrcAndLyr('ESRI Shapefile', self.fileName, wkt, ogr.wkbPoint25D)
        if ds is None:
            return

        flds = ['Profillaenge', 'Segmentlaenge', 'Rechtswert', 'Hochwert']
        for fld in flds:
            fldDfn = ogr.FieldDefn(fld, ogr.OFTReal)
            fldDfn.SetWidth(12)
            fldDfn.SetPrecision(3)
            if lyr.CreateField(fldDfn) != 0:
                QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld))
                return

        #raster
        for r in self.settings.mapData.rasters.selectedRasters():
            #QgsMessageLog.logMessage('rasterName: {0}'.format(r.name), 'VoGis')
            fldDfn = ogr.FieldDefn(r.name, ogr.OFTReal)
            fldDfn.SetWidth(8)
            fldDfn.SetPrecision(2)
            if lyr.CreateField(fldDfn) != 0:
                QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(r.name))
                return

        #Punkttypen
        flds = ['ProfilNr', 'SegNr', 'PktNr']
        for fld in flds:
            fldDfn = ogr.FieldDefn(fld, ogr.OFTInteger)
            if lyr.CreateField(fldDfn) != 0:
                QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld))
                return

        #PktKlasse
        fldDfn = ogr.FieldDefn('PktKlasse', ogr.OFTString)
        fldDfn.SetWidth(1)
        if lyr.CreateField(fldDfn) != 0:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format('PktKlasse'))
            return

        if self.hekto is True:
            QgsMessageLog.logMessage('Creating HEKTO field', 'VoGis')
            fldDfn = ogr.FieldDefn('Hekto', ogr.OFTString)
            fldDfn.SetWidth(10)
            if lyr.CreateField(fldDfn) != 0:
                QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format('Hekto'))
                return

        if self.attribs is True:
            #QgsMessageLog.logMessage('EXPORT POINT attribs TRUE', 'VoGis')
            if self.settings.modeLine == enumModeLine.line:
                provider = self.settings.mapData.selectedLineLyr.line.dataProvider()
                if QGis.QGIS_VERSION_INT < 10900:
                    for(idx, fld) in provider.fields().iteritems():
                        fldTyp = fld.type()
                        if fldTyp == QVariant.Double:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTReal)
                        elif fldTyp == QVariant.Int:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTInteger)
                        else:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTString)
                            fldDfn.SetWidth(50)
                        if lyr.CreateField(fldDfn) != 0:
                            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld.name()))
                            return
                else:
                    for fld in provider.fields():
                        fldTyp = fld.type()
                        if fldTyp == QVariant.Double:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTReal)
                        elif fldTyp == QVariant.Int:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTInteger)
                        else:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTString)
                            fldDfn.SetWidth(50)
                        if lyr.CreateField(fldDfn) != 0:
                            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld.name()))
                            return
        else:
            QgsMessageLog.logMessage('attribs FALSE', 'VoGis')

        segOld = None
        for p in self.profiles:
            for s in p.segments:
                if segOld is not None:
                    v = segOld.vertices[len(segOld.vertices) - 1]
                    feat = self.u.createOgrPointFeature(lyr, v)
                    feat = self.__addValues(feat, v, s.id)
                    if lyr.CreateFeature(feat) != 0:
                        QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Feature nicht erstellen: {0}'.format(v.id))
                        return
                    feat.Destroy()
                for v in s.vertices:
                    feat = self.u.createOgrPointFeature(lyr, v)
                    feat = self.__addValues(feat, v, None)
                    if lyr.CreateFeature(feat) != 0:
                        QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Feature nicht erstellen: {0}'.format(v.id))
                        return
                    feat.Destroy()
                segOld = s
            segOld = None

        ds.Destroy()
        ds = None
        self.u.loadVectorFile(self.fileName)

    def __addValues(self, feat, v, sId):
        feat.SetField(0, round(v.distanceProfile, 3))
        if sId is None:
            feat.SetField(1, round(v.distanceSegment, 3))
        else:
            feat.SetField(1, 0)
        #feat.SetField(2, round(v.x, 3))
        feat.SetField(2, v.x * 1000 / 1000)
        feat.SetField(3, round(v.y, 3))
        fldCnt = 4
        if len(v.zvals) > 0:
            for z in v.zvals:
                zVal = -9999
                if z is not None:
                    zVal = z
                feat.SetField(fldCnt, round(zVal, 3))
                fldCnt += 1
        feat.SetField(fldCnt, v.profileId)
        fldCnt += 1
        if sId is None:
            feat.SetField(fldCnt, v.segmentId)
        else:
            feat.SetField(fldCnt, sId)
        fldCnt += 1
        feat.SetField(fldCnt, v.vertexId)
        fldCnt += 1
        feat.SetField(fldCnt, v.getType())
        fldCnt += 1
        if self.hekto is True:
            #QgsMessageLog.logMessage('fldIdx:{0} {1}'.format(fldCnt, v.getHekto(self.decimalDelimiter)), 'VoGis')
            #feat.SetField(fldCnt, 'HEKTO')
            if QGis.QGIS_VERSION_INT < 10900:
                feat.SetField(fldCnt, v.getHekto(self.decimalDelimiter))
            else:
                feat.SetField(fldCnt, str(v.getHekto(self.decimalDelimiter)))
            fldCnt += 1
        if self.attribs is True:
            #QgsMessageLog.logMessage('modeLine:{0}'.format(self.settings.modeLine), 'VoGis')
            if self.settings.modeLine == enumModeLine.line:
                for a in v.getAttributeVals():
                    feat.SetField(fldCnt, a)
                    fldCnt += 1
        return feat

    def exportLine(self):

        if self.u.deleteVectorFile(self.fileName) is False:
            return

        #self.settings.mapData.selectedLineLyr.line.crs().epsg()
        wkt = self.iface.mapCanvas().mapRenderer().destinationCrs().toWkt()
        ds, lyr = self.u.createOgrDataSrcAndLyr('ESRI Shapefile', self.fileName, wkt, ogr.wkbLineString25D)
        if ds is None:
            return

        fld = 'Profillaenge'
        fldDfn = ogr.FieldDefn(fld, ogr.OFTReal)
        fldDfn.SetWidth(12)
        fldDfn.SetPrecision(3)
        if lyr.CreateField(fldDfn) != 0:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld))
            return

        fld = 'DHM'
        fldDfn = ogr.FieldDefn(fld, ogr.OFTString)
        fldDfn.SetWidth(20)
        if lyr.CreateField(fldDfn) != 0:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld))
            return

        if self.attribs is True:
            QgsMessageLog.logMessage('EXPORT LINE attribs TRUE', 'VoGis')
            if self.settings.modeLine == enumModeLine.line:
                provider = self.settings.mapData.selectedLineLyr.line.dataProvider()
                if QGis.QGIS_VERSION_INT < 10900:
                    for(idx, fld) in provider.fields().iteritems():
                        fldTyp = fld.type()
                        if fldTyp == QVariant.Double:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTReal)
                        elif fldTyp == QVariant.Int:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTInteger)
                        else:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTString)
                            fldDfn.SetWidth(50)
                        if lyr.CreateField(fldDfn) != 0:
                            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld.name()))
                            return
                else:
                    for fld in provider.fields():
                        fldTyp = fld.type()
                        if fldTyp == QVariant.Double:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTReal)
                        elif fldTyp == QVariant.Int:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTInteger)
                        else:
                            fldDfn = ogr.FieldDefn(str(fld.name()), ogr.OFTString)
                            fldDfn.SetWidth(50)
                        if lyr.CreateField(fldDfn) != 0:
                            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Konnte Attribut nicht erstellen: {0}'.format(fld.name()))
                            return
        else:
            QgsMessageLog.logMessage('attribs FALSE', 'VoGis')

        if self.settings.onlyHektoMode is True:
            for p in self.profiles:
                feat = ogr.Feature(lyr.GetLayerDefn())
                lineGeom = ogr.Geometry(ogr.wkbLineString25D)
                lastV = None
                for s in p.segments:
                    for idxV in range(len(s.vertices)):
                        v = s.vertices[idxV]
                        lastV = v
                        lineGeom.AddPoint(v.x, v.y, 0)
                feat.SetField(0, lastV.distanceProfile)
                fldCnt = 1
                if self.attribs is True:
                    #QgsMessageLog.logMessage('modeLine:{0}'.format(self.settings.modeLine), 'VoGis')
                    if self.settings.modeLine == enumModeLine.line:
                        for a in v.getAttributeVals():
                            feat.SetField(fldCnt, a)
                            fldCnt += 1
                feat.SetGeometry(lineGeom)
                if lyr.CreateFeature(feat) != 0:
                    QMessageBox.warning(self.iface.mainWindow(),
                                        "VoGIS-Profiltool",
                                        'Konnte Feature nicht erstellen: {0}'.format(p.id)
                                        )
                    return
                lineGeom.Destroy()
                feat.Destroy()
        else:
            selRstrs = self.settings.mapData.rasters.selectedRasters()
            for p in self.profiles:
                feats = {}
                lineGeoms = {}
                lastV = {}
                for idx in range(len(selRstrs)):
                    feats[idx] = ogr.Feature(lyr.GetLayerDefn())
                    lineGeoms[idx] = ogr.Geometry(ogr.wkbLineString25D)
                for s in p.segments:
                    for idxV in range(len(s.vertices)):
                        v = s.vertices[idxV]
                        for idx in range(len(selRstrs)):
                            lastV[idx] = v
                            #QgsMessageLog.logMessage('zVal: {0}'.format(v.zvals[idx]), 'VoGis')
                            lineGeoms[idx].AddPoint(v.x, v.y, v.zvals[idx])
                for idx in range(len(selRstrs)):
                    feats[idx].SetField(0, round(lastV[idx].distanceProfile, 3))
                    feats[idx].SetField(1, selRstrs[idx].name)
                    fldCnt = 2
                    if self.attribs is True:
                        #QgsMessageLog.logMessage('modeLine:{0}'.format(self.settings.modeLine), 'VoGis')
                        if self.settings.modeLine == enumModeLine.line:
                            for a in v.getAttributeVals():
                                feats[idx].SetField(fldCnt, a)
                                fldCnt += 1
                    feats[idx].SetGeometry(lineGeoms[idx])
                    if lyr.CreateFeature(feats[idx]) != 0:
                        QMessageBox.warning(self.iface.mainWindow(),
                                            "VoGIS-Profiltool",
                                            'Konnte Feature nicht erstellen: {0}'.format(p.id)
                                            )
                        return
                    lineGeoms[idx].Destroy()
                    feats[idx].Destroy()
        ds.Destroy()
        ds = None
        self.u.loadVectorFile(self.fileName)

        # for p in self.profiles:
        #     vertices = []
        #     lastV = None
        #     profileLength = 0
        #     for s in p.segments:
        #         for v in s.vertices:
        #             lastV = v
        #             profileLength = v.distanceProfile
        #             vertices.append(QgsPoint(v.x, v.y))
        #     feat = ut.createQgLineFeature(vertices)
        #     feat.addAttribute(0, profileLength)
        #     fldCnt = 1
        #     if self.attribs is True:
        #         if self.settings.modeLine == enumModeLine.line:
        #             lastV
        #             for a in lastV.attributes:
        #                 feat.addAttribute(fldCnt, a)
        #                 fldCnt += 1
        #     shpWriter.addFeature(feat)

        # del shpWriter
        # self.__loadShp(self.fileName)
