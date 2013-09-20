# -*- coding: utf-8 -*-

# -*- coding: iso-8859-15 -*-

"""
/***************************************************************************
VoGisProfileDialog
copyright : (C) 2012 by BergWerk GIS EDV-Dienstleistungen e.U.
email : wb@BergWerk-GIS.at
 ***************************************************************************/

"""

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt
from ui_vogisprofileplot import *
from profilehelper import *
from ExportTxt import *
from ExportShp import ExportShp
from ExportXls import ExportXls
from vogisprofileutil import *


class VoGisProfilePlot(QDialog):


	def __init__(self, interface, profiles, showDataPoints, lineLayerCrs):

		QDialog.__init__(self, interface.mainWindow())
		self.Interface=interface
		self.Profiles=profiles
		self.ShowDataPoints=showDataPoints
		self.LineLayerCrs=lineLayerCrs
		self.ui =Ui_VoGisProfilePlot()
		self.ui.setupUi(self)

		QObject.connect(self.ui.IDC_sliderZ, SIGNAL("valueChanged(int)"), self._adjustZ)
		self.ui.IDC_sliderZ.setMinimum(1)
		self.ui.IDC_sliderZ.setMaximum(100)
		self.ui.IDC_sliderZ.setValue(100)

		COLORS = ['brown', 'cyan', 'blue', 'red', 'limegreen', 'navy']
		#http://doc.trolltech.com/4.6/qt.html#GlobalColor-enum
		#globalColors=[3,2,7,13,8,14,9, 15, 10, 16, 11, 17, 12, 18, 5, 4, 6, 19, 0, 1]
		self.GLOBALCOLORS=['black','red','darkRed','green', 'darkGreen','blue','darkBlue','cyan','darkCyan','magenta','darkMagenta','yellow','darkYellow','gray','darkGray']

		#self.Plot=Qwt.QwtPlot(self)
		self.ui.qwtPlot.setTitle('VoGIS-Profiltool Plot')
		self.ui.qwtPlot.setCanvasBackground(Qt.Qt.white)
		self.ui.qwtPlot.plotLayout().setMargin(0)
		self.ui.qwtPlot.plotLayout().setCanvasMargin(0)
		self.ui.qwtPlot.plotLayout().setAlignCanvasToScales(True)
		#self.ui.qwtPlot.setAxisScale(0,1000,100,0)

		grid = Qwt.QwtPlotGrid()
		pen = Qt.QPen(Qt.Qt.DotLine)
		pen.setColor(Qt.Qt.black)
		pen.setWidth(1)
		grid.setPen(pen)
		grid.attach(self.ui.qwtPlot)

		legend = Qwt.QwtLegend()
		self.ui.qwtPlot.insertLegend(legend,Qwt.QwtPlot.BottomLegend)

		self.createPlot()

		QApplication.restoreOverrideCursor()



	def createPlot(self):

		self.ui.qwtPlot.detachItems()

		idxColor=0

		ph=ProfileHelper(self.Profiles)

		#loop thru profiles (features)
		for i in range(ph.ProfileCount()):

			#loop thru rasters
			for j in range(ph.RasterCount(i)):

				#QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool",  str(i) +'/' + str(j))

				curve1 = Qwt.QwtPlotCurve(ph.GetRasterName(j) + '/' + str(i+1))
				curve1.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased);
				#curve1.setPen(QPen(Qt.Qt.black))
				#curve1.setPen(QPen(coloriter.next()))
				curve1.setPen(QPen(QColor(self.GLOBALCOLORS[idxColor])))
				#self.curve1.setYAxis(Qwt.QwtPlot.yLeft)
				#self.curve1.setData([0,100,200,300,400], [0,10,40,70,65])

				curve1.setStyle(Qwt.QwtPlotCurve.Lines)
				#self.curve1.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)

				if self.ShowDataPoints:
					curve1.setSymbol(Qwt.QwtSymbol(
						Qwt.QwtSymbol.Cross,
						Qt.QBrush(),
						Qt.QPen(Qt.Qt.black),
						Qt.QSize(5, 5)
					))

				curve1.setData(ph.GetDistances(i), ph.GetRasterVals(i,j))
				curve1.attach(self.ui.qwtPlot)

				idxColor=idxColor+1
				if idxColor==len(self.GLOBALCOLORS):
					idxColor=0

		self.ui.qwtPlot.replot()



	def exportGraphic(self):

		pixMap=QPixmap()
		pixMap=QPixmap.grabWidget(self.ui.qwtPlot)

		if pixMap.isNull():
			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Konnte Graphik nicht zum Speichern vorbereiten!')
			return

		filter="PNG (*.png);;JPG (*.jpg);;BMP (*.bmp)"
		fileName=self._getFileName(filter)

		if fileName=='':
			return

		graphikType = fileName[-3:]
		if pixMap.save(fileName,graphikType):
			QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Datei erfolgreich gespeichert! [' + fileName + ']')
		else:
			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Unerwarteter Fehler beim Speichern! [' + fileName + ']')



	def exportTxt(self):

		delimiter=util.getDelimiter(self.Interface)
		if delimiter=='':
			return

		filter = "TXT (*.txt)"
		fileName=self._getFileName(filter)

		if fileName=='':
			return

		ph=ProfileHelper(self.Profiles)

		exportText=ExportTxt(self.Interface, ph, fileName, delimiter, '\t')
		exportText.Export()



	def exportShp(self):
		filter = "SHP (*.shp)"
		fileName=self._getFileName(filter)

		if fileName=='':
			return

		ph=ProfileHelper(self.Profiles)

		exportShape=ExportShp(self.Interface, ph, fileName, self.LineLayerCrs)
		exportShape.Export()



	def exportXls(self):

		delimiter=util.getDelimiter(self.Interface)
		if delimiter=='':
			return

		filter = "CSV (*.csv)"
		fileName=self._getFileName(filter)

		if fileName=='':
			return

		ph=ProfileHelper(self.Profiles)

		#don't use working real Excel export for now
		#HACK export TXT with XLS extension
		#exportExcel = ExportXls(self.Interface, ph, fileName)
		#exportExcel.Export()

		exportText=ExportTxt(self.Interface, ph, fileName, delimiter, ';')
		exportText.Export()



	def flipProfile(self):

		ph=ProfileHelper(self.Profiles)
		self.Profiles=ph.Flip()

		self.createPlot()


	def _getFileName(self, filter):
		selectedFilter=QString()
		fileDlg =QFileDialog(self.Interface.mainWindow())
		fileName=fileDlg.getSaveFileName(
			self.Interface.mainWindow()
			, "Graphik speichern"
			, ""
			, filter
			, selectedFilter
		)


		if fileName.isEmpty():
			return ''

		fileExt = str(selectedFilter[:3]).lower()
		if str(fileName).lower().endswith(fileExt)==False:
			fileName =fileName + '.' + fileExt

		return fileName



	def _adjustZ(self):

		ph=ProfileHelper(self.Profiles)
		zMin, zMax= ph.GetRasterMinMax()
		#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", '{0}/{1}'.format(zMin,zMax))

		if zMin>=zMax:
			zMax = zMin+1

		newZ= zMax * ( float(100) / float(self.ui.IDC_sliderZ.value()))
		self.ui.qwtPlot.setAxisScale(0,zMin,newZ,0)
		self.ui.qwtPlot.replot()
