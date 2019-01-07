# -*- coding: utf-8 -*-

import VoGisProfilTool.util.xlsxwriter as xlsxwriter

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import Qgis, QgsMessageLog


class ExportXls:

    def __init__(self, iface, fileName, settings, profiles, hekto, attribs, decimalDelimiter):
        self.iface = iface
        self.fileName = fileName
        self.settings = settings
        self.profiles = profiles
        self.hekto = hekto
        self.attribs = attribs
        self.decimalDelimiter = decimalDelimiter

    def create(self):
        workbook = xlsxwriter.Workbook(self.fileName)

        worksheet_1 = workbook.add_worksheet('Data')
        worksheet_1.set_paper(9)                        # A4
        worksheet_1.set_column('A:AL', 15)              # Spalten breiter machen

        format_center = workbook.add_format()
        format_center.set_align('center')
        format_float = workbook.add_format()
        format_float.set_align('right')
        format_float.set_num_format('0.00')
        format_nofloat = workbook.add_format()
        format_nofloat.set_align('right')
        format_nofloat.set_num_format('0')

        row = 0
        col = 0
        profilspalte = 0

        header = self.profiles[0].writeArrayHeader(self.settings.mapData.rasters.selectedRasters(),
                                                   self.hekto,
                                                   self.attribs)
        for kopfspalte in header:
            worksheet_1.write(row, col, kopfspalte, format_center)

            spalten_name_profil_nr = QApplication.translate('code', 'Profilnummer')
            QgsMessageLog.logMessage(u'spalten_name_profil_nr: {0}'.format(spalten_name_profil_nr), 'VoGis', Qgis.Info)

            if (kopfspalte == spalten_name_profil_nr):
                profilspalte = col

            col += 1

        row = 1
        col = 0
        previous_profile = 1

        profiles = []
        lines = []

        #TODO: aus profilspalte diagram_spalte erzeugen!
        diagram_spalte = "E"
        line_beginn = 1

        for profil in self.profiles:
            profilArray = profil.toArray(self.hekto, self.attribs, self.decimalDelimiter)
            profiles.append(profilArray)

            spalte = 0

            for segmente in profilArray:
                for vertex in segmente:
                    for eigenschaft in vertex:
                        if self.XlsFormat_NoFloat(header, spalte):
                            worksheet_1.write(row, col + spalte, eigenschaft, format_nofloat)
                        else:
                            worksheet_1.write(row, col + spalte, eigenschaft, format_float)

                        if spalte == profilspalte:
                            profile_ID = eigenschaft

                            if profile_ID == previous_profile:
                                previous_profile = eigenschaft
                            else:
                                lines.append('Data!${0}${1}:${0}${2}'.format(diagram_spalte,
                                                                             line_beginn,
                                                                             row))
                                line_beginn = row + 1
                                previous_profile = eigenschaft

                        spalte += 1

                        if spalte >= len(vertex):
                            spalte = 0
                            row += 1

        self.CreateXlsDiagram(workbook, lines)

        workbook.close()

    def CreateXlsDiagram(self, workbook, lines, name='Diagram'):
        if 1 == 1:
            return

        worksheet = workbook.add_worksheet(name)
        worksheet.set_paper(9)                        # A4

        chart = workbook.add_chart({'type': 'line'})

        #i = 0
        for line in lines:
            #worksheet.write(i, 0, line)
            #i += 1
            chart.add_series({
                'values': line
            })

        worksheet.insert_chart('B23', chart)

    def XlsFormat_NoFloat(self, header, spalte):
        nofloat = False
        if (header[spalte] == "Profilenumber") or (header[spalte] == "Profilnummer"):
            nofloat = True
        elif (header[spalte] == "Segmentnumber") or (header[spalte] == "Segmentnummer"):
            nofloat = True
        elif (header[spalte] == "Pointnumber") or (header[spalte] == "Punktnummer"):
            nofloat = True
        return nofloat
