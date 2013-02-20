# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/slicethickness.ui'
#
# Created: Tue Mar 13 14:57:09 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SliceThickness(object):
    def setupUi(self, SliceThickness):
        SliceThickness.setObjectName("SliceThickness")
        SliceThickness.resize(167, 81)
        self.verticalLayout = QtGui.QVBoxLayout(SliceThickness)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(SliceThickness)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.thicknessSpin = QtGui.QDoubleSpinBox(SliceThickness)
        self.thicknessSpin.setObjectName("thicknessSpin")
        self.horizontalLayout.addWidget(self.thicknessSpin)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(SliceThickness)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_2.addWidget(self.okButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(SliceThickness)
        QtCore.QMetaObject.connectSlotsByName(SliceThickness)

    def retranslateUi(self, SliceThickness):
        SliceThickness.setWindowTitle(QtGui.QApplication.translate("SliceThickness", "Slice Distance", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SliceThickness", "Distance:", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("SliceThickness", "Close", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SliceThickness = QtGui.QWidget()
    ui = Ui_SliceThickness()
    ui.setupUi(SliceThickness)
    SliceThickness.show()
    sys.exit(app.exec_())

