class ZVal:
    def __init__(self):
        self.rasterVals = {}

    def add(self, rasterId, rasterVal):
        self.rasterVals[rasterId] = rasterVal

    def getRasterVal(self, rasterId):
        return self.rasterVals[rasterId]

    def getAllRasterVals(self):
        return self.rasterVals
