class Polygon:
    def __init__(self, id, name, polygon):
        self.id = id
        self.name = name
        self.polygon = polygon
        self.selected = False

    def toStr(self):
        return self.id + ": " + self.name
