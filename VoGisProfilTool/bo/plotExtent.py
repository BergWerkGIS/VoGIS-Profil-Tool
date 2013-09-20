class PlotExtent:

    def __init__(self, xmin=99999, ymin=99999, xmax=-99999, ymax=-99999):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def union(self, pExt):
        if self.xmin > pExt.xmin:
            self.xmin = pExt.xmin
        if self.ymin > pExt.ymin:
            self.ymin = pExt.ymin
        if self.xmax < pExt.xmax:
            self.xmax = pExt.xmax
        if self.ymax < pExt.ymax:
            self.ymax = pExt.ymax

    def expand(self, distance=50):
        self.xmin -= distance
        self.ymin -= distance
        self.xmax += distance
        self.ymax += distance

    def toString(self):
        return '{0}/{1} {2}/{3}'.format(self.xmin, self.ymin, self.xmax, self.ymax)
