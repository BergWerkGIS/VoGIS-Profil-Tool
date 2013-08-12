class Profile:

    def __init__(self, id, segments):
        self.id = id
        self.segments = segments

    def toString(self, delimiter, decimalDelimiter):

        txt = ''
        oldSeg = None

        for idxS in range(len(self.segments)):

            s = self.segments[idxS]

            #letzten Punkt des vorigen Segements zusaetzliche als ersten Punkt
            #des neuen Segemnts schreiben
            if oldSeg is not None:
                txt += '{0}'.format(oldSeg.toStringLastVertex(s.id, delimiter, decimalDelimiter))

            txt += '{0}'.format(s.toString(delimiter, decimalDelimiter))
            oldSeg = s

        return txt
