#-*- coding: UTF-8 -*-

# coding: iso-8859-15

from PyQt4.QtGui import *
import re

class util:

	@staticmethod
	def stripUmlauts(interface, txt):

		#case insensitve replace of umlauts does not work??
		#wrong regex??
		#QMessageBox.warning(interface.mainWindow(), "VoGIS-Profiltool", txt)
		txt = re.sub( u'(?i)ä', 'ae', txt )
		txt = re.sub( u'(?i)Ä', 'AE', txt )
		#QMessageBox.warning(interface.mainWindow(), "VoGIS-Profiltool", txt)
		txt = re.sub( u'(?i)ö', 'oe', txt )
		txt = re.sub( u'(?i)Ö', 'OE', txt )
		#QMessageBox.warning(interface.mainWindow(), "VoGIS-Profiltool", txt)
		txt = re.sub( u'(?i)ü', 'ue', txt )
		txt = re.sub( u'(?i)Ü', 'UE', txt )
		#QMessageBox.warning(interface.mainWindow(), "VoGIS-Profiltool", txt)
		txt = re.sub( u'(?i)ß', 'ss', txt )
		#QMessageBox.warning(interface.mainWindow(), "VoGIS-Profiltool", txt)

		return txt



	@staticmethod
	def getDelimiter(interface):

		delimiters = [',','.']
		delim, ok = QInputDialog.getItem(interface.mainWindow(), "Dezimaltrenner?", u"Dezimaltrenner wählen", delimiters, True)
		if ok :
			return delim
		else:
			return ''
