# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VoGISProfilToolMainDialog
                                 A QGIS plugin
 VoGIS ProfilTool
                             -------------------
        begin                : 2013-05-28
        copyright            : (C) 2013 by BergWerk GIS
        email                : wb@BergWerk-GIS.at
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui.ui_vogisprofiltoolplot import Ui_VoGISProfilToolPlot
from util.u import Util
from util.exportShape import ExportShape
import locale
import ogr


class VoGISProfilToolPlotDialog(QDialog):
    def __init__(self, interface, settings, profiles):

        QDialog.__init__(self)
        self.iface = interface
        self.settings = settings
        self.profiles = profiles
        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolPlot()
        self.ui.setupUi(self)

        #nimmt die Locale vom System, nicht von QGIS
        #kein Weg gefunden, um QGIS Locale: QSettings().value("locale/userLocale")
        #zu initialisieren, nur um Dezimaltrenne auszulesen
        QgsMessageLog.logMessage('QGIS Locale:{0}'.format(QSettings().value("locale/userLocale").toString()), 'VoGis')
        decimalDelimiter = locale.nl_langinfo(locale.RADIXCHAR)
        QgsMessageLog.logMessage('delimiter:{0}'.format(decimalDelimiter), 'VoGis')
        idx = self.ui.IDC_cbDecimalDelimiter.findText(decimalDelimiter, Qt.MatchExactly)
        QgsMessageLog.logMessage('idx:{0}'.format(idx), 'VoGis')
        self.ui.IDC_cbDecimalDelimiter.setCurrentIndex(idx)

    def accept(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "ACCEPTED")
        QDialog.accept(self)

    def reject(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "REJECTED")
        QDialog.reject(self)

    def exportShpPnt(self):
        self.__exportShp(True)

    def exportShpLine(self):
        self.__exportShp(False)

    def __exportShp(self, asPnt):

        u = Util(self.iface)
        if asPnt is True:
            caption = 'Punkt Shapefile exportieren'
        else:
            caption = 'Linien Shapefile exportieren'
        fileName = u.getFileName(caption, "SHP (*.shp)")
        if fileName == '':
            return
        expShp = ExportShape(self.iface,
                             (self.ui.IDC_chkHekto.checkState() == Qt.Checked),
                             (self.ui.IDC_chkLineAttributes.checkState() == Qt.Checked),
                             self.__getDelimiter(),
                             self.__getDecimalDelimiter(),
                             fileName,
                             self.settings,
                             self.profiles
                             )
        if asPnt is False:
            expShp.exportLine()
        else:
            expShp.exportPoint()

    def exportCsvXls(self):
        u = Util(self.iface)
        fileName = u.getFileName("CSV-datei exportieren", "CSV (*.csv)")
        if fileName == '':
            return

        hekto = (self.ui.IDC_chkHekto.checkState() == Qt.Checked)
        attribs = (self.ui.IDC_chkLineAttributes.checkState() == Qt.Checked)
        delimiter = ';'
        decimalDelimiter = self.__getDecimalDelimiter()

        txt = open(fileName, 'w')

        txt.write(self.profiles[0].writeHeader(self.settings.mapData.rasters.selectedRasters(), hekto, attribs, delimiter))
        for p in self.profiles:
            #txt.write('=====Profil {0}======\r\n'.format(p.id))
            #txt.write('Segments:{0}\r\n'.format(len(p.segments)))
            #for s in p.segments:
            #    txt.write('Vertices:{0}\r\n'.format(len(s.vertices)))
            txt.write(p.toString(hekto,
                                 attribs,
                                 delimiter,
                                 decimalDelimiter
                                 ))

    def exportTxt(self):

        u = Util(self.iface)
        fileName = u.getFileName("Textdatei exportieren", "TXT (*.txt)")
        if fileName == '':
            return

        hekto = (self.ui.IDC_chkHekto.checkState() == Qt.Checked)
        attribs = (self.ui.IDC_chkLineAttributes.checkState() == Qt.Checked)
        delimiter = self.__getDelimiter()
        decimalDelimiter = self.__getDecimalDelimiter()

        txt = open(fileName, 'w')

        txt.write(self.profiles[0].writeHeader(self.settings.mapData.rasters.selectedRasters(), hekto, attribs, delimiter))
        for p in self.profiles:
            #txt.write('=====Profil {0}======\r\n'.format(p.id))
            #txt.write('Segments:{0}\r\n'.format(len(p.segments)))
            #for s in p.segments:
            #    txt.write('Vertices:{0}\r\n'.format(len(s.vertices)))
            txt.write(p.toString(hekto,
                                 attribs,
                                 delimiter,
                                 decimalDelimiter
                                 ))

        txt.close()

    def exportAutoCadTxt(self):
        u = Util(self.iface)
        fileName = u.getFileName("AutoCad Textdatei exportieren", "TXT (*.txt)")
        if fileName == '':
            return
        txt = open(fileName, 'w')
        for p in self.profiles:
            txt.write(p.toACadTxt(' ', '.'))
        txt.close()

    def exportDxfPnt(self):
        u = Util(self.iface)
        fileName = u.getFileName("DXF exportieren", "DXF (*.dxf)")
        if fileName == '':
            return

        driverName = "DXF"
        drv = ogr.GetDriverByName(driverName)
        if drv is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                '{0} Treiber nicht verfügbar'.format(driverName)
                                )
            return

        ds = drv.CreateDataSource(fileName)
        if ds is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte DXF nicht erstellen: {0}'.format(fileName)
                                )
            return

