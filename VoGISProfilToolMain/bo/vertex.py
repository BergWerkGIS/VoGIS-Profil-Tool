# -*- coding: utf-8 -*-

from settings import enumVertexType


class Vertex:

    def __init__(self,
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

    def toString(self, delimiter, decimalDelimiter):
        #dirty HACK! toString() replace, um unabhaengig von LOCALE Dezimaltrenner setzen zu können
        txt = '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}'.format(delimiter,
                                                                     ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(self.distanceSegment)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                                     self.__getZVals(delimiter, decimalDelimiter),
                                                                     self.profileId,
                                                                     self.segmentId,
                                                                     self.vertexId
                                                                     )
        return self.__appendType(txt, delimiter, decimalDelimiter)

    def toString2(self, distanceSegment, segmentId, delimiter, decimalDelimiter):
        #dirty HACK! toString() replace, um unabhaengig von LOCALE Dezimaltrenner setzen zu können
        txt = '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}'.format(delimiter,
                                                                     ('{0:.2f}'.format(self.distanceProfile)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(distanceSegment)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(self.x)).replace('.', decimalDelimiter),
                                                                     ('{0:.2f}'.format(self.y)).replace('.', decimalDelimiter),
                                                                     self.__getZVals(delimiter, decimalDelimiter),
                                                                     self.profileId,
                                                                     segmentId,
                                                                     self.vertexId
                                                                     )
        return self.__appendType(txt, delimiter, decimalDelimiter)

    def __appendType(self, txt, delimiter, decimalDelimiter):
        hm = ('{0}hm {1:.2f}'.format(delimiter, self.distanceProfile / 100)).replace('.', decimalDelimiter)
        if self.vertexType == enumVertexType.node:
            txt += '{0}K'.format(delimiter) + hm
        elif self.vertexType == enumVertexType.vertex:
            txt += '{0}S'.format(delimiter) + hm
        else:
            txt += '{0}P'.format(delimiter) + hm
        return txt

    def __getZVals(self, delimiter, decimalDelimiter):
        z = ''
        if len(self.zvals) > 0:
            valCnter = 1
            for zVal in self.zvals:
                if zVal is None:
                    z += '-9999'
                else:
                    z += str(zVal).replace('.', decimalDelimiter)
                if valCnter < len(self.zvals):
                    z += delimiter
                valCnter += 1
        return z
