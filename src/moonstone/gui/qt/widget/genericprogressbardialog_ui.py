# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/moonstone/src/resources/ui/qt/genericprogressbardialog.ui'
#
# Created: Wed May 15 15:27:34 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_GenericProgressBarDialog(object):
    def setupUi(self, GenericProgressBarDialog):
        GenericProgressBarDialog.setObjectName("GenericProgressBarDialog")
        GenericProgressBarDialog.resize(307, 148)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        GenericProgressBarDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(GenericProgressBarDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout2 = QtGui.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.loadingText = QtGui.QLabel(GenericProgressBarDialog)
        self.loadingText.setMaximumSize(QtCore.QSize(300, 32))
        self.loadingText.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadingText.setObjectName("loadingText")
        self.horizontalLayout2.addWidget(self.loadingText)
        self.loadingLabel = QtGui.QLabel(GenericProgressBarDialog)
        self.loadingLabel.setMaximumSize(QtCore.QSize(32, 32))
        self.loadingLabel.setText("")
        self.loadingLabel.setObjectName("loadingLabel")
        self.horizontalLayout2.addWidget(self.loadingLabel)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        self.progressBar = QtGui.QProgressBar(GenericProgressBarDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.stopButton = QtGui.QPushButton(GenericProgressBarDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/process-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon1)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        self.cancelButton = QtGui.QPushButton(GenericProgressBarDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon2)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(GenericProgressBarDialog)
        QtCore.QMetaObject.connectSlotsByName(GenericProgressBarDialog)

    def retranslateUi(self, GenericProgressBarDialog):
        GenericProgressBarDialog.setWindowTitle(QtGui.QApplication.translate("GenericProgressBarDialog", "Progress Bar", None, QtGui.QApplication.UnicodeUTF8))
        self.loadingText.setText(QtGui.QApplication.translate("GenericProgressBarDialog", "Loading...", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("GenericProgressBarDialog", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("GenericProgressBarDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    GenericProgressBarDialog = QtGui.QDialog()
    ui = Ui_GenericProgressBarDialog()
    ui.setupUi(GenericProgressBarDialog)
    GenericProgressBarDialog.show()
    sys.exit(app.exec_())

