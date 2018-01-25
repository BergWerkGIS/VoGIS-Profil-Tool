# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsMessageLog

from VoGisProfilTool.bo.settings import enumVertexType


class Vertex:

    def __init__(self,
                 fields,
                 attribMap,
                 vertexType,
                 x,
                 y,
                 profileId,
                 lyrId,
                 featureId,
                 segmentId,
                 vertexId,
                 distanceProfile,
                 distanceSegment,
                 zvals,
                 nodata_value=-9999,
                 raster_nodata=None,
                 ):
        self.attribNames = []
        self.attributes = []
        for k in range(len(attribMap)):
            if fields is not None:
                self.attribNames.append(fields[k].name())
            self.attributes.append(attribMap[k])

        self.vertexType = vertexType
        self.x = x
        self.y = y
        self.profileId = profileId
        self.lyrId = lyrId
        self.featureId = featureId
        self.segmentId = segmentId
        self.vertexId = vertexId
        self.distanceProfile = distanceProfile
        self.distanceSegment = distanceSegment
        self.zvals = zvals
        self.nodata_value = nodata_value
        self.raster_nodata = raster_nodata

    def toString(self, hekto, attribs, delimiter, decimalDelimiter):
        #dirty HACK! toString() replace, um unabhaengig von LOCALE Dezimaltrenner setzen zu können
        txt = '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}{0}{9}'.format(delimiter,
                                                                           ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(self.distanceSegment)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                                           self.__getZVals(delimiter, decimalDelimiter),
                                                                           self.profileId,
                                                                           self.segmentId,
                                                                           self.vertexId,
                                                                           self.getType()
                                                                           )
        if hekto is True:
            txt += self.__getHekto(delimiter, decimalDelimiter)
        if attribs is True:
            txt += self.__getAttribs(delimiter, decimalDelimiter)
        return txt

    def toString2(self, hekto, attribs, distanceSegment, segmentId, delimiter, decimalDelimiter):
        """Ersten Vertex eines Segments als letzten des vorigen ausgeben"""
        #dirty HACK! toString() replace, um unabhaengig von LOCALE Dezimaltrenner setzen zu können
        txt = '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}{0}{9}'.format(delimiter,
                                                                           ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(distanceSegment)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                                           ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                                           self.__getZVals(delimiter, decimalDelimiter),
                                                                           self.profileId,
                                                                           segmentId,
                                                                           self.vertexId,
                                                                           self.getType()
                                                                           )
        if hekto is True:
            txt += self.__getHekto(delimiter, decimalDelimiter)
        if attribs is True:
            txt += self.__getAttribs(delimiter, decimalDelimiter)
        return txt

    def toArray(self, hekto, attribs, decimalDelimiter):
        """ Fuer die Weiterverarbeitung im Excel-Writer        """
        feld = []
        feld.append(self.distanceProfile)
        feld.append(self.distanceSegment)
        feld.append(self.x)
        feld.append(self.y)
        zVals = self.getZVals()
        for zVal in zVals:
            feld.append(zVal)
        feld.append(self.profileId)
        feld.append(self.segmentId)
        feld.append(self.vertexId)
        feld.append(self.getType())

        if hekto is True:
            feld.append(self.getHekto(decimalDelimiter))
        if attribs is True:
            attribute = self.getAttributeVals()
            for attribut in attribute:
                feld.append(attribut)

        return feld

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        #profillaenge, rechtswert, hochwert hoehe
        for rVal in self.zvals:
            acadTxt += '{1}{0}{2}{0}{3}{0}{4}'.format(delimiter,
                                                      ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                      ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                      ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                      ('' if rVal is None else '{0:.2f}'.format(rVal)).replace('.', decimalDelimiter),
                                                      )
            #acadTxt += os.linesep
            acadTxt += '\n'
        return acadTxt

    def __getAttribs(self, delimiter, decimalDelimiter):
        """internal: for text output"""
        aTxt = ''
        for a in self.attributes:
            if isinstance(a, QVariant):
                a2 = str(a)
            else:
                a2 = a
            #if isinstance(a2, (int, long, float, complex)):
            if isinstance(a2, (long, float, complex)):
                aTxt += ('{0}{1:.2f}'.format(delimiter, a2)).replace('.', decimalDelimiter)
            else:
                aTxt += '{0}{1}'.format(delimiter, a2)
        return aTxt

    def getAttributeVals(self):
        """for writing to shapefile"""
        attribs = []
        for a in self.attributes:
            if isinstance(a, QVariant):
                a2 = str(a)
            else:
                a2 = a
            #if isinstance(a2, (int, long, float, complex)):
            if isinstance(a2, float):
                attribs.append(round(a2, 3))
            elif isinstance(a2, (long, float, complex)):
                attribs.append(a2)
            else:
                attribs.append(a2)
        return attribs

    def getType(self):
        vType = ''
        if self.vertexType == enumVertexType.node:
            vType = 'K'
        elif self.vertexType == enumVertexType.vertex:
            vType = 'S'
        else:
            vType = 'P'
        return vType

    def __getHekto(self, delimiter, decimalDelimiter):
        """Fuer Textausgabe"""
        hm = ('{0}hm {1:.2f}'.format(delimiter, self.distanceProfile / 100)).replace('.', decimalDelimiter)
        return hm

    def getHekto(self, decimalDelimiter):
        """Fuer Shapeausgabe"""
        hm = ('hm {0:.2f}'.format(self.distanceProfile / 100)).replace('.', decimalDelimiter)
        return hm

    def getZVals(self):
        z = []
        if len(self.zvals) > 0:
            for zVal in self.zvals:
                if zVal is None:
                    z.append("" if self.nodata_value is None else str(self.nodata_value))
                else:
                    z.append(zVal)
        return z

    def __getZVals(self, delimiter, decimalDelimiter):
        z = ''
        if len(self.zvals) > 0:
            valCnter = 1
            for zVal in self.zvals:
                if zVal is None:
                    z += "" if self.nodata_value is None else str(self.nodata_value)
                else:
                    z += ('{0:.2f}'.format(zVal)).replace('.', decimalDelimiter)
                if valCnter < len(self.zvals):
                    z += delimiter
                valCnter += 1
        return z
