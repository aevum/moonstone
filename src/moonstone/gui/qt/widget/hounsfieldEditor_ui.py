# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igorznt/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/hounsfieldEditor.ui'
#
# Created: Thu Sep 27 18:15:05 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_HounsfieldEditor(object):
    def setupUi(self, HounsfieldEditor):
        HounsfieldEditor.setObjectName("HounsfieldEditor")
        HounsfieldEditor.resize(444, 479)
        self.verticalLayout_3 = QtGui.QVBoxLayout(HounsfieldEditor)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scalesCombo = QtGui.QComboBox(HounsfieldEditor)
        self.scalesCombo.setObjectName("scalesCombo")
        self.horizontalLayout.addWidget(self.scalesCombo)
        self.cancelButton = QtGui.QPushButton(HounsfieldEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/process-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.newScaleButton = QtGui.QPushButton(HounsfieldEditor)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newScaleButton.setIcon(icon1)
        self.newScaleButton.setObjectName("newScaleButton")
        self.horizontalLayout.addWidget(self.newScaleButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deleteScaleButton = QtGui.QPushButton(HounsfieldEditor)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteScaleButton.setIcon(icon2)
        self.deleteScaleButton.setObjectName("deleteScaleButton")
        self.horizontalLayout.addWidget(self.deleteScaleButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(HounsfieldEditor)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.groupBox_3 = QtGui.QGroupBox(HounsfieldEditor)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.typeCombo = QtGui.QComboBox(self.groupBox_3)
        self.typeCombo.setObjectName("typeCombo")
        self.horizontalLayout_2.addWidget(self.typeCombo)
        self.editButton = QtGui.QPushButton(self.groupBox_3)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-export.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editButton.setIcon(icon3)
        self.editButton.setObjectName("editButton")
        self.horizontalLayout_2.addWidget(self.editButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.groupBox_2 = QtGui.QGroupBox(HounsfieldEditor)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.okButton = QtGui.QPushButton(HounsfieldEditor)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon4)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_3.addWidget(self.okButton)
        self.saveButton = QtGui.QPushButton(HounsfieldEditor)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon5)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_3.addWidget(self.saveButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.retranslateUi(HounsfieldEditor)
        QtCore.QMetaObject.connectSlotsByName(HounsfieldEditor)

    def retranslateUi(self, HounsfieldEditor):
        HounsfieldEditor.setWindowTitle(QtGui.QApplication.translate("HounsfieldEditor", "Hounsfield Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.newScaleButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteScaleButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("HounsfieldEditor", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("HounsfieldEditor", "Transfer Function", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("HounsfieldEditor", "Save", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    HounsfieldEditor = QtGui.QWidget()
    ui = Ui_HounsfieldEditor()
    ui.setupUi(HounsfieldEditor)
    HounsfieldEditor.show()
    sys.exit(app.exec_())

