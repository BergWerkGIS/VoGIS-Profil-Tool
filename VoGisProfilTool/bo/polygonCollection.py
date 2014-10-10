class PolygonCollection(object):
    """docstring for LineCollection"""
    def __init__(self):
        self.__polygons = []

    def addPolygon(self, polygon):
        self.__polygons.append(polygon)

    def getById(self, id):
        if len(self.__polygons) < 1:
            return None
        for l in self.__polygons:
            if l.id == id:
                return l

    def count(self):
        return len(self.__polygons)

    def polygons(self):
        return self.__polygons
