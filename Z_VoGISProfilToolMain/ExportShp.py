# coding: iso-8859-15


#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bergw
#
# Copyright:   (c) bergw 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------


from os.path import basename
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from profilehelper import *
from vogisprofileutil import *



class ExportShp:


	def __init__(
		self
		, interface
		, profileHelper
		, fileName
		, lineLayerCrs
		):

		self.Interface=interface
		self.PH=profileHelper
		self.FileName=fileName
		self.LineLayerCrs=lineLayerCrs



	def Export(self):

#		try:

		#delete if shapefile already exists
		try:

			with open('filename') as f: pass
			f.close()

			if QgsVectorFileWriter.deleteShapeFile(self.FileName)==False:
				QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Konnte vorhandenes Shapefile nicht löschen: {0}'.format(self.FileName))
				return
		except IOError as e:
			pass


		fldIdx=0
		flds={}

		flds[fldIdx]=QgsField('ExportId', QVariant.Int)
		fldIdx=+1

		attrCnt =self.PH.AttributeCount(0)
		if attrCnt>0:
			attribs=self.PH.GetAttributes(0)
			for (fld, fldVal) in attribs.iteritems():
				flds[fldIdx]=fld
				fldIdx+=1

		flds[fldIdx]=QgsField('x', QVariant.Double)
		fldIdx+=1
		flds[fldIdx]=QgsField('y', QVariant.Double)
		fldIdx+=1
		flds[fldIdx]=QgsField('d', QVariant.Double)
		fldIdx+=1


		for k in range(self.PH.RasterCount(0)):
			fldName = str(self.PH.GetRasterName(k).toUtf8()).decode("utf-8")
			fldName=util.stripUmlauts(self.Interface, fldName)
			flds[fldIdx]=QgsField(fldName,QVariant.Double)
			fldIdx+=1


		# create an instance of vector file writer, it will create the shapefile. Arguments:
		# 1. path to new shapefile (will fail if exists already)
		# 2. encoding of the attributes
		# 3. field map
		# 4. geometry type - from WKBTYPE enum
		# 5. layer?s spatial reference (instance of QgsCoordinateReferenceSystem) - optional
		shpWriter=QgsVectorFileWriter(self.FileName,"CP1250", flds, QGis.WKBPoint,self.LineLayerCrs)

		if shpWriter.hasError() != QgsVectorFileWriter.NoError:
			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Konnte Shapefile nicht erstellen: {0}'.format(self.FileName))
			return


		#loop thru profiles (features)
		profileCnt=self.PH.ProfileCount()
		#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'ProfileCnt:{0} AttrCnt:{1}'.format(profileCnt, attrCnt))
		for i in range(profileCnt):

			pnts = self.PH.GetPoints(i)
			dists =self.PH.GetDistances(i)

			#write coordinates and distance
			for j in range(len(pnts)):

				fldIdx=0

				feat=QgsFeature()
				feat.setGeometry(QgsGeometry.fromPoint(pnts[j]))

				#exportId
				feat.addAttribute(fldIdx,i+1)
				fldIdx=+1

				#write attributes
				if attrCnt >0 :
					attribs=self.PH.GetAttributes(i)
					for(fld,fldVal)in attribs.iteritems():
						#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Fld[{0}]:{1}'.format(fld.name(), fldVal.toString()))
						feat.addAttribute(fldIdx,fldVal)
						fldIdx+=1

				#write coordinates and distance
				feat.addAttribute(fldIdx,QVariant(pnts[j].x()))
				fldIdx+=1
				feat.addAttribute(fldIdx,QVariant(pnts[j].y()))
				fldIdx+=1
				feat.addAttribute(fldIdx,QVariant(dists[j]))
				fldIdx+=1

				#write rastervalues
				for k in range(self.PH.RasterCount(i)):
					rasterVals=self.PH.GetRasterVals(i,k)
					z=rasterVals[j]
					feat.addAttribute(fldIdx, QVariant(z))
					fldIdx+=1

				shpWriter.addFeature(feat)


		del shpWriter

		reply = QMessageBox.question(
			self.Interface.mainWindow()
			, "VoGIS-Profiltool"
			, 'Datei erfolgreich gespeichert! [' + self.FileName + ']\r\n\r\n\r\nShapefile laden?'
			, QMessageBox.Yes | QMessageBox.No
			, QMessageBox.Yes
		)

		if reply == QMessageBox.Yes:
			self.Interface.addVectorLayer(
				self.FileName
				, basename(str(self.FileName))
				, "ogr"
			)

#		except Exception, e:
#			import traceback, os.path
#			top = traceback.extract_stack()[-1]
#			msg = ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
#			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Unerwarteter Fehler:\r\n' + msg )
