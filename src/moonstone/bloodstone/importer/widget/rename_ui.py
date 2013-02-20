# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../src/importer/resources/ui/qt/rename.ui'
#
# Created: Mon Jan  9 10:57:26 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Rename(object):
    def setupUi(self, Rename):
        Rename.setObjectName("Rename")
        Rename.resize(259, 103)
        self.verticalLayout = QtGui.QVBoxLayout(Rename)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(Rename)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.newName = QtGui.QLineEdit(Rename)
        self.newName.setObjectName("newName")
        self.verticalLayout.addWidget(self.newName)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Cancel = QtGui.QPushButton(Rename)
        self.Cancel.setObjectName("Cancel")
        self.horizontalLayout.addWidget(self.Cancel)
        self.Ok = QtGui.QPushButton(Rename)
        self.Ok.setObjectName("Ok")
        self.horizontalLayout.addWidget(self.Ok)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Rename)
        QtCore.QMetaObject.connectSlotsByName(Rename)

    def retranslateUi(self, Rename):
        Rename.setWindowTitle(QtGui.QApplication.translate("Rename", "Rename", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Rename", "Write the name bellow:", None, QtGui.QApplication.UnicodeUTF8))
        self.Cancel.setText(QtGui.QApplication.translate("Rename", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.Ok.setText(QtGui.QApplication.translate("Rename", "Ok", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Rename = QtGui.QWidget()
    ui = Ui_Rename()
    ui.setupUi(Rename)
    Rename.show()
    sys.exit(app.exec_())

