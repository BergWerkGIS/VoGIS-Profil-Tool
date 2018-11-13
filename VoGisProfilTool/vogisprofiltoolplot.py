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
import os
import locale
from random import randrange
from math import floor, pow, sqrt

#import ogr
import numpy
import matplotlib
#not available on Windows by default
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import font_manager
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from qgis.PyQt.QtCore import Qt, QFileInfo
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QPushButton, QLineEdit, QLabel, QDialog, QApplication, QSizePolicy, QMessageBox, QAction

from qgis.core import Qgis, QgsSettings, QgsMessageLog, QgsProject, QgsLayoutItemPicture, QgsLayoutSize, QgsUnitTypes

from VoGisProfilTool.ui.ui_vogisprofiltoolplot import Ui_VoGISProfilToolPlot

from VoGisProfilTool.vogisprofiltoollayouts import VoGISProfilToolLayoutsDialog
from VoGisProfilTool.vogisprofiltoolscale import VoGISProfilToolScaleDialog

from VoGisProfilTool.bo.plotExtent import PlotExtent
from VoGisProfilTool.bo.chartpoint import ChartPoint

from VoGisProfilTool.util.u import Util
from VoGisProfilTool.util.exportShape import ExportShape
from VoGisProfilTool.util.exportDxf import ExportDxf
from VoGisProfilTool.util.exportXls import ExportXls

import VoGisProfilTool.resources_rc

LEFT_MARGIN = 0.08
BOTTOM_MARGIN = 0.15
RIGHT_MARGIN = 0.92
TOP_MARGIN = 0.82

TO_INCH = 0.393700787


class VoGISProfilToolPlotDialog(QDialog):
    def __init__(self, interface, settings, profiles, intersections, cadastre):
        QDialog.__init__(self, interface.mainWindow())

        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolPlot()
        self.ui.setupUi(self)

        self.ui.btnAddLayout.clicked.connect(self.addToLayout)

        self.iface = interface
        #output debug Log Messages: mainly for debugging matplotlib
        self.debug = False
        self.settings = settings
        self.profiles = profiles
        self.intersections = intersections
        self.cadastre = cadastre

        if self.settings.onlyHektoMode is True:
            self.ui.IDC_frPlot.hide()
            self.ui.IDC_frToolbar.hide()
            self.adjustSize()
            self.ui.IDC_chkHekto.setCheckState(Qt.Checked)
            self.ui.IDC_chkHekto.setEnabled(False)

        self.filePath = QgsSettings().value("vogisprofiltoolmain/savepath", "")

        #nimmt die Locale vom System, nicht von QGIS
        #kein Weg gefunden, um QGIS Locale: QSettings().value("locale/userLocale")
        #zu initialisieren, nur um Dezimaltrenne auszulesen
        #QgsMessageLog.logMessage("QGIS Locale:{0}".format(QSettings().value("locale/userLocale").toString()), "VoGis", Qgis.Info)
        #!!!nl_langinfo not available on Windows!!!
        #http://docs.python.org/2.7/library/locale.html#locale.nl_langinfo
        # ...  This function is not available on all systems ...
        #decimalDelimiter = locale.nl_langinfo(locale.RADIXCHAR)
        decimalDelimiter = locale.localeconv()["decimal_point"]
        QgsMessageLog.logMessage("delimiter:{0}".format(decimalDelimiter), "VoGis", Qgis.Info)
        idx = self.ui.IDC_cbDecimalDelimiter.findText(decimalDelimiter, Qt.MatchExactly)
        QgsMessageLog.logMessage("idx:{0}".format(idx), "VoGis", Qgis.Info)
        self.ui.IDC_cbDecimalDelimiter.setCurrentIndex(idx)

        plt_extent = PlotExtent()
        for profile in self.profiles:
            plt_extent.union(profile.getExtent())
            if self.debug:
                QgsMessageLog.logMessage(plt_extent.toString(), "VoGis", Qgis.Info)

        plt_extent.expand()

        self.orig_plt_xtnt = PlotExtent(plt_extent.xmin, plt_extent.ymin, plt_extent.xmax, plt_extent.ymax)
        self.plt_widget = self.__createMatplotlibCanvas(plt_extent)
        layout = self.ui.IDC_frPlot.layout()
        #QgsMessageLog.logMessage("layout: {0}".format(layout), "VoGis", Qgis.Info)
        layout.addWidget(self.plt_widget)

        plt_toolbar = NavigationToolbar2QT(self.plt_widget, self.ui.IDC_frPlot)
        self.ui.IDC_frToolbar.layout().addWidget(plt_toolbar)

        #adjust actions
        #QgsMessageLog.logMessage("{0}".format(dir(lstActions[0])), "VoGis", Qgis.Info)
