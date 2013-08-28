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
from bo.plotExtent import PlotExtent
from util.u import Util
from util.exportShape import ExportShape
from util.exportDxf import ExportDxf
import locale
#import ogr
import matplotlib
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg


class VoGISProfilToolPlotDialog(QDialog):
    def __init__(self, interface, settings, profiles):

        QDialog.__init__(self, interface.mainWindow())
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

        pltExt = PlotExtent()
        for p in self.profiles:
            pltExt.union(p.getExtent())

        self.pltWidget = self.__createMatplotlibCanvas(pltExt)
        layout = self.ui.IDC_frPlot.layout()
        #QgsMessageLog.logMessage('layout: {0}'.format(layout), 'VoGis')
        layout.addWidget(self.pltWidget)
        pltToolbar = matplotlib.backends.backend_qt4agg.NavigationToolbar2QTAgg(self.pltWidget, self.ui.IDC_frPlot)
        self.ui.IDC_frToolbar.layout().addWidget(pltToolbar)
        lstActions = pltToolbar.actions()
        pltToolbar.removeAction(lstActions[7])

        #x = [100, 500, 620, 770, 1200]
        #y = [900, 540, 893, 999, 2500]
        #line = Line2D(x, y, linewidth=2, linestyle='-', picker=True)
        #self.subplot.add_line(line)
        colors =[(1.0, 0.5, 0.5, 0.5), (0.5, 1.0, 0.0, 0.5)]
        for p in self.profiles:
            #x, pltSegs = p.getPlotSegments()
            #QgsMessageLog.logMessage('x: {0}'.format(x), 'VoGis')
            pltSegs = p.getPlotSegments()
            #QgsMessageLog.logMessage('pltSegs: {0}'.format(pltSegs), 'VoGis')
            lineColl = LineCollection(pltSegs, linewidths=2, linestyles='solid', colors=colors)
            #lineColl.set_array(x)
            self.subplot.add_collection(lineColl)

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

    def __plotPicked(self, event):
        if isinstance(event.artist, Line2D):
            line = event.artist
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            ind = event.ind
            QgsMessageLog.logMessage('{0}: {1} {2}'.format(ind, xdata, ydata), 'VoGis')
            QgsMessageLog.logMessage(help(line), 'VoGis')
        else:
            QgsMessageLog.logMessage('no Line2D', 'VoGis')

    def __createMatplotlibCanvas(self, pltExt):
            fig = Figure((1.0, 1.0),
                         linewidth=0.0,
                         subplotpars=matplotlib.figure.SubplotParams(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
                         )
            #font = {'family': 'arial', 'weight': 'normal', 'size': 12}
            #rc('font', **font)
            rect = fig.patch
            rect.set_facecolor((0.9, 0.9, 0.9))

            self.subplot = fig.add_axes((0.05, 0.15, 0.92, 0.82))
            self.subplot.set_xbound(pltExt.xmin, pltExt.xmax)
            self.subplot.set_ybound(pltExt.ymin, pltExt.ymax)
            self.__setupAxes(self.subplot)
            canvas = FigureCanvasQTAgg(fig)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            canvas.setSizePolicy(sizePolicy)
            canvas.mpl_connect('pick_event', self.__plotPicked)
            return canvas

    def __setupAxes(self, axe1):
        axe1.grid()
        axe1.tick_params(axis="both",
                         which="major",
                         direction="out",
                         length=10,
                         width=1,
                         bottom=True,
                         top=False,
                         left=True,
                         right=False
                         )
        axe1.minorticks_on()
        axe1.tick_params(axis="both",
                         which="minor",
                         direction="out",
                         length=5,
                         width=1,
                         bottom=True,
                         top=False,
                         left=True,
                         right=False
                         )

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
