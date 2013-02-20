# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/saveas.ui'
#
# Created: Tue Mar  6 18:01:46 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SaveAs(object):
    def setupUi(self, SaveAs):
        SaveAs.setObjectName("SaveAs")
        SaveAs.resize(263, 85)
        self.formLayout = QtGui.QFormLayout(SaveAs)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(SaveAs)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.name = QtGui.QLineEdit(SaveAs)
        self.name.setObjectName("name")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.name)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(SaveAs)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.okButton = QtGui.QPushButton(SaveAs)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.formLayout.setLayout(1, QtGui.QFormLayout.SpanningRole, self.horizontalLayout)

        self.retranslateUi(SaveAs)
        QtCore.QMetaObject.connectSlotsByName(SaveAs)

    def retranslateUi(self, SaveAs):
        SaveAs.setWindowTitle(QtGui.QApplication.translate("SaveAs", "Save as", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SaveAs", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("SaveAs", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("SaveAs", "Ok", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SaveAs = QtGui.QDialog()
    ui = Ui_SaveAs()
    ui.setupUi(SaveAs)
    SaveAs.show()
    sys.exit(app.exec_())

