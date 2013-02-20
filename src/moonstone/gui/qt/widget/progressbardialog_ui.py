# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/progressbardialog.ui'
#
# Created: Tue Mar 13 14:24:32 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ProgressBarDialog(object):
    def setupUi(self, ProgressBarDialog):
        ProgressBarDialog.setObjectName("ProgressBarDialog")
        ProgressBarDialog.resize(393, 157)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ProgressBarDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ProgressBarDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadingText = QtGui.QLabel(ProgressBarDialog)
        self.loadingText.setObjectName("loadingText")
        self.verticalLayout.addWidget(self.loadingText)
        self.progressBar = QtGui.QProgressBar(ProgressBarDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.stopButton = QtGui.QPushButton(ProgressBarDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/process-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon1)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        self.cancelButton = QtGui.QPushButton(ProgressBarDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon2)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ProgressBarDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressBarDialog)

    def retranslateUi(self, ProgressBarDialog):
        ProgressBarDialog.setWindowTitle(QtGui.QApplication.translate("ProgressBarDialog", "Progress Bar", None, QtGui.QApplication.UnicodeUTF8))
        self.loadingText.setText(QtGui.QApplication.translate("ProgressBarDialog", "Loading...", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("ProgressBarDialog", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("ProgressBarDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ProgressBarDialog = QtGui.QDialog()
    ui = Ui_ProgressBarDialog()
    ui.setupUi(ProgressBarDialog)
    ProgressBarDialog.show()
    sys.exit(app.exec_())

