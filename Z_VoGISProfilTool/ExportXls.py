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


import sys
#from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from qgis.core import *
from profilehelper import *



class ExportXls:


	def __init__(
		self
		, interface
		, profileHelper
		, fileName
		):

		self.Interface=interface
		self.PH=profileHelper
		self.FileName=fileName



	def Export(self):

		try:
			from excel import *
		except:
			QMessageBox.warning(self.Interface.mainWindow(), "Konnte Excel Support nicht initialisieren", "Das Paket 'xlwt' konnte nicht gefunden werden. Bitte befolgen Sie die Installationsanleitung unter http://www.python-excel.org/")
			return

		try:

			wb=xlwt.Workbook()
			ws=wb.add_sheet("QGIS Export")


			#row,col
			idxCol=0
			idxRow=0


			#exportID
			ws.write(idxRow,idxCol,'ExportID')
			idxCol=+1

			attrCnt =self.PH.AttributeCount(0)
			if attrCnt>0:
				attribs=self.PH.GetAttributes(0)
				for (fld, fldVal) in attribs.iteritems():
					ws.write(idxRow, idxCol, str(fld.name()))
					idxCol+=1

			for token in ['x','y','d']:
				ws.write(idxRow,idxCol,token)
				idxCol+=1

			for k in range(self.PH.RasterCount(0)):
				ws.write(idxRow, idxCol,str(self.PH.GetRasterName(k).toUtf8()).decode("utf-8"))
				idxCol+=1

			idxRow+=1

			#loop thru profiles (features)
			profileCnt=self.PH.ProfileCount()
			#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'ProfileCnt:{0} AttrCnt:{1}'.format(profileCnt, attrCnt))
			for i in range(profileCnt):

				pnts = self.PH.GetPoints(i)
				dists =self.PH.GetDistances(i)

				#write coordinates and distance
				for j in range(len(pnts)):

					idxCol=0

					#exportId
					ws.write(idxRow,idxCol,'{0}'.format(i+1))
					idxCol+=1

					#write attributes
					if attrCnt >0 :
						attribs=self.PH.GetAttributes(i)
						for(fld,fldVal)in attribs.iteritems():
							ws.write(idxRow,idxCol,str(fldVal.toString()))
							idxCol+=1

					ws.write(idxRow,idxCol, pnts[j].x())
					idxCol+=1
					ws.write(idxRow,idxCol, pnts[j].y())
					idxCol+=1
					ws.write(idxRow,idxCol, dists[j])
					idxCol+=1

					#write rastervalues
					for k in range(self.PH.RasterCount(i)):
						rasterVals=self.PH.GetRasterVals(i,k)
						z=rasterVals[j]
						ws.write(idxRow,idxCol,z)
						idxCol+=1

					idxRow+=1



			#ws.write(0, 0, 'Test')
			#ws.write(1, 0, 1.1)
			#ws.write(2, 0, 1)
			#ws.write(2, 1, 1)
			#ws.write(2, 2, excel.xlwt.Formula("A3+B3"))

			wb.save(self.FileName)

			QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Datei erfolgreich gespeichert! [' + self.FileName + ']')


		except Exception as ex:
			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Unerwarteter Fehler: ' + str(ex) )




