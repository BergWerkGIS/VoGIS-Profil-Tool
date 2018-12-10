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
import traceback

from qgis.PyQt.QtCore import Qt, QThread
from qgis.PyQt.QtGui import QIntValidator, QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QApplication, QDialogButtonBox, QListWidgetItem, QInputDialog, QDialog

from qgis.core import Qgis, QgsMessageLog, QgsGeometry, QgsPointXY, QgsProject, QgsMapLayer, QgsCoordinateTransform, QgsProject
from qgis.gui import QgsRubberBand

from VoGisProfilTool.ui.ui_vogisprofiltoolmain import Ui_VoGISProfilToolMain

from VoGisProfilTool.vogisprofiltoolplot import VoGISProfilToolPlotDialog

from VoGisProfilTool.bo.settings import enumModeLine, enumModeVertices
from VoGisProfilTool.bo.rasterCollection import RasterCollection
from VoGisProfilTool.bo.raster import Raster

from VoGisProfilTool.util.u import Util
from VoGisProfilTool.util.ptmaptool import ProfiletoolMapTool
from VoGisProfilTool.util.createProfile import CreateProfile

import VoGisProfilTool.resources_rc


class VoGISProfilToolMainDialog(QDialog):
    def __init__(self, interface, settings):
        QDialog.__init__(self, interface.mainWindow())

        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolMain()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setText(QApplication.translate("code", "Profil erstellen"))
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).setText(QApplication.translate("code", "Schließen"))

        self.ui.grpCadastre.toggled.connect(self._toggleCadastreLayer)
        self.ui.cmbCadastreLayer.currentIndexChanged.connect(self._updateCadastreLayer)

        self.settings = settings
        self.iface = interface
        self.selectingVisibleRasters = False
        self.thread = None

        if self.settings.onlyHektoMode is True:
            self.ui.IDC_widRaster.hide()
            self.adjustSize()

        self.ui.IDC_dblspinDistance.setValue(self.settings.equiDistance)
        self.ui.IDC_dblspinVertexCnt.setValue(self.settings.vertexCnt)

        validator = QIntValidator(-32768, 32768, self)
        self.ui.IDC_tbNoDataExport.setValidator(validator)

        self.ui.IDC_tbFromX.setText("-30000")
        self.ui.IDC_tbFromY.setText("240000")
        self.ui.IDC_tbToX.setText("-20000")
        self.ui.IDC_tbToY.setText("230000")

        self.__addRastersToGui()
        self.__addPolygonsToGui()

        for line_lyr in self.settings.mapData.lines.lines():
            self.ui.IDC_cbLineLayers.addItem(line_lyr.name, line_lyr)

        if self.settings.mapData.lines.count() < 1:
            self.ui.IDC_rbDigi.setChecked(True)
            self.ui.IDC_rbShapeLine.setEnabled(False)

        #Einstellungen fuer Linie zeichen
        self.action = QAction(
            QIcon(":/plugins/vogisprofiltoolmain/icons/icon.png"),
            "VoGIS-Profiltool",
            self.iface.mainWindow())
        self.action.setWhatsThis("VoGIS-Profiltool")

        self.canvas = self.iface.mapCanvas()
        self.tool = ProfiletoolMapTool(self.canvas, self.action)
        self.savedTool = self.canvas.mapTool()
        self.polygon = False

        self.rubberband = QgsRubberBand(self.canvas, self.polygon)
        self.rubberband.setLineStyle(Qt.SolidLine)
        self.rubberband.setWidth(4.0)
        self.rubberband.setColor(QColor(0, 255, 0))
        #http://www.qgis.org/api/classQgsRubberBand.html#a6f7cdabfcf69b65dfc6c164ce2d01fab

        self.pointsToDraw = []
        self.dblclktemp = None
        self.drawnLine = None

    def accept(self):
        try:
            nodata = self.ui.IDC_tbNoDataExport.text()
            self.settings.nodata_value = int(nodata) if nodata != "" else None
            QgsMessageLog.logMessage("Maindlg: nodata: {0}".format(self.settings.nodata_value), "VoGis", Qgis.Info)

            if self.settings.onlyHektoMode is True and self.settings.mapData.rasters.count() > 0:
                self.settings.onlyHektoMode = False

            if self.settings.onlyHektoMode is False:
                if self.settings.mapData.rasters.count() < 1:
                   retVal = QMessageBox.warning(self.iface.mainWindow(),
                                                "VoGIS-Profiltool",
                                                QApplication.translate("code", "Keine Rasterebene vorhanden oder sichtbar! Nur hektometrieren?"),
                                                QMessageBox.Yes | QMessageBox.No,
                                                QMessageBox.Yes)
                   if retVal == QMessageBox.No:
                       return
                   else:
                       self.settings.onlyHektoMode = True
                       self.settings.createHekto = True

            if self.__getSettingsFromGui() is False:
                return

            if self.settings.onlyHektoMode is False:
                if len(self.settings.mapData.rasters.selectedRasters()) < 1:
                    QMessageBox.warning(self.iface.mainWindow(),
                                        "VoGIS-Profiltool",
                                        QApplication.translate("code", "Kein Raster selektiert!"))
                    return

            QgsMessageLog.logMessage("modeLine!=line: {0}".format(self.settings.modeLine != enumModeLine.line), "VoGis", Qgis.Info)
            QgsMessageLog.logMessage("customLine is None: {0}".format(self.settings.mapData.customLine is None), "VoGis", Qgis.Info)

            if self.settings.modeLine != enumModeLine.line and self.settings.mapData.customLine is None:
                QMessageBox.warning(self.iface.mainWindow(),
                                    "VoGIS-Profiltool",
                                    QApplication.translate("code", "Keine Profillinie vorhanden!"))
                return

            if len(self.settings.mapData.polygons.selected_polygons()) > 0 and len(self.settings.mapData.rasters.selectedRasters()) > 1:
                raster_names = list(raster.name for raster in self.settings.mapData.rasters.selectedRasters())
                sel_raster, ok_clicked = QInputDialog.getItem(
                                                self.iface.mainWindow(),
                                                "DHM?",
                                                "Welches DHM soll zur Flächenverschneidung verwendet werden?",
                                                raster_names,
                                                0,
                                                False
                                                )
                if ok_clicked is False:
                    return

                self.settings.intersection_dhm_idx = raster_names.index(sel_raster)

            QApplication.setOverrideCursor(Qt.WaitCursor)

            create_profile = CreateProfile(self.iface, self.settings)
            thread = QThread(self)
            create_profile.moveToThread(thread)
            create_profile.finished.connect(self.profiles_finished)
            create_profile.error.connect(self.profiles_error)
            create_profile.progress.connect(self.profiles_progress)
            thread.started.connect(create_profile.create)
            thread.start(QThread.LowestPriority)
            self.thread = thread
            self.create_profile = create_profile
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        except:
            QApplication.restoreOverrideCursor()
            ex = "{0}".format(traceback.format_exc())
            msg = "Unexpected ERROR:\n\n{0}".format(ex[:2000])
            QMessageBox.critical(self.iface.mainWindow(), "VoGIS-Profiltool", msg)

    def profiles_finished(self, profiles, intersections, cadastre):
        QApplication.restoreOverrideCursor()
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.thread.quit()
        self.thread.wait()

        #QGIS 2.0 http://gis.stackexchange.com/a/58754 http://gis.stackexchange.com/a/57090
        self.iface.mainWindow().statusBar().showMessage("VoGIS-Profiltool, {0} Profile".format(len(profiles)))
        QgsMessageLog.logMessage("Profile Count: {0}".format(len(profiles)), "VoGis", Qgis.Info)

        if len(profiles) < 1:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                QApplication.translate("code", "Es konnten keine Profile erstellt werden."))
            return

        dlg = VoGISProfilToolPlotDialog(self.iface, self.settings, profiles, intersections, cadastre)
        dlg.show()
        dlg.exec_()

    def profiles_error(self, exception_string):
        QApplication.restoreOverrideCursor()
        QgsMessageLog.logMessage("Error during profile creation: {0}".format(exception_string), "VoGis", Qgis.Critical)
        QMessageBox.critical(self.iface.mainWindow(), "VoGIS-Profiltool", exception_string)

    def profiles_progress(self, msg):
        self.iface.mainWindow().statusBar().showMessage(msg)
        self.ui.IDC_lblCreateStatus.setText(msg)
        QApplication.processEvents()

    def reject(self):
        if not self.thread is None:
            if self.thread.isRunning():
                self.create_profile.abort()
                return

        self.rubberband.reset(self.polygon)
        QDialog.reject(self)

    def selectVisibleRasters(self):
        self.refreshRasterList()
        self.selectingVisibleRasters = True
        extCanvas = self.iface.mapCanvas().extent()
        #alle raster in den einstellunge deselektieren
        for r in self.settings.mapData.rasters.rasters():
            r.selected = False
        #alle raster in der ListView deselektieren
        for idx in range(self.ui.IDC_listRasters.count()):
            item = self.ui.IDC_listRasters.item(idx)
            item.setCheckState(Qt.Unchecked)
        #Raster im Extent selektieren
        canvasCrs = self.iface.mapCanvas().mapSettings().destinationCrs()
        for idx in range(self.ui.IDC_listRasters.count()):
            item = self.ui.IDC_listRasters.item(idx)
            raster = item.data(Qt.UserRole)
            for r in self.settings.mapData.rasters.rasters():
                layerCrs = r.grid.crs()
                ct = QgsCoordinateTransform(layerCrs, canvasCrs, QgsProject.instance())
                extent = ct.transform(r.grid.extent())
                if extCanvas.intersects(extent):
                    if r.id == raster.id:
                        r.selected = True
                        item.setCheckState(Qt.Checked)
        self.selectingVisibleRasters = False

    def lineLayerChanged(self, idx):
        if self.ui.IDC_rbShapeLine.isChecked() is False:
            self.ui.IDC_rbShapeLine.setChecked(True)
        lineLyr = (self.ui.IDC_cbLineLayers.itemData(self.ui.IDC_cbLineLayers.currentIndex()))

        lyr = lineLyr.line
        if hasattr(lyr, "selectedFeatureCount"):
            if(lyr.selectedFeatureCount() < 1):
                self.ui.IDC_chkOnlySelectedFeatures.setChecked(False)
            else:
                self.ui.IDC_chkOnlySelectedFeatures.setChecked(True)

    def valueChangedEquiDistance(self, val):
        if self.ui.IDC_rbEquiDistance.isChecked() is False:
            self.ui.IDC_rbEquiDistance.setChecked(True)

    def valueChangedVertexCount(self, val):
        if self.ui.IDC_rbVertexCount.isChecked() is False:
            self.ui.IDC_rbVertexCount.setChecked(True)

    def lvRasterItemChanged(self, item):
        if self.selectingVisibleRasters is True:
            return
        if item.checkState() == Qt.Checked:
            selected = True
        if item.checkState() == Qt.Unchecked:
            selected = False

        item_data = item.data(Qt.UserRole)
        raster_lyr = item_data
        self.settings.mapData.rasters.getById(raster_lyr.id).selected = selected

    def lvPolygonItemChanged(self, item):
        if item.checkState() == Qt.Checked:
            selected = True
        if item.checkState() == Qt.Unchecked:
            selected = False

        item_data = item.data(Qt.UserRole)
        poly_lyr = item_data
        self.settings.mapData.polygons.getById(poly_lyr.id).selected = selected

    def refreshRasterList(self):
        root = QgsProject.instance().layerTreeRoot()
        avail_lyrs = root.findLayers()

        raster_coll = RasterCollection()

        for lyr in avail_lyrs:
            if lyr.isVisible():
                mapLayer = lyr.layer()
                lyr_type = mapLayer.type()
                lyr_name = mapLayer.name()
                if lyr_type == QgsMapLayer.RasterLayer:
                    if mapLayer.bandCount() < 2:
                        new_raster = Raster(mapLayer.id(), lyr_name, mapLayer)
                        raster_coll.addRaster(new_raster)

        self.settings.mapData.rasters = raster_coll
        self.__addRastersToGui()

    def __addRastersToGui(self):
        self.ui.IDC_listRasters.clear()
        check = Qt.Unchecked
        if self.settings.mapData.rasters.count() == 1:
            check = Qt.Checked
            self.settings.mapData.rasters.rasters()[0].selected = True

        for raster_lyr in self.settings.mapData.rasters.rasters():
            item = QListWidgetItem(raster_lyr.name)
            item.setData(Qt.UserRole, raster_lyr)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(check)
            self.ui.IDC_listRasters.addItem(item)

    def __addPolygonsToGui(self):
        self.ui.IDC_listPolygons.clear()
        self.ui.cmbCadastreLayer.clear()
        check = Qt.Unchecked
        for poly_lyr in self.settings.mapData.polygons.polygons():
            item = QListWidgetItem(poly_lyr.name)
            item.setData(Qt.UserRole, poly_lyr)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(check)
            self.ui.IDC_listPolygons.addItem(item)
            self.ui.cmbCadastreLayer.addItem(poly_lyr.name, poly_lyr.id)

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
        self.showNormal()
        self.raise_()
        self.activateWindow()

        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        newPoint = QgsPointXY(mapPos.x(), mapPos.y())
        self.pointsToDraw.append(newPoint)
        #launch analyses
        self.iface.mainWindow().statusBar().showMessage(str(self.pointsToDraw))
        if len(self.pointsToDraw) < 2:
            self.__cleanDigi()
            self.pointsToDraw = []
            self.dblclktemp = newPoint
            self.drawnLine = None
            QMessageBox.warning(self,
                                "VoGIS-Profiltool",
                                QApplication.translate("code", "Profillinie digitalisieren abgebrochen!"))
        self.drawnLine = self.__createDigiFeature(self.pointsToDraw)
        self.__cleanDigi()

        self.pointsToDraw = []
        self.dblclktemp = newPoint

    def __cleanDigi(self):
        self.pointsToDraw = []
        self.canvas.unsetMapTool(self.tool)
        self.canvas.setMapTool(self.savedTool)

    def __activateDigiTool(self):
        self.tool.moved.connect(self.__moved)
        self.tool.rightClicked.connect(self.__rightClicked)
        self.tool.leftClicked.connect(self.__leftClicked)
        self.tool.doubleClicked.connect(self.__doubleClicked)
        self.tool.deactivated.connect(self.__deactivateDigiTool)

    def __deactivateDigiTool(self):
        # TODO: how to check if not connected???
        try:
            self.tool.moved.disconnect(self.__moved)
        except:
            pass
        try:
            self.tool.leftClicked.disconnect(self.__leftClicked)
        except:
            pass
        try:
            self.tool.rightClicked.disconnect(self.__rightClicked)
        except:
            pass
        try:
            self.tool.doubleClicked.disconnect(self.__doubleClicked)
        except:
            pass
        try:
            self.iface.mainWindow().statusBar().showMessage("")
        except:
            pass

    def __moved(self, position):
        if len(self.pointsToDraw) > 0:
            mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
            self.rubberband.reset(self.polygon)
            newPnt = QgsPointXY(mapPos.x(), mapPos.y())
            pnts = self.pointsToDraw + [newPnt]
            self.rubberband.setToGeometry(QgsGeometry.fromPolylineXY(pnts), None)

    def __rightClicked(self, position):
        self.__lineFinished(position)

    def __leftClicked(self, position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        newPoint = QgsPointXY(mapPos.x(), mapPos.y())
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

        self.settings.mapData.selectedLineLyr = (self.ui.IDC_cbLineLayers.itemData(self.ui.IDC_cbLineLayers.currentIndex()))

        if self.settings.onlySelectedFeatures is True and self.settings.mapData.selectedLineLyr.line.selectedFeatureCount() < 1:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                QApplication.translate("code", u"Der gewählte Layer hat keine selektierten Elemente."))
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
            if ut.isFloat(self.ui.IDC_tbFromX.text(), QApplication.translate("code", "Rechtswert von")) is False:
                return False
            else:
                fromX = float(self.ui.IDC_tbFromX.text())
            if ut.isFloat(self.ui.IDC_tbFromY.text(), QApplication.translate("code", "Hochwert von")) is False:
                return False
            else:
                fromY = float(self.ui.IDC_tbFromY.text())
            if ut.isFloat(self.ui.IDC_tbToX.text(), QApplication.translate("code", "Rechtswert nach")) is False:
                return False
            else:
                toX = float(self.ui.IDC_tbToX.text())
            if ut.isFloat(self.ui.IDC_tbToY.text(), QApplication.translate("code", "Hochwert nach")) is False:
                return False
            else:
                toY = float(self.ui.IDC_tbToY.text())

            fromPnt = QgsPointXY(fromX, fromY)
            toPnt = QgsPointXY(toX, toY)

            self.settings.mapData.customLine = ut.createQgLineFeature([fromPnt, toPnt])

        return True

    def _toggleCadastreLayer(self, toggled):
        if toggled:
            layerId = self.ui.cmbCadastreLayer.itemData(self.ui.cmbCadastreLayer.currentIndex())
            self.settings.mapData.cadastre = layerId
        else:
            self.settings.mapData.cadastre = None

    def _updateCadastreLayer(self, index):
        if self.ui.grpCadastre.isChecked():
            layerId = self.ui.cmbCadastreLayer.itemData(index)
            self.settings.mapData.cadastre = layerId
