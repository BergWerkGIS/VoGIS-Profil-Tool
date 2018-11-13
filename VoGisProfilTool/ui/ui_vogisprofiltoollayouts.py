# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_vogisprofiltoollayouts.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VoGISProfilToolLayouts(object):
    def setupUi(self, VoGISProfilToolLayouts):
        VoGISProfilToolLayouts.setObjectName("VoGISProfilToolLayouts")
        VoGISProfilToolLayouts.resize(298, 76)
        self.gridLayout = QtWidgets.QGridLayout(VoGISProfilToolLayouts)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(VoGISProfilToolLayouts)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbLayouts = QtWidgets.QComboBox(VoGISProfilToolLayouts)
        self.cmbLayouts.setObjectName("cmbLayouts")
        self.gridLayout.addWidget(self.cmbLayouts, 0, 1, 1, 1)
        self.dialogButtonBox = QtWidgets.QDialogButtonBox(VoGISProfilToolLayouts)
        self.dialogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialogButtonBox.setObjectName("dialogButtonBox")
        self.gridLayout.addWidget(self.dialogButtonBox, 1, 0, 1, 2)

        self.retranslateUi(VoGISProfilToolLayouts)
        self.dialogButtonBox.accepted.connect(VoGISProfilToolLayouts.accept)
        self.dialogButtonBox.rejected.connect(VoGISProfilToolLayouts.reject)
        QtCore.QMetaObject.connectSlotsByName(VoGISProfilToolLayouts)

    def retranslateUi(self, VoGISProfilToolLayouts):
        _translate = QtCore.QCoreApplication.translate
        VoGISProfilToolLayouts.setWindowTitle(_translate("VoGISProfilToolLayouts", "Layout wählen"))
        self.label.setText(_translate("VoGISProfilToolLayouts", "Layout verwenden"))

