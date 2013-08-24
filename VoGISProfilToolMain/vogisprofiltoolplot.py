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
from util.exportDxf import ExportDxf
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
        #QgsMessageLog.logMessage('QGIS Locale:{0}'.format(QSettings().value("locale/userLocale").toString()), 'VoGis')
        #!!!nl_langinfo not available on Windows!!!
        #http://docs.python.org/2.7/library/locale.html#locale.nl_langinfo
        # ...  This function is not available on all systems ...
        #decimalDelimiter = locale.nl_langinfo(locale.RADIXCHAR)
        decimalDelimiter = locale.localeconv()['decimal_point']
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
        self.__exportDxf(True)

    def exportDxfLine(self):
        self.__exportDxf(False)

    def __exportDxf(self, asPnt):
        u = Util(self.iface)
        fileName = u.getFileName("DXF exportieren", "DXF (*.dxf)")
        if fileName == '':
            return

        exDxf = ExportDxf(self.iface, fileName, self.settings, self.profiles)
        if asPnt is True:
            exDxf.exportPoint()
        else:
            exDxf.exportLine()

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
