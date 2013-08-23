class Profile:

    def __init__(self, id, segments):
        self.id = id
        self.segments = segments

    def writeHeader(self, selectedRasters, hekto, attribs, delimiter):
        #Profillaenge;Segmentlaenge;Rechtswert;Hochwert;
        #"Laser - Hoehenmodell Oberflaeche 1m";"Laser Hoehenmodell Gelaende1m";
        #Profilnummer;Segmentnummer;Punktnummer;Punktklasse;
        #Hektometer
        #ATTRIBUTE
        hdr = '{1}{0}{2}{0}{3}{0}{4}'.format(delimiter, 'Profillaenge', 'Segmentlaenge', 'Rechtswert', 'Hochwert')
        for r in selectedRasters:
            hdr += '{0}"{1}"'.format(delimiter, r.name)
        hdr += '{0}{1}{0}{2}{0}{3}{0}{4}'.format(delimiter, 'Profilnummer', 'Segmentnummer', 'Punktnummer', 'Punktklasse')
        if hekto is True:
            hdr += '{0}{1}'.format(delimiter, 'Hektometer')
        if attribs is True:
            for fldName in self.segments[0].vertices[0].attribNames:
                hdr += '{0}{1}'.format(delimiter, fldName)
        hdr += '\r\n'
        return hdr

    def toString(self, hekto, attribs, delimiter, decimalDelimiter):

        txt = ''
        oldSeg = None

        for idxS in range(len(self.segments)):
            s = self.segments[idxS]
            #letzten Punkt des vorigen Segements zusaetzliche als ersten Punkt
            #des neuen Segemnts schreiben
            if oldSeg is not None:
                txt += '{0}'.format(oldSeg.toStringLastVertex(hekto,
                                                              attribs,
                                                              s.id,
                                                              delimiter,
                                                              decimalDelimiter
                                                              ))
            txt += '{0}'.format(s.toString(hekto,
                                           attribs,
                                           delimiter,
                                           decimalDelimiter
                                           ))
            oldSeg = s

        return txt

    def toACadTxt(self, delimiter, decimalDelimiter):
        acadTxt = ''
        for s in self.segments:
          acadTxt += s.toACadTxt(delimiter, decimalDelimiter)
        return acadTxt
