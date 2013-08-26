# -*- coding: utf-8 -*-

#from os.path import basename
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QMessageBox
import ogr
from qgis.core import QgsMessageLog
from qgis.core import QGis
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsField
from qgis.core import QgsPoint
#from qgis.core import QgsGeometry
#from qgis.core import QgsFeature
from u import Util
from ..bo.settings import enumModeLine


class ExportDxf:

    def __init__(self, iface, fileName, settings, profiles):
        self.iface = iface
        self.fileName = fileName
        self.settings = settings
        self.profiles = profiles
        self.u = Util(self.iface)

    def exportPoint(self):

        if self.u.deleteVectorFile(self.fileName) is False:
            return

        ds, lyr = self.u.createOgrDataSrcAndLyr("DXF", self.fileName, None, ogr.wkbPoint25D)
        if ds is None:
            return

        field_defn = ogr.FieldDefn('Layer', ogr.OFTString)
        field_defn.SetWidth(32)

        if lyr.CreateField(field_defn) != 0:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte Attribut nicht erstellen: {0}'.format('Layer')
                                )
            return

        selRstrs = self.settings.mapData.rasters.selectedRasters()
        for p in self.profiles:
            for s in p.segments:
                for v in s.vertices:
                    for idx in range(len(selRstrs)):
                        #QgsMessageLog.logMessage('rasterName: {0}'.format(selRstrs[idx].name), 'VoGis')
                        feat = ogr.Feature(lyr.GetLayerDefn())
                        feat.SetField('Layer', str(selRstrs[idx].name))
                        pt = ogr.Geometry(ogr.wkbPoint25D)
                        pt.SetPoint(0, v.x, v.y, v.zvals[idx])
                        feat.SetGeometry(pt)
                        if lyr.CreateFeature(feat) != 0:
                            QMessageBox.warning(self.iface.mainWindow(),
                                                "VoGIS-Profiltool",
                                                'Konnte Feature nicht erstellen: {0}'.format(v.id)
                                                )
                            return
                        feat.Destroy()
        ds = None
        #crashes QGIS: why?
        #self.u.loadVectorFile(self.fileName)

    def exportLine(self):

        if self.u.deleteVectorFile(self.fileName) is False:
            return

        ds, lyr = self.u.createOgrDataSrcAndLyr("DXF", self.fileName, None, ogr.wkbLineString25D)
        if ds is None:
            return

        field_defn = ogr.FieldDefn('Layer', ogr.OFTString)
        field_defn.SetWidth(32)

        if lyr.CreateField(field_defn) != 0:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte Attribut nicht erstellen: {0}'.format('Layer')
                                )
            return

        selRstrs = self.settings.mapData.rasters.selectedRasters()
        for p in self.profiles:
            feats = {}
            lineGeoms = {}
            for idx in range(len(selRstrs)):
                feats[idx] = ogr.Feature(lyr.GetLayerDefn())
                feats[idx].SetField('Layer', str('{0} {1}'.format(selRstrs[idx].name, p.id)))
                lineGeoms[idx] = ogr.Geometry(ogr.wkbLineString25D)
            for s in p.segments:
                for idxV in range(len(s.vertices)):
                    v = s.vertices[idxV]
                    for idx in range(len(selRstrs)):
                        #QgsMessageLog.logMessage('zVal: {0}'.format(v.zvals[idx]), 'VoGis')
                        lineGeoms[idx].AddPoint(v.x, v.y, v.zvals[idx])
            for idx in range(len(selRstrs)):
                feats[idx].SetGeometry(lineGeoms[idx])
                if lyr.CreateFeature(feats[idx]) != 0:
                    QMessageBox.warning(self.iface.mainWindow(),
                                        "VoGIS-Profiltool",
                                        'Konnte Feature nicht erstellen: {0}'.format(p.id)
                                        )
                    return
                feats[idx].Destroy()
        ds.Destroy()
        ds = None
        #crashes QGIS: why?
        #self.u.loadVectorFile(self.fileName)
