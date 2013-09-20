# -*- coding: iso-8859-15 -*-

"""
/***************************************************************************
VoGisProfileDialog
copyright : (C) 2012 by BergWerk GIS EDV-Dienstleistungen e.U.
email : wb@BergWerk-GIS.at
 ***************************************************************************/

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui_vogisprofile import Ui_VoGisProfile
from vogisprofileplot import *
from createprofile import *
from selectedsettings import *
from selectlinetool import SelectLineTool
from ptmaptool import *
# Based on Profile tool
# 2008 Borys Jurgiel
# 2012 Borys Jurgiel, Partice Verchere



class VoGisProfileDialog(QDialog):


#	def __init__(self, availableLyrs, callBack):
	def __init__(self,interface, availableLyrs):

		QDialog.__init__(self, interface.mainWindow())
		self.iface=interface
		self.canvas = interface.mapCanvas()
		self.availableLayers = availableLyrs
		#self.callBack = callBack
		self.ui = Ui_VoGisProfile()
		self.ui.setupUi(self)


#		self.ui.IDC_tbFromX.setText('540000')
#		self.ui.IDC_tbFromY.setText('275000')
#		self.ui.IDC_tbToX.setText('575000')
#		self.ui.IDC_tbToY.setText('245000')

		self.ui.IDC_tbFromX.setText('-30000')
		self.ui.IDC_tbFromY.setText('240000')
		self.ui.IDC_tbToX.setText('-20000')
		self.ui.IDC_tbToY.setText('230000')


		self.action = QAction(QIcon(":/plugins/VoGisProfilTool/icon.png"), "VoGIS-Profiltool", self.iface.mainWindow())
		self.action.setWhatsThis("VoGIS-Profiltool")

		self.tool = ProfiletoolMapTool(self.iface.mapCanvas(),self.action)
		self.saveTool = self.canvas.mapTool()
		self.polygon = False
		self.rubberband = QgsRubberBand(self.canvas, self.polygon)
		self.polygon = False
		self.rubberband = QgsRubberBand(self.canvas, self.polygon)
		#init the table where is saved the poyline
		self.pointstoDraw = []
		self.dblclktemp = None
		self.DrawnLine=None
		#self.pointstoCal = []
		#self.lastClicked = QgsPoint(-9999999999.9,9999999999.9)



		#add raster layers to listview
		for rasterLyr in self.availableLayers["raster"]:
			item= QListWidgetItem(rasterLyr.name())
			item.setData(Qt.UserRole, rasterLyr)
			item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
			item.setCheckState(Qt.Unchecked)
			self.ui.IDC_lvwRaster.addItem(item)


		#line layers to combobox
		#self.ui.IDC_cbLineLayer.clear()
		#self.ui.IDC_cbLineLayer.addItems([ll.name() for ll in self.availableLayers["line"]])
		for vLyr in self.availableLayers["line"]:
			self.ui.IDC_cbLineLayer.addItem(vLyr.name(), vLyr)

		#validator = QDoubleValidator(1.0,10.0,2,self.ui.IDC_tbFromY);
		#validator.setNotation(QDoubleValidator.StandardNotation)
		#self.ui.IDC_tbFromY.setValidator(validator)


	def accept(self):
		self.rubberband.reset(self.polygon)
		QDialog.accept(self)



	def valueChangedEquiDistance(self, val):
		if self.ui.IDC_radioEquiDistance.isChecked()==False:
			self.ui.IDC_radioEquiDistance.setChecked(True)



	def valueChangedVertexCount(self, val):
		if self.ui.IDC_radioVertexCount.isChecked()==False:
			self.ui.IDC_radioVertexCount.setChecked(True)



	def plotProfile(self):

		#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'getSettings')
		settings =self._getSettings()

		#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'checkSettings')
		if self._checkSettings(settings)==False:
			return

		if settings.LineType==EnumLineType.FromDrawing:
			#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'LineType==EnumLineType.FromDrawing')
			#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", str(self.DrawnLine))
			settings.CoordFeature=self.DrawnLine
			if settings.CoordFeature==None:
				QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'Es wurde noch keine Linie digitalisiert!')
				return

			self.Settings=settings


		QApplication.setOverrideCursor(Qt.WaitCursor)

		self._createAndPlot(settings)



	def drawLine(self):

		if self.ui.IDC_radioDrawLine.isChecked()==False:
			self.ui.IDC_radioDrawLine.setChecked(True)

		#settings =self._getSettings()

		#if self._checkSettings(settings)==False:
		#	return

		#self.Settings=settings

		self.dblclktemp = None
		self.rubberband.reset(self.polygon)
		self._cleaning()
		self._activateTool()
		self.canvas.setMapTool(self.tool)



	def _createAndPlot(self, settings):

		#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", '_createAndPlot:'+ str(settings.CoordFeature))

		cp = CreateProfile(self.iface, settings)
		profiles = cp.create()

		showDataPoints=False
		if settings.PointInterval == -1 and settings.NumberOfPoints == -1:
			showDataPoints=True

		lineLayerCrs=None
		if settings.LineType==EnumLineType.FromFeature:
			lineLayerCrs=self.LineLayer.crs()
		else:
			lineLayerCrs=self.iface.mapCanvas().mapRenderer().destinationCrs()

		plotDlg = VoGisProfilePlot(self.iface, profiles, showDataPoints, lineLayerCrs)
		plotDlg.show()
		result=plotDlg.exec_()



	def _getSettings(self):

		equiDistance = -1
		vertexCount = -1

		self.ChkdRasters=self._checkedRasters()
		#self.LineLayer=self._getLineLayer(self.ui.IDC_cbLineLayer.currentText())
		self.LineLayer=self.ui.IDC_cbLineLayer.itemData(self.ui.IDC_cbLineLayer.currentIndex()).toPyObject()

		if self.ui.IDC_radioEquiDistance.isChecked():
			equiDistance=self.ui.IDC_dblspinDistance.value()

		if self.ui.IDC_radioVertexCount.isChecked():
			vertexCount=self.ui.IDC_dblspinVertexCnt.value()


		if self.ui.IDC_radioCoords.isChecked():
			lineType= EnumLineType.FromCoordinates
		elif self.ui.IDC_radioDrawLine.isChecked():
			lineType=EnumLineType.FromDrawing
		elif self.ui.IDC_radioLineLayer.isChecked():
			lineType=EnumLineType.FromFeature
		else:
			lineType=EnumLineType.Unknown


		return SelectedSettings(
			self.LineLayer
			, self.ChkdRasters
			, equiDistance
			, vertexCount
			, self.ui.IDC_chkSelFeatures.isChecked()
			, lineType
			,self.ui.IDC_tbFromX.text()
			,self.ui.IDC_tbFromY.text()
			,self.ui.IDC_tbToX.text()
			,self.ui.IDC_tbToY.text()
		)



	def _checkSettings(self, settings):

		if len(settings.RasterLayers) < 1:
			QMessageBox.warning(self, "VoGIS-Profiltool", "Kein Raster selektiert!")
			return False


		if settings.LineType == EnumLineType.FromFeature:
			if settings.LineLayer == None:
				QMessageBox.warning(self, "VoGIS-Profiltool", "Kein Linienlayer vorhanden!")
				return False

			if settings.UseSelectedFeatures:
				if settings.LineLayer.selectedFeatureCount() < 1:
					QMessageBox.warning(self, "VoGIS-Profiltool", "Keine Elemente im Linienlayer selektiert!")
					return False

			#check for multipart features: not supported
			provider = settings.LineLayer.dataProvider()
			feat=QgsFeature()
			while provider.nextFeature(feat):
				geom= feat.geometry()
				if geom.isMultipart():
					QMessageBox.warning(self, "VoGIS-Profiltool", "Multipart Features werden nicht unterstützt!")
					return False


		if settings.LineType==EnumLineType.FromCoordinates:
			if self._isFloat(settings.XMin, 'XMin') == False:
				return False
			if self._isFloat(settings.YMin, 'YMin') == False:
				return False
			if self._isFloat(settings.XMax, 'XMax') == False:
				return False
			if self._isFloat(settings.YMax, 'YMax') == False:
				return False
			settings.CoordFeature=self._createFeature([QgsPoint(float(settings.XMin),float(settings.YMin)),QgsPoint(float(settings.XMax),float(settings.YMax))] )
		else:
			settings.CoordFeature=None



	def _createFeature(self, linePnts):
		line=QgsGeometry.fromPolyline(linePnts)
		qgFeat = QgsFeature()
		qgFeat.setGeometry(line)

		return qgFeat



	def _activateTool(self):
		QObject.connect(self.tool, SIGNAL("moved"), self._moved)
		QObject.connect(self.tool, SIGNAL("rightClicked"), self._rightClicked)
		QObject.connect(self.tool, SIGNAL("leftClicked"), self._leftClicked)
		QObject.connect(self.tool, SIGNAL("doubleClicked"), self._doubleClicked)
		QObject.connect(self.tool, SIGNAL("deactivate"), self._deactivateTool)



	def _deactivateTool(self):		#enable clean exit of the plugin
		QObject.disconnect(self.tool, SIGNAL("moved"), self._moved)
		QObject.disconnect(self.tool, SIGNAL("leftClicked"), self._leftClicked)
		QObject.disconnect(self.tool, SIGNAL("rightClicked"), self._rightClicked)
		QObject.disconnect(self.tool, SIGNAL("doubleClicked"), self._doubleClicked)
		#self.rubberband.reset(self.polygon)
		self.iface.mainWindow().statusBar().showMessage(QString(""))



	def _cleaning(self):
		#try:
			#print str(self.previousLayer)
			#self.previousLayer.removeSelection(False)
			#self.previousLayer.select(None)
		#except:
		#	pass

		pointstoDraw = []

		self.canvas.unsetMapTool(self.tool)
		self.canvas.setMapTool(self.saveTool)

		#keep rubberband visible
		#self.rubberband.reset(self.polygon)



#************************************* Mouse listener actions ***********************************************

	def _moved(self,position):
		if len(self.pointstoDraw) > 0:
			mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
			self.rubberband.reset(self.polygon)
			for i in range(0,len(self.pointstoDraw)):
				self.rubberband.addPoint(self.pointstoDraw[i])
			self.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))



	def _rightClicked(self,position):
		self._lineFinished(position)



	def _leftClicked(self,position):

		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoint = QgsPoint(mapPos.x(), mapPos.y())
		#if self.selectionmethod == 0:
		if newPoint == self.dblclktemp:
			self.dblclktemp = None
			return
		else :
			if len(self.pointstoDraw) == 0:
				self.rubberband.reset(self.polygon)
			self.pointstoDraw.append( newPoint)
#		if self.selectionmethod == 1:
#			result = SelectLineTool().getPointTableFromSelectedLine(self.iface, self.tool, newPoints, self.layerindex, self.previousLayer , self.pointstoDraw)
#			self.pointstoDraw = result[0]
#			self.layerindex = result[1]
#			self.previousLayer = result[2]
#			self.doprofile.calculateProfil(self.pointstoDraw, self.mdl,self.plotlibrary, False)
#			self.pointstoDraw = []
#			self.iface.mainWindow().statusBar().showMessage(QString(self.textquit1))



	def _doubleClicked(self,position):
		pass



	#not in use right now
	def _lineCancel(self):

		pass

		#if self.selectionmethod == 0:
		#	mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		#	newPoints = QgsPoint(mapPos.x(), mapPos.y())
		#	#if newPoints == self.lastClicked: return # sometimes a strange "double click" is given
		#	if len(self.pointstoDraw) > 0:
		#		self.pointstoDraw = []
		#		self.pointstoCal = []
		#		self.rubberband.reset(self.polygon)
		#	else:
		#		self.cleaning()
		#if self.selectionmethod == 1:
		#	try:
		#		self.previousLayer.removeSelection( False )
		#	except:
		#		self.iface.mainWindow().statusBar().showMessage("error right click")
		#	self.cleaning()



	def _lineFinished(self, position):

		mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
		newPoint = QgsPoint(mapPos.x(), mapPos.y())
		self.pointstoDraw.append( newPoint)
		#launch analyses
		self.iface.mainWindow().statusBar().showMessage(str(self.pointstoDraw))

		if len(self.pointstoDraw) < 2:
			self._cleaning()
			self.pointstoDraw = []
			self.dblclktemp = newPoint
			self.DrawnLine =None
			QMessageBox.warning(self, "VoGIS-Profiltool", "Profillinie digitalisieren abgebrochen!")
			return



		#self.doprofile.calculateProfil(self.pointstoDraw,self.mdl, self.plotlibrary)
		self.DrawnLine = self._createFeature(self.pointstoDraw)
		#QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", 'doubleClicked:' + str(self.Settings.CoordFeature))
		#self._createAndPlot(self.Settings)
		self._cleaning()

		#Reset
		self.pointstoDraw = []
		#temp point to distinct leftclick and dbleclick
		self.dblclktemp = newPoint
		#self.iface.mainWindow().statusBar().showMessage(QString(self.textquit0))



#************************************* Util Methods ***********************************************



#	def _getLineLayer(self,name):
#		lineLyr = None
#		for lyr in self.availableLayers["line"]:
#			if name == lyr.name():
#				lineLyr = lyr
#		return lineLyr



#	def _getRasterLayer(self,name):
#		rasterLyr = None
#		for lyr in self.availableLayers["raster"]:
#			if name == lyr.name():
#				rasterLyr = lyr
#		return rasterLyr



	def _checkedRasters(self):
		rasters=[]
		for i in range(self.ui.IDC_lvwRaster.count()):
			if self.ui.IDC_lvwRaster.item(i).checkState() == Qt.Checked:
				#rasters.append(self._getRasterLayer( self.ui.IDC_lvwRaster.item(i).text()))
				rasters.append(self.ui.IDC_lvwRaster.item(i).data(Qt.UserRole).toPyObject())
		return rasters



	def _isFloat(self, val, valName):
		try:
			f = float(val)
			return True
		except:
			QMessageBox.warning(self, "VoGIS-Profiltool",  valName + ' ist keine gültige Zahl!')
			return False