class ChartPoint:

    def __init__(self, xpixel=0, ypixel=0, xdata=0, ydata=0):
        self.xpixel = xpixel
        self.ypixel = ypixel
        self.xdata = xdata
        self.ydata = ydata


    def toString(self):
        return 'pixel:{0}/{1} data:{2}/{3}'.format(
                                        self.xpixel,
                                        self.ypixel,
                                        self.xdata,
                                        self.ydata)
