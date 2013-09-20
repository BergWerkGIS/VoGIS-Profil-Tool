# coding: iso-8859-15

"""
/***************************************************************************
VoGisProfile
copyright : (C) 2012 by BergWerk GIS EDV-Dienstleistungen e.U.
email : wb@BergWerk-GIS.at
 ***************************************************************************/

"""

from shapely.wkb import loads
from shapely.wkb import dumps
import shapely.geos

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from vogisprofiledialog import VoGisProfileDialog



class VoGisProfile:



	def __init__(self, iface):
		# Save reference to the QGIS interface
		self.iface = iface
		self.legIface = iface.legendInterface()



	def initGui(self):

		# Create action that will start plugin configuration
		self.action = QAction(QIcon(":/plugins/VoGisProfilTool/icon.png"), "VoGIS-Profiltool", self.iface.mainWindow())
		self.action.setWhatsThis("Konfiguration für VoGIS-Profiltool")
		self.action.setStatusTip("-= VoGIS-Profiltool =-")

		# connect the action to the run method
		QObject.connect(self.action, SIGNAL("triggered()"), self.run)

		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu("&VoGIS-Profiltool", self.action)



	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu("&VoGIS-Profiltool",self.action)
		self.iface.removeToolBarIcon(self.action)



	# run method that performs all the real work
	def run(self):

		try:
			geosCAPIVersion = shapely.geos.geos_capi_version
		except AttributeError:
			geosCAPIVersion = (-1,-1,-1)

		if int(geosCAPIVersion[0]) < 1 or int(geosCAPIVersion[1]) < 6:
			QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Falsche Version von GEOS oder shapely!")
			return 2


		if self.iface.mapCanvas().layerCount() == 0:
			QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Keine Layer vorhanden!")
			return 2

		loadedLayers=self._get_loaded_layers()

		#if len(loadedLayers['line']) < 1:
		#	QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Es muss mindestens ein Linienlayer geladen sein!")
		#	return 1

		if len(loadedLayers['raster']) < 1:
			QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", "Es muss mindestens ein Rasterlayer geladen sein!")
			return 1


		dlg = VoGisProfileDialog(self.iface,loadedLayers)
		dlg.show()
		result = dlg.exec_()





	def _get_loaded_layers(self):

		availableLayers = {"line" : [], "raster" : []}
		loadedLayers = self.legIface.layers()
		for layerObj in loadedLayers:
			layerType = layerObj.type()
			if layerType == 0:
				if layerObj.geometryType() == 1: # it's a line
					availableLayers["line"].append(layerObj)
			elif layerType == 1: # it's a raster layer
				if layerObj.bandCount() == 1:
					availableLayers["raster"].append(layerObj)
		return availableLayers


