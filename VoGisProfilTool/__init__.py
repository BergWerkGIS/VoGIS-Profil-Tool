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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load VoGISProfilToolMain class from file VoGISProfilToolMain
    from VoGisProfilTool.vogisprofiltoolmain import VoGISProfilToolMain
    return VoGISProfilToolMain(iface)
