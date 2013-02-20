# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/hounsfieldColorSegmentEditor.ui'
#
# Created: Tue Mar  6 18:01:46 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_HounsfieldColorSegmentEditor(object):
    def setupUi(self, HounsfieldColorSegmentEditor):
        HounsfieldColorSegmentEditor.setObjectName("HounsfieldColorSegmentEditor")
        HounsfieldColorSegmentEditor.resize(418, 237)
        self.verticalLayout_2 = QtGui.QVBoxLayout(HounsfieldColorSegmentEditor)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtGui.QGroupBox(HounsfieldColorSegmentEditor)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.newPointButton = QtGui.QPushButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newPointButton.setIcon(icon)
        self.newPointButton.setObjectName("newPointButton")
        self.horizontalLayout.addWidget(self.newPointButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.scrollArea = QtGui.QScrollArea(self.groupBox)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 373, 120))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.cancelButton = QtGui.QPushButton(HounsfieldColorSegmentEditor)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.okButton = QtGui.QPushButton(HounsfieldColorSegmentEditor)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon2)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_2.addWidget(self.okButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(HounsfieldColorSegmentEditor)
        QtCore.QMetaObject.connectSlotsByName(HounsfieldColorSegmentEditor)

    def retranslateUi(self, HounsfieldColorSegmentEditor):
        HounsfieldColorSegmentEditor.setWindowTitle(QtGui.QApplication.translate("HounsfieldColorSegmentEditor", "Hounsfiel Color Segment Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("HounsfieldColorSegmentEditor", "Points", None, QtGui.QApplication.UnicodeUTF8))
        self.newPointButton.setText(QtGui.QApplication.translate("HounsfieldColorSegmentEditor", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("HounsfieldColorSegmentEditor", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("HounsfieldColorSegmentEditor", "OK", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    HounsfieldColorSegmentEditor = QtGui.QWidget()
    ui = Ui_HounsfieldColorSegmentEditor()
    ui.setupUi(HounsfieldColorSegmentEditor)
    HounsfieldColorSegmentEditor.show()
    sys.exit(app.exec_())