#        for a in plt_toolbar.actions():
#            QgsMessageLog.logMessage("{0}".format(a.text()), "VoGis", Qgis.Info)
#        for t in plt_toolbar.toolitems:
#            QgsMessageLog.logMessage("{0}".format(t), "VoGis", Qgis.Info)
        #lstActions = plt_toolbar.actions()

        #https://hub.qgis.org/wiki/17/Icons_20

        firstaction = None
        for a in plt_toolbar.actions():
            atxt = a.text()
            if atxt == "Home":
                firstaction = a
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/home.png"))
            elif atxt == "Back":
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/zoomlast.png"))
            elif atxt == "Forward":
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/zoomnext.png"))
            elif atxt == "Pan":
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/pan.png"))
            elif atxt == "Zoom":
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/zoomselect.png"))
            elif atxt == "Save":
                a.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/save.png"))
            else:
                plt_toolbar.removeAction(a)

        self.actionSaveScale = QAction(QIcon(":/plugins/vogisprofiltoolmain/icons/save.png"),
                                       QApplication.translate("code", "Maßstab speichern"),
                                       plt_toolbar)
        plt_toolbar.addAction(self.actionSaveScale)
        self.actionSaveScale.triggered.connect(self.saveScale)

        #insert 1:1 zoom button
        self.one2one = QPushButton()
        self.one2one.setText("1:1")
        self.one2one.clicked.connect(self.__one2oneClicked)
        #plt_toolbar.addWidget(self.one2one)
        #insert QLineEdit to change the exaggeration
        #catch updating of figure, when exaggeration QLineEdit has been updated from draw_event of figure
        self.draw_event_fired = False
        #catch closing of dialog, when enter key has been used accept exaggeration edit field
        self.exaggeration_edited = False

        #insert edit field for exaggeration
        self.editExaggeration = QLineEdit()
        self.editExaggeration.setFixedWidth(60)
        self.editExaggeration.setMaximumWidth(60)
        plt_toolbar.insertWidget(firstaction, self.editExaggeration)
        self.editExaggeration.editingFinished.connect(self.__exaggeration_edited)

        #insert identify button -> deactivate all tools
        #HACK: picked event gets fired before click event
        self.plotpicked = False
        plt_toolbar.insertWidget(firstaction, self.one2one)
        self.identify = QPushButton()
        self.identify.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/identify.png"))
        self.identify.clicked.connect(self.__identify)
        plt_toolbar.insertWidget(firstaction, self.identify)

        #insert identify label to show name of clicked dhm
        self.dhmLbl = QLabel()
        plt_toolbar.insertWidget(firstaction, self.dhmLbl)

        #insert measure tool
        self.measuring = False
        self.measure_tool = QPushButton()
        self.measure_tool.setIcon(QIcon(":/plugins/vogisprofiltoolmain/icons/measure.png"))
        self.measure_tool.clicked.connect(self.__measure)
        plt_toolbar.insertWidget(firstaction, self.measure_tool)

        #show measure results
        self.click1 = None
        self.click2 = None
        self.click1pnt = None
        self.click2pnt = None
        self.measure_lbl = QLabel()
        self.measure_lbl.setText("  ")
        plt_toolbar.insertWidget(firstaction, self.measure_lbl)

        self.__drawProfiles(self.subplot)

        #save inital view in history
        plt_toolbar.push_current()
        #select pan tool
        plt_toolbar.pan()
        self.plt_toolbar = plt_toolbar
        #(matplotlib.pyplot).tight_layout(True)
        #plt.tight_layout()
        #self.fig.tight_layout()
        QApplication.restoreOverrideCursor()

    def accept(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "ACCEPTED")
        QgsMessageLog.logMessage("accept: {0}".format(self.exaggeration_edited), "VoGis", Qgis.Info)
        if self.exaggeration_edited is True:
            self.exaggeration_edited = False
            return
        QDialog.accept(self)

    def reject(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "REJECTED")
        QgsMessageLog.logMessage("reject: {0}".format(self.exaggeration_edited), "VoGis", Qgis.Info)
        if self.exaggeration_edited is True:
            self.exaggeration_edited = False
            return
        QDialog.reject(self)

    def exportShpPnt(self):
        self.__exportShp(True)

    def exportShpLine(self):
        self.__exportShp(False)

    def __exportShp(self, asPnt):
        u = Util(self.iface)
        if asPnt is True:
            caption = QApplication.translate("code", "Punkt Shapefile exportieren")
        else:
            caption = QApplication.translate("code", "Linien Shapefile exportieren")
        fileName, file_ext = u.getFileName(caption, [["shp", "shp"]], self.filePath)
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
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
        caption = QApplication.translate("code", "Excel- oder CSV-Datei exportieren")
        file_format = []
        file_format.append(["Microsoft Excel 2007/2010 XML", "xlsx"])
        file_format.append(["Comma-Separated Values CSV", "csv"])

        fileName, fileExt = u.getFileName(caption, file_format, self.filePath)
        QgsMessageLog.logMessage("fileName: {0} fileExt:{1}".format(fileName, fileExt), "VoGis", Qgis.Info)

        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
        hekto = (self.ui.IDC_chkHekto.checkState() == Qt.Checked)
        attribs = (self.ui.IDC_chkLineAttributes.checkState() == Qt.Checked)
        delimiter = ";"
        decimalDelimiter = self.__getDecimalDelimiter()

        if fileExt == "csv":
            txt = open(fileName, "w")
            txt.write(self.profiles[0].writeHeader(self.settings.mapData.rasters.selectedRasters(), hekto, attribs, delimiter))
            for p in self.profiles:
                #txt.write("=====Profil {0}======{1}".format(p.id, os.linesep))
                #txt.write("Segments:{0}{1}".format(len(p.segments), os.linesep))
                #for s in p.segments:
                #    txt.write("Vertices:{0}{1}".format(len(s.vertices), os.linesep))
                txt.write(p.toString(hekto,
                                     attribs,
                                     delimiter,
                                     decimalDelimiter))
        else:
            # BEGIN XLSX-Export
            exXls = ExportXls(self.iface, fileName, self.settings, self.profiles, hekto, attribs, decimalDelimiter)
            exXls.create()

    def exportTxt(self):
        delimiter = self.__getDelimiter()
        decimalDelimiter = self.__getDecimalDelimiter()
        if delimiter == decimalDelimiter:
            msg = QApplication.translate("code", "Gleiches Dezimal- und Spaltentrennzeichen gewählt!")
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", msg)
            return

        u = Util(self.iface)
        caption = QApplication.translate("code", "Textdatei exportieren")
        fileName, file_ext = u.getFileName(caption, [["txt", "txt"]], self.filePath)
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
        hekto = (self.ui.IDC_chkHekto.checkState() == Qt.Checked)
        attribs = (self.ui.IDC_chkLineAttributes.checkState() == Qt.Checked)
        txt = open(fileName, "w")

        txt.write(self.profiles[0].writeHeader(self.settings.mapData.rasters.selectedRasters(), hekto, attribs, delimiter))
        for p in self.profiles:
            #txt.write("=====Profil {0}======{1}".format(p.id, os.linesep))
            #txt.write("Segments:{0}{1}".format(len(p.segments), os.linesep))
            #for s in p.segments:
            #    txt.write("Vertices:{0}{1}".format(len(s.vertices), os.linesep))
            txt.write(p.toString(hekto,
                                 attribs,
                                 delimiter,
                                 decimalDelimiter
                                 ))
        txt.close()

    def exportAutoCadTxt(self):
        u = Util(self.iface)
        caption = QApplication.translate("code", "AutoCad Textdatei exportieren")
        fileName, file_ext = u.getFileName(caption, [["txt", "txt"]], self.filePath)
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
        txt = open(fileName, "w")
        for p in self.profiles:
            txt.write(p.toACadTxt(" ", "."))
        txt.close()

    def exportDxfPnt(self):
        self.__exportDxf(True)

    def exportDxfLine(self):
        self.__exportDxf(False)

    def __exportDxf(self, asPnt):
        u = Util(self.iface)
        caption = QApplication.translate("code", "DXF exportieren")
        fileName, file_ext = u.getFileName(caption, [["dxf", "dxf"]], self.filePath)
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
        exDxf = ExportDxf(self.iface, fileName, self.settings, self.profiles)
        if asPnt is True:
            exDxf.exportPoint()
        else:
            exDxf.exportLine()

    def __identify(self):
        #dirty hack: deselect all tools
        #selecting a tool twice deselects it
        self.plt_toolbar.pan()
        self.plt_toolbar.zoom()
        self.plt_toolbar.zoom()

    def __measure(self):
        self.measuring = True
        #dirty hack: deselect all tools
        #selecting a tool twice deselects it
        self.plt_toolbar.pan()
        self.plt_toolbar.zoom()
        self.plt_toolbar.zoom()

    def __figureDrawn(self, event):
        if self.debug:
            QgsMessageLog.logMessage("__figureDrawn, draw_event_fired:{0} exaggeration_edited: {1}".format(self.draw_event_fired, self.exaggeration_edited), "VoGis", Qgis.Info)
        #draw event seems to get fired twice?????
        if self.draw_event_fired == True:
            return
        self.draw_event_fired = True
        axes = self.plt_widget.figure.get_axes()[0]
        xlim = axes.get_xlim()
        ylim = axes.get_ylim()
        if self.debug:
            QgsMessageLog.logMessage("__figureDrawn: xlim:{0} ylim:{1}".format(xlim, ylim), "VoGis", Qgis.Info)
        dpi = self.plt_widget.figure.get_dpi()
        fig_width = self.plt_widget.figure.get_figwidth() * dpi
        fig_height = self.plt_widget.figure.get_figheight() * dpi
        #bbox = axes.get_window_extent().transformed(self.plt_widget.figure.dpi_scale_trans.inverted())
        #fig_width, fig_height = bbox.width * dpi, bbox.height * dpi
        fig_width *= (TOP_MARGIN - BOTTOM_MARGIN)
        fig_height *= (RIGHT_MARGIN - LEFT_MARGIN)
        delta_x = xlim[1] - xlim[0]
        delta_y = ylim[1] - ylim[0]
        ratio = (delta_x / fig_width) / (delta_y / fig_height)
        ratio = floor(ratio * 10) / 10
        if self.debug:
            QgsMessageLog.logMessage("__figureDrawn: fig_width:{0} fig_height:{1} dpi:{2} delta_x:{3} delta_y:{4}, ratio:{5}".format(fig_width, fig_height, dpi, delta_x, delta_y, ratio), "VoGis", Qgis.Info)
        if self.debug:
            QgsMessageLog.logMessage("__figureDrawn: axes.get_data_ratio:{0}".format(axes.get_data_ratio()), "VoGis", Qgis.Info)
        #self.editExaggeration.setText("{0:.1f}".format(ratio))
        self.editExaggeration.setText("{0:.1f}".format(axes.get_aspect()))
        self.draw_event_fired = False

    def __exaggeration_edited(self, *args):
        if self.debug:
            QgsMessageLog.logMessage("__exaggeration_edited, exaggeration_edited:{0} draw_event_fired: {1}".format(self.exaggeration_edited, self.draw_event_fired), "VoGis", Qgis.Info)
        #this event handler seems to get called twice????
        if self.draw_event_fired == True:
            return
        if self.exaggeration_edited == True:
            return
        self.exaggeration_edited = True
        #QgsMessageLog.logMessage("__exaggeration_edited: {0}".format(self.exaggeration_edited), "VoGis", Qgis.Info)
        ut = Util(self.iface)
        txtExa = QApplication.translate("code", "Überhöhung")
        if ut.isFloat(self.editExaggeration.text(), txtExa) is False:
            return False
        #clear focus of lineedit, otherwise it gets called even when the user wants to close the dialog
        self.editExaggeration.clearFocus()
        exa = float(self.editExaggeration.text().replace(",", "."))
        self.__adjustAxes(exa)

    def __one2oneClicked(self):
        if self.debug: QgsMessageLog.logMessage("1:1 clicked", "VoGis", Qgis.Info)
        #QgsMessageLog.logMessage("axes:{0}".format(self.plt_widget.figure.get_axes()), "VoGis", Qgis.Info)
        self.__adjustAxes(1.0)

    def __adjustAxes(self, exaggeration):
        # avoid rounding errors for exaggeration
        exaggerationOrig = exaggeration
        # one digit after the comma
        exaggeration = floor(exaggerationOrig * 10) / 10
        # two digits after the comma
        if exaggeration == 0.0:
            exaggeration = floor(exaggerationOrig * 100) / 100
        # three digits after the comma
        if exaggeration == 0.0:
            exaggeration == floor(exaggerationOrig * 1000) / 1000
        # if still 0 give up and reset to 1
        if exaggeration == 0.0:
            exaggeration = 1.0

        axes = self.plt_widget.figure.get_axes()[0]
        #axes.set_aspect(exaggeration)
        #axes.set_autoscalex_on(False)
        #axes.set_autoscaley_on(True)
        if self.debug:
            QgsMessageLog.logMessage("__adjustAxes, get_aspect:{0}".format(axes.get_aspect()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, get_position:{0}".format(axes.get_position()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, xBound:{0} xlim:{1}".format(axes.get_xbound(),axes.get_xlim()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, yBound:{0} ylim:{1}".format(axes.get_ybound(),axes.get_ylim()), "VoGis", Qgis.Info)
        oldexa = axes.get_aspect()
        ratioexa = oldexa / exaggeration
        ylim = axes.get_ylim()
        deltaYold = ylim[1] - ylim[0]
        deltaYnew = deltaYold * ratioexa
        centerY = ylim[0] + (deltaYold / 2)
        axes.set_ylim(centerY - deltaYnew/2,centerY + deltaYnew/2)
        axes.set_aspect(exaggeration, "datalim", "C")
        self.plt_widget.draw()
        if self.debug:
            QgsMessageLog.logMessage("__adjustAxes, get_aspect:{0}".format(axes.get_aspect()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, get_position:{0}".format(axes.get_position()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, xBound:{0} xlim:{1}".format(axes.get_xbound(),axes.get_xlim()), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("__adjustAxes, yBound:{0} ylim:{1}".format(axes.get_ybound(),axes.get_ylim()), "VoGis", Qgis.Info)

    def __plotPicked(self, event):
        self.plotpicked = True
        if self.debug: QgsMessageLog.logMessage("__plotPicked", "VoGis", Qgis.Info)
        #QgsMessageLog.logMessage("artist:{0}".format(type(event.artist)), "VoGis", Qgis.Info)
        self.dhmLbl.setText(" ? ")
        if isinstance(event.artist, Line2D):
            QgsMessageLog.logMessage("Line2D", "VoGis", Qgis.Info)
            line = event.artist
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            ind = event.ind
            QgsMessageLog.logMessage("{0}: {1} {2}".format(ind, xdata, ydata), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage(help(line), "VoGis", Qgis.Info)
        elif isinstance(event.artist, LineCollection):
            QgsMessageLog.logMessage("LineCollection", "VoGis", Qgis.Info)
            r = self.settings.mapData.rasters.selectedRasters()[event.ind[0]]
            QgsMessageLog.logMessage("Raster: {0}".format(r.name), "VoGis", Qgis.Info)
            self.dhmLbl.setText("  [" + r.name + "] ")
        else:
            QgsMessageLog.logMessage("no Line2D or LineCollection", "VoGis", Qgis.Info)

    def __mouse_move(self, event):
        if self.measuring is False:
            return
        if self.click1 is None:
            return
        if event.xdata is None or event.ydata is None:
            return

        dx = event.xdata - self.click1.xdata
        dy = event.ydata - self.click1.ydata

        if self.debug:
            #QgsMessageLog.logMessage("mouse move name {0}".format(event.name), "VoGis", Qgis.Info)
            #QgsMessageLog.logMessage("mouse move xdata {0}".format(event.xdata), "VoGis", Qgis.Info)
            #QgsMessageLog.logMessage("mouse move ydata {0}".format(event.ydata), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("dx/dy {0}/{1}".format(dx, dy), "VoGis", Qgis.Info)
        self.measure_lbl.setText(" x/y:{0:.1f}/{1:.1f} dx/dy:{2:.1f}/{3:.1f}".format(
            self.click1.xdata,
            self.click1.ydata,
            dx,
            dy
            ))
        self.plt_toolbar.draw_rubberband("xy", self.click1.xpixel, self.click1.ypixel, event.x, event.y)

    def __buttonPressed(self, event):
        if self.debug:
            QgsMessageLog.logMessage("__buttonPressed", "VoGis", Qgis.Info)

        if self.plotpicked is False:
            self.dhmLbl.setText(" ? ")

        #reset flag to show "?" next time a button gets pressed
        self.plotpicked = False

        if self.measuring is False:
            return

        if self.debug:
            QgsMessageLog.logMessage("{0}".format(dir(event)), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("{0}".format(dir(event.xdata)), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("{0}".format(dir(event.ydata)), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage(
                "x:{0} y:{1} xdata:{2} ydata:{3} click1:{4} click2:{5} click1pnt:{6} click2pnt:{7}".format(
                    event.x, event.y, event.xdata, event.ydata, self.click1, self.click2, self.click1pnt, self.click2pnt), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("click1pnt: {0}".format(dir(self.click1pnt)), "VoGis", Qgis.Info)

        if event.xdata is None or event.ydata is None:
            return
        if self.click1 is None:
            self.click1 = ChartPoint(event.x, event.y, event.xdata, event.ydata)
            self.click2 = None
            #self.measure_lbl.setText(u"")
            self.measure_lbl.setText(" x/y:{0:.1f}/{1:.1f} dx/dy:0/0".format(event.xdata, event.ydata))
            if not self.click1pnt is None:
                p = self.click1pnt.pop(0);
                p.remove()
                del p
                self.click1pnt = None
            if not self.click2pnt is None:
                p = self.click2pnt.pop(0);
                p.remove()
                del p
                self.click2pnt = None
            self.click1pnt = self.subplot.plot(event.xdata, event.ydata, "ro")
        elif self.click2 is None:
            self.click2 = ChartPoint(event.x, event.y, event.xdata, event.ydata)
            #delta_x = abs(self.click2[0] - self.click1[0])
            #delta_y = abs(self.click2[1] - self.click1[1])
            #dist = ((delta_x ** 2) + (delta_y ** 2)) ** 0.5
            #self.measure_lbl.setText(u" dist: {0:.1f} ".format(dist))
            delta_x = self.click2.xdata - self.click1.xdata
            delta_y = self.click2.ydata - self.click1.ydata
            dist = sqrt(pow(delta_x, 2) + pow(delta_y, 2))
            self.measure_lbl.setText(u" dx/dy:{0:.1f}/{1:.1f} d:{2:.1f}".format(delta_x, delta_y, dist))
            self.click1 = None
            self.measuring = False
            if not self.click2pnt is None:
                p = self.click2pnt.pop(0);
                p.remove()
                del p
                self.click2pnt = None
            self.click2pnt = self.subplot.plot(event.xdata, event.ydata, "go")
        #refresh plot to show points, when identify tool active
        #if self.debug: QgsMessageLog.logMessage("__buttonPressed: active: {0}".format(self.plt_toolbar._active), "VoGis", Qgis.Info)
        #if self.plotpicked is True:
        if self.plt_toolbar._active is None:
            self.plt_widget.draw()

    def __createMatplotlibCanvas(self, plt_extent):
            fig = Figure(#figsize=(1, 1),
                         #tight_layout=True,
                         linewidth=0.0,
                         subplotpars=matplotlib.figure.SubplotParams(left=0,
                                                                     bottom=0,
                                                                     right=1,
                                                                     top=1,
                                                                     wspace=0,
                                                                     hspace=0
                                                                     )
                         )
            #fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
            #fig = Figure((24, 24), tight_layout=True)
            # try:
            #     fig = Figure(tight_layout=True)
            # except:
            #     #tight layout not available
            #     fig = Figure()
            #fig = plt.figure()
            #fig.set_tight_layout(True)
            #font = {"family": "arial", "weight": "normal", "size": 12}
            #rc("font", **font)
            rect = fig.patch
            rect.set_facecolor((0.9, 0.9, 0.9))

            # self.subplot = fig.add_axes(
            #                             #(0.08, 0.15, 0.92, 0.82),
            #                             (0.0, 0.0, 1.0, 1.0),
            #                             anchor="SW",
            #                             adjustable="box-forced"
            #                             )
            #left bottom right top
            self.subplot = fig.add_axes(
                                        (LEFT_MARGIN, BOTTOM_MARGIN, RIGHT_MARGIN, TOP_MARGIN),
                                        adjustable="datalim",
                                        aspect=1
                                        )
            #self.subplot.plot.tight_layout(True)
            self.subplot.set_xbound(plt_extent.xmin, plt_extent.xmax)
            self.subplot.set_ybound(plt_extent.ymin, plt_extent.ymax)

            self.__setupAxes(self.subplot)
            #fig.tight_layout()
            canvas = FigureCanvasQTAgg(fig)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            canvas.setSizePolicy(sizePolicy)
            canvas.mpl_connect("pick_event", self.__plotPicked)
            canvas.mpl_connect("draw_event", self.__figureDrawn)
            canvas.mpl_connect("button_press_event", self.__buttonPressed)
            canvas.mpl_connect("motion_notify_event", self.__mouse_move)
            return canvas

    def __setupAxes(self, axe1):
        axe1.grid()
        axe1.ticklabel_format(style="plain", useOffset=False)
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
        #QgsMessageLog.logMessage("delim:" + str(delim), "VoGis", Qgis.Info)
        return delim

    def __getDelimiter(self):
        #delim = self.ui.IDC_cbDelimiter.itemData(self.ui.IDC_cbDelimiter.currentIndex())
        delim = self.ui.IDC_cbDelimiter.currentText()
        if delim == "tab":
            delim = "\t"
        return delim

    def addToLayout(self):
        mgr = QgsProject.instance().layoutManager()
        layout = None
        layouts = mgr.layouts()
        if len(layouts) == 0:
            QMessageBox.warning(self,
                                QApplication.translate("code", "Keine Layouts"),
                                QApplication.translate("code", "Zuerst ein Layout erstellen"))
            return
        elif len(layouts) == 1:
            layout = layouts[0]
        else:
            d = VoGISProfilToolLayoutsDialog(self, layouts)
            result = d.exec_()
            if result == QDialog.Accepted:
                layout = mgr.layoutByName(d.ui.cmbLayouts.currentText())
            else:
                return

        u = Util(self.iface)
        caption = QApplication.translate("code", "PNG Datei")
        file_format = []
        file_format.append(["PNG files", "png"])
        fileName, fileExt = u.getFileName(caption, file_format, QgsProject.instance().homePath())
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        figure = self.subplot.figure
        figure.savefig(fileName, format="png")

        image = QgsLayoutItemPicture(layout)
        image.setPicturePath(fileName)
        image.attemptResize(QgsLayoutSize(200, 200))
        layout.addLayoutItem(image)

    def __drawProfiles(self, axes):
        #for less thatn 10 colors:
        #alternative method: http://stackoverflow.com/a/14720445
        colors = [(1.0, 0.0, 0.0, 1.0),
                  (0.0, 1.0, 0.0, 1.0),
                  (0.0, 0.0, 1.0, 1.0),
                  (1.0, 1.0, 0.5, 1.0),
                  (1.0, 0.0, 1.0, 1.0),
                  (0.0, 1.0, 1.0, 1.0),
                  (0.415686275, 0.807843137, 0.890196078, 1.0),
                  (0.121568627, 0.470588235, 0.705882353, 1.0),
                  (0.698039216, 0.874509804, 0.541176471, 1.0),
                  (0.2, 0.62745098, 0.17254902, 1.0),
                  (0.984313725, 0.603921569, 0.6, 1.0),
                  (0.890196078, 0.101960784, 0.109803922, 1.0),
                  (0.992156863, 0.749019608, 0.435294118, 1.0),
                  (1, 0.498039216, 0, 1.0),
                  (0.792156863, 0.698039216, 0.839215686, 1.0),
                  (0.415686275, 0.239215686, 0.603921569, 1.0),
                  (1, 1, 0.521568627, 1.0),
                  ]

        max_profile_length = 0
        #idxCol = 0
        for idx, p in enumerate(self.profiles):
            max_profile_length = max(p.getExtent().xmax, max_profile_length)
            #if idxCol > len(colors) - 1:
            #    idxCol = 0
            #x, plt_segments = p.getPlotSegments()
            #QgsMessageLog.logMessage("x: {0}".format(x), "VoGis", Qgis.Info)
            plt_segments = p.getPlotSegments()
            #QgsMessageLog.logMessage("plt_segments: {0}".format(plt_segments), "VoGis", Qgis.Info)
            lineColl = LineCollection(plt_segments,
                                      linewidths=2,
                                      linestyles="solid",
                                      #colors=colors[randrange(len(colors))],
                                      #colors=colors[idxCol],
                                      colors=colors[:len(self.settings.mapData.rasters.selectedRasters())],
                                      picker=True,
                                      label="LBL"
                                      )
            #lineColl.set_array(x)
            #lineColl.text.set_text("line label")
            axes.add_collection(lineColl)
            #idxCol += 1

        #LINE STYLES: http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
        cmap = cm.get_cmap(cm.gist_rainbow)
        color_intersection = [cmap(i) for i in numpy.linspace(0, 0.9, len(self.intersections))]
        for idx, intersection in enumerate(self.intersections):
            x_1 = intersection.from_dist
            x_2 = intersection.to_dist
            z_1 = intersection.from_z[self.settings.intersection_dhm_idx]
            z_2 = intersection.to_z[self.settings.intersection_dhm_idx]
            axes.plot(
                      (x_1, x_2),
                      (z_1, z_2),
                      linestyle="--",
                      color=color_intersection[idx],
                      linewidth=4,
                      zorder=1
                      )
            #http://matplotlib.org/users/annotations_guide.html#using-complex-coordinate-with-annotation
            axes.annotate(u"{0:.2f}".format(z_1), (x_1, z_1), xytext=(0, 30), textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"), ha="center", va="bottom", rotation=90)
            axes.annotate(u"{0:.2f}".format(z_2), (x_2, z_2), xytext=(0, 30), textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"), ha="center", va="bottom", rotation=90)

        if self.cadastre is not None:
            fm = font_manager.FontProperties()
            s = fm.get_size_in_points()
            for intersection in self.cadastre:
                x_1 = intersection.from_dist
                x_2 = intersection.to_dist
                axes.plot((x_1, x_1), (0, s), color="black", linewidth=1)
                axes.plot((x_2, x_2), (0, s), color="black", linewidth=1)

    def saveScale(self):
        d = VoGISProfilToolScaleDialog(self)
        result = d.exec_()
        if result == QDialog.Rejected:
            return

        scale = d.ui.cmbScale.currentText()
        dpi = d.ui.cmbDpi.currentText()
        scaleFactor = float(scale.split(":")[1])

        crsUnit = self.iface.mapCanvas().mapSettings().destinationCrs().mapUnits()
        toCm = QgsUnitTypes.fromUnitToUnitFactor(crsUnit, QgsUnitTypes.DistanceCentimeters)
        m2Cm = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceMeters, QgsUnitTypes.DistanceCentimeters)

        profile_length = 0
        profile_height = 0
        plt_extent = PlotExtent()
        for p in self.profiles:
            profile_length = max(p.getExtent().xmax, profile_length)
            profile_height = max(p.getExtent().ymax, profile_height)
            plt_extent.union(p.getExtent())
        plt_extent.expand()

        s = self.subplot.figure.get_size_inches()
        maxLength = toCm * profile_length
        maxHeight = m2Cm * profile_height
        imgWidth = (maxLength / scaleFactor) * TO_INCH
        imgHeight = s[1] * imgWidth / s[0]
        fig = plt.figure(figsize=(imgWidth, imgHeight),
                         dpi=10,
                         linewidth=0.0,
                         subplotpars=matplotlib.figure.SubplotParams(left=0,
                                                                     bottom=0,
                                                                     right=1,
                                                                     top=1,
                                                                     wspace=0,
                                                                     hspace=0
                                                                    )
                        )

        axes = fig.add_axes((LEFT_MARGIN, BOTTOM_MARGIN, RIGHT_MARGIN, TOP_MARGIN),
                            adjustable="datalim",
                            aspect=1
                           )
        axes.set_xbound(plt_extent.xmin, plt_extent.xmax)
        axes.set_ybound(plt_extent.ymin, plt_extent.ymax)
        self.__setupAxes(axes)
        self.__drawProfiles(axes)

        exaggeration = floor(float(self.editExaggeration.text().replace(",", ".")) * 10) / 10
        oldexa = axes.get_aspect()
        ratioexa = oldexa / exaggeration
        ylim = axes.get_ylim()
        deltaYold = ylim[1] - ylim[0]
        deltaYnew = deltaYold * ratioexa
        centerY = ylim[0] + (deltaYold / 2)
        axes.set_ylim(centerY - deltaYnew/2,centerY + deltaYnew/2)
        axes.set_aspect(exaggeration, "datalim", "C")

        axes.set_xlim(self.subplot.get_xlim())
        axes.set_ylim(self.subplot.get_ylim())
        axes.set_xbound(self.subplot.get_xbound())
        axes.set_ybound(self.subplot.get_ybound())

        u = Util(self.iface)
        caption = QApplication.translate("code", "PNG export")
        file_format = [["PNG files", "png"]]
        fileName, fileExt = u.getFileName(caption, file_format, self.filePath)
        if fileName == "":
            return
        fInfo = QFileInfo(fileName)
        self.filePath = fInfo.path()
        QgsSettings().setValue("vogisprofiltoolmain/savepath", self.filePath)
        fig.show()
        fig.savefig(fileName, dpi=int(dpi), format="png", bbox_inches='tight')
        plt.close(fig)
