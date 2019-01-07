class RasterCollection(object):
    """docstring for RasterCollection"""

    def __init__(self):
        self.__rasters = []

    def addRaster(self, raster):
        self.__rasters.append(raster)

    def getById(self, id):
        if len(self.__rasters) < 1:
            return None
        for raster in self.__rasters:
            if raster.id == id:
                return raster

    def count(self):
        return len(self.__rasters)

    def rasters(self):
        return self.__rasters

    def selectedRasters(self):
        sel_rasters = []
        for raster in self.__rasters:
            if raster.selected is True:
                sel_rasters.append(raster)

        return sel_rasters
