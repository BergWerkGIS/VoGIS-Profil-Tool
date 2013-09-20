# coding: iso-8859-15



#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bergw
#
# Copyright:   (c) bergw 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from shapely.wkb import loads
from shapely.wkb import dumps
from shapely.geometry import Point
import shapely.geos
import collections #ordereddic

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from math import *
from selectedsettings import EnumLineType


class CreateProfile:


	def __init__(
		self
		, interface
		, settings
		):

		self.InterFace=interface
		self.Settings=settings



	def create(self):

		profiles=[]


		#QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", 'CreateProfile:'+ str(self.Settings.CoordFeature))


		#line from coordinates or digitizing
		if self.Settings.CoordFeature != None:
			profiles.append(self.processFeature(None, self.Settings.CoordFeature))
			return profiles


		#all or seletected features from linelayer
		feat=QgsFeature()

		if self.Settings.UseSelectedFeatures:
			for feat in self.Settings.LineLayer.selectedFeatures():
				profiles.append(self.processFeature(self.Settings.LineLayer.dataProvider(), feat))
		else:
			provider = self.Settings.LineLayer.dataProvider()
			attribIndices = provider.attributeIndexes()
			provider.select(attribIndices)
			while(provider.nextFeature(feat)):
				profiles.append(self.processFeature(provider, feat ))

		return profiles



	def processFeature(self, provider, feat):

		geom=feat.geometry()

		if self.Settings.PointInterval == -1 and self.Settings.NumberOfPoints == -1:
			vertices=geom.asPolyline()
			return self.processFeatureVertices(vertices, self._getRasterNames(), self._getFields(provider, feat))
		else:
			return self.processEquiDistance(geom, self._getRasterNames(), self._getFields(provider, feat))



	def processEquiDistance(self, geom, rasterNames, fields):

		shapelyGeom=loads(geom.asWkb())

		shapelyVertices=[]
		for v in shapelyGeom.coords:
			shapelyVertices.append(Point(v[0], v[1]))

		if self.Settings.PointInterval <> -1:
			step=self.Settings.PointInterval
		else:
			step=shapelyGeom.length / (self.Settings.NumberOfPoints - 1)

		pnts=[]
		distances=[]
		rasterValues=[]

		distance = 0
		while distance < shapelyGeom.length:

			#process vertices also
			if distance > 0:
				prevDist = distance-step
				for vertex in shapelyVertices:
					vDist=shapelyGeom.project(vertex)
					if vDist > prevDist and vDist < distance:
						pnts.append(self.qgPntFromShapelyPnt(vertex))
						distances.append(vDist)

			shapelyPnt = shapelyGeom.interpolate(distance,False)
			pnts.append(self.qgPntFromShapelyPnt(shapelyPnt))
			distances.append(distance)
			distance+=step

		shapelyPnt=shapelyGeom.interpolate(shapelyGeom.length,False)
		pnts.append(self.qgPntFromShapelyPnt(shapelyPnt))
		distances.append(shapelyGeom.length)


		for pnt in pnts:
			rasterValues.append( self.getValsAtPoint(pnt))

		return [pnts,distances,rasterValues,rasterNames,fields]



	def processFeatureVertices(self, vertices, rasterNames, fields):
		pnts=[]
		distances=[]
		rasterValues=[]
		distance = 0
		oldVertex=None

		#work thru all vertices
		for vertex in vertices:

			#calculate distance
			if oldVertex==None:
				distance=0
			else:
				distance = distance + sqrt( vertex.sqrDist(oldVertex) )

			#QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", vertex.toString() + ' ' + str(distance))

			pnts.append(vertex)
			distances.append(distance)
			#get values from all rasters at vertex
			rasterValues.append( self.getValsAtPoint(vertex) )
			#add vertexvalues to collection
			oldVertex=vertex

		return [pnts,distances,rasterValues,rasterNames, fields]



	def _getFields(self,provider, feat):

		flds=collections.OrderedDict()

		#line was drawn or entered with coordinates
		if provider==None:
			return flds

		attrs = feat.attributeMap()

		for idx, fld in provider.fields().iteritems():
			flds[fld]=attrs[idx]

		return flds



	def _getRasterNames(self):

		rasterNames=[]

		for raster in self.Settings.RasterLayers:
			rasterNames.append(raster.name())

		return rasterNames



	def qgPntFromShapelyPnt(self, shapelyPnt):
		wkbPnt=dumps(shapelyPnt)
		qgGeom=QgsGeometry()
		qgGeom.fromWkb(wkbPnt)
		#qgFeat = QgsFeature()
		#qgFeat.setGeometry(qgGeom)

		return qgGeom.asPoint()



	def getValsAtPoint(self, pnt):

		vals=[]

		for raster in self.Settings.RasterLayers:
			noDataVal, validNoData=raster.noDataValue()
			if validNoData:
				rasterVal=noDataVal
			else:
				rasterVal=float('nan') #0


			#check if coordinate systems match
			if self.Settings.LineType==EnumLineType.FromFeature:
				if raster.crs() != self.Settings.LineLayer.crs():
					transform = QgsCoordinateTransform(self.Settings.LineLayer.crs(),raster.crs())
					pnt=transform.transform(pnt)
			else:
				if raster.crs() != self.InterFace.mapCanvas().mapRenderer().destinationCrs():
					transform = QgsCoordinateTransform(self.InterFace.mapCanvas().mapRenderer().destinationCrs(),raster.crs())
					pnt=transform.transform(pnt)

			result, identifyDic=raster.identify(pnt)
			if result:
				for bandName, pixelValue in identifyDic.iteritems():
					if str(bandName)==raster.bandName(1):
						try:
							rasterVal=float(pixelValue)
						except ValueError:
							rasterVal= 0 #float('nan') #0
							pass

			vals.append(rasterVal)

		#QMessageBox.warning(self.InterFace.mainWindow(), "VoGIS-Profiltool", str(vals))
		return vals

