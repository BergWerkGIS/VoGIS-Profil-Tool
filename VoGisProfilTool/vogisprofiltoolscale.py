# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QDialog

from qgis.core import QgsSettings

from VoGisProfilTool.ui.ui_vogisprofiltoolscale import Ui_VoGISProfilToolScale


class VoGISProfilToolScaleDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # Set up the user interface from Designer.
        self.ui = Ui_VoGISProfilToolScale()
        self.ui.setupUi(self)

        t = QgsSettings().value("vogisprofiltoolmain/scale", "")
        if t != "":
            self.ui.cmbScale.setCurrentText(t)

        t = QgsSettings().value("vogisprofiltoolmain/dpi", "")
        if t != "":
            self.ui.cmbDpi.setCurrentText(t)

    def accept(self):
        QgsSettings().setValue("vogisprofiltoolmain/scale", self.ui.cmbScale.currentText())
        QgsSettings().setValue("vogisprofiltoolmain/dpi", self.ui.cmbDpi.currentText())
        QDialog.accept(self)
