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
from ..bo.intersection import Intersection
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
        self.util = Util(self.iface)
        self.intersections = []


    def abort(self):
        self.stop = True


    finished = pyqtSignal(object, object)
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
                self.finished.emit(profiles, self.intersections)
                return

            #Line aus gezeichneter Linie erstellen
            if self.settings.modeLine == enumModeLine.customLine:
                profiles.append(self.processFeature(None,
                                                    1,
                                                    1,
                                                    self.settings.mapData.customLine
                                                    )
                                )
                self.finished.emit(profiles, self.intersections)
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

                feats, err_msg = self.util.prepareFeatures(self.settings, provider, feats)

                if not err_msg is None:
                    #QMessageBox.critical(self.iface.mainWindow(), 'PREPARE ERROR', err_msg)
                    self.error.emit(err_msg)
                    self.finished.emit([], [])
                    return

                for feat in feats:
                    geom = feat.geometry()
                    if geom.isMultipart():
                        msg = QApplication.translate('code', 'Multipart Feature vorhanden! Option zum Explodieren verwenden.', None, QApplication.UnicodeUTF8)
                        self.error.emit(msg)
                        self.finished.emit([], [])
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

            self.finished.emit(profiles, self.intersections)
        except Exception, ex:
            self.error.emit(traceback.format_exc())
            self.finished.emit([], [])


    def processFeature(self, fields, profileId, layerId, feat):

        #QgsMessageLog.logMessage('processFeature', 'VoGis')
        geom = feat.geometry()
        if QGis.QGIS_VERSION_INT < 10900:
            segments = self.processVertices(fields, feat.attributeMap(), profileId, geom, layerId, feat.id())
        else:
            segments = self.processVertices(fields, feat.attributes(), profileId, geom, layerId, feat.id())

        #intersection with area
        #QgsMessageLog.logMessage(u'{0}'.format(dir(feat)), 'VoGis')
        line_geom = feat.geometry()
        if not self.settings.mapData.polygons is None:
            polys = self.settings.mapData.polygons.polygons()
            for poly in polys:
                if poly.selected is False:
                    continue
                poly_feats = self.util.get_features(poly.polygon)
                if len(poly_feats) < 1:
                    continue
                for poly_feat in poly_feats:
                    intersection = poly_feat.geometry().intersection(line_geom)
                    inter_geom_coll = intersection.asGeometryCollection()
                    for inter_geom in inter_geom_coll:
                        if QGis.WKBLineString != inter_geom.wkbType():
                            continue
                        inter_line = inter_geom.asPolyline()
                        from_x = inter_line[0][0]
                        from_y = inter_line[0][1]
                        from_pnt = QgsPoint(from_x, from_y)
                        from_z = self.__getValsAtPoint(from_pnt)
                        from_dist = self.__get_distance(feat, from_pnt)
                        to_x = inter_line[1][0]
                        to_y = inter_line[1][1]
                        to_pnt = QgsPoint(to_x, to_y)
                        to_z = self.__getValsAtPoint(to_pnt)
                        to_dist = self.__get_distance(feat, to_pnt)
                        bo_intersection = Intersection(
                                                       from_x,
                                                       from_y,
                                                       from_z,
                                                       from_dist,
                                                       to_x,
                                                       to_y,
                                                       to_z,
                                                       to_dist
                                                       )
                        self.intersections.append(bo_intersection)

        return Profile(profileId, segments)


    def __get_distance(self, line, qgis_pnt):
        shply_line = loads(line.geometry().asWkb())
        shply_pnt = Point(qgis_pnt.x(), qgis_pnt.y())
        return shply_line.project(shply_pnt)


    def processVertices(self, fields, attribMap, profileId, qgGeom, layerId, featId):

        #QgsMessageLog.logMessage('{0}: {1}'.format('processFeature',attribMap), 'VoGis')

        step = -1
        segment_counter = 1
        segments = []
        segmentvertices = []
        dist_segment = 0
        dist_total = 0
        qg_pnt_old = None
        vtx_type = None
        vtx_id = 1

        qg_line_vertices = qgGeom.asPolyline()
        shply_geom = loads(qgGeom.asWkb())
        shply_vertices = []
        #for shplyV in shply_geom.coords:
        for idx_vtx in range(1, len(shply_geom.coords) - 1):
            #shply_vertices.append(Point(shplyV[0], shplyV[1]))
            shply_vertices.append(Point(shply_geom.coords[idx_vtx][0], shply_geom.coords[idx_vtx][1]))

        if self.settings.modeVertices == enumModeVertices.equiDistant:
            step = self.settings.equiDistance
        else:
            step = shply_geom.length / (self.settings.vertexCnt - 1)

        #erster, echter Punkt der Geometrie
        qg_pnt_old = qg_line_vertices[0]
        vtx_type = enumVertexType.node
        new_vtx = Vertex(fields,
                        attribMap,
                        vtx_type,
                        qg_line_vertices[0].x(),
                        qg_line_vertices[0].y(),
                        profileId,
                        layerId,
                        featId,
                        segment_counter,
                        vtx_id,
                        dist_total,
                        dist_segment,
                        self.__getValsAtPoint(qg_line_vertices[0]),
                        self.settings.nodata_value
                        )
        segmentvertices.append(new_vtx)

        #QgsMessageLog.logMessage('GeomLength:' + str(shply_geom.length), 'VoGis')

        while dist_total < shply_geom.length:

            dist_segment += step
            dist_total += step

            #überprüfen, ob echter Vertex zwischen den
            # zu berechnenden Ṕrofilpunkten liegt
            #nur falls diese auch ausgegeben werden sollen
            if self.settings.nodesAndVertices is True:
                if dist_total > 0:
                    prev_dist = dist_total - step
                    for shply_vtx in shply_vertices:
                        vtx_dist = shply_geom.project(shply_vtx)
                        if vtx_dist > prev_dist and vtx_dist < dist_total:
                            qg_pnt = self.__qgPntFromShplyPnt(shply_vtx)
                            dist_qg_vertices = sqrt(qg_pnt.sqrDist(qg_pnt_old))
                            vtx_type = enumVertexType.vertex
                            vtx_id += 1
                            new_vtx = Vertex(fields,
                                            attribMap,
                                            vtx_type,
                                            shply_vtx.x,
                                            shply_vtx.y,
                                            profileId,
                                            layerId,
                                            featId,
                                            segment_counter,
                                            vtx_id,
                                            vtx_dist,
                                            dist_qg_vertices,
                                            self.__getValsAtPoint(qg_pnt),
                                            self.settings.nodata_value
                                            )
                            segmentvertices.append(new_vtx)
                            segments.append(Segment(segment_counter, segmentvertices))
                            #neues Segment beginnen
                            qg_pnt_old = self.__qgPntFromShplyPnt(shply_vtx)
                            segmentvertices = []
                            dist_segment -= dist_qg_vertices
                            segment_counter += 1

            #Profilpunkte berechnen
            #nur wenn noch unter Featurelaenge
            if dist_total < shply_geom.length:
                shply_pnt = shply_geom.interpolate(dist_total, False)
                vtx_type = enumVertexType.point
                vtx_id += 1
                new_vtx = Vertex(fields,
                                attribMap,
                                vtx_type,
                                shply_pnt.x,
                                shply_pnt.y,
                                profileId,
                                layerId,
                                featId,
                                segment_counter,
                                vtx_id,
                                dist_total,
                                dist_segment,
                                self.__getValsAtPoint(self.__qgPntFromShplyPnt(shply_pnt)),
                                self.settings.nodata_value
                                )
                segmentvertices.append(new_vtx)

        #letzter, echter Punkt der Geometrie
        qg_last_pnt = qg_line_vertices[len(qg_line_vertices)-1]
        #keine echten Knoten, nur berechnete -> letzter Pkt entspricht kompletter Laenge der Geometrie
        if self.settings.nodesAndVertices is False:
            dist_segment = shply_geom.length
        else:
            dist_segment = sqrt(qg_last_pnt.sqrDist(qg_pnt_old))
        vtx_type = enumVertexType.node
        vtx_id += 1
        new_vtx = Vertex(fields,
                        attribMap,
                        vtx_type,
                        qg_last_pnt.x(),
                        qg_last_pnt.y(),
                        profileId,
                        layerId,
                        featId,
                        segment_counter,
                        vtx_id,
                        shply_geom.length,
                        dist_segment,
                        self.__getValsAtPoint(qg_last_pnt),
                        self.settings.nodata_value
                        )
        segmentvertices.append(new_vtx)
        segments.append(Segment(segment_counter, segmentvertices))

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

            #QgsMessageLog.logMessage('raster_val NACH identify:' + str(raster_val), 'VoGis')

            vals.append(raster_val)

        #QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", str(vals))
        return vals
