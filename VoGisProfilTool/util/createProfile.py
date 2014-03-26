# -*- coding: utf-8 -*-

try:
    from shapely.wkb import loads
    from shapely.wkb import dumps
    from shapely.geometry import Point
    import shapely.geos
except ImportError:
    pass
except:
    pass
from ..bo.settings import enumModeLine
from ..bo.settings import enumModeVertices
from ..bo.settings import enumVertexType
#from bo.line import Line
from ..bo.profile import Profile
from ..bo.segment import Segment
from ..bo.vertex import Vertex
from u import Util
#from bo.zVal import ZVal
from qgis.core import *
from math import *
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QApplication
#if QGis.QGIS_VERSION_INT >= 10900:
#    import processing


class CreateProfile:

    def __init__(self, interface, settings):
        self.iface = interface
        self.settings = settings

    def create(self):

        profiles = []

        #Line aus den Textboxwerten erstellen
        if self.settings.modeLine == enumModeLine.straightLine:
            profiles.append(self.processFeature(None,
                                                1,
                                                1,
                                                self.settings.mapData.customLine
                                                )
                            )
            return profiles

        #Line aus gezeichneter Linie erstellen
        if self.settings.modeLine == enumModeLine.customLine:
            profiles.append(self.processFeature(None,
                                                1,
                                                1,
                                                self.settings.mapData.customLine
                                                )
                            )
            return profiles

        #Shapefile Geometrien abarbeiten
        if self.settings.modeLine == enumModeLine.line:

            #feat = QgsFeature()
            #if self.settings.onlySelectedFeatures is True:
            #    for feat in self.settings.mapData.selectedLineLyr.line.selectedFeatures():
            #        profiles.append(self.processFeature(len(profiles) + 1,
            #                                            self.settings.mapData.selectedLineLyr.line.id(),
            #                                            feat
            #                                            )
            #                        )
            #else:
            #    provider = self.settings.mapData.selectedLineLyr.line.dataProvider()
            #    attrIndices = provider.attributeIndexes()
            #    provider.select(attrIndices)
            #    while (provider.nextFeature(feat)):
            #        #QgsMessageLog.logMessage(str(self.settings.mapData.selectedLineLyr.line.id()), 'VoGis')
            #        profiles.append(self.processFeature(len(profiles) + 1,
            #                                            self.settings.mapData.selectedLineLyr.line.id(),
            #                                            feat
            #                                            )
            #                        )

            provider = self.settings.mapData.selectedLineLyr.line.dataProvider()
            feats = []

            #Alle Attribute holen
            if QGis.QGIS_VERSION_INT < 10900: provider.select(provider.attributeIndexes())

            if self.settings.onlySelectedFeatures is True:
                feats = self.settings.mapData.selectedLineLyr.line.selectedFeatures()
            else:
                if QGis.QGIS_VERSION_INT < 10900:
                    attrIndices = provider.attributeIndexes()
                    provider.select(attrIndices)
                    feat = QgsFeature()
                    while (provider.nextFeature(feat)):
                        #geom = feat.geometry()
                        #QgsMessageLog.logMessage( 'isMultipart: {0}'.format(str(geom.isMultipart())), 'VoGis')
                        #attrs = feat.attributeMap()
                        # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
                        # show all attributes and their values
                        #for (k, attr) in feat.attributeMap().iteritems():
                        #    QgsMessageLog.logMessage('{0}: {1}'.format(k, attr.toString()), 'VoGis')
                        feats.append(feat)
                        #neues Feature verwenden, weil sonst die Multiparts
                        #nicht als solche erkannt werden
                        feat = QgsFeature()
                else:
                    QgsMessageLog.logMessage('PROVIDER SELECT', 'VoGis')
                    #processing.getfeatures: This will iterate over all the features in the layer, in case there is no selection, or over the selected features otherwise.
                    #obviously not available with windows standalone installer
                    #features = processing.getfeatures(self.settings.mapData.selectedLineLyr.line)
                    features = self.settings.mapData.selectedLineLyr.line.getFeatures()
                    for feat in features:
                        feats.append(feat)

            #for feat in feats:
            #    if feat.isValid() is False:
            #        return []

            ut = Util(self.iface)
            feats, err_msg = ut.prepareFeatures(self.settings, provider, feats)

            if not err_msg is None:
                #QMessageBox.critical(self.iface.mainWindow(), "VoGIS-Profiltool", err_msg)
                QMessageBox.critical(self.iface.mainWindow(), 'PREPARE ERROR', err_msg)
                return []

            for f in feats:
                geom = f.geometry()
                if geom.isMultipart():
                    msg = QApplication.translate('code', 'Multipart Feature vorhanden! Option zum Explodieren verwenden.', None, QApplication.UnicodeUTF8)
                    QMessageBox.warning(self.iface.mainWindow(), "VoGIS-Profiltool", msg)
                    return profiles

            featCnt = len(feats)
            for idx, feat in enumerate(feats):
                #QGIS 2.0 http://gis.stackexchange.com/a/58754 http://gis.stackexchange.com/a/57090
                #http://acaciaecho.wordpress.com/2011/01/11/pyqtprogressbar/
                self.iface.mainWindow().statusBar().showMessage('VoGIS-Profiltool, Element: {0}/{1}'.format(idx, featCnt))
                profiles.append(self.processFeature(provider.fields(),
                                                    len(profiles) + 1,
                                                    self.settings.mapData.selectedLineLyr.line.id(),
                                                    feat
                                                    )
                                )

        #QGIS 2.0 http://gis.stackexchange.com/a/58754 http://gis.stackexchange.com/a/57090
        self.iface.mainWindow().statusBar().showMessage('VoGIS-Profiltool, {0} Profile'.format(len(profiles)))
        return profiles

    def processFeature(self, fields, profileId, layerId, feat):

        #QgsMessageLog.logMessage('processFeature', 'VoGis')
        geom = feat.geometry()
        if QGis.QGIS_VERSION_INT < 10900:
            segments = self.processVertices(fields, feat.attributeMap(), profileId, geom, layerId, feat.id())
        else:
            segments = self.processVertices(fields, feat.attributes(), profileId, geom, layerId, feat.id())

        return Profile(profileId, segments)

    def processVertices(self, fields, attribMap, profileId, qgGeom, layerId, featId):

        #QgsMessageLog.logMessage('{0}: {1}'.format('processFeature',attribMap), 'VoGis')

        step = -1
        segmentCnter = 1
        segments = []
        segmentvertices = []
        distSegment = 0
        distTotal = 0
        qgPntOld = None
        vtxType = None
        vtxId = 1

        qgLineVertices = qgGeom.asPolyline()
        shplyGeom = loads(qgGeom.asWkb())
        shplyVertices = []
        #for shplyV in shplyGeom.coords:
        for idxV in range(1, len(shplyGeom.coords) - 1):
            #shplyVertices.append(Point(shplyV[0], shplyV[1]))
            shplyVertices.append(Point(shplyGeom.coords[idxV][0], shplyGeom.coords[idxV][1]))

        if self.settings.modeVertices == enumModeVertices.equiDistant:
            step = self.settings.equiDistance
        else:
            step = shplyGeom.length / (self.settings.vertexCnt - 1)

        #erster, echter Punkt der Geometrie
        qgPntOld = qgLineVertices[0]
        vtxType = enumVertexType.node
        newVtx = Vertex(fields,
                        attribMap,
                        vtxType,
                        qgLineVertices[0].x(),
                        qgLineVertices[0].y(),
                        profileId,
                        layerId,
                        featId,
                        segmentCnter,
                        vtxId,
                        distTotal,
                        distSegment,
                        self.__getValsAtPoint(qgLineVertices[0])
                        )
        segmentvertices.append(newVtx)

        #QgsMessageLog.logMessage('GeomLength:' + str(shplyGeom.length), 'VoGis')

        while distTotal < shplyGeom.length:

            distSegment += step
            distTotal += step

            #überprüfen, ob echter Vertex zwischen den
            # zu berechnenden Ṕrofilpunkten liegt
            #nur falls diese auch ausgegeben werden sollen
            if self.settings.nodesAndVertices is True:
                if distTotal > 0:
                    prevDist = distTotal - step
                    for v in shplyVertices:
                        vDist = shplyGeom.project(v)
                        if vDist > prevDist and vDist < distTotal:
                            qgPnt = self.__qgPntFromShplyPnt(v)
                            distQgVertices = sqrt(qgPnt.sqrDist(qgPntOld))
                            vtxType = enumVertexType.vertex
                            vtxId += 1
                            newVtx = Vertex(fields,
                                            attribMap,
                                            vtxType,
                                            v.x,
                                            v.y,
                                            profileId,
                                            layerId,
                                            featId,
                                            segmentCnter,
                                            vtxId,
                                            vDist,
                                            distQgVertices,
                                            self.__getValsAtPoint(qgPnt)
                                            )
                            segmentvertices.append(newVtx)
                            segments.append(Segment(segmentCnter, segmentvertices))
                            #neues Segment beginnen
                            qgPntOld = self.__qgPntFromShplyPnt(v)
                            segmentvertices = []
                            distSegment -= distQgVertices
                            segmentCnter += 1

            #Profilpunkte berechnen
            #nur wenn noch unter Featurelaenge
            if distTotal < shplyGeom.length:
                shplyPnt = shplyGeom.interpolate(distTotal, False)
                vtxType = enumVertexType.point
                vtxId += 1
                newVtx = Vertex(fields,
                                attribMap,
                                vtxType,
                                shplyPnt.x,
                                shplyPnt.y,
                                profileId,
                                layerId,
                                featId,
                                segmentCnter,
                                vtxId,
                                distTotal,
                                distSegment,
                                self.__getValsAtPoint(self.__qgPntFromShplyPnt(shplyPnt))
                                )
                segmentvertices.append(newVtx)

        #letzter, echter Punkt der Geometrie
        qgLastPnt = qgLineVertices[len(qgLineVertices)-1]
        #keine echten Knoten, nur berechnete -> letzter Pkt entspricht kompletter Laenge der Geometrie
        if self.settings.nodesAndVertices is False:
            distSegment = shplyGeom.length
        else:
            distSegment = sqrt(qgLastPnt.sqrDist(qgPntOld))
        vtxType = enumVertexType.node
        vtxId += 1
        newVtx = Vertex(fields,
                        attribMap,
                        vtxType,
                        qgLastPnt.x(),
                        qgLastPnt.y(),
                        profileId,
                        layerId,
                        featId,
                        segmentCnter,
                        vtxId,
                        shplyGeom.length,
                        distSegment,
                        self.__getValsAtPoint(qgLastPnt)
                        )
        segmentvertices.append(newVtx)
        segments.append(Segment(segmentCnter, segmentvertices))

        return segments

    def __qgPntFromShplyPnt(self, shapelyPnt):
        wkbPnt = dumps(shapelyPnt)
        qgGeom = QgsGeometry()
        qgGeom.fromWkb(wkbPnt)
        return qgGeom.asPoint()

    def __getValsAtPoint(self, pnt):

        vals = []

        for rObj in self.settings.mapData.rasters.selectedRasters():

            raster = rObj.grid

            #TODO!!!! QGIS BUG: QGIS 2.0.1: raster.noDataValue() = > AttributeError: 'QgsRasterLayer' object has no attribute 'noDataValue'
            if QGis.QGIS_VERSION_INT < 10900:
                noDataVal, validNoData = raster.noDataValue()
                if validNoData:
                    rasterVal = noDataVal
                else:
                    #rasterVal = float('nan')
                    rasterVal = -9999
            else:
                rasterVal = -9999

            #QgsMessageLog.logMessage('rasterVal VOR identify:' + str(rasterVal), 'VoGis')

            #check if coordinate systems match
            if self.settings.modeLine == enumModeLine.line:
                if raster.crs() != self.settings.mapData.selectedLineLyr.line.crs():
                    transform = QgsCoordinateTransform(self.settings.mapData.selectedLineLyr.line.crs(),
                                                       raster.crs()
                                                       )
                    pnt = transform.transform(pnt)
            else:
                if raster.crs() != self.iface.mapCanvas().mapRenderer().destinationCrs():
                    transform = QgsCoordinateTransform(self.iface.mapCanvas().mapRenderer().destinationCrs(),
                                                       raster.crs()
                                                       )
                    pnt = transform.transform(pnt)

            #QgsMessageLog.logMessage(str(pnt), 'VoGis')

            if QGis.QGIS_VERSION_INT < 10900:
                result, identifyDic = raster.identify(pnt)
                if result:
                    for bandName, pixelValue in identifyDic.iteritems():
                        #QgsMessageLog.logMessage('bandName:' + str(bandName), 'VoGis')
                        if str(bandName) == raster.bandName(1):
                            try:
                                #QgsMessageLog.logMessage('pixelValue:' + str(pixelValue), 'VoGis')
                                rasterVal = float(pixelValue)
                            except ValueError:
                                #float('nan') #0
                                rasterVal = -9999
                                pass
            else:
                identifyResult = raster.dataProvider().identify(pnt, 1)
                for bndNr, pixVal in identifyResult.results().iteritems():
                    if 1 == bndNr:
                        try:
                            rasterVal = float(pixVal)
                        #except ValueError:
                        except:
                            QgsMessageLog.logMessage('pixVal Exception: ' + str(pixVal), 'VoGis')
                            rasterVal = -9999
                            pass

            #QgsMessageLog.logMessage('rasterVal NACH identify:' + str(rasterVal), 'VoGis')

            vals.append(rasterVal)

        #QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", str(vals))
        return vals
