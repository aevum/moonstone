# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/blendthickness.ui'
#
# Created: Tue Mar 13 14:57:06 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_BlendThickness(object):
    def setupUi(self, BlendThickness):
        BlendThickness.setObjectName("BlendThickness")
        BlendThickness.resize(344, 102)
        self.gridLayout = QtGui.QGridLayout(BlendThickness)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(BlendThickness)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.qualitySlider = QtGui.QSlider(BlendThickness)
        self.qualitySlider.setMaximum(9)
        self.qualitySlider.setSliderPosition(8)
        self.qualitySlider.setOrientation(QtCore.Qt.Horizontal)
        self.qualitySlider.setObjectName("qualitySlider")
        self.horizontalLayout.addWidget(self.qualitySlider)
        self.label_2 = QtGui.QLabel(BlendThickness)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.thicknessSlider = QtGui.QSlider(BlendThickness)
        self.thicknessSlider.setMaximum(30)
        self.thicknessSlider.setOrientation(QtCore.Qt.Horizontal)
        self.thicknessSlider.setObjectName("thicknessSlider")
        self.horizontalLayout.addWidget(self.thicknessSlider)
        self.thicknessLabel = QtGui.QLabel(BlendThickness)
        self.thicknessLabel.setObjectName("thicknessLabel")
        self.horizontalLayout.addWidget(self.thicknessLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(BlendThickness)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.okButton.setIcon(icon)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_2.addWidget(self.okButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 3, 1, 1)

        self.retranslateUi(BlendThickness)
        QtCore.QMetaObject.connectSlotsByName(BlendThickness)

    def retranslateUi(self, BlendThickness):
        BlendThickness.setWindowTitle(QtGui.QApplication.translate("BlendThickness", "Thickness", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("BlendThickness", "Quality:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("BlendThickness", "Thickness:", None, QtGui.QApplication.UnicodeUTF8))
        self.thicknessLabel.setText(QtGui.QApplication.translate("BlendThickness", "0.0mm", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("BlendThickness", "Close", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    BlendThickness = QtGui.QWidget()
    ui = Ui_BlendThickness()
    ui.setupUi(BlendThickness)
    BlendThickness.show()
    sys.exit(app.exec_())

