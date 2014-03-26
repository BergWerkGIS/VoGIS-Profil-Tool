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


def name():
    return "VoGIS-Profiltool"


def description():
    return "Create profiles from DHMs using vector geometries or a digitized line."


def version():
    return "1.8.7"


def icon():
    return "icons/icon.png"

def category():
    return 'Raster'

def qgisMinimumVersion():
    return "1.8"


def qgisMaximumVersion():
    return "2.99"


def experimental():
    return False


def author():
    return "BergWerk GIS"


def email():
    return "wb@BergWerk-GIS.at"


def classFactory(iface):
    # load VoGISProfilToolMain class from file VoGISProfilToolMain
    from vogisprofiltoolmain import VoGISProfilToolMain
    return VoGISProfilToolMain(iface)
