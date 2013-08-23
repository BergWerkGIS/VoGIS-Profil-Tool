class Segment:

    def __init__(self, id, vertices):
        self.id = id
        self.vertices = vertices

    def toString(self, hekto, attribs, delimiter, decimalDelimiter):

        txt = ''
        vCnt = len(self.vertices)
        for idxV in range(vCnt):
            txt += '{0}\r\n'.format(self.vertices[idxV].toString(hekto,
                                                                 attribs,
                                                                 delimiter,
                                                                 decimalDelimiter
                                                                 ))

        return txt

    def toStringLastVertex(self, hekto, attribs, segmentId, delimiter, decimalDelimiter):
        return '{0}\r\n'.format(self.vertices[len(self.vertices) - 1].toString2(hekto,
                                                                                attribs,
                                                                                0,
                                                                                segmentId,
                                                                                delimiter,
                                                                                decimalDelimiter
                                                                                ))

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        for v in self.vertices:
            acadTxt += v.toACadTxt(delimiter, decimalDelimiter)
        return acadTxt
