#from qgis.core import QgsMessageLog

import os
#import itertools

from qgis.PyQt.QtWidgets import QApplication
from VoGisProfilTool.bo.plotExtent import PlotExtent


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
                    if z == v.nodata_value or z in v.raster_nodata:
                        continue
                    if ymin > z:
                        ymin = z
                    if ymax < z:
                        ymax = z
                    #QgsMessageLog.logMessage('z:{0} ymin:{1} ymax:{2}'.format(z, ymin, ymax), 'VoGis', Qgis.Info)
        return PlotExtent(xmin, ymin, xmax, ymax)

    def getPlotSegments(self):
        # x = []
        # pltSegs = []
        # for s in self.segments:
        #     for v in s.vertices:
        #         #QgsMessageLog.logMessage('zvals: {0}'.format(v.zvals), 'VoGis', Qgis.Info)
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
                    z = v.zvals[idx]
                    if z == v.nodata_value or z in v.raster_nodata:
                        z = None
                    #!!!double parentheses!!! -> tuples
                    pltSeg.append((v.distanceProfile, z))
            pltSegs.append(pltSeg)
        return pltSegs

    def writeHeader(self, selectedRasters, hekto, attribs, delimiter):
        #Profillaenge;Segmentlaenge;Rechtswert;Hochwert;
        #"Laser - Hoehenmodell Oberflaeche 1m";"Laser Hoehenmodell Gelaende1m";
        #Profilnummer;Segmentnummer;Punktnummer;Punktklasse;
        #Hektometer
        #ATTRIBUTE
        hdr_prof_len = QApplication.translate('code', 'Profillaenge')
        hdr_seg_len = QApplication.translate('code', 'Segmentlaenge')
        hdr_xval = QApplication.translate('code', 'Rechtswert')
        hdr_yval = QApplication.translate('code', 'Hochwert')
        hdr_prof_nr = QApplication.translate('code', 'Profilnummer')
        hdr_seg_nr = QApplication.translate('code', 'Segmentnummer')
        hdr_pnt_nr = QApplication.translate('code', 'Punktnummer')
        hdr_pnt_class = QApplication.translate('code', 'Punktklasse')
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

    def toArray(self, hekto, attribs, decimalDelimiter):
        """ Fuer die Weiterverarbeitung im Excel-Writer        """
        feld = []
        oldSeg = None
        for idxS in range(len(self.segments)):
            s = self.segments[idxS]
            if oldSeg is not None:
                feld.append(oldSeg.toArray(hekto, attribs, decimalDelimiter))

            feld.append(s.toArray(hekto, attribs, decimalDelimiter))
            oldSeg = s

        return feld

    def writeArrayHeader(self, selectedRasters, hekto, attribs):
        """ Kopfzeile fuer Excel        """
        #Profillaenge;Segmentlaenge;Rechtswert;Hochwert;
        #"Laser - Hoehenmodell Oberflaeche 1m";"Laser Hoehenmodell Gelaende1m";
        #Profilnummer;Segmentnummer;Punktnummer;Punktklasse;
        #Hektometer
        #ATTRIBUTE
        hdr_prof_len = QApplication.translate('code', 'Profillaenge')
        hdr_seg_len = QApplication.translate('code', 'Segmentlaenge')
        hdr_xval = QApplication.translate('code', 'Rechtswert')
        hdr_yval = QApplication.translate('code', 'Hochwert')
        hdr_prof_nr = QApplication.translate('code', 'Profilnummer')
        hdr_seg_nr = QApplication.translate('code', 'Segmentnummer')
        hdr_pnt_nr = QApplication.translate('code', 'Punktnummer')
        hdr_pnt_class = QApplication.translate('code', 'Punktklasse')

        hdr = []
        hdr.append(hdr_prof_len)
        hdr.append(hdr_seg_len)
        hdr.append(hdr_xval)
        hdr.append(hdr_yval)
        for r in selectedRasters:
            hdr.append(r.name)
        hdr.append(hdr_prof_nr)
        hdr.append(hdr_seg_nr)
        hdr.append(hdr_pnt_nr)
        hdr.append(hdr_pnt_class)
        if hekto is True:
            hdr.append('Hektometer')
        if attribs is True:
            for fldName in self.segments[0].vertices[0].attribNames:
                hdr.append(fldName)
        return hdr

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        for s in self.segments:
            acadTxt += s.toACadTxt(delimiter, decimalDelimiter)
        return acadTxt