http://www.digital-geography.com/create-and-edit-shapefiles-with-python-only/
   sdf  ((   lyr = ds.CreateLayer("dxf1", 'Spatial REFERENCE, ogr.wkbPoint)
        if lyr is None:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte DXF-Layer nicht erstellen: {0}'.format(fileName)
                                )
            return

        field_defn = ogr.FieldDefn('Layer', ogr.OFTString)
        field_defn.SetWidth(32)

        if lyr.CreateField(field_defn) != 0:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Konnte Attribut nicht erstellen: {0}'.format('Layer')
                                )
            return

        for p in self.profiles:
            for s in p.segments:
                for v in s.vertices:
                    feat = ogr.Feature(lyr.GetLayerDefn())
                    feat.SetField('Layer', 'TheLayer')
                    pt = ogr.Geometry(ogr.wkbPoint)
                    pt.SetPoint(0, v.x, v.y, v.zvals[0])
                    feat.SetGeometry(pt)
                    if lyr.CreateFeature(feat) != 0:
                        QMessageBox.warning(self.iface.mainWindow(),
                                            "VoGIS-Profiltool",
                                            'Konnte Feature nicht erstellen: {0}'.format(v.id)
                                            )
                        return
                    feat.Destroy()
        ds = None

        # flds = {}
        # flds[0] = QgsField('Layer', QVariant.String)
        # flds[1] = QgsField('Text', QVariant.String)
        # flds[2] = QgsField('BlockName', QVariant.String)
        # flds[3] = QgsField('SubClasses', QVariant.String)
        # flds[4] = QgsField('ExtendedEntity', QVariant.String)
        # #flds[5] = QgsField('Elevation', QVariant.Double)

        # dxfWriter = QgsVectorFileWriter(fileName,
        #                                 "CP1250",
        #                                 flds,
        #                                 QGis.WKBPoint,
        #                                 None,
        #                                 'DXF'
        #                                 )
        # if dxfWriter.hasError() != QgsVectorFileWriter.NoError:
        #     QMessageBox.warning(self.iface.mainWindow(),
        #                         "VoGIS-Profiltool",
        #                         'Konnte DXF nicht erstellen: {0}\r\n{1}'.format(fileName, dxfWriter.errorMessage())
        #                         )
        #     return

        # for p in self.profiles:
        #     for s in p.segments:
        #         for v in s.vertices:
        #             feat = u.createQgPointFeature(v)
        #             feat.addAttribute(0, 'TheLyr')
        #             feat.addAttribute(1, 'TheTxt')
        #             feat.addAttribute(2, 'BlckNm')
        #             feat.addAttribute(3, 'SbCls')
        #             feat.addAttribute(4, 'XEnt')
        #             #feat.addAttribute(5, 'ntity')
        #             dxfWriter.addFeature(feat)
        # del dxfWriter

    def __getDecimalDelimiter(self):
        #delim = self.ui.IDC_cbDecimalDelimiter.itemData(self.ui.IDC_cbDecimalDelimiter.currentIndex())
        delim = self.ui.IDC_cbDecimalDelimiter.currentText()
        #QgsMessageLog.logMessage('delim:' + str(delim), 'VoGis')
        return delim

    def __getDelimiter(self):
        #delim = self.ui.IDC_cbDelimiter.itemData(self.ui.IDC_cbDelimiter.currentIndex())
        delim = self.ui.IDC_cbDelimiter.currentText()
        if delim == "tab":
            delim = '\t'
        return delim
