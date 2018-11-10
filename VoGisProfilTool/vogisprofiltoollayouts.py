# -*- coding: utf-8 -*-

from VoGisProfilTool.ui.ui_vogisprofiltoollayouts import Ui_VoGISProfilToolLayouts

from qgis.PyQt.QtWidgets import QDialog


class VoGISProfilToolLayoutsDialog(QDialog):
    def __init__(self, parent, layouts):
        QDialog.__init__(self, parent)

        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolLayouts()
        self.ui.setupUi(self)

        for l in layouts:
            self.ui.cmbLayouts.addItem(l.name())
