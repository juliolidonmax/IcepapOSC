# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_settings.ui'
#
# Created: Tue Jun 25 08:50:57 2019
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        DialogSettings.setObjectName(_fromUtf8("DialogSettings"))
        DialogSettings.resize(559, 364)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DialogSettings)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.hl1 = QtGui.QHBoxLayout()
        self.hl1.setObjectName(_fromUtf8("hl1"))
        self.gbSampling = QtGui.QGroupBox(DialogSettings)
        self.gbSampling.setChecked(False)
        self.gbSampling.setObjectName(_fromUtf8("gbSampling"))
        self.glDataCollection = QtGui.QGridLayout(self.gbSampling)
        self.glDataCollection.setObjectName(_fromUtf8("glDataCollection"))
        self.labelGuiRate = QtGui.QLabel(self.gbSampling)
        self.labelGuiRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelGuiRate.setObjectName(_fromUtf8("labelGuiRate"))
        self.glDataCollection.addWidget(self.labelGuiRate, 2, 1, 1, 1)
        self.sbSampleRate = QtGui.QSpinBox(self.gbSampling)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sbSampleRate.sizePolicy().hasHeightForWidth())
        self.sbSampleRate.setSizePolicy(sizePolicy)
        self.sbSampleRate.setMinimumSize(QtCore.QSize(80, 0))
        self.sbSampleRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbSampleRate.setObjectName(_fromUtf8("sbSampleRate"))
        self.glDataCollection.addWidget(self.sbSampleRate, 0, 2, 1, 1)
        self.leGuiUpdateRate = QtGui.QLineEdit(self.gbSampling)
        self.leGuiUpdateRate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leGuiUpdateRate.sizePolicy().hasHeightForWidth())
        self.leGuiUpdateRate.setSizePolicy(sizePolicy)
        self.leGuiUpdateRate.setMinimumSize(QtCore.QSize(80, 0))
        self.leGuiUpdateRate.setMaximumSize(QtCore.QSize(80, 16777215))
        self.leGuiUpdateRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.leGuiUpdateRate.setObjectName(_fromUtf8("leGuiUpdateRate"))
        self.glDataCollection.addWidget(self.leGuiUpdateRate, 2, 2, 1, 1)
        self.labelSampleRate = QtGui.QLabel(self.gbSampling)
        self.labelSampleRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelSampleRate.setObjectName(_fromUtf8("labelSampleRate"))
        self.glDataCollection.addWidget(self.labelSampleRate, 0, 1, 1, 1)
        self.sbDumpRate = QtGui.QSpinBox(self.gbSampling)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sbDumpRate.sizePolicy().hasHeightForWidth())
        self.sbDumpRate.setSizePolicy(sizePolicy)
        self.sbDumpRate.setMinimumSize(QtCore.QSize(80, 0))
        self.sbDumpRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDumpRate.setObjectName(_fromUtf8("sbDumpRate"))
        self.glDataCollection.addWidget(self.sbDumpRate, 1, 2, 1, 1)
        self.labelDumpRate = QtGui.QLabel(self.gbSampling)
        self.labelDumpRate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelDumpRate.setObjectName(_fromUtf8("labelDumpRate"))
        self.glDataCollection.addWidget(self.labelDumpRate, 1, 1, 1, 1)
        self.hl1.addWidget(self.gbSampling)
        self.gbXAxis = QtGui.QGroupBox(DialogSettings)
        self.gbXAxis.setObjectName(_fromUtf8("gbXAxis"))
        self.glXAxis = QtGui.QGridLayout(self.gbXAxis)
        self.glXAxis.setObjectName(_fromUtf8("glXAxis"))
        self.labelXAxisLength = QtGui.QLabel(self.gbXAxis)
        self.labelXAxisLength.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelXAxisLength.setObjectName(_fromUtf8("labelXAxisLength"))
        self.glXAxis.addWidget(self.labelXAxisLength, 0, 0, 1, 1)
        self.sbLenAxisX = QtGui.QSpinBox(self.gbXAxis)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sbLenAxisX.sizePolicy().hasHeightForWidth())
        self.sbLenAxisX.setSizePolicy(sizePolicy)
        self.sbLenAxisX.setMinimumSize(QtCore.QSize(80, 0))
        self.sbLenAxisX.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbLenAxisX.setObjectName(_fromUtf8("sbLenAxisX"))
        self.glXAxis.addWidget(self.sbLenAxisX, 0, 1, 1, 1)
        self.hl1.addWidget(self.gbXAxis)
        self.verticalLayout_2.addLayout(self.hl1)
        self.hl2 = QtGui.QHBoxLayout()
        self.hl2.setObjectName(_fromUtf8("hl2"))
        self.gbAutoSave = QtGui.QGroupBox(DialogSettings)
        self.gbAutoSave.setMinimumSize(QtCore.QSize(0, 0))
        self.gbAutoSave.setObjectName(_fromUtf8("gbAutoSave"))
        self.gridLayout = QtGui.QGridLayout(self.gbAutoSave)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cbAppend = QtGui.QCheckBox(self.gbAutoSave)
        self.cbAppend.setText(_fromUtf8(""))
        self.cbAppend.setObjectName(_fromUtf8("cbAppend"))
        self.gridLayout.addWidget(self.cbAppend, 1, 1, 1, 1)
        self.labelAutoSaveFolder = QtGui.QLabel(self.gbAutoSave)
        self.labelAutoSaveFolder.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelAutoSaveFolder.setObjectName(_fromUtf8("labelAutoSaveFolder"))
        self.gridLayout.addWidget(self.labelAutoSaveFolder, 3, 0, 1, 1)
        self.leDataFolder = QtGui.QLineEdit(self.gbAutoSave)
        self.leDataFolder.setMinimumSize(QtCore.QSize(200, 0))
        self.leDataFolder.setObjectName(_fromUtf8("leDataFolder"))
        self.gridLayout.addWidget(self.leDataFolder, 3, 1, 1, 1)
        self.cbUseAutoSave = QtGui.QCheckBox(self.gbAutoSave)
        self.cbUseAutoSave.setText(_fromUtf8(""))
        self.cbUseAutoSave.setObjectName(_fromUtf8("cbUseAutoSave"))
        self.gridLayout.addWidget(self.cbUseAutoSave, 0, 1, 1, 1)
        self.btnOpenFolderDlg = QtGui.QPushButton(self.gbAutoSave)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOpenFolderDlg.sizePolicy().hasHeightForWidth())
        self.btnOpenFolderDlg.setSizePolicy(sizePolicy)
        self.btnOpenFolderDlg.setMaximumSize(QtCore.QSize(32, 32))
        self.btnOpenFolderDlg.setAutoDefault(False)
        self.btnOpenFolderDlg.setObjectName(_fromUtf8("btnOpenFolderDlg"))
        self.gridLayout.addWidget(self.btnOpenFolderDlg, 3, 2, 1, 1)
        self.sbAutoSaveInterval = QtGui.QSpinBox(self.gbAutoSave)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sbAutoSaveInterval.sizePolicy().hasHeightForWidth())
        self.sbAutoSaveInterval.setSizePolicy(sizePolicy)
        self.sbAutoSaveInterval.setMinimumSize(QtCore.QSize(80, 0))
        self.sbAutoSaveInterval.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbAutoSaveInterval.setObjectName(_fromUtf8("sbAutoSaveInterval"))
        self.gridLayout.addWidget(self.sbAutoSaveInterval, 2, 1, 1, 1)
        self.labelUseAutoSave = QtGui.QLabel(self.gbAutoSave)
        self.labelUseAutoSave.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelUseAutoSave.setObjectName(_fromUtf8("labelUseAutoSave"))
        self.gridLayout.addWidget(self.labelUseAutoSave, 0, 0, 1, 1)
        self.labelAppend = QtGui.QLabel(self.gbAutoSave)
        self.labelAppend.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelAppend.setObjectName(_fromUtf8("labelAppend"))
        self.gridLayout.addWidget(self.labelAppend, 1, 0, 1, 1)
        self.labelAutoSaveInterval = QtGui.QLabel(self.gbAutoSave)
        self.labelAutoSaveInterval.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelAutoSaveInterval.setObjectName(_fromUtf8("labelAutoSaveInterval"))
        self.gridLayout.addWidget(self.labelAutoSaveInterval, 2, 0, 1, 1)
        self.hl2.addWidget(self.gbAutoSave)
        self.verticalLayout_2.addLayout(self.hl2)
        self.bbApplyClose = QtGui.QDialogButtonBox(DialogSettings)
        self.bbApplyClose.setOrientation(QtCore.Qt.Horizontal)
        self.bbApplyClose.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close)
        self.bbApplyClose.setCenterButtons(True)
        self.bbApplyClose.setObjectName(_fromUtf8("bbApplyClose"))
        self.verticalLayout_2.addWidget(self.bbApplyClose)

        self.retranslateUi(DialogSettings)
        QtCore.QObject.connect(self.bbApplyClose, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogSettings.accept)
        QtCore.QObject.connect(self.bbApplyClose, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogSettings)

    def retranslateUi(self, DialogSettings):
        DialogSettings.setWindowTitle(_translate("DialogSettings", "IcePapOSC Settings", None))
        self.gbSampling.setTitle(_translate("DialogSettings", "Data Collection", None))
        self.labelGuiRate.setText(_translate("DialogSettings", "GUI Update Rate [ms]", None))
        self.labelSampleRate.setText(_translate("DialogSettings", "Sample Rate [ms]", None))
        self.labelDumpRate.setText(_translate("DialogSettings", "Dump Rate [samples/dump]", None))
        self.gbXAxis.setTitle(_translate("DialogSettings", "X-axis", None))
        self.labelXAxisLength.setText(_translate("DialogSettings", "Default Length [sec]", None))
        self.gbAutoSave.setTitle(_translate("DialogSettings", "Auto Save (filename: IcepapOSC_<date>_<time>.csv)", None))
        self.labelAutoSaveFolder.setText(_translate("DialogSettings", "Folder", None))
        self.btnOpenFolderDlg.setText(_translate("DialogSettings", "...", None))
        self.labelUseAutoSave.setText(_translate("DialogSettings", "Enable", None))
        self.labelAppend.setText(_translate("DialogSettings", "Use Single File", None))
        self.labelAutoSaveInterval.setText(_translate("DialogSettings", "Interval [minutes]", None))

