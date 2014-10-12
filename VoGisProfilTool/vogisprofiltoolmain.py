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
import unicodedata
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources_rc
from vogisprofiltoolmaindialog import VoGISProfilToolMainDialog
from bo.raster import Raster
from bo.line import Line
from bo.polygon import Polygon
from bo.rasterCollection import RasterCollection
from bo.lineCollection import LineCollection
from bo.polygonCollection import PolygonCollection
from bo.mapdata import MapData
from bo.settings import Settings


class VoGISProfilToolMain:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/VoGisProfilTool"
        # initialize locale
        localePath = ""
        if QGis.QGIS_VERSION_INT < 10900:
            loc = QSettings().value("locale/userLocale").toString()[0:2]
        else:
            loc = QSettings().value("locale/userLocale")[0:2]

        if QFileInfo(self.plugin_dir).exists():
            #QgsMessageLog.logMessage('plugin_dir exits', 'VoGis')
            localePath = self.plugin_dir + "/i18n/vogisprofiltoolmain_" + loc + ".qm"

        if QFileInfo(localePath).exists():
            #QgsMessageLog.logMessage('localePath exits', 'VoGis')
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                #QgsMessageLog.logMessage("qVersion() > '4.3.3'", 'VoGis')
                QCoreApplication.installTranslator(self.translator)

        self.settings = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/vogisprofiltoolmain/icons/icon.png"),
            #QIcon(":/plugins/vogisprofiltoolmain/icons/home.png"),
            u"VoGIS Profil Tool", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        #self.iface.addPluginToMenu(u"&VoGIS ProfilTool", self.action)
        self.iface.addPluginToRasterMenu(u"&VoGIS ProfilTool", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&VoGIS ProfilTool", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):

        try:
            import shapely
        except ImportError:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'Library "shapely" not found. Please install!')
            return
        except:
            QMessageBox.warning(self.iface.mainWindow(),
                                "VoGIS-Profiltool",
                                'There seems to be a problem with your shapely/geos install.\nSee:\nhttp://comments.gmane.org/gmane.linux.debian.devel.bugs.general/1111838!')
            return

        self.settings = Settings(self.__getMapData())
        #QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "lines:" + str(self.settings.mapData.lines.count()) + " rasters:" + str(self.settings.mapData.rasters.count()))

        #checken ob raster und oder lines vorhanden sind
        #if self.settings.mapData.lines.count() < 1:
        #    QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Keine Linienebene vorhanden")
        #    return 2
        if self.settings.mapData.rasters.count() < 1:
            retVal = QMessageBox.warning(self.iface.mainWindow(),
                                         "VoGIS-Profiltool",
                                         QApplication.translate('code', 'Keine Rasterebene vorhanden oder sichtbar! Nur hektometrieren?', None, QApplication.UnicodeUTF8),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
            if retVal == QMessageBox.No:
                return 2
            else:
                self.settings.onlyHektoMode = True
                self.settings.createHekto = True

        # Create the dialog (after translation) and keep reference
        self.dlg = VoGISProfilToolMainDialog(self.iface, self.settings)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        #result = self.dlg.exec_()
        self.dlg.exec_()


    def __getMapData(self):

        legend = self.iface.legendInterface()
        avail_lyrs = legend.layers()

        raster_coll = RasterCollection()
        line_coll = LineCollection()
        poly_coll = PolygonCollection()

        for lyr in avail_lyrs:
            if legend.isLayerVisible(lyr):
                lyr_type = lyr.type()
                lyr_name = unicodedata.normalize('NFKD', unicode(lyr.name())).encode('ascii', 'ignore')
                #lyr_name = unicodedata.normalize('NFKD', unicode(lyr.name()))
                if lyr_type == 0:
                    #vector
                    if lyr.geometryType() == 1:
                        #Line
                        new_line = Line(lyr.id(), lyr_name, lyr)
                        line_coll.addLine(new_line)
                    elif lyr.geometryType() == 2:
                        #Polygon
                        new_poly = Polygon(lyr.id(), lyr_name, lyr)
                        poly_coll.addPolygon(new_poly)
                elif lyr_type == 1:
                    #Raster
                    QgsMessageLog.logMessage(u'[{0}] provider type: {1}'.format(lyr.name(), lyr.providerType()), 'VoGis')
                    if lyr.providerType() == 'gdal':
                        if lyr.bandCount() < 2:
                            new_raster = Raster(lyr.id(), lyr_name, lyr)
                            raster_coll.addRaster(new_raster)

        map_data = MapData()
        map_data.lines = line_coll
        map_data.rasters = raster_coll
        map_data.polygons = poly_coll

        return map_data
