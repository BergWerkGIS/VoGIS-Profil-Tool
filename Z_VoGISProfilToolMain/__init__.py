"""
/***************************************************************************
 VoGisProfile
                                 A QGIS plugin
 VOGIS Profile Tool
                             -------------------
        begin                : 2012-06-23
        copyright            : (C) 2012 by BergWerk GIS EDV-Dienstleistungen e.U.
        email                : wb@BergWerk-GIS.at
 ***************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "VoGIS-Profiltool"
def description():
    return "VoGIS-Profiltool"
def version():
    return "Version 0.6"
#def icon():
#    return "icon.png"
def qgisMinimumVersion():
    return "1.8"
def classFactory(iface):
    # load VoGisProfile class from file VoGisProfile
    from vogisprofile import VoGisProfile
    return VoGisProfile(iface)
