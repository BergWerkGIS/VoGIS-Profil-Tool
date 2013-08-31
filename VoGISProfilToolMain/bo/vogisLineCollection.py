from matplotlib.collections import LineCollection


class vogisLineCollection(LineCollection):

    def __init__(self, coords, plotSegments, linewidths, linestyle, colors, picker):
        LineCollection.__init__(self,
                                plotSegments,
                                linewidths=linewidths,
                                linestyle=linestyle,
                                colors=colors,
                                picker=picker
                                )
