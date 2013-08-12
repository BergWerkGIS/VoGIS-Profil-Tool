class Segment:

    def __init__(self, id, vertices):
        self.id = id
        self.vertices = vertices

    def toString(self, delimiter, decimalDelimiter):

        txt = ''
        vCnt = len(self.vertices)
        for idxV in range(vCnt):
            txt += '{0}\r\n'.format(self.vertices[idxV].toString(delimiter, decimalDelimiter))

        return txt

    def toStringLastVertex(self, segmentId, delimiter, decimalDelimiter):
        return '{0}\r\n'.format(self.vertices[len(self.vertices) - 1].toString2(0, segmentId, delimiter, decimalDelimiter))
