# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\bergw\.qgis\python\plugins\VoGisProfilTool\ui_vogisprofileplot.ui'
#
# Created: Mon Aug 06 15:57:41 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_VoGisProfilePlot(object):
    def setupUi(self, VoGisProfilePlot):
        VoGisProfilePlot.setObjectName(_fromUtf8("VoGisProfilePlot"))
        VoGisProfilePlot.setWindowModality(QtCore.Qt.ApplicationModal)
        VoGisProfilePlot.resize(650, 400)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VoGisProfilePlot.sizePolicy().hasHeightForWidth())
        VoGisProfilePlot.setSizePolicy(sizePolicy)
        VoGisProfilePlot.setMinimumSize(QtCore.QSize(650, 400))
        VoGisProfilePlot.setFocusPolicy(QtCore.Qt.NoFocus)
        VoGisProfilePlot.setSizeGripEnabled(True)
        VoGisProfilePlot.setModal(True)
        self.gridLayout = QtGui.QGridLayout(VoGisProfilePlot)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.qwtPlot = QwtPlot(VoGisProfilePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwtPlot.sizePolicy().hasHeightForWidth())
        self.qwtPlot.setSizePolicy(sizePolicy)
        self.qwtPlot.setAutoFillBackground(False)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.gridLayout.addWidget(self.qwtPlot, 0, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.IDC_bFlip = QtGui.QPushButton(VoGisProfilePlot)
        self.IDC_bFlip.setObjectName(_fromUtf8("IDC_bFlip"))
        self.horizontalLayout.addWidget(self.IDC_bFlip)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.IDC_bExportGraphic = QtGui.QPushButton(VoGisProfilePlot)
        self.IDC_bExportGraphic.setObjectName(_fromUtf8("IDC_bExportGraphic"))
        self.horizontalLayout.addWidget(self.IDC_bExportGraphic)
        self.IDC_bExportTXT = QtGui.QPushButton(VoGisProfilePlot)
        self.IDC_bExportTXT.setObjectName(_fromUtf8("IDC_bExportTXT"))
        self.horizontalLayout.addWidget(self.IDC_bExportTXT)
        self.IDC_bExportSHP = QtGui.QPushButton(VoGisProfilePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IDC_bExportSHP.sizePolicy().hasHeightForWidth())
        self.IDC_bExportSHP.setSizePolicy(sizePolicy)
        self.IDC_bExportSHP.setObjectName(_fromUtf8("IDC_bExportSHP"))
        self.horizontalLayout.addWidget(self.IDC_bExportSHP)
        self.IDC_bExportXLS = QtGui.QPushButton(VoGisProfilePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IDC_bExportXLS.sizePolicy().hasHeightForWidth())
        self.IDC_bExportXLS.setSizePolicy(sizePolicy)
        self.IDC_bExportXLS.setObjectName(_fromUtf8("IDC_bExportXLS"))
        self.horizontalLayout.addWidget(self.IDC_bExportXLS)
        self.IDC_bClose = QtGui.QPushButton(VoGisProfilePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IDC_bClose.sizePolicy().hasHeightForWidth())
        self.IDC_bClose.setSizePolicy(sizePolicy)
        self.IDC_bClose.setObjectName(_fromUtf8("IDC_bClose"))
        self.horizontalLayout.addWidget(self.IDC_bClose)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.IDC_sliderZ = QtGui.QSlider(VoGisProfilePlot)
        self.IDC_sliderZ.setOrientation(QtCore.Qt.Vertical)
        self.IDC_sliderZ.setObjectName(_fromUtf8("IDC_sliderZ"))
        self.gridLayout.addWidget(self.IDC_sliderZ, 0, 0, 1, 1)

        self.retranslateUi(VoGisProfilePlot)
        QtCore.QObject.connect(self.IDC_bClose, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.accept)
        QtCore.QObject.connect(self.IDC_bExportGraphic, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.exportGraphic)
        QtCore.QObject.connect(self.IDC_bExportSHP, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.exportShp)
        QtCore.QObject.connect(self.IDC_bExportXLS, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.exportXls)
        QtCore.QObject.connect(self.IDC_bFlip, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.flipProfile)
        QtCore.QObject.connect(self.IDC_bExportTXT, QtCore.SIGNAL(_fromUtf8("clicked()")), VoGisProfilePlot.exportTxt)
        QtCore.QMetaObject.connectSlotsByName(VoGisProfilePlot)

    def retranslateUi(self, VoGisProfilePlot):
        VoGisProfilePlot.setWindowTitle(QtGui.QApplication.translate("VoGisProfilePlot", "VoGIS-Profiltool", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bFlip.setText(QtGui.QApplication.translate("VoGisProfilePlot", "Profilrichtung(en) umdrehen", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bExportGraphic.setText(QtGui.QApplication.translate("VoGisProfilePlot", "Grafik", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bExportTXT.setText(QtGui.QApplication.translate("VoGisProfilePlot", "Textdatei", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bExportSHP.setText(QtGui.QApplication.translate("VoGisProfilePlot", "Shapefile", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bExportXLS.setText(QtGui.QApplication.translate("VoGisProfilePlot", "csv-File (Für Excel)", None, QtGui.QApplication.UnicodeUTF8))
        self.IDC_bClose.setText(QtGui.QApplication.translate("VoGisProfilePlot", "Schließen", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import QwtPlot
