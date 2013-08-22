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
from qgis.core import QgsPoint
from qgis.gui import QgsRubberBand
from ui.ui_vogisprofiltoolmain import Ui_VoGISProfilToolMain
#from bo.raster import Raster
from util.u import Util
from bo.settings import enumModeLine, enumModeVertices
from util.ptmaptool import ProfiletoolMapTool


class VoGISProfilToolMainDialog(QDialog):
    def __init__(self, interface, settings):

        QDialog.__init__(self)
        self.selectingVisibleRasters = False
        self.settings = settings
        self.iface = interface
        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolMain()
        self.ui.setupUi(self)

        self.ui.IDC_tbFromX.setText('-30000')
        self.ui.IDC_tbFromY.setText('240000')
        self.ui.IDC_tbToX.setText('-20000')
        self.ui.IDC_tbToY.setText('230000')

        if self.settings.onlyHektoMode is True:
            self.ui.IDC_chkCreateHekto.setCheckState(Qt.Checked)
            self.ui.IDC_chkCreateHekto.setEnabled(False)

        check = Qt.Unchecked

        if self.settings.mapData.rasters.count() == 1:
            check = Qt.Checked
            self.settings.mapData.rasters.rasters()[0].selected = True

        for rLyr in self.settings.mapData.rasters.rasters():
            item = QListWidgetItem(rLyr.name)
            item.setData(Qt.UserRole, rLyr)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(check)
            self.ui.IDC_listRasters.addItem(item)

        for lLyr in self.settings.mapData.lines.lines():
            self.ui.IDC_cbLineLayers.addItem(lLyr.name, lLyr)

        #Einstellungen fuer Linie zeichen
        self.action = QAction(QIcon(":/plugins/vogisprofiltoolmain/icons/icon.png"), "VoGIS-Profiltool", self.iface.mainWindow())
        self.action.setWhatsThis("VoGIS-Profiltool")
        self.canvas = self.iface.mapCanvas()
        self.tool = ProfiletoolMapTool(self.canvas, self.action)
        self.savedTool = self.canvas.mapTool()
        self.polygon = False
        self.rubberband = QgsRubberBand(self.canvas, self.polygon)
        self.pointsToDraw = []
        self.dblclktemp = None
        self.drawnLine = None

    def accept(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "ACCEPTED")
        if self.__getSettingsFromGui() is False:
            return

        if len(self.settings.mapData.rasters.selectedRasters()) < 1:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Kein Raster selektiert!")
            return

        if self.settings.modeLine is not enumModeLine.line and self.settings.mapData.customLine is None:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Keine Profillinie vorhanden!")
            return

        self.rubberband.reset(self.polygon)
        QDialog.accept(self)

    def reject(self):
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "REJECTED")
        self.rubberband.reset(self.polygon)
        QDialog.reject(self)

    def selectVisibleRasters(self):
        self.selectingVisibleRasters = True
        extCanvas = self.iface.mapCanvas().extent()
        #alle raster in den einstellunge deselektieren
        for r in self.settings.mapData.rasters.rasters():
            r.selected = False
        #alle raster in der ListView deselektieren
        for idx in xrange(self.ui.IDC_listRasters.count()):
            item = self.ui.IDC_listRasters.item(idx)
            item.setCheckState(Qt.Unchecked)
        #Raster im Extent selektieren
        for idx in xrange(self.ui.IDC_listRasters.count()):
            item = self.ui.IDC_listRasters.item(idx)
            raster = item.data(Qt.UserRole).toPyObject()
            for r in self.settings.mapData.rasters.rasters():
                if extCanvas.intersects(r.grid.extent()):
                    if r.id == raster.id:
                        r.selected = True
                        item.setCheckState(Qt.Checked)
        self.selectingVisibleRasters = False

    def lvRasterItemChanged(self, item):
        if self.selectingVisibleRasters is True: return
        if item.checkState() == Qt.Checked:
            selected = True
        if item.checkState() == Qt.Unchecked:
            selected = False

        iData = item.data(Qt.UserRole)
        rl = iData.toPyObject()
        self.settings.mapData.rasters.getById(rl.id).selected = selected

    def drawLine(self):
        if self.ui.IDC_rbDigi.isChecked() is False:
            self.ui.IDC_rbDigi.setChecked(True)
        self.dblckltemp = None
        self.rubberband.reset(self.polygon)
        self.__cleanDigi()
        self.__activateDigiTool()
        self.canvas.setMapTool(self.tool)

    def __createDigiFeature(self, pnts):
        u = Util(self.iface)
        f = u.createQgLineFeature(pnts)
        self.settings.mapData.customLine = f

    def __lineFinished(self, position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        newPoint = QgsPoint(mapPos.x(), mapPos.y())
        self.pointsToDraw.append(newPoint)
        #launch analyses
        self.iface.mainWindow().statusBar().showMessage(str(self.pointsToDraw))
        if len(self.pointsToDraw) < 2:
            self.__cleanDigi()
            self.pointsToDraw = []
            self.dblclktemp = newPoint
            self.drawnLine = None
            QMessageBox.warning(self, "VoGIS-Profiltool", "Profillinie digitalisieren abgebrochen!")
        self.drawnLine = self.__createDigiFeature(self.pointsToDraw)
        self.__cleanDigi()

        self.pointsToDraw = []
        self.dblclktemp = newPoint

    def __cleanDigi(self):
        self.pointsToDraw = []
        self.canvas.unsetMapTool(self.tool)
        self.canvas.setMapTool(self.savedTool)

    def __activateDigiTool(self):
        QObject.connect(self.tool, SIGNAL("moved"), self.__moved)
        QObject.connect(self.tool, SIGNAL("rightClicked"), self.__rightClicked)
        QObject.connect(self.tool, SIGNAL("leftClicked"), self.__leftClicked)
        QObject.connect(self.tool, SIGNAL("doubleClicked"), self.__doubleClicked)
        QObject.connect(self.tool, SIGNAL("deactivate"), self.__deactivateDigiTool)

    def __deactivateDigiTool(self):
        QObject.disconnect(self.tool, SIGNAL("moved"), self.__moved)
        QObject.disconnect(self.tool, SIGNAL("leftClicked"), self.__leftClicked)
        QObject.disconnect(self.tool, SIGNAL("rightClicked"), self.__rightClicked)
        QObject.disconnect(self.tool, SIGNAL("doubleClicked"), self.__doubleClicked)
        self.iface.mainWindow().statusBar().showMessage(QString(""))

    def __moved(self, position):
        if len(self.pointsToDraw) > 0:
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
            self.rubberband.reset(self.polygon)
            for i in range(0, len(self.pointsToDraw)):
                self.rubberband.addPoint(self.pointsToDraw[i])
            self.rubberband.addPoint(QgsPoint(mapPos.x(), mapPos.y()))

    def __rightClicked(self, position):
        self.__lineFinished(position)

    def __leftClicked(self, position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        newPoint = QgsPoint(mapPos.x(), mapPos.y())
        #if self.selectionmethod == 0:
        if newPoint == self.dblclktemp:
            self.dblclktemp = None
            return
        else:
            if len(self.pointsToDraw) == 0:
                self.rubberband.reset(self.polygon)
            self.pointsToDraw.append(newPoint)

    def __doubleClicked(self, position):
        pass

    #not in use right now
    def __lineCancel(self):
        pass

    def __getSettingsFromGui(self):
        self.settings.linesExplode = (self.ui.IDC_chkLinesExplode.checkState() == Qt.Checked)
        self.settings.linesMerge = (self.ui.IDC_chkLinesMerge.checkState() == Qt.Checked)
        self.settings.onlySelectedFeatures = (self.ui.IDC_chkOnlySelectedFeatures.checkState() == Qt.Checked)
        self.settings.equiDistance = self.ui.IDC_dblspinDistance.value()
        self.settings.vertexCnt = self.ui.IDC_dblspinVertexCnt.value()
        #self.settings.createHekto = (self.ui.IDC_chkCreateHekto.checkState() == Qt.Checked)
        self.settings.nodesAndVertices = (self.ui.IDC_chkNodesAndVertices.checkState() == Qt.Checked)

        self.settings.mapData.selectedLineLyr = (self.ui.IDC_cbLineLayers.itemData(
                                                 self.ui.IDC_cbLineLayers.currentIndex()
                                                 ).toPyObject()
                                                 )

        if self.settings.onlySelectedFeatures is True and self.settings.mapData.selectedLineLyr.line.selectedFeatureCount() < 1:
            QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", u"Der gewählte Layer hat keine selektierten Elemente.")
            return False

        if self.ui.IDC_rbDigi.isChecked():
            self.settings.modeLine = enumModeLine.customLine
        elif self.ui.IDC_rbShapeLine.isChecked():
            self.settings.modeLine = enumModeLine.line
        else:
            #self.ui.IDC_rbStraigthLine
            self.settings.modeLine = enumModeLine.straightLine

        if self.ui.IDC_rbEquiDistance.isChecked():
            self.settings.modeVertices = enumModeVertices.equiDistant
        else:
            self.settings.modeVertices = enumModeVertices.vertexCnt

        if self.ui.IDC_rbStraigthLine.isChecked():
            ut = Util(self.iface)
            if ut.isFloat(self.ui.IDC_tbFromX.text(), "Rechtswert von") is False:
                return False
            else:
                fromX = float(self.ui.IDC_tbFromX.text())
            if ut.isFloat(self.ui.IDC_tbFromY.text(), "Hochwert von") is False:
                return False
            else:
                fromY = float(self.ui.IDC_tbFromY.text())
            if ut.isFloat(self.ui.IDC_tbToX.text(), "Rechtswert nach") is False:
                return False
            else:
                toX = float(self.ui.IDC_tbToX.text())
            if ut.isFloat(self.ui.IDC_tbToY.text(), "Hochwert nach") is False:
                return False
            else:
                toY = float(self.ui.IDC_tbToY.text())

            fromPnt = QgsPoint(fromX, fromY)
            toPnt = QgsPoint(toX, toY)

            self.settings.mapData.customLine = ut.createQgLineFeature([fromPnt, toPnt])

        return True
