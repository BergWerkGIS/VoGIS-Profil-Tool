# -*- coding: iso-8859-15 -*-

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
import locale
#from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from qgis.core import *
from profilehelper import *
from vogisprofileutil import *


class ExportTxt:


	def __init__(
		self
		, interface
		, profileHelper
		, fileName
		, delimiter
		, separator
		):

		self.Interface=interface
		self.PH=profileHelper
		self.FileName=fileName
		self.Delimiter=delimiter # decimal point
		self.Separator=separator # separator between values



	def Export(self):

#		try:

		txt = open(self.FileName,'w')

		txt.write('ExportID' + self.Separator)

		attrCnt =self.PH.AttributeCount(0)
		if attrCnt>0:
			attribs=self.PH.GetAttributes(0)
			for (fld, fldVal) in attribs.iteritems():
				txt.write('{0}{1}'.format(fld.name()), self.Separator)

		txt.write('x{0}y{0}d{0}'.format(self.Separator))

		for k in range(self.PH.RasterCount(0)):
			fldName = util.stripUmlauts(self.Interface, str(self.PH.GetRasterName(k).toUtf8()).decode("utf-8"))
			txt.write('"{0}"{1}'.format(fldName, self.Separator))

		txt.write('\r\n')

		#loop thru profiles (features)
		profileCnt=self.PH.ProfileCount()
		#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'ProfileCnt:{0} AttrCnt:{1}'.format(profileCnt, attrCnt))
		for i in range(profileCnt):

			pnts = self.PH.GetPoints(i)
			dists =self.PH.GetDistances(i)

			#write coordinates and distance
			for j in range(len(pnts)):

				#exportId
				txt.write('{0}{1}'.format(i+1, self.Separator))

				#write attributes
				if attrCnt >0 :
					attribs=self.PH.GetAttributes(i)
					for(fld,fldVal)in attribs.iteritems():
						#QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Fld[{0}]:{1}'.format(fld.name(), fldVal.toString()))
						txt.write('{0}{1}'.format(fldVal.toString()).replace('.', self.Delimiter), self.Separator)
				txt.write('{0}{3}{1}{3}{2}{3}'.format( pnts[j].x(),pnts[j].y(),dists[j], self.Separator).replace('.', self.Delimiter))

				#write rastervalues
				for k in range(self.PH.RasterCount(i)):
					rasterVals=self.PH.GetRasterVals(i,k)
					z=rasterVals[j]
					txt.write('{0}{1}'.format(z, self.Separator).replace('.', self.Delimiter))

				txt.write('\r\n')


		txt.close()
		QMessageBox.information(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Datei erfolgreich gespeichert! [' + self.FileName + ']')
#		except Exception as ex:
#			QMessageBox.warning(self.Interface.mainWindow(), "VoGIS-Profiltool", 'Unerwarteter Fehler: ' + str(ex) )

