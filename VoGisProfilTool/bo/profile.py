#from qgis.core import QgsMessageLog
from plotExtent import PlotExtent
#import itertools
from PyQt4.QtGui import *
import os


class Profile:

    def __init__(self, id, segments):
        self.id = id
        self.segments = segments

    def getExtent(self):
        #always 0: distance
        xmin = 0
        xmax = -99999
        ymin = 99999
        ymax = -99999
        for s in self.segments:
            for v in s.vertices:
                if xmax < v.distanceProfile:
                    xmax = v.distanceProfile
                for z in v.zvals:
                    if ymin > z:
                        ymin = z
                    if ymax < z:
                        ymax = z
                    #QgsMessageLog.logMessage('z:{0} ymin:{1} ymax:{2}'.format(z, ymin, ymax), 'VoGis')
        return PlotExtent(xmin, ymin, xmax, ymax)

    def getPlotSegments(self):
        # x = []
        # pltSegs = []
        # for s in self.segments:
        #     for v in s.vertices:
        #         #QgsMessageLog.logMessage('zvals: {0}'.format(v.zvals), 'VoGis')
        #         x.append(v.distanceProfile)
        #         pltSegs.append(list(zip(itertools.repeat(v.distanceProfile, len(v.zvals)), v.zvals)))
        # return x, pltSegs
        #one segement for each DHM
        pltSegs = []
        zCnt = len(self.segments[0].vertices[0].zvals)
        for idx in range(zCnt):
            pltSeg = []
            for s in self.segments:
                for v in s.vertices:
                    #!!!double parentheses!!! -> tuples
                    pltSeg.append((v.distanceProfile, v.zvals[idx]))
            pltSegs.append(pltSeg)
        return pltSegs

    def writeHeader(self, selectedRasters, hekto, attribs, delimiter):
        #Profillaenge;Segmentlaenge;Rechtswert;Hochwert;
        #"Laser - Hoehenmodell Oberflaeche 1m";"Laser Hoehenmodell Gelaende1m";
        #Profilnummer;Segmentnummer;Punktnummer;Punktklasse;
        #Hektometer
        #ATTRIBUTE
        hdr_prof_len = QApplication.translate('code', 'Profillaenge', None, QApplication.UnicodeUTF8)
        hdr_seg_len = QApplication.translate('code', 'Segmentlaenge', None, QApplication.UnicodeUTF8)
        hdr_xval = QApplication.translate('code', 'Rechtswert', None, QApplication.UnicodeUTF8)
        hdr_yval = QApplication.translate('code', 'Hochwert', None, QApplication.UnicodeUTF8)
        hdr_prof_nr = QApplication.translate('code', 'Profilnummer', None, QApplication.UnicodeUTF8)
        hdr_seg_nr = QApplication.translate('code', 'Segmentnummer', None, QApplication.UnicodeUTF8)
        hdr_pnt_nr = QApplication.translate('code', 'Punktnummer', None, QApplication.UnicodeUTF8)
        hdr_pnt_class = QApplication.translate('code', 'Punktklasse', None, QApplication.UnicodeUTF8)
        hdr = '{1}{0}{2}{0}{3}{0}{4}'.format(delimiter, hdr_prof_len, hdr_seg_len, hdr_xval, hdr_yval)
        for r in selectedRasters:
            hdr += '{0}"{1}"'.format(delimiter, r.name)
        hdr += '{0}{1}{0}{2}{0}{3}{0}{4}'.format(delimiter, hdr_prof_nr, hdr_seg_nr, hdr_pnt_nr, hdr_pnt_class)
        if hekto is True:
            hdr += '{0}{1}'.format(delimiter, 'Hektometer')
        if attribs is True:
            for fldName in self.segments[0].vertices[0].attribNames:
                hdr += '{0}{1}'.format(delimiter, fldName)
        #hdr += '\r\n'
        #hdr += os.linesep
        hdr += '\n'
        return hdr

    def toString(self, hekto, attribs, delimiter, decimalDelimiter):

        txt = ''
        oldSeg = None

        for idxS in range(len(self.segments)):
            s = self.segments[idxS]
            #letzten Punkt des vorigen Segements zusaetzliche als ersten Punkt
            #des neuen Segemnts schreiben
            if oldSeg is not None:
                txt += '{0}'.format(oldSeg.toStringLastVertex(hekto,
                                                              attribs,
                                                              s.id,
                                                              delimiter,
                                                              decimalDelimiter
                                                              ))
            txt += '{0}'.format(s.toString(hekto,
                                           attribs,
                                           delimiter,
                                           decimalDelimiter
                                           ))
            oldSeg = s

        return txt

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        for s in self.segments:
            acadTxt += s.toACadTxt(delimiter, decimalDelimiter)
        return acadTxt
