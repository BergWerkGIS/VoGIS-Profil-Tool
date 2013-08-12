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

from PyQt4 import QtCore, QtGui
from ui_vogisprofiltoolmain import Ui_VoGISProfilToolMain
# create the dialog for zoom to point


class VoGISProfilToolMainDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolMain()
        self.ui.setupUi(self)
