# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_vogisprofiltoolscale.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VoGISProfilToolScale(object):
    def setupUi(self, VoGISProfilToolScale):
        VoGISProfilToolScale.setObjectName("VoGISProfilToolScale")
        VoGISProfilToolScale.resize(184, 105)
        self.gridLayout = QtWidgets.QGridLayout(VoGISProfilToolScale)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(VoGISProfilToolScale)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbScale = QtWidgets.QComboBox(VoGISProfilToolScale)
        self.cmbScale.setEditable(True)
        self.cmbScale.setObjectName("cmbScale")
        self.cmbScale.addItem("")
        self.cmbScale.addItem("")
        self.cmbScale.addItem("")
        self.cmbScale.addItem("")
        self.cmbScale.addItem("")
        self.gridLayout.addWidget(self.cmbScale, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(VoGISProfilToolScale)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cmbDpi = QtWidgets.QComboBox(VoGISProfilToolScale)
        self.cmbDpi.setEditable(True)
        self.cmbDpi.setObjectName("cmbDpi")
        self.cmbDpi.addItem("")
        self.cmbDpi.addItem("")
        self.cmbDpi.addItem("")
        self.cmbDpi.addItem("")
        self.cmbDpi.addItem("")
        self.gridLayout.addWidget(self.cmbDpi, 1, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(VoGISProfilToolScale)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(VoGISProfilToolScale)
        self.buttonBox.accepted.connect(VoGISProfilToolScale.accept)
        self.buttonBox.rejected.connect(VoGISProfilToolScale.reject)
        QtCore.QMetaObject.connectSlotsByName(VoGISProfilToolScale)

    def retranslateUi(self, VoGISProfilToolScale):
        _translate = QtCore.QCoreApplication.translate
        VoGISProfilToolScale.setWindowTitle(_translate("VoGISProfilToolScale", "Speichern mit Maßstab/DPI"))
        self.label.setText(_translate("VoGISProfilToolScale", "Maßstab"))
        self.cmbScale.setItemText(0, _translate("VoGISProfilToolScale", "1:500"))
        self.cmbScale.setItemText(1, _translate("VoGISProfilToolScale", "1:1000"))
        self.cmbScale.setItemText(2, _translate("VoGISProfilToolScale", "1:2000"))
        self.cmbScale.setItemText(3, _translate("VoGISProfilToolScale", "1:5000"))
        self.cmbScale.setItemText(4, _translate("VoGISProfilToolScale", "1:10000"))
        self.label_2.setText(_translate("VoGISProfilToolScale", "DPI"))
        self.cmbDpi.setItemText(0, _translate("VoGISProfilToolScale", "72"))
        self.cmbDpi.setItemText(1, _translate("VoGISProfilToolScale", "96"))
        self.cmbDpi.setItemText(2, _translate("VoGISProfilToolScale", "150"))
        self.cmbDpi.setItemText(3, _translate("VoGISProfilToolScale", "300"))
        self.cmbDpi.setItemText(4, _translate("VoGISProfilToolScale", "600"))

