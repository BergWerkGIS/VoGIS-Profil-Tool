class RasterCollection(object):
    """docstring for RasterCollection"""
    def __init__(self):
        self.__rasters = []

    def addRaster(self, raster):
        self.__rasters.append(raster)

    def getById(self, id):
        if len(self.__rasters) < 1:
            return None
        for r in self.__rasters:
            if r.id == id:
                return r

    def count(self):
        return len(self.__rasters)

    def rasters(self):
        return self.__rasters

    def selectedRasters(self):
        selR = []
        for idx, r in enumerate(self.__rasters):
            if r.selected is True:
                selR.append(r)

        return selR
