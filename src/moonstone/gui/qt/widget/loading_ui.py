# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igorznt/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/loading.ui'
#
# Created: Thu Sep 27 18:12:03 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Loading(object):
    def setupUi(self, Loading):
        Loading.setObjectName("Loading")
        Loading.resize(278, 115)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Loading.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Loading)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadingText = QtGui.QLabel(Loading)
        self.loadingText.setObjectName("loadingText")
        self.verticalLayout.addWidget(self.loadingText)
        self.progressBar = QtGui.QProgressBar(Loading)
        self.progressBar.setToolTip("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Loading)
        QtCore.QMetaObject.connectSlotsByName(Loading)

    def retranslateUi(self, Loading):
        Loading.setWindowTitle(QtGui.QApplication.translate("Loading", "Moonstone :: Loading", None, QtGui.QApplication.UnicodeUTF8))
        self.loadingText.setText(QtGui.QApplication.translate("Loading", "Loading...", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Loading = QtGui.QDialog()
    ui = Ui_Loading()
    ui.setupUi(Loading)
    Loading.show()
    sys.exit(app.exec_())

