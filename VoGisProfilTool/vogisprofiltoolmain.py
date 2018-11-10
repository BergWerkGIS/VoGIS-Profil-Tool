# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VoGISProfilToolMain
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

from qgis.PyQt.QtCore import QLocale, QTranslator
from qgis.PyQt.QtWidgets import QApplication, QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from qgis.core import Qgis, QgsSettings, QgsMessageLog, QgsMapLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgsMessageBar

from VoGisProfilTool.vogisprofiltoolmaindialog import VoGISProfilToolMainDialog
from VoGisProfilTool.bo.raster import Raster
from VoGisProfilTool.bo.line import Line
from VoGisProfilTool.bo.polygon import Polygon
from VoGisProfilTool.bo.rasterCollection import RasterCollection
from VoGisProfilTool.bo.lineCollection import LineCollection
from VoGisProfilTool.bo.polygonCollection import PolygonCollection
from VoGisProfilTool.bo.mapdata import MapData
from VoGisProfilTool.bo.settings import Settings

import VoGisProfilTool.resources_rc

pluginPath = os.path.dirname(__file__)


class VoGISProfilToolMain:

    def __init__(self, iface):
        self.iface = iface
        self.settings = None

        overrideLocale = QgsSettings().value("locale/overrideFlag", False, bool)
        if not overrideLocale:
            locale = QLocale.system().name()[:2]
        else:
            locale = QgsSettings().value("locale/userLocale", "")

        QgsMessageLog.logMessage("Locale: {}".format(locale), "VoGis", Qgis.Info)
        qmPath = "{}/i18n/vogisprofiltoolmain_{}.qm".format(pluginPath, locale)

        if locale != 'de' and not os.path.exists(qmPath):
            qmPath = "{}/i18n/vogisprofiltoolmain_en.qm".format(pluginPath)

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QApplication.installTranslator(self.translator)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/vogisprofiltoolmain/icons/icon.png"),
            "VoGIS Profil Tool", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToRasterMenu("&VoGIS ProfilTool", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&VoGIS ProfilTool", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        is_open = QgsSettings().value("vogisprofiltoolmain/isopen", False, bool)
        QgsMessageLog.logMessage("Is open: {0}".format(is_open), "VoGis", Qgis.Info)
        if is_open:
            QgsMessageLog.logMessage(u"Dialog already opened", "VoGis", Qgis.Info)
            return

        try:
            import shapely
        except ImportError:
            self.iface.messageBar().pushCritical(
                "VoGIS-Profiltool",
                "Library 'shapely' not found. Please install!")
            return
        except:
            self.iface.messageBar().pushCritical(
                "VoGIS-Profiltool",
                "There seems to be a problem with your shapely/geos install.\nSee:\nhttp://comments.gmane.org/gmane.linux.debian.devel.bugs.general/1111838!")
            return

        self.settings = Settings(self.__getMapData())

        #checken ob raster und oder lines vorhanden sind
        #if self.settings.mapData.lines.count() < 1:
        #    QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Keine Linienebene vorhanden")
        #    return 2
        if self.settings.mapData.rasters.count() < 1:
            retVal = QMessageBox.warning(self.iface.mainWindow(),
                                         "VoGIS-Profiltool",
                                         QApplication.translate("code", "Keine Rasterebene vorhanden oder sichtbar! Nur hektometrieren?"),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if retVal == QMessageBox.No:
                return 2
            else:
                self.settings.onlyHektoMode = True
                self.settings.createHekto = True

        try:
            QgsSettings().setValue("vogisprofiltoolmain/isopen", True)
            # Create the dialog (after translation) and keep reference
            self.dlg = VoGISProfilToolMainDialog(self.iface, self.settings)
            # show the dialog
            self.dlg.show()
            # Run the dialog event loop
            self.dlg.exec_()
        finally:
            QgsSettings().setValue("vogisprofiltoolmain/isopen", False)


    def __getMapData(self):
        raster_coll = RasterCollection()
        line_coll = LineCollection()
        poly_coll = PolygonCollection()

        root = QgsProject.instance().layerTreeRoot()
        avail_lyrs = root.findLayers()

        for lyr in avail_lyrs:
            if lyr.isVisible():
                mapLayer = lyr.layer()
                lyr_type = mapLayer.type()
                lyr_name = mapLayer.name()
                if lyr_type == QgsMapLayer.VectorLayer:
                    #vector
                    if mapLayer.geometryType() == QgsWkbTypes.LineGeometry:
                        #Line
                        new_line = Line(mapLayer.id(), lyr_name, mapLayer)
                        line_coll.addLine(new_line)
                    elif mapLayer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        #Polygon
                        new_poly = Polygon(mapLayer.id(), lyr_name, mapLayer)
                        poly_coll.addPolygon(new_poly)
                elif lyr_type == QgsMapLayer.RasterLayer:
                    #Raster
                    QgsMessageLog.logMessage("[{0}] provider type: {1}".format(lyr_name, mapLayer.providerType()), "VoGis", Qgis.Info)
                    if mapLayer.providerType() == "gdal":
                        if mapLayer.bandCount() < 2:
                            new_raster = Raster(mapLayer.id(), lyr_name, mapLayer)
                            raster_coll.addRaster(new_raster)

        map_data = MapData()
        map_data.lines = line_coll
        map_data.rasters = raster_coll
        map_data.polygons = poly_coll

        return map_data
