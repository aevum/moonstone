# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/moonstone/ilsa/plugins/contrastandbrightness/resources/ui/qt/contrastandbrightnessproperties.ui'
#
# Created: Mon Mar 19 10:28:44 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ContrastAndBrightnessProperties(object):
    def setupUi(self, ContrastAndBrightnessProperties):
        ContrastAndBrightnessProperties.setObjectName("ContrastAndBrightnessProperties")
        ContrastAndBrightnessProperties.resize(183, 500)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/step_object_Controller.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ContrastAndBrightnessProperties.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(ContrastAndBrightnessProperties)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtGui.QWidget(ContrastAndBrightnessProperties)
        self.widget.setObjectName("widget")
        self.formLayout = QtGui.QFormLayout(self.widget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.contrastLabel = QtGui.QLabel(self.widget)
        self.contrastLabel.setObjectName("contrastLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.contrastLabel)
        self.contrastSlider = QtGui.QSlider(self.widget)
        self.contrastSlider.setOrientation(QtCore.Qt.Horizontal)
        self.contrastSlider.setObjectName("contrastSlider")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.contrastSlider)
        self.brightnessLabel = QtGui.QLabel(self.widget)
        self.brightnessLabel.setObjectName("brightnessLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.brightnessLabel)
        self.brightnessSlider = QtGui.QSlider(self.widget)
        self.brightnessSlider.setOrientation(QtCore.Qt.Horizontal)
        self.brightnessSlider.setObjectName("brightnessSlider")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.brightnessSlider)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.retranslateUi(ContrastAndBrightnessProperties)
        QtCore.QMetaObject.connectSlotsByName(ContrastAndBrightnessProperties)

    def retranslateUi(self, ContrastAndBrightnessProperties):
        ContrastAndBrightnessProperties.setWindowTitle(QtGui.QApplication.translate("ContrastAndBrightnessProperties", "Contrast And Brightnessaction Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.contrastLabel.setText(QtGui.QApplication.translate("ContrastAndBrightnessProperties", "Contrast", None, QtGui.QApplication.UnicodeUTF8))
        self.brightnessLabel.setText(QtGui.QApplication.translate("ContrastAndBrightnessProperties", "Brightness", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ContrastAndBrightnessProperties = QtGui.QWidget()
    ui = Ui_ContrastAndBrightnessProperties()
    ui.setupUi(ContrastAndBrightnessProperties)
    ContrastAndBrightnessProperties.show()
    sys.exit(app.exec_())

