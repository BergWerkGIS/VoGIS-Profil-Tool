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


class VoGISProfilToolPlotDialog(QDialog):
    def __init__(self, interface, settings, profiles):

        QDialog.__init__(self)
        self.iface = interface
        self.settings = settings
        self.profiles = profiles
        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolPlot()
        self.ui.setupUi(self)

    def accept(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "ACCEPTED")
        QDialog.accept(self)

    def reject(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "REJECTED")
        QDialog.reject(self)

    def exportTxt(self):

        u = Util(self.iface)
        fileName = u.getFileName("Textdatei exportieren", "TXT (*.txt)")

        txt = open(fileName, 'w')

        for p in self.profiles:
            #txt.write('=====Profil {0}======\r\n'.format(p.id))
            #txt.write('Segments:{0}\r\n'.format(len(p.segments)))
            #for s in p.segments:
            #    txt.write('Vertices:{0}\r\n'.format(len(s.vertices)))
            txt.write(p.toString(self.__getDelimiter(), self.__getDecimalDelimiter()))

        txt.close()

    def __getDecimalDelimiter(self):
        #delim = self.ui.IDC_cbDecimalDelimiter.itemData(self.ui.IDC_cbDecimalDelimiter.currentIndex())
        delim = self.ui.IDC_cbDecimalDelimiter.currentText()
        #QgsMessageLog.logMessage('delim:' + str(delim), 'VoGis')
        return delim

    def __getDelimiter(self):
        #delim = self.ui.IDC_cbDelimiter.itemData(self.ui.IDC_cbDelimiter.currentIndex())
        delim = self.ui.IDC_cbDelimiter.currentText()
        if delim == "tab":
            #QgsMessageLog.logMessage('IsTab YEaH' + str(delim), 'VoGis')
            delim = '\t'
        #else:
            #QgsMessageLog.logMessage('NO TAB' + str(delim), 'VoGis')
        return delim
