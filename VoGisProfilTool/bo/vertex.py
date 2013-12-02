# -*- coding: utf-8 -*-

import os
import unicodedata
from PyQt4.QtCore import QVariant
from settings import enumVertexType
from qgis.core import QGis
from qgis.core import QgsMessageLog


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
                 zvals
                 ):
        self.attribNames = []
        self.attributes = []
        if QGis.QGIS_VERSION_INT < 10900:
            for (k, attr) in attribMap.iteritems():
                #QgsMessageLog.logMessage('new Vextex: {0}:{1}'.format(k, attr.toString()), 'VoGis')
                if fields is not None:
                    self.attribNames.append(fields[k].name())
                self.attributes.append(attr)
        else:
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

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        #profillaenge, rechtswert, hochwert hoehe
        for rVal in self.zvals:
            acadTxt += '{1}{0}{2}{0}{3}{0}{4}'.format(delimiter,
                                                      ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                      ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                      ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                      ('{0:.2f}'.format(rVal)).replace('.', decimalDelimiter),
                                                      )
            #acadTxt += os.linesep
            acadTxt += '\n'
        return acadTxt

    def __getAttribs(self, delimiter, decimalDelimiter):
        """internal: for text output"""
        aTxt = ''
        for a in self.attributes:
            if isinstance(a, QVariant):
                a2 = a.toPyObject()
            else:
                a2 = a
            #if isinstance(a2, (int, long, float, complex)):
            if isinstance(a2, (long, float, complex)):
                aTxt += ('{0}{1:.2f}'.format(delimiter, a2)).replace('.', decimalDelimiter)
            else:
                aTxt += '{0}{1}'.format(delimiter, unicodedata.normalize('NFKD', unicode(a2)).encode('ascii', 'ignore'))
        return aTxt

    def getAttributeVals(self):
        """for writing to shapefile"""
        attribs = []
        for a in self.attributes:
            if isinstance(a, QVariant):
                a2 = a.toPyObject()
            else:
                a2 = a
            #if isinstance(a2, (int, long, float, complex)):
            if isinstance(a2, float):
                attribs.append(round(a2, 3))
            elif isinstance(a2, (long, float, complex)):
                attribs.append(a2)
            else:
                attribs.append(unicodedata.normalize('NFKD', unicode(a2)).encode('ascii', 'ignore'))
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

    def __getZVals(self, delimiter, decimalDelimiter):
        z = ''
        if len(self.zvals) > 0:
            valCnter = 1
            for zVal in self.zvals:
                if zVal is None:
                    z += '-9999'
                else:
                    z += ('{0:.2f}'.format(zVal)).replace('.', decimalDelimiter)
                if valCnter < len(self.zvals):
                    z += delimiter
                valCnter += 1
        return z
