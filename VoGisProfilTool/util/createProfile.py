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
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal
import traceback
#if QGis.QGIS_VERSION_INT >= 10900:
#    import processing


class CreateProfile(QObject):

    def __init__(self, interface, settings):
        QObject.__init__(self)
        self.iface = interface
        self.settings = settings
        self.stop = False


    def abort(self):
        self.stop = True


    finished = pyqtSignal(object)
    error = pyqtSignal(basestring)
    progress = pyqtSignal(basestring)


    def create(self):

        profiles = []

        try:
            #Line aus den Textboxwerten erstellen
            if self.settings.modeLine == enumModeLine.straightLine:
                profiles.append(self.processFeature(None,
                                                    1,
                                                    1,
                                                    self.settings.mapData.customLine
                                                    )
                                )
                self.finished.emit(profiles)
                return

            #Line aus gezeichneter Linie erstellen
            if self.settings.modeLine == enumModeLine.customLine:
                profiles.append(self.processFeature(None,
                                                    1,
                                                    1,
                                                    self.settings.mapData.customLine
                                                    )
                                )
                self.finished.emit(profiles)
                return

            #Shapefile Geometrien abarbeiten
            if self.settings.modeLine == enumModeLine.line:

                provider = self.settings.mapData.selectedLineLyr.line.dataProvider()
                feats = []

                #Alle Attribute holen
                if QGis.QGIS_VERSION_INT < 10900:
                    provider.select(provider.attributeIndexes())

                if self.settings.onlySelectedFeatures is True:
                    feats = self.settings.mapData.selectedLineLyr.line.selectedFeatures()
                else:
                    if QGis.QGIS_VERSION_INT < 10900:
                        attrib_indices = provider.attributeIndexes()
                        provider.select(attrib_indices)
                        feat = QgsFeature()
                        while provider.nextFeature(feat):
                            feats.append(feat)
                            #neues Feature verwenden, weil sonst die Multiparts
                            #nicht als solche erkannt werden
                            feat = QgsFeature()
                    else:
                        #processing.getfeatures: This will iterate over all the features in the layer, in case there is no selection, or over the selected features otherwise.
                        #obviously not available with windows standalone installer
                        #features = processing.getfeatures(self.settings.mapData.selectedLineLyr.line)
                        features = self.settings.mapData.selectedLineLyr.line.getFeatures()
                        for feat in features:
                            feats.append(feat)

                util = Util(self.iface)
                feats, err_msg = util.prepareFeatures(self.settings, provider, feats)

                if not err_msg is None:
                    #QMessageBox.critical(self.iface.mainWindow(), 'PREPARE ERROR', err_msg)
                    self.error.emit(err_msg)
                    self.finished.emit([])
                    return

                for feat in feats:
                    geom = feat.geometry()
                    if geom.isMultipart():
                        msg = QApplication.translate('code', 'Multipart Feature vorhanden! Option zum Explodieren verwenden.', None, QApplication.UnicodeUTF8)
                        self.error.emit(msg)
                        self.finished.emit([])
                        return

                feat_cnt = len(feats)
                for idx, feat in enumerate(feats):
                    if self.stop is True:
                        profiles = []
                        break
                    if idx == 0 or idx % 5 == 0:
                        msg = 'Profil {0}/{1}'.format(idx+1, feat_cnt)
                        self.progress.emit(msg)
                    profiles.append(self.processFeature(provider.fields(),
                                                        len(profiles) + 1,
                                                        self.settings.mapData.selectedLineLyr.line.id(),
                                                        feat
                                                        )
                                    )
                msg = 'Profil {0}/{1}'.format(idx+1, feat_cnt)
                self.progress.emit(msg)

            self.finished.emit(profiles)
        except Exception, ex:
            self.error.emit(traceback.format_exc())
            self.finished.emit(profiles)

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
                        self.__getValsAtPoint(qgLineVertices[0]),
                        self.settings.nodata_value
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
                                            self.__getValsAtPoint(qgPnt),
                                            self.settings.nodata_value
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
                                self.__getValsAtPoint(self.__qgPntFromShplyPnt(shplyPnt)),
                                self.settings.nodata_value
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
                        self.__getValsAtPoint(qgLastPnt),
                        self.settings.nodata_value
                        )
        segmentvertices.append(newVtx)
        segments.append(Segment(segmentCnter, segmentvertices))

        return segments

    def __qgPntFromShplyPnt(self, shapelyPnt):
        wkb_pnt = dumps(shapelyPnt)
        qg_geom = QgsGeometry()
        qg_geom.fromWkb(wkb_pnt)
        return qg_geom.asPoint()

    def __getValsAtPoint(self, pnt):

        vals = []

        for rObj in self.settings.mapData.rasters.selectedRasters():

            raster = rObj.grid

            #TODO!!!! QGIS BUG: QGIS 2.0.1: raster.noDataValue() = > AttributeError: 'QgsRasterLayer' object has no attribute 'noDataValue'
            if QGis.QGIS_VERSION_INT < 10900:
                nodata_val, valid_nodata = raster.noDataValue()
                if valid_nodata:
                    raster_val = nodata_val
                else:
                    #raster_val = float('nan')
                    raster_val = self.settings.nodata_value
            else:
                raster_val = self.settings.nodata_value

            #QgsMessageLog.logMessage('raster_val VOR identify:' + str(raster_val), 'VoGis')

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
                result, identify_dic = raster.identify(pnt)
                if result:
                    for band_name, pixel_value in identify_dic.iteritems():
                        #QgsMessageLog.logMessage('band_name:' + str(band_name), 'VoGis')
                        if str(band_name) == raster.band_name(1):
                            try:
                                #QgsMessageLog.logMessage('pixel_value:' + str(pixel_value), 'VoGis')
                                raster_val = float(pixel_value)
                            except ValueError:
                                #float('nan') #0
                                raster_val = self.settings.nodata_value
                                pass
            else:
                identify_result = raster.dataProvider().identify(pnt, 1)
                for bnd_nr, pix_val in identify_result.results().iteritems():
                    if 1 == bnd_nr:
                        try:
                            if pix_val is None:
                                raster_val = self.settings.nodata_value
                            else:
                                raster_val = float(pix_val)
                        #except ValueError:
                        except:
                            QgsMessageLog.logMessage('pix_val Exception: ' + str(pix_val), 'VoGis')
                            raster_val = self.settings.nodata_value
                            pass

            #QgsMessageLog.logMessage('raster_val NACH identify:' + str(raster_val), 'VoGis')

            vals.append(raster_val)

        #QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", str(vals))
        return vals
