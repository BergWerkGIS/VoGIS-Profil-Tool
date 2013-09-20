#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bergw
#
# Copyright:   (c) bergw 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class SelectedSettings:


	def __init__(
		self
		, lineLayer
		, rasterLayers
		, pointInterval
		, numberOfPoints
		, useSelectedFeatures
		, lineType
		, xMin
		, yMin
		, xMax
		, yMax
		):

		self.LineLayer=lineLayer
		self.RasterLayers=rasterLayers
		self.PointInterval=pointInterval
		self.NumberOfPoints=numberOfPoints
		self.UseSelectedFeatures=useSelectedFeatures
		self.LineType=lineType
		self.XMin=xMin
		self.YMin=yMin
		self.XMax=xMax
		self.YMax=yMax



class EnumLineType:
	Unknown=0
	FromCoordinates=1
	FromDrawing=2
	FromFeature=3